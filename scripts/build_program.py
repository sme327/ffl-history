"""Emit the facts behind one issue of The Program, the weekly matchup preview.

    python3 scripts/build_program.py --week 1 [--out data/program]

Reads the 2026 schedule and divisions (data/schedule_2026.csv,
data/divisions_2026.csv) plus the scraped history, and writes two files per
week: a JSON facts file and a markdown brief of ranked storyline candidates.
The brief is raw material — the published prose is written from it, not by it.

Current-season results are layered in from data/results_2026.csv (written by
scripts/fetch_week_lineups.py; one row per team) — only weeks before the
issue's own week, so a back issue never shows its own result. Week 1's issue
is pure history.

Lifetime series count every meeting, consolation games included (commissioner,
2026-09-15) — unlike the career win totals below, which exclude consolation.

Every matchup card gets the same treatment: a lifetime series line plus the
top-ranked facts. The ranker chooses which facts, never how much coverage.

THE EDITORIAL CONTRACT for the -copy.json notes (learned the hard way when a
footer claimed "neither man has ever led by more than a game or two" above a
fact line reading "Tom once led the series by 5"):
  1. Every quantitative or historical claim in a note — records, leads,
     streaks, frequency, margins, dates — must be verifiable from this
     script's facts JSON for the same card. Check the fact_pool before
     writing; never write from memory of the data.
  2. Notes run 25–35 words, two lines on the card, occasionally three.
  3. Dramatic is good; unverifiable is not.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

MILESTONE_WINS_STEP = 25
MILESTONE_POINTS_STEP = 2500
MILESTONE_POINTS_REACH = 150  # flag when within a strong week of the line


def read_csv(name: str) -> list[dict]:
    with open(DATA / name, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_manager_map() -> dict[tuple[str, str], str]:
    """(season, team_name) -> canonical manager, resolved by email when known."""
    email2canon = {
        r["email"].strip().lower(): r["canonical_name"]
        for r in read_csv("manager_lookup.csv")
        if r["email"].strip()
    }
    out = {}
    for r in read_csv("season_managers.csv"):
        canon = email2canon.get(r["email"].strip().lower()) or r["manager_name"].strip()
        out[(r["season"], r["team_name"].strip())] = canon
    return out


CURRENT_SEASON = 2026


def current_results(before_week: int | None) -> list[dict]:
    """data/results_2026.csv reshaped like weekly_matchups.csv rows, weeks < before_week."""
    path = DATA / f"results_{CURRENT_SEASON}.csv"
    if before_week is None or not path.exists():
        return []
    out = []
    for r in read_csv(path.name):
        if int(r["week"]) >= before_week:
            continue
        score, opp = float(r["score"]), float(r["opponent_score"])
        out.append({"season": str(CURRENT_SEASON), "week": r["week"], "team_name": r["team_name"],
                    "opponent": r["opponent"], "result": "Win" if score > opp else "Loss" if score < opp else "Tie",
                    "team_score": r["score"], "opponent_score": r["opponent_score"],
                    "is_bye": "false", "is_playoff": "false"})
    return out


def load_history(team2mgr, managers: set[str], before_week: int | None = None):
    """All games between current managers, chronological, deduped to one row per game."""
    games = []
    for r in read_csv("weekly_matchups.csv") + current_results(before_week):
        if r["is_bye"] == "true":
            continue
        a = team2mgr.get((r["season"], r["team_name"].strip()))
        b = team2mgr.get((r["season"], r["opponent"].strip()))
        if a not in managers or b not in managers or a >= b:  # keep one perspective
            continue
        games.append({
            "season": int(r["season"]), "week": int(r["week"]),
            "a": a, "b": b,
            "score_a": float(r["team_score"]), "score_b": float(r["opponent_score"]),
            "winner": a if r["result"] == "Win" else (b if r["result"] == "Loss" else None),
            "playoff": r["is_playoff"] == "true",
        })
    games.sort(key=lambda g: (g["season"], g["week"]))
    return games


def load_finals(team2mgr):
    finals = defaultdict(list)
    for r in read_csv("playoff_games.csv"):
        if r["bracket"] != "championship" or r["game_type"] != "final":
            continue
        a = team2mgr.get((r["season"], r["team_1"].strip()))
        b = team2mgr.get((r["season"], r["team_2"].strip()))
        w = team2mgr.get((r["season"], r["winner"].strip()))
        if a and b:
            finals[tuple(sorted([a, b]))].append({"season": int(r["season"]), "winner": w})
    return finals


def series_facts(a: str, b: str, games, finals) -> dict:
    """Everything the card ranker needs about one pair, from a's perspective."""
    pair = [g for g in games if {g["a"], g["b"]} == {a, b}]
    wins = {a: 0, b: 0}
    rs = {a: 0, b: 0, "ties": 0}
    po = {a: 0, b: 0, "ties": 0}
    ties = 0
    closest = biggest = high = low = None
    # Running series lead and win-run tracking, in chronological order
    lead_holder, max_lead = None, 0
    run_holder, run_len, run_start = None, 0, None
    best_run = None
    for g in pair:
        bucket = po if g["playoff"] else rs
        if g["winner"]:
            wins[g["winner"]] += 1
            bucket[g["winner"]] += 1
            if g["winner"] == run_holder:
                run_len += 1
            else:
                run_holder, run_len, run_start = g["winner"], 1, g["season"]
            if best_run is None or run_len > best_run["length"]:
                best_run = {"manager": run_holder, "length": run_len,
                            "start": run_start, "end": g["season"]}
            diff = wins[a] - wins[b]
            if abs(diff) > max_lead:
                max_lead, lead_holder = abs(diff), (a if diff > 0 else b)
        else:
            ties += 1
            bucket["ties"] += 1
            run_holder, run_len = None, 0
        margin = abs(g["score_a"] - g["score_b"])
        combined = g["score_a"] + g["score_b"]
        if g["winner"] and (closest is None or margin < closest[0]):
            closest = (margin, g)
        if biggest is None or margin > biggest[0]:
            biggest = (margin, g)
        if high is None or combined > high[0]:
            high = (combined, g)
        if low is None or combined < low[0]:
            low = (combined, g)
    streak_holder, streak_len = None, 0
    for g in reversed(pair):
        if not g["winner"]:
            break
        if streak_holder is None:
            streak_holder, streak_len = g["winner"], 1
        elif g["winner"] == streak_holder:
            streak_len += 1
        else:
            break
    # Recent form — guaranteed on every card once a series has real history
    # (5+ meetings): a live streak if one exists, otherwise the last-5 split.
    form_line = None
    decided = [g for g in pair if g["winner"]]
    if len(pair) > 4 and decided:
        if streak_len >= 3:
            form_line = f"{streak_holder} has won {streak_len} in a row"
        else:
            last5 = decided[-5:]
            counts = {}
            for g in last5:
                counts[g["winner"]] = counts.get(g["winner"], 0) + 1
            leader = max(counts, key=lambda m: counts[m])
            form_line = f"{leader} has won {counts[leader]} of the last {len(last5)}"
    def game_ref(entry):
        if entry is None:
            return None
        val, g = entry
        return {"value": round(val, 2), "season": g["season"], "week": g["week"],
                "winner": g["winner"],
                "score_hi": max(g["score_a"], g["score_b"]),
                "score_lo": min(g["score_a"], g["score_b"])}

    return {
        "form_line": form_line,
        "games": len(pair),
        "first_season": pair[0]["season"] if pair else None,
        "record": {a: wins[a], b: wins[b], "ties": ties},
        "record_rs": rs,
        "record_po": po,
        "playoff_meetings": sum(g["playoff"] for g in pair),
        "finals": finals.get(tuple(sorted([a, b])), []),
        "streak": {"manager": streak_holder, "length": streak_len} if streak_len > 1 else None,
        "best_run": best_run,
        "max_lead": {"manager": lead_holder, "lead": max_lead} if lead_holder else None,
        "last": pair[-1] if pair else None,
        "closest": game_ref(closest),
        "biggest": game_ref(biggest),
        "highest": game_ref(high),
        "lowest": game_ref(low),
    }


# Word-joiner (U+2060) on both sides of the en dash keeps a range or
# scoreline from breaking across lines on the card ("2006– / 08" must never
# happen).
NB_DASH = "⁠–⁠"


def year_span(y1: int, y2: int) -> str:
    """Sports-publication year ranges: 2006–08, 2016–20, 1998–2004."""
    if y1 == y2:
        return str(y1)
    tail = str(y2)[2:] if str(y1)[:2] == str(y2)[:2] else str(y2)
    return f"{y1}{NB_DASH}{tail}"


def scoreline(hi: float, lo: float) -> str:
    return f"{hi}{NB_DASH}{lo}"


def fact_candidates(a: str, b: str, f: dict) -> list[dict]:
    """Typed fact candidates for one card, each {category, priority, text}.

    Texts read as a sports historian's sentences, never "category: value".
    Categories exist so the selector never shows two facts that say the same
    thing, and so nothing repeats what the card hero already carries: the
    lifetime record and the RS/playoff split. Total-meetings and dead-even
    facts are deliberately absent for the same reason."""
    cands = []

    def add(category, priority, text):
        cands.append({"category": category, "priority": priority, "text": text})

    # Priorities follow the editorial tiers: unique history and championship
    # meetings first, then streaks/leads, then single-game extremes, then
    # recent form, then contextual color. Tier-6 material never fills a
    # fourth slot (see select_storylines).
    if not f["games"]:
        add("first_meeting", 100, "the first meeting ever between these two")
        return cands

    # A live streak of 3+ is a Tier-3 streak fact; a last-5 split is Tier-5
    # recent form.
    if f["form_line"]:
        live = f["streak"]["length"] if f["streak"] else 0
        add("form", 60 if live >= 3 else 36, f["form_line"])

    if f["finals"]:
        if len(f["finals"]) == 1:
            fin = f["finals"][0]
            loser = b if fin["winner"] == a else a
            add("title_game", 100, f"a rematch of the {fin['season']} championship final — {fin['winner']} beat {loser} for the title")
        else:
            winners = [fin["winner"] for fin in f["finals"]]
            years = ", ".join(str(fin["season"]) for fin in f["finals"])
            if len(set(winners)) == 1:
                verdict = f"{winners[0]} won both" if len(winners) == 2 else f"{winners[0]} won them all"
            else:
                counts = {w: winners.count(w) for w in dict.fromkeys(winners)}
                verdict = "split " + "–".join(str(n) for n in counts.values())
            add("title_game", 100, f"they've met {len(f['finals'])} times for the championship ({years}) — {verdict}")

    if f["last"] and f["last"]["winner"]:
        g = f["last"]
        margin = round(abs(g["score_a"] - g["score_b"]), 2)
        loser = b if g["winner"] == a else a
        if margin <= 3:
            add("last_meeting", 56, f"{loser} lost their last meeting by just {margin} points")
        elif margin >= 45:
            # A lopsided last meeting is a live grudge, not trivia
            add("last_meeting", 56, f"{g['winner']} won the last meeting by {margin} points")
        else:
            add("last_meeting", 20,
                f"{g['winner']} won the most recent meeting "
                f"{scoreline(max(g['score_a'], g['score_b']), min(g['score_a'], g['score_b']))} in {g['season']}")

    if f["games"] < 10:
        ordinals = [None, None, "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"]
        add("young_series", 28, f"this is only their {ordinals[f['games'] + 1]} meeting")

    run = f["best_run"]
    live = f["streak"]["length"] if f["streak"] else 0
    if run and run["length"] >= 4 and run["length"] > live:
        add("longest_run", 62,
            f"{run['manager']}'s {run['length']} straight from {year_span(run['start'], run['end'])} is the longest streak in the series")

    lead = f["max_lead"]
    rec = f["record"]
    if lead and lead["lead"] >= 4:
        current_diff = abs(rec[a] - rec[b])
        current_leader = a if rec[a] > rec[b] else b
        if lead["manager"] == current_leader and lead["lead"] == current_diff:
            add("biggest_lead", 58, f"{lead['manager']}'s series lead has never been bigger")
        else:
            add("biggest_lead", 58, f"{lead['manager']}'s largest series lead was {lead['lead']} games")

    if f["closest"] and f["closest"]["value"] < 2:
        c = f["closest"]
        add("closest_game", 52, f"{c['winner']} won their closest meeting by {c['value']} points in {c['season']}")

    if f["biggest"] and f["biggest"]["value"] >= 45:
        bg = f["biggest"]
        add("biggest_win", 46, f"{bg['winner']} owns the biggest blowout in the series — by {bg['value']} in {bg['season']}")

    if f["highest"]:
        h = f["highest"]
        add("shootout", 40,
            f"their {h['season']} meeting ({scoreline(h['score_hi'], h['score_lo'])}) is the highest-scoring in the series")
    if f["lowest"] and f["games"] >= 10:
        lo = f["lowest"]
        add("slugfest", 26,
            f"their {lo['season']} meeting ({scoreline(lo['score_hi'], lo['score_lo'])}) is the lowest-scoring in the series")

    return cands


def select_storylines(cands: list[dict], min_fourth_priority: int = 40) -> list[str]:
    """The best 3–4 facts, one per category. A fourth makes the card only
    when it's genuinely interesting on its own — never to fill the slot."""
    used = set()
    picked = []
    for c in sorted(cands, key=lambda c: -c["priority"]):
        if c["category"] in used:
            continue
        if len(picked) >= 3 and c["priority"] < min_fourth_priority:
            break
        used.add(c["category"])
        picked.append(c["text"])
        if len(picked) == 4:
            break
    return picked


def week_in_history(week: int, team2mgr) -> dict:
    """Best and worst week-N performances all-time, by anyone who ever played."""
    rows = []
    for r in read_csv("weekly_matchups.csv"):
        if r["is_bye"] == "true" or int(r["week"]) != week:
            continue
        mgr = team2mgr.get((r["season"], r["team_name"].strip()))
        rows.append({"season": int(r["season"]), "manager": mgr,
                     "team": r["team_name"], "score": float(r["team_score"]),
                     "result": r["result"]})
    rows.sort(key=lambda x: -x["score"])
    return {"best": rows[:3], "worst": rows[-1] if rows else None,
            "best_losing": next((x for x in rows if x["result"] == "Loss"), None)}


def career_totals(team2mgr, managers: set[str], before_week: int | None = None) -> dict:
    """Career wins and points per current manager, all opponents counted —
    but only games that matter: regular season plus championship-bracket
    playoffs (mirroring utils/data.py's pl_wins). Consolation-bracket games
    don't count, per the commissioner's ruling."""
    out = {m: {"wins": 0, "losses": 0, "points": 0.0} for m in managers}
    for r in read_csv("weekly_matchups.csv") + current_results(before_week):
        if r["is_bye"] == "true" or r["is_playoff"] == "true":
            continue
        m = team2mgr.get((r["season"], r["team_name"].strip()))
        if m in out:
            out[m]["points"] += float(r["team_score"])
            if r["result"] == "Win":
                out[m]["wins"] += 1
            elif r["result"] == "Loss":
                out[m]["losses"] += 1
    for r in read_csv("playoff_games.csv"):
        if r["bracket"] != "championship":
            continue
        for team, score in ((r["team_1"], r["score_1"]), (r["team_2"], r["score_2"])):
            m = team2mgr.get((r["season"], team.strip()))
            if m in out:
                out[m]["points"] += float(score)
                if r["winner"].strip() == team.strip():
                    out[m]["wins"] += 1
                else:
                    out[m]["losses"] += 1
    return out


def milestone_watch(career: dict) -> list[str]:
    notes = []
    for m in sorted(career):
        wins, points = career[m]["wins"], career[m]["points"]
        if wins and wins % MILESTONE_WINS_STEP == 0:
            notes.append(f"{m} sits at exactly {wins} career wins")
        elif (wins + 1) % MILESTONE_WINS_STEP == 0:
            notes.append(f"{m} is one win from {wins + 1} career wins")
        next_p = ((points // MILESTONE_POINTS_STEP) + 1) * MILESTONE_POINTS_STEP
        if next_p - points <= MILESTONE_POINTS_REACH:
            notes.append(f"{m} is {next_p - points:.2f} points from {next_p:,.0f} career points")
    leaders = sorted(career.items(), key=lambda kv: -kv[1]["wins"])[:2]
    if leaders[0][1]["wins"] - leaders[1][1]["wins"] <= 2:
        notes.append(f"all-time wins race: {leaders[0][0]} {leaders[0][1]['wins']}, {leaders[1][0]} {leaders[1][1]['wins']}")
    return notes


def emit_site(out: Path) -> None:
    """Merge each issue's facts with its editorial copy (the -copy.json a human
    writes from the brief) and emit site JSON for lib/data.ts, plus an index.
    Runs after build_site_data.py in `npm run data`, which wipes build/data."""
    src = DATA / "program"
    issues = []
    for path in sorted(src.glob("[0-9]*-week-*.json")):
        if path.stem.endswith("-copy") or "-recap" in path.stem:
            continue  # recaps are emitted by scripts/build_recap.py --site
        issue = json.loads(path.read_text(encoding="utf-8"))
        issue["slug"] = path.stem
        issue["season"] = int(path.stem[:4])
        copy_path = src / f"{path.stem}-copy.json"
        if copy_path.exists():
            copy = json.loads(copy_path.read_text(encoding="utf-8"))
            if copy.get("draft"):
                print(f"skipping draft copy {copy_path.name} — not yet approved")
            else:
                issue["copy"] = copy
        out_path = out / f"{path.stem}.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(issue), encoding="utf-8")
        issues.append({"slug": issue["slug"], "season": issue["season"], "week": issue["week"]})
    issues.sort(key=lambda i: (i["season"], i["week"]))
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.json").write_text(json.dumps(issues), encoding="utf-8")
    print(f"emitted {len(issues)} program issue(s) to {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", type=int)
    ap.add_argument("--site", action="store_true",
                    help="emit merged issue JSON for the site into build/data/program")
    ap.add_argument("--out", type=Path, default=DATA / "program")
    args = ap.parse_args()

    if args.site:
        emit_site(ROOT / "build" / "data" / "program")
        return
    if args.week is None:
        ap.error("--week N (build an issue's facts) or --site (emit site JSON)")

    divisions = read_csv("divisions_2026.csv")
    team_div = {r["team_name"]: r["division"] for r in divisions}
    team_mgr = {r["team_name"]: r["manager"] for r in divisions}
    managers = set(team_mgr.values())

    team2mgr = load_manager_map()
    for team, mgr in team_mgr.items():
        team2mgr[(str(CURRENT_SEASON), team)] = mgr
    games = load_history(team2mgr, managers, before_week=args.week)
    finals = load_finals(team2mgr)

    cards = []
    for r in read_csv("schedule_2026.csv"):
        if int(r["week"]) != args.week:
            continue
        ta, tb = r["team_a"], r["team_b"]
        ma, mb = team_mgr[ta], team_mgr[tb]
        facts = series_facts(ma, mb, games, finals)
        cards.append({
            "team_a": ta, "team_b": tb, "manager_a": ma, "manager_b": mb,
            "division_a": team_div[ta], "division_b": team_div[tb],
            "in_division": team_div[ta] == team_div[tb],
            "facts": facts,
            "storylines": select_storylines(fact_candidates(ma, mb, facts)),
            "fact_pool": fact_candidates(ma, mb, facts),
        })

    career = career_totals(team2mgr, managers, before_week=args.week)
    issue = {
        "week": args.week,
        "cards": cards,
        "week_in_history": week_in_history(args.week, team2mgr),
        "career": career,
        "milestone_watch": milestone_watch(career),
    }

    args.out.mkdir(parents=True, exist_ok=True)
    json_path = args.out / f"2026-week-{args.week:02d}.json"
    json_path.write_text(json.dumps(issue, indent=2), encoding="utf-8")

    brief = [f"# The Program — 2026 Week {args.week} — brief\n"]
    for c in cards:
        rec = c["facts"]["record"]
        tag = f"{c['division_a']} division" if c["in_division"] else f"{c['division_a']} vs {c['division_b']}"
        brief.append(f"## {c['team_a']} ({c['manager_a']}) vs {c['team_b']} ({c['manager_b']}) — {tag}")
        brief.append(f"Lifetime: {c['manager_a']} {rec[c['manager_a']]}-{rec[c['manager_b']]}"
                     + (f"-{rec['ties']}" if rec["ties"] else "") + f" over {c['facts']['games']} games")
        if c["facts"]["form_line"]:
            brief.append(f"- form: {c['facts']['form_line']}")
        brief.append("Selected: " + " | ".join(c["storylines"]))
        brief.extend(f"- [{p['category']}] {p['text']}" for p in c["fact_pool"])
        brief.append("")
    wih = issue["week_in_history"]
    brief.append(f"## Week {args.week} in league history")
    brief.extend(f"- best: {x['manager'] or x['team']} {x['score']} ({x['season']})" for x in wih["best"])
    if wih["worst"]:
        x = wih["worst"]
        brief.append(f"- worst: {x['manager'] or x['team']} {x['score']} ({x['season']})")
    if wih["best_losing"]:
        x = wih["best_losing"]
        brief.append(f"- best losing effort: {x['manager'] or x['team']} {x['score']} ({x['season']})")
    brief.append("\n## Milestone watch")
    brief.extend(f"- {n}" for n in issue["milestone_watch"] or ["- none in reach"])
    md_path = args.out / f"2026-week-{args.week:02d}-brief.md"
    md_path.write_text("\n".join(brief) + "\n", encoding="utf-8")

    print(f"wrote {json_path.relative_to(ROOT)} and {md_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
