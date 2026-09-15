"""Emit The Recap — the Tuesday look back at a finished week, the Program's
second tab.

    python3 scripts/build_recap.py --week 1   # facts + writer's brief into data/program/
    python3 scripts/build_recap.py --site     # merge facts + approved copy into build/data/program/

Inputs: data/lineups_2026.csv and data/results_2026.csv (scripts/
fetch_week_lineups.py), data/divisions_2026.csv, and the scraped history.
Writes data/program/2026-week-NN-recap.json (facts) and -recap-brief.md (the
raw material for the copy). The prose is hand-approved in
data/program/2026-week-NN-recap-copy.json; a copy file still marked
"draft": true never reaches the site.

Awards come from scripts/recap_engine.py — byte-identical with Dynasty 22's
copy; fix both or neither. Series count every meeting, consolation included —
the same games the preview counts (build_program.load_history).
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from build_program import CURRENT_SEASON, current_results, load_history, load_manager_map, read_csv
from photos import headshot, sleeper_id_for, team_logo
from recap_engine import series_update, week_awards

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SEASON = CURRENT_SEASON

CONFIG = {
    "slots": [("QB", ["QB"]), ("RB", ["RB"]), ("RB", ["RB"]), ("WR", ["WR"]), ("WR", ["WR"]), ("TE", ["TE"]),
              ("W/R/T", ["WR", "RB", "TE"]), ("K", ["K"]), ("DEF", ["DEF"])],
    "inactive": ["IR", "IR+"],
    "award_positions": ["QB", "RB", "WR", "TE", "K", "DEF"],
    "bench_positions": ["QB", "RB", "WR", "TE"],
}


def ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }"


def build_week(week: int) -> dict:
    divisions = read_csv("divisions_2026.csv")
    team_mgr = {r["team_name"]: r["manager"] for r in divisions}
    team_div = {r["team_name"]: r["division"] for r in divisions}
    managers = set(team_mgr.values())

    by_mgr = defaultdict(list)
    for r in read_csv("lineups_2026.csv"):
        if int(r["week"]) != week:
            continue
        by_mgr[team_mgr[r["team_name"]]].append({
            "name": r["player_name"] or None,
            "positions": [p for p in r["position"].split("/") if p],
            "slot": r["slot"],
            "points": float(r["points"]) if r["points"] else 0.0,
            "projected": float(r["projected"]) if r["projected"] else None,
            "id": r["player_id"],
            "nfl_team": r.get("nfl_team", ""),
            "opponent": r.get("opponent", ""),
        })
    results = [r for r in read_csv("results_2026.csv") if int(r["week"]) == week]
    if not results:
        raise SystemExit(f"recap: no results for week {week} — run scripts/fetch_week_lineups.py --week {week}")
    games, seen = [], set()
    for r in results:
        a, b = team_mgr[r["team_name"]], team_mgr[r["opponent"]]
        if frozenset((a, b)) not in seen:
            seen.add(frozenset((a, b)))
            games.append((a, b))
    res = week_awards([{"key": k, "players": v} for k, v in by_mgr.items()], games, CONFIG)

    # Pictures for every featured player: a headshot via the Sleeper id, a team logo for a defense
    for row in [r for rows in res["players_of_week"].values() for r in rows] + \
               [r for rows in res["bench_best"].values() for r in rows] + res["dud"]:
        if row["position"] == "DEF":
            row["photo"] = team_logo(row.get("nfl_team"))
        else:
            row["photo"] = headshot(sleeper_id_for(row.get("id", ""), row["name"], row.get("nfl_team", "")))

    official = {team_mgr[r["team_name"]]: float(r["score"]) for r in results}
    for k, t in res["teams"].items():
        if abs(t["actual"] - official[k]) > 0.011:
            raise SystemExit(f"recap week {week}: {k} lineup sums to {t['actual']} but Yahoo says {official[k]}")

    # Lifetime series before and after — the same games the Week N+1 preview counts
    team2mgr = load_manager_map()
    for team, mgr in team_mgr.items():
        team2mgr[(str(SEASON), team)] = mgr
    history = load_history(team2mgr, managers, before_week=week)
    for g in res["games"]:
        prior = [{"season": x["season"], "week": x["week"], "winner": x["winner"]}
                 for x in history if {x["a"], x["b"]} == {g["a"], g["b"]}]
        g["series"] = series_update(prior, g["a"], g["b"], g["winner"])

    # Standings through this week, with divisions
    table = defaultdict(lambda: {"wins": 0, "losses": 0, "ties": 0, "points_for": 0.0})
    for r in current_results(week + 1):
        s = table[team_mgr[r["team_name"]]]
        s[{"Win": "wins", "Loss": "losses", "Tie": "ties"}[r["result"]]] += 1
        s["points_for"] = round(s["points_for"] + float(r["team_score"]), 2)
    standings = sorted(({"manager": k, "division": team_div[t], **table[k]} for t, k in team_mgr.items()),
                       key=lambda s: (-s["wins"], s["losses"], -s["points_for"]))

    # Records: this week's extremes against every regular-season score since 2001
    past = [r for r in read_csv("weekly_matchups.csv") + current_results(week)
            if r["is_bye"] != "true" and r["is_playoff"] != "true"]
    all_scores = [float(r["team_score"]) for r in past]
    week_scores = [float(r["team_score"]) for r in past if int(r["week"]) == week]
    margins = [abs(float(r["team_score"]) - float(r["opponent_score"])) for r in past if r["result"] == "Win"]
    hi, lo = res["awards"]["highest_score"][0], res["awards"]["lowest_score"][0]
    records = [
        {"kind": "high_all_time", "team": hi["team"], "value": hi["value"], "rank": 1 + sum(x > hi["value"] for x in all_scores), "of": len(all_scores) + len(res["teams"])},
        {"kind": "low_all_time", "team": lo["team"], "value": lo["value"], "rank": 1 + sum(x < lo["value"] for x in all_scores), "of": len(all_scores) + len(res["teams"])},
        {"kind": "high_week", "team": hi["team"], "value": hi["value"], "week": week, "rank": 1 + sum(x > hi["value"] for x in week_scores), "of": len(week_scores) + len(res["teams"])},
        {"kind": "low_week", "team": lo["team"], "value": lo["value"], "week": week, "rank": 1 + sum(x < lo["value"] for x in week_scores), "of": len(week_scores) + len(res["teams"])},
    ]
    if res["awards"]["biggest_blowout"]:
        bb = res["awards"]["biggest_blowout"][0]
        records.append({"kind": "blowout_all_time", "team": bb["winner"], "value": bb["value"],
                        "rank": 1 + sum(x > bb["value"] for x in margins), "of": len(margins) + len(games)})
    for k, t in res["teams"].items():
        mine = [float(r["team_score"]) for r in past if team2mgr.get((r["season"], r["team_name"].strip())) == k]
        if mine and t["actual"] > max(mine):
            records.append({"kind": "career_high", "team": k, "value": t["actual"], "previous": max(mine)})
        if mine and t["actual"] < min(mine):
            records.append({"kind": "career_low", "team": k, "value": t["actual"], "previous": min(mine)})

    mgr_team = {m: t for t, m in team_mgr.items()}
    return {
        "season": SEASON, "week": week,
        "managers": {k: {"name": k, "team": mgr_team[k], "division": team_div[mgr_team[k]]} for k in res["teams"]},
        "standings": standings, "records": records, **res,
    }


def brief(recap: dict) -> str:
    M = recap["managers"]
    n = lambda k: f"{k} ({M[k]['team']})"
    lines = [f"# The Recap — {recap['season']} Week {recap['week']} — brief", "", "## Results"]
    for g in recap["games"]:
        w, l = (g["a"], g["b"]) if g["winner"] == g["a"] else (g["b"], g["a"])
        tw, tl = recap["teams"][w], recap["teams"][l]
        s = g["series"]
        lines.append(f"- {n(w)} {tw['actual']} def. {n(l)} {tl['actual']} (margin {g['margin']})")
        lines.append(f"  - projected {w} {tw['projected']} / {l} {tl['projected']}; optimal {tw['optimal']} / {tl['optimal']}")
        lines.append(f"  - series before {s['before']}, after {s['after']} over {s['games_after']} games; notes {s['notes']}")
        if g["coulda_won"]:
            lines.append(f"  - COULDA WON: {n(g['coulda_won']['team'])} optimal {g['coulda_won']['optimal']} > {g['coulda_won']['needed']}")
        if g["swap_flip"]:
            sf = g["swap_flip"]
            lines.append(f"  - ONE SWAP FLIPS IT: {sf['bench']} ({sf['bench_points']}) for {sf['starter']} ({sf['starter_points']}) at {sf['slot']}, +{sf['gain']}")
    lines += ["", "## Teams"]
    for k, t in sorted(recap["teams"].items(), key=lambda kv: -kv[1]["actual"]):
        lines.append(f"- {n(k)}: {t['actual']} ({ordinal(t['score_rank'])}), {t['result']}, proj {t['projected']} ({t['vs_projection']:+}), "
                     f"optimal {t['optimal']} ({t['efficiency']}%), bench left {t['left_on_bench']}, "
                     f"all-play {t['all_play']['wins']}-{t['all_play']['losses']}, best swap {t['best_swap']}")
    lines += ["", "## Awards"]
    for key, winners in recap["awards"].items():
        lines.append(f"- {key}: " + "; ".join(f"{n(w.get('team') or w.get('winner'))} {w['value']}"
                                             + (f" over {n(w['loser'])}" if w.get("loser") else "") for w in winners))
    lines += ["", "## Players"]
    for pos, rows in recap["players_of_week"].items():
        lines.append(f"- {pos} of the week: " + "; ".join(f"{r['name']} {r['points']} (proj {r['projected']}) for {n(r['team'])}" for r in rows))
    for pos, rows in recap["bench_best"].items():
        lines.append(f"- best bench {pos}: " + "; ".join(f"{r['name']} {r['points']} for {n(r['team'])}" for r in rows))
    lines.append("- dud: " + "; ".join(f"{r['name']} {r['points']} vs proj {r['projected']} for {n(r['team'])}" for r in recap["dud"]))
    lines += ["", "## Records"] + [f"- {r}" for r in recap["records"]]
    lines += ["", "## Standings"] + [f"- {n(s['manager'])} [{s['division']}]: {s['wins']}-{s['losses']}, PF {s['points_for']}" for s in recap["standings"]]
    return "\n".join(lines) + "\n"


def emit_site(out: Path) -> None:
    """Merge each recap's facts with its approved copy into build/data/program/."""
    src = DATA / "program"
    out.mkdir(parents=True, exist_ok=True)
    weeks = []
    for path in sorted(src.glob("[0-9]*-week-*-recap.json")):
        recap = json.loads(path.read_text(encoding="utf-8"))
        copy_path = src / f"{path.stem}-copy.json"
        if copy_path.exists():
            copy = json.loads(copy_path.read_text(encoding="utf-8"))
            if copy.get("draft"):
                print(f"recap: skipping draft copy {copy_path.name}")
            else:
                recap["copy"] = copy
        recap["slug"] = path.stem.removesuffix("-recap")
        (out / path.name).write_text(json.dumps(recap), encoding="utf-8")
        weeks.append({"slug": recap["slug"], "season": recap["season"], "week": recap["week"]})
    (out / "recaps.json").write_text(json.dumps(weeks), encoding="utf-8")
    print(f"emitted {len(weeks)} recap(s) to {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", type=int)
    ap.add_argument("--site", action="store_true")
    args = ap.parse_args()
    if args.site:
        emit_site(ROOT / "build" / "data" / "program")
        return
    if args.week is None:
        ap.error("--week N (build a recap's facts) or --site (emit site JSON)")
    recap = build_week(args.week)
    slug = f"{SEASON}-week-{args.week:02d}"
    (DATA / "program" / f"{slug}-recap.json").write_text(json.dumps(recap, indent=2), encoding="utf-8")
    (DATA / "program" / f"{slug}-recap-brief.md").write_text(brief(recap), encoding="utf-8")
    print(f"wrote data/program/{slug}-recap.json and -recap-brief.md")


if __name__ == "__main__":
    main()
