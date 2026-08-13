#!/usr/bin/env python3
"""
fetch_yahoo_data.py

Scrapes Yahoo Fantasy Football historical data directly from Yahoo's website.
Uses Playwright for browser automation (handles Yahoo's JS-rendered pages).

Usage:
    python fetch_yahoo_data.py                    # fetch all years
    python fetch_yahoo_data.py --year 2010        # single year
    python fetch_yahoo_data.py --year 2005 2010   # range of years
    python fetch_yahoo_data.py --section draft    # only draft picks for all years
"""

import asyncio
import csv
import json
import re
import sys
import time
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

# ─── Config ──────────────────────────────────────────────────────────────────
LEAGUE_SLUG = "sme327"
YEARS = list(range(2001, 2026))
BASE_URL = "https://football.fantasysports.yahoo.com"
DATA_DIR = Path(__file__).parent / "data"
SESSION_FILE = Path(__file__).parent / ".yahoo_cookies.json"
DELAY = 3.5  # seconds between page loads — be polite to Yahoo

# (game_code, league_id) extracted from each year's URL bar
LEAGUE_IDS: dict[int, tuple[str, int]] = {
    2001: ("f1", 31746),
    2002: ("f1", 59229),
    2003: ("f1", 37125),
    2004: ("f2", 260),
    2005: ("f2", 1172),
    2006: ("f2", 16269),
    2007: ("f2", 6884),
    2008: ("f2", 6837),
    2009: ("f1", 178327),
    2010: ("f1", 62122),
    2011: ("f1", 57404),
    2012: ("f1", 1028),
    2013: ("f1", 31910),
    2014: ("f1", 19850),
    2015: ("f1", 18121),
    2016: ("f1", 5261),
    2017: ("f1", 122329),
    2018: ("f1", 68726),
    2019: ("f1", 216543),
    2020: ("f1", 736850),
    2021: ("f1", 34806),
    2022: ("f1", 396466),
    2023: ("f1", 5426),
    2024: ("f1", 12853),
    2025: ("f1", 66116),
}

# ─── Auth ────────────────────────────────────────────────────────────────────

async def ensure_logged_in(context, stealth=False):
    """Load saved cookies; if session is stale, go to login.yahoo.com and wait."""
    if SESSION_FILE.exists():
        try:
            cookies = json.loads(SESSION_FILE.read_text())
            await context.add_cookies(cookies)
            print("Loaded saved Yahoo session.\n")
        except Exception:
            pass
    else:
        # No saved session — open yahoo login (not the fantasy URL, to avoid bot detection)
        page = await context.new_page()
        if stealth:
            await Stealth().apply_stealth_async(page)
        await page.goto("https://login.yahoo.com", wait_until="domcontentloaded")
        print("\n" + "="*60)
        print("Please log in to Yahoo in the browser window.")
        print("After you're fully logged in, come back here and press Enter.")
        print("="*60)
        input("\nPress Enter after logging in > ")
        await asyncio.sleep(1)
        cookies = await context.cookies()
        SESSION_FILE.write_text(json.dumps(cookies))
        print("Session saved.\n")
        await page.close()

    page = await context.new_page()
    if stealth:
        await Stealth().apply_stealth_async(page)
    return page


# ─── Helpers ─────────────────────────────────────────────────────────────────

def league_url(year, section="", week=None):
    year = int(year)
    game, lid = LEAGUE_IDS[year]
    base = f"{BASE_URL}/{year}/{game}/{lid}"
    if section == "standings":
        return f"{base}?lhst=stand#leaguehomestandings"
    elif section == "matchups":
        return f"{base}?matchup_week={week}&module=matchups&lhst=matchups" if week else f"{base}/matchup"
    elif section == "playoffs":
        return f"{base}?module=standings&lhst=playoff#lhstplayoff"
    elif section == "teams":
        return f"{base}/teams"
    elif section:
        return f"{base}/{section}"
    return base


async def goto_wait(page, url, delay=DELAY):
    await page.goto(url, wait_until="domcontentloaded")
    await asyncio.sleep(delay)
    html = await page.content()
    if "Request denied" in html or len(html) < 500:
        print(f"\n  ⚠ Yahoo rate-limited on: {url}")
        print("  Pausing 5 minutes then retrying once...")
        await asyncio.sleep(300)
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(delay)
        html = await page.content()
    return BeautifulSoup(html, "html.parser")


def clean(text):
    return re.sub(r'\s+', ' ', text or "").strip()


def csv_path(name):
    return DATA_DIR / f"{name}.csv"


def load_existing_rows(filename, key_fields):
    """Load existing CSV rows into a set of key tuples to avoid duplicates."""
    path = csv_path(filename)
    if not path.exists():
        return set(), []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    keys = {tuple(r[k] for k in key_fields) for r in rows}
    return keys, rows


def append_rows(filename, fieldnames, new_rows):
    """Append new_rows to CSV, creating with header if needed."""
    path = csv_path(filename)
    write_header = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(new_rows)
    print(f"  → Wrote {len(new_rows)} rows to {path.name}")


def overwrite_csv(filename, fieldnames, all_rows):
    """Write all rows to CSV (used when replacing a year's data)."""
    path = csv_path(filename)
    write_header = not path.exists()
    existing_keys, existing_rows = load_existing_rows(filename, ["season"] if "season" in fieldnames else [fieldnames[0]])

    # Drop existing rows for the seasons in new_rows, then add new
    seasons_in_new = {str(r["season"]) for r in all_rows}
    kept = [r for r in existing_rows if str(r.get("season", "")) not in seasons_in_new]
    combined = kept + all_rows
    combined.sort(key=lambda r: (str(r.get("season", "")), str(r.get("week", "")).zfill(2), str(r.get("rank", "")).zfill(3), str(r.get("round", "")).zfill(2), str(r.get("overall_pick", "")).zfill(3)))

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(combined)
    print(f"  → Saved {len(all_rows)} new rows for this season to {path.name} ({len(combined)} total)")


# ─── Standings ───────────────────────────────────────────────────────────────

STANDINGS_FIELDS = ["season", "rank", "team_name", "wins", "losses", "ties",
                    "points_for", "points_against", "streak", "waiver_priority", "moves"]

async def scrape_standings(page, year):
    print(f"  Standings...")
    soup = await goto_wait(page, league_url(year, "standings"))
    rows = []

    # Confirmed selector from 2004: id="standingstable"
    # Fallback for modern years: any table with "standings" in id/class
    table = (
        soup.find("table", id="standingstable") or
        soup.find("table", id=re.compile(r"standings", re.I)) or
        soup.find("table", class_=re.compile(r"standings", re.I))
    )

    if not table:
        print(f"    WARNING: No standings table found for {year}.")
        return []

    for tr in table.find_all("tr"):
        cells = [clean(td.get_text()) for td in tr.find_all(["td", "th"])]

        # Skip header row and division-name separator rows (only 1 cell)
        if len(cells) < 5 or cells[0].lower() in ("rank", ""):
            continue

        try:
            # Rank cell: "*1" for playoff teams, "9" for non-playoff — strip the *
            raw_rank = cells[0].lstrip("*").strip()
            if not raw_rank.isdigit():
                continue

            team = re.sub(r'[-]', '', cells[1]).strip()  # strip private-use unicode icons

            # W-L-T is one column like "6-8-0"
            wlt = cells[2].split("-")
            w, l, t = wlt[0], wlt[1], wlt[2] if len(wlt) > 2 else "0"

            # Remaining columns: Div record, PF, PA, Streak, Waiver, Moves
            pf     = cells[4] if len(cells) > 4 else ""
            pa     = cells[5] if len(cells) > 5 else ""
            streak = cells[6] if len(cells) > 6 else ""
            waiver = cells[7] if len(cells) > 7 else ""
            moves  = cells[8] if len(cells) > 8 else ""

            rows.append({
                "season": year, "rank": raw_rank, "team_name": team,
                "wins": w, "losses": l, "ties": t,
                "points_for": pf, "points_against": pa,
                "streak": streak, "waiver_priority": waiver, "moves": moves,
            })
        except (IndexError, ValueError):
            continue

    print(f"    Found {len(rows)} teams")
    return rows


# ─── Draft Results ────────────────────────────────────────────────────────────

DRAFT_FIELDS = ["season", "round", "pick_in_round", "overall_pick", "team_name", "player_name", "is_keeper"]

def strip_player_name(raw):
    """'Hakeem Nicks(NYG - WR)' -> 'Hakeem Nicks'"""
    return re.sub(r'\s*\(.*?\)\s*$', '', raw).strip()


async def scrape_draft(page, year):
    print(f"  Draft results...")
    soup = await goto_wait(page, league_url(year, "draftresults"))
    rows = []

    # ── Format A: snake draft displayed in auction-style flat table ───────────
    # Yahoo incorrectly shows some snake drafts as auction format (seen in 2011).
    # Table headers: Pick | Player | Salary | Team
    # Picks are in chronological draft order; snake reversal must be applied
    # manually — even rounds reverse pick_in_round to get the team's consistent slot.
    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        if "salary" in headers or ({"pick", "player", "team"} <= set(headers)):
            overall = 0
            num_teams = 12
            for tr in table.find_all("tr"):
                cells = tr.find_all("td")
                if len(cells) < 3:
                    continue
                pick_str = clean(cells[0].get_text()).rstrip(".")
                if not pick_str.isdigit():
                    continue
                overall += 1
                player_cell = cells[1]
                # Use <a> tag for clean name — avoids "(TEAM - POS)" suffix text
                name_tag = player_cell.find("a")
                player_raw = name_tag.get_text(strip=True) if name_tag else clean(player_cell.get_text())
                # Team is in cells[3]; cells[2] is the salary/cost column
                team_cell = cells[3] if len(cells) > 3 else cells[2]
                team_span = team_cell.find("span")
                team = team_span.get_text(strip=True) if team_span else clean(team_cell.get_text())
                round_num = ((overall - 1) // num_teams) + 1
                pos_in_group = (overall - 1) % num_teams   # 0-based within round
                # Snake correction: even rounds reverse the pick slot
                if round_num % 2 == 0:
                    pick_in_round = num_teams - pos_in_group
                else:
                    pick_in_round = pos_in_group + 1
                # Keeper detection — same span as snake format
                is_keeper = bool(player_cell.find("span", title=re.compile(r"keeper", re.I)))
                rows.append({
                    "season": year,
                    "round": round_num,
                    "pick_in_round": pick_in_round,
                    "overall_pick": overall,
                    "team_name": team,
                    "player_name": strip_player_name(player_raw),
                    "is_keeper": is_keeper,
                })
            if rows:
                keepers = sum(1 for r in rows if r["is_keeper"])
                print(f"    Found {len(rows)} picks (snake-in-auction format); {keepers} keepers; snake correction applied")
                break  # fall through to pre-2014 keeper normalization below

    # ── Format B: snake draft ────────────────────────────────────────────────
    # One table per round, header cell contains "Round N"
    if not rows:
        overall = 0
        round_num = 0
        for table in soup.find_all("table"):
            header = table.find("th", class_="Fw-b") or table.find("th")
            if not header:
                continue
            m = re.search(r"Round\s+(\d+)", header.get_text(), re.I)
            if not m:
                continue
            round_num = int(m.group(1))
            for tr in table.find_all("tr"):
                cells = tr.find_all("td")
                if len(cells) < 3:
                    continue
                pick_str = clean(cells[0].get_text()).rstrip(".")
                if not pick_str.isdigit():
                    continue
                overall += 1
                player_cell = cells[1]
                # Prefer <a class="name"> to avoid keeper span text leaking into the name
                name_tag = player_cell.find("a", class_="name")
                player_raw = name_tag.get_text(strip=True) if name_tag else clean(player_cell.get_text())
                # Prefer title attribute on team cell; display text can be truncated ("Return to Gl...")
                team_cell = cells[2]
                team = team_cell.get("title") or clean(team_cell.get_text())
                # Keeper detection by era:
                #   2001-2002: no keeper system
                #   2003:      keepers entered as round 1 by Yahoo (conceptually the "15th round" slot)
                #   2004-2009: round 15 = keeper slot; Yahoo has no indicator yet
                #   2010+:     Yahoo marks keepers with span whose title contains "keeper";
                #              title was "This player is a keeper." early on, then "Keeper Salary: N"
                player_name = strip_player_name(player_raw)
                if year <= 2002:
                    is_keeper = False
                elif year == 2003:
                    is_keeper = (round_num == 1)
                elif year <= 2009:
                    is_keeper = (round_num == 15 and player_name not in ("--empty--", ""))
                else:
                    is_keeper = bool(player_cell.find("span", title=re.compile(r"keeper", re.I)))
                rows.append({
                    "season": year,
                    "round": round_num,
                    "pick_in_round": int(pick_str),
                    "overall_pick": overall,
                    "team_name": team,
                    "player_name": player_name,
                    "is_keeper": is_keeper,
                })
        if rows:
            keepers = sum(1 for r in rows if r["is_keeper"])
            print(f"    Found {len(rows)} picks across {round_num} rounds (snake format); {keepers} keepers")

    # Pre-2014 keepers were entered by Yahoo as R1 artifacts (not real first-round picks).
    # Normalize them to R15 so they don't pollute first-round analysis.
    if year < 2014 and rows:
        num_teams = max(r["pick_in_round"] for r in rows)
        for r in rows:
            if r["is_keeper"] and r["round"] != 15:
                r["round"] = 15
                r["overall_pick"] = (14 * num_teams) + r["pick_in_round"]

    if not rows:
        print(f"    WARNING: Could not parse draft for {year}")
        with open(DATA_DIR.parent / f"debug_{year}_draftresults.html", "w") as f:
            f.write(str(soup))

    return rows


# ─── Weekly Matchups ──────────────────────────────────────────────────────────

MATCHUP_FIELDS = ["season", "week", "team_name", "opponent", "result",
                  "team_score", "opponent_score", "is_bye", "is_playoff"]

def parse_matchup_cards(soup, year, week):
    """
    Parse matchup <li> cards from the #matchupweek section.
    Each card has two team sides (div.Grid-u-6-13), team names in a.F-link,
    primary scores in div.Fz-lg (bold Fw-b = winner), secondary score in div.F-shade.
    """
    section = soup.find(id="matchupweek")
    if not section:
        return []

    rows = []
    for li in section.find_all("li", attrs={"data-target": re.compile(r"matchup")}):
        sides = li.find_all("div", class_=lambda c: c and "Grid-u-6-13" in c)
        if len(sides) < 2:
            continue

        def extract_side(div):
            name_el = div.find("a", class_="F-link")
            score_el = div.find("div", class_=lambda c: c and "Fz-lg" in c)
            name = clean(name_el.get_text()) if name_el else ""
            score = clean(score_el.get_text()) if score_el else ""
            won = score_el and "Fw-b" in (score_el.get("class") or [])
            return name, score, won

        team1, score1, won1 = extract_side(sides[0])
        team2, score2, won2 = extract_side(sides[1])

        if not team1 or not team2:
            continue

        try:
            s1, s2 = float(score1), float(score2)
            result1 = "Win" if s1 > s2 else ("Loss" if s1 < s2 else "Tie")
            result2 = "Win" if s2 > s1 else ("Loss" if s2 < s1 else "Tie")
        except ValueError:
            result1 = result2 = ""

        rows.extend([
            {"season": year, "week": week, "team_name": team1, "opponent": team2,
             "result": result1, "team_score": score1, "opponent_score": score2, "is_bye": "false"},
            {"season": year, "week": week, "team_name": team2, "opponent": team1,
             "result": result2, "team_score": score2, "opponent_score": score1, "is_bye": "false"},
        ])
    return rows


async def scrape_matchups(page, year, max_weeks=17):
    print(f"  Weekly matchups...")
    all_rows = []
    seen_weeks = set()

    for week in range(1, max_weeks + 1):
        url = league_url(year, "matchups", week=week)
        soup = await goto_wait(page, url, delay=1.5)

        week_rows = parse_matchup_cards(soup, year, week)

        if week_rows:
            seen_weeks.add(week)
            all_rows.extend(week_rows)
        elif week > 14:
            break  # past end of season

    print(f"    Found data for weeks: {sorted(seen_weeks)}")
    return all_rows


# ─── Playoff Bracket ─────────────────────────────────────────────────────────

PLAYOFF_FIELDS = ["season", "bracket", "week", "round", "game_type",
                  "seed_1", "team_1", "score_1", "seed_2", "team_2", "score_2", "winner"]

ROUND_ORDER = {"quarterfinal": 1, "semifinal": 2, "final": 3, "place_3": 3}
CONSOLATION_ROUND_ORDER = {"semifinal": 1, "place_5": 2, "place_7": 2}
GAME_TYPE_LABEL = {
    "quarterfinal": "quarterfinal",
    "semifinal":    "semifinal",
    "final":        "final",
    "place_3":      "3rd_place",
    "place_5":      "5th_place",
    "place_7":      "7th_place",
}
_ALL_ROUND_KEYS = ("quarterfinal", "semifinal", "final", "place_3", "place_5", "place_7")

def parse_bracket_side(div):
    seed_el = div.find("span", class_="yfa-rank")
    seed = clean(seed_el.get_text()) if seed_el else ""
    name_el = div.find("span", class_="Ell")
    name = ""
    if name_el:
        a = name_el.find("a")
        name = clean(a.get_text()) if a else clean(name_el.get_text())
    score = ""
    for span in div.find_all("span", class_="Block"):
        text = clean(span.get_text())
        if re.match(r"^\d+\.?\d*$", text):
            score = text
    won = "ahead" in (div.get("class") or [])
    return seed, name, score, won


async def scrape_playoffs(page, year):
    print(f"  Playoff bracket...")
    base = league_url(year)
    bracket_configs = [
        ("championship", f"{base}?module=standings&lhst=playoff&ptype=champ",        ROUND_ORDER),
        ("consolation",  f"{base}?module=standings&lhst=playoff&ptype=consolation",   CONSOLATION_ROUND_ORDER),
    ]
    rows = []
    last_soup = None

    for bracket_name, url, round_order in bracket_configs:
        soup = await goto_wait(page, url)
        last_soup = soup

        for div in soup.find_all("div", class_="bracket"):
            classes = set(div.get("class", []))
            round_key = next((c for c in _ALL_ROUND_KEYS if c in classes), None)
            if not round_key or round_key not in round_order:
                continue

            target = div.get("data-target", "")
            week_m = re.search(r"week=(\d+)", target)
            week = int(week_m.group(1)) if week_m else 0

            sides = [d for d in div.find_all("div", recursive=False)
                     if any(c in (d.get("class") or []) for c in ("No-bdrbot", "Bdrtop"))]
            if not sides:
                sides = div.find_all("div", class_=re.compile(r"ahead|behind"))
            if len(sides) < 2:
                continue

            seed1, team1, score1, won1 = parse_bracket_side(sides[0])
            seed2, team2, score2, won2 = parse_bracket_side(sides[1])
            winner = team1 if won1 else (team2 if won2 else "")

            rows.append({
                "season":    year,
                "bracket":   bracket_name,
                "week":      week,
                "round":     round_order[round_key],
                "game_type": GAME_TYPE_LABEL[round_key],
                "seed_1": seed1, "team_1": team1, "score_1": score1,
                "seed_2": seed2, "team_2": team2, "score_2": score2,
                "winner": winner,
            })

        n = sum(1 for r in rows if r["bracket"] == bracket_name)
        print(f"    {bracket_name}: {n} games")

    if not rows:
        print(f"    WARNING: Could not parse playoff bracket for {year}")
        with open(DATA_DIR.parent / f"debug_{year}_playoffs.html", "w") as f:
            f.write(str(last_soup))

    return rows


# ─── Manager / Team Info ──────────────────────────────────────────────────────

MANAGER_FIELDS = ["season", "team_name", "manager_name", "email",
                  "waiver_priority", "moves", "trades"]

async def scrape_managers(page, year):
    print(f"  Manager info...")
    soup = await goto_wait(page, league_url(year, "teams"))
    rows = []

    # /teams page has one table: Team Name | Manager | Email | Waiver | Moves | Trades
    table = soup.find("table", class_="Tst-table")
    if not table:
        print(f"    WARNING: No managers table found for {year}")
        return []

    for tr in table.find_all("tr"):
        cells = [clean(td.get_text()) for td in tr.find_all("td")]
        if len(cells) < 6:
            continue
        team, manager, email, waiver, moves, trades = cells[:6]
        if not team or team.lower() == "team name":
            continue
        rows.append({
            "season": year,
            "team_name": team,
            "manager_name": "" if manager == "--hidden--" else manager,
            "email": "" if email == "--hidden--" else email,
            "waiver_priority": waiver,
            "moves": moves,
            "trades": trades,
        })

    print(f"    Found {len(rows)} managers")
    return rows


# ─── League Settings ─────────────────────────────────────────────────────────

SETTINGS_FIELDS = [
    "season", "num_teams", "scoring_type", "draft_type", "roster_slots",
    "play_against_median", "divisions", "trade_deadline", "waiver_type",
    "max_acquisitions_season", "max_acquisitions_week", "draft_pick_trades",
    "fractional_points", "negative_points", "playoff_tiebreaker",
]

# Map from Yahoo's "Setting" label (stripped of colon) → our CSV column name
_SETTINGS_KEY_MAP = {
    "Max Teams":                             "num_teams",
    "Scoring Type":                          "scoring_type",
    "Draft Type":                            "draft_type",
    "Roster Positions":                      "roster_slots",
    "Play Against Median Score":             "play_against_median",
    "Divisions":                             "divisions",
    "Trade End Date":                        "trade_deadline",
    "Waiver Type":                           "waiver_type",
    "Max Acquisitions for Entire Season":    "max_acquisitions_season",
    "Max Acquisitions per Week":             "max_acquisitions_week",
    "Allow Draft Pick Trades":               "draft_pick_trades",
    "Fractional Points":                     "fractional_points",
    "Negative Points":                       "negative_points",
    "Playoff Tie-Breaker":                   "playoff_tiebreaker",
}

async def scrape_settings(page, year):
    print(f"  League settings...")
    soup = await goto_wait(page, league_url(year, "settings"))

    table = soup.find("table", id="settings-table")
    if not table:
        print(f"    WARNING: No settings table found for {year}")
        return []

    row = {"season": year}
    for tr in table.find_all("tr"):
        cells = [clean(td.get_text()) for td in tr.find_all("td")]
        if len(cells) < 2:
            continue
        key = cells[0].rstrip(":").strip()
        val = cells[1].strip()
        if key in _SETTINGS_KEY_MAP:
            row[_SETTINGS_KEY_MAP[key]] = val

    for field in SETTINGS_FIELDS:
        row.setdefault(field, "")

    print(f"    num_teams={row['num_teams']}  scoring={row['scoring_type']}  "
          f"draft={row['draft_type']}  median={row['play_against_median']}")
    return [row]


# ─── Transactions / Trades ────────────────────────────────────────────────────
#
# Trade filter page structure (transactionsfilter=trade):
#   4-cell row with span.F-trade icon  = start of new trade (side A)
#   3-cell row (no icon)               = other side of same trade (side B)
#
# Each side row: [icon?] [player cell] ["Traded to"] [team+date cell]
# player cell may contain multiple <a> player links (multi-player trades).

TRADE_FIELDS = ["season", "date", "team_name", "players_in", "players_in_pos", "trade_partner"]


def _parse_trade_cell_players(td):
    """Return (pipe-joined names, pipe-joined positions) from a player cell."""
    links = td.find_all("a")
    spans = td.find_all("span", class_="F-position")
    names = [clean(a.get_text()) for a in links]
    poss  = [clean(s.get_text()) for s in spans]
    return "|".join(names), "|".join(poss)


def _parse_trade_cell_team(td):
    """Return (team_name, date_str) from the rightmost cell of a trade row."""
    a = td.find("a")
    date_span = td.find("span", class_="F-timestamp")
    return (clean(a.get_text()) if a else "",
            clean(date_span.get_text()) if date_span else "")


async def scrape_transactions(page, year, tx_type="trade"):
    print(f"  Transactions ({tx_type})...")
    game, lid = LEAGUE_IDS[year]
    base_url = f"{BASE_URL}/{year}/{game}/{lid}/transactions"

    all_rows = []
    count = 0
    while True:
        url = f"{base_url}?transactionsfilter={tx_type}&count={count}"
        soup = await goto_wait(page, url, delay=DELAY)

        table = soup.find("table", class_="Tst-transaction-table")
        if not table:
            break

        tr_list = table.find_all("tr")
        if not tr_list:
            break

        # Parse each table row into a side tuple: (is_new_trade, players, pos, team, date)
        sides = []
        for tr in tr_list:
            tds = tr.find_all("td")
            has_icon = tr.find("span", class_="F-trade") is not None
            if has_icon and len(tds) == 4:
                # [icon] [players] ["Traded to"] [team+date]
                players, pos = _parse_trade_cell_players(tds[1])
                team, date   = _parse_trade_cell_team(tds[3])
                sides.append((True, players, pos, team, date))
            elif not has_icon and len(tds) >= 3:
                # [players] ["Traded to"] [team+date]
                players, pos = _parse_trade_cell_players(tds[0])
                team, date   = _parse_trade_cell_team(tds[-1])
                sides.append((False, players, pos, team, date))

        # Group into trades: icon row + following non-icon rows = one trade
        page_trades = 0
        i = 0
        while i < len(sides):
            if not sides[i][0]:          # stray non-icon row, skip
                i += 1
                continue
            _, p_a, pos_a, team_a, date_a = sides[i]
            # Collect all immediately-following non-icon rows (usually just 1)
            j = i + 1
            while j < len(sides) and not sides[j][0]:
                j += 1
            other_sides = sides[i + 1:j]
            for _, p_b, pos_b, team_b, _ in other_sides:
                all_rows.append({
                    "season": year, "date": date_a,
                    "team_name": team_a, "players_in": p_a, "players_in_pos": pos_a,
                    "trade_partner": team_b,
                })
                all_rows.append({
                    "season": year, "date": date_a,
                    "team_name": team_b, "players_in": p_b, "players_in_pos": pos_b,
                    "trade_partner": team_a,
                })
                page_trades += 1
            i = j

        print(f"    count={count}: {len(tr_list)} rows → {page_trades} trades")
        if len(tr_list) < 25:
            break
        count += 25

    print(f"    Total: {len(all_rows)//2} trades ({len(all_rows)} rows) for {year}")
    return all_rows


# ─── Main Orchestrator ────────────────────────────────────────────────────────

async def fetch_year(page, year, sections=None):
    sections = sections or ["standings", "draft", "matchups", "playoffs", "managers", "transactions", "settings"]
    print(f"\n{'='*50}")
    print(f"  Season {year}")
    print(f"{'='*50}")

    results = {}

    if "standings" in sections:
        rows = await scrape_standings(page, year)
        if rows:
            overwrite_csv("season_standings", STANDINGS_FIELDS, rows)
            results["standings"] = len(rows)

    if "draft" in sections:
        rows = await scrape_draft(page, year)
        if rows:
            overwrite_csv("draft_picks", DRAFT_FIELDS, rows)
            results["draft"] = len(rows)

    if "matchups" in sections:
        rows = await scrape_matchups(page, year)
        if rows:
            overwrite_csv("weekly_matchups", MATCHUP_FIELDS, rows)
            results["matchups"] = len(rows)

    if "playoffs" in sections:
        rows = await scrape_playoffs(page, year)
        if rows:
            overwrite_csv("playoff_games", PLAYOFF_FIELDS, rows)
            results["playoffs"] = len(rows)

    if "managers" in sections:
        rows = await scrape_managers(page, year)
        if rows:
            overwrite_csv("season_managers", MANAGER_FIELDS, rows)
            results["managers"] = len(rows)

    if "transactions" in sections:
        rows = await scrape_transactions(page, year)
        if rows:
            overwrite_csv("season_trades", TRADE_FIELDS, rows)
            results["transactions"] = len(rows)

    if "settings" in sections:
        rows = await scrape_settings(page, year)
        if rows:
            overwrite_csv("league_settings", SETTINGS_FIELDS, rows)
            results["settings"] = len(rows)

    return results


async def main():
    # Parse CLI args
    years = YEARS
    sections = None

    args = sys.argv[1:]
    if "--year" in args:
        idx = args.index("--year")
        year_args = []
        for a in args[idx+1:]:
            if a.startswith("--"):
                break
            year_args.append(int(a))
        if len(year_args) == 1:
            years = [year_args[0]]
        elif len(year_args) == 2:
            years = list(range(year_args[0], year_args[1] + 1))

    if "--section" in args:
        idx = args.index("--section")
        sections = []
        for a in args[idx+1:]:
            if a.startswith("--"):
                break
            sections.append(a)

    DATA_DIR.mkdir(exist_ok=True)

    async with async_playwright() as p:
        # Use a persistent context so login state survives between script runs
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        page = await ensure_logged_in(context, stealth=True)

        summary = {}
        for year in years:
            try:
                result = await fetch_year(page, year, sections)
                summary[year] = result
            except Exception as e:
                print(f"\n  ERROR for {year}: {e}")
                summary[year] = {"error": str(e)}

        await browser.close()

    print("\n\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    for year, result in summary.items():
        print(f"  {year}: {result}")


if __name__ == "__main__":
    asyncio.run(main())
