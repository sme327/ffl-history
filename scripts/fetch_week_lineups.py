"""Scrape one finished week's six box scores from Yahoo — both lineups, bench
included, every player's slot, fantasy points and original projection.

    python3 scripts/fetch_week_lineups.py --week 1
    python3 scripts/fetch_week_lineups.py --week 1 --dry-run   # parse and validate, write nothing

Feeds The Recap (scripts/build_recap.py) and layers current-season results into
The Program's preview (scripts/build_program.py). Writes, replacing only that
week's rows:

  data/lineups_2026.csv   week, team_id, team_name, player_id, player_name,
                          position, slot, points, projected
  data/results_2026.csv   week, team_name, score, opponent, opponent_score,
                          projected — one row per team

Source: the matchup page, /f1/55402/matchup?week=N&mid1=T. Its two lineup
tables (starters, then bench/IR) carry, per row: the left team's player, Proj,
Fan Pts, the slot, then the right team's Fan Pts, Proj, player. Proj is
Yahoo's original pregame projection — the starters' Proj column sums to the
page's "Orig Proj" total, which this script checks.

Session: the museum's own .yahoo_cookies.json (fetch_yahoo_data.py's login),
falling back to My FFL's Playwright storage state. Raw pages are kept under
.local/raw/ (git-ignored — Yahoo's header carries the signed-in account's
email). Sequential, 3.5 s between pages, per DATA-SOURCES.md.

Refuses to write unless all 12 teams appear exactly once, every team has 9
filled-or-empty starter rows, and each team's starters add up to the score
Yahoo shows for it.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = ROOT / ".local" / "raw" / "yahoo-matchups"
LEAGUE = "55402"
SEASON = 2026
TEAMS = 12
DELAY = 3.5
COOKIES = ROOT / ".yahoo_cookies.json"
STORAGE_STATE = Path("~/.draft-queue/yahoo-session.json").expanduser()
SLOTS = {"QB", "RB", "WR", "TE", "W/R/T", "K", "DEF", "BN", "IR", "IR+"}
STARTER_SLOTS = {"QB", "RB", "WR", "TE", "W/R/T", "K", "DEF"}

LINEUP_FIELDS = ["week", "team_id", "team_name", "player_id", "player_name", "position", "slot", "points", "projected"]
RESULT_FIELDS = ["week", "team_name", "score", "opponent", "opponent_score", "projected"]


def num(text: str) -> float | None:
    t = (text or "").strip().replace("–", "").replace("—", "")
    try:
        return float(t)
    except ValueError:
        return None


def player_cell(td) -> dict:
    a = td.select_one("a.name")
    if not a:
        return {"player_id": "", "player_name": "", "position": ""}
    pos = ""
    for span in td.select("span.D-b span.Fz-xxs"):
        m = re.search(r"-\s*([A-Z/,]+)\s*$", span.get_text(" ", strip=True))
        if m:
            pos = m.group(1).replace(",", "/")
            break
    return {"player_id": a.get("data-ys-playerid", ""), "player_name": a.get("title") or a.get_text(strip=True), "position": pos}


def parse_page(html: str, week: int) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    teams = []
    for a in soup.find_all("a", class_="F-link", href=re.compile(rf"/f1/{LEAGUE}/(\d+)$")):
        tid = re.search(r"/(\d+)$", a["href"]).group(1)
        if tid not in [t["team_id"] for t in teams]:
            teams.append({"team_id": tid, "team_name": a.get_text(strip=True)})
    if len(teams) != 2:
        raise ValueError(f"expected 2 team headers, found {len(teams)} — logged out, or the page changed")

    header = soup.find("table", class_="M-a")
    cells = [td.get_text(strip=True) for td in header.find_all("td")] if header else []
    if len(cells) < 4:
        raise ValueError("score header not found")
    score = [num(cells[0]), num(cells[1])]
    orig_proj = [num(cells[2]), num(cells[3])]

    rows = []
    for table in soup.find_all("table"):
        body = table.find("tbody")
        if not body:
            continue
        for tr in body.find_all("tr", recursive=False):
            tds = tr.find_all("td", recursive=False)
            if len(tds) < 11:
                continue
            slot = tds[5].get_text(strip=True)
            if slot not in SLOTS:
                continue
            for side, (pc, proj_i, pts_i) in enumerate(((1, 2, 3), (9, 8, 7))):
                p = player_cell(tds[pc])
                rows.append({
                    "week": week, "team_id": teams[side]["team_id"], "team_name": teams[side]["team_name"],
                    **p, "slot": slot,
                    "points": num(tds[pts_i].get_text(strip=True)) if p["player_name"] else "",
                    "projected": num(tds[proj_i].get_text(strip=True)) if p["player_name"] else "",
                })
    return {"teams": teams, "score": score, "orig_proj": orig_proj, "rows": rows}


def validate(week: int, games: list[dict]) -> None:
    seen = [t["team_id"] for g in games for t in g["teams"]]
    if len(seen) != TEAMS or len(set(seen)) != TEAMS:
        raise SystemExit(f"week {week}: expected {TEAMS} distinct teams, got {seen}")
    for g in games:
        for side, t in enumerate(g["teams"]):
            starters = [r for r in g["rows"] if r["team_id"] == t["team_id"] and r["slot"] in STARTER_SLOTS]
            if len(starters) != 9:
                raise SystemExit(f"week {week}: {t['team_name']} has {len(starters)} starter rows, expected 9")
            total = round(sum(r["points"] or 0 for r in starters), 2)
            if abs(total - (g["score"][side] or 0)) > 0.011:
                raise SystemExit(f"week {week}: {t['team_name']} starters sum to {total}, Yahoo shows {g['score'][side]}")
            proj = round(sum(r["projected"] or 0 for r in starters), 2)
            if g["orig_proj"][side] is not None and abs(proj - g["orig_proj"][side]) > 0.011:
                raise SystemExit(f"week {week}: {t['team_name']} projections sum to {proj}, Yahoo's Orig Proj is {g['orig_proj'][side]}")


def replace_week(path: Path, fields: list[str], week: int, new_rows: list[dict]) -> None:
    kept = []
    if path.exists():
        with open(path, newline="", encoding="utf-8") as fh:
            kept = [r for r in csv.DictReader(fh) if int(r["week"]) != week]
    rows = sorted(kept + new_rows, key=lambda r: int(r["week"]))
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"  -> {path.relative_to(ROOT)}: {len(new_rows)} rows for week {week} ({len(rows)} total)")


async def scrape(week: int) -> list[dict]:
    from playwright.async_api import async_playwright

    RAW.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        attempts = []
        if COOKIES.exists():
            attempts.append(("museum cookies", {}, json.loads(COOKIES.read_text())))
        if STORAGE_STATE.exists():
            attempts.append(("My FFL session", {"storage_state": str(STORAGE_STATE)}, None))
        for label, ctx_args, cookies in attempts:
            context = await browser.new_context(**ctx_args)
            if cookies:
                await context.add_cookies(cookies)
            page = await context.new_page()
            games, covered = [], set()
            try:
                for mid in range(1, TEAMS + 1):
                    if str(mid) in covered:
                        continue
                    url = f"https://football.fantasysports.yahoo.com/f1/{LEAGUE}/matchup?week={week}&mid1={mid}"
                    await page.goto(url, wait_until="domcontentloaded")
                    await page.wait_for_timeout(int(DELAY * 1000))
                    html = await page.content()
                    if "Request denied" in html:
                        print("  Yahoo said 'Request denied' — pausing 5 minutes")
                        await asyncio.sleep(300)
                        await page.goto(url, wait_until="domcontentloaded")
                        await page.wait_for_timeout(int(DELAY * 1000))
                        html = await page.content()
                    (RAW / f"{SEASON}-week-{week:02d}-mid{mid:02d}.html").write_text(html, encoding="utf-8")
                    game = parse_page(html, week)
                    covered.update(t["team_id"] for t in game["teams"])
                    games.append(game)
                    print(f"  {game['teams'][0]['team_name']} {game['score'][0]} – {game['score'][1]} {game['teams'][1]['team_name']}")
                await browser.close()
                return games
            except ValueError as err:
                print(f"  {label}: {err}")
                await context.close()
        await browser.close()
    raise SystemExit("No working Yahoo session. Log in with `python3 fetch_yahoo_data.py` (refreshes .yahoo_cookies.json).")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", type=int, required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    games = asyncio.run(scrape(args.week))
    validate(args.week, games)
    lineups, results = [], []
    for g in games:
        lineups.extend(g["rows"])
        for side in (0, 1):
            results.append({
                "week": args.week, "team_name": g["teams"][side]["team_name"], "score": g["score"][side],
                "opponent": g["teams"][1 - side]["team_name"], "opponent_score": g["score"][1 - side],
                "projected": g["orig_proj"][side],
            })
    print(f"week {args.week}: {len(games)} games, {len(lineups)} player rows — validated")
    if args.dry_run:
        return
    replace_week(DATA / "lineups_2026.csv", LINEUP_FIELDS, args.week, lineups)
    replace_week(DATA / "results_2026.csv", RESULT_FIELDS, args.week, results)


if __name__ == "__main__":
    main()
