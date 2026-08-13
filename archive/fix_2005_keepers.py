#!/usr/bin/env python3
"""
fix_2005_keepers.py
One-time script: scrapes the 2005 transactions page to find the 12 keeper
adds from Sep 6 (entered by commissioner since Yahoo's draft page showed
round-15 as --empty-- that year), then inserts them into draft_picks.csv.
"""

import asyncio, csv, io, json, re
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

BASE_URL   = "https://football.fantasysports.yahoo.com"
LEAGUE_URL = f"{BASE_URL}/2005/f2/1172/transactions"
SESSION_FILE = Path(__file__).parent / ".yahoo_cookies.json"
DATA_DIR     = Path(__file__).parent / "data"
DRAFT_PATH   = DATA_DIR / "draft_picks.csv"
DRAFT_FIELDS = ["season", "round", "pick_in_round", "overall_pick",
                "team_name", "player_name", "is_keeper"]


def parse_add_row(tr):
    """
    Return (player_name, team_name) for an add-transaction row, or None.
    Each row has: [icon cell] [player cell (add on top / drop below)] [team+date cell]
    We want the ADDED player (first div in the player cell).
    """
    tds = tr.find_all("td")
    if len(tds) < 3:
        return None

    player_cell = tds[1]
    team_cell   = tds[2]

    # First div = added player
    divs = player_cell.find_all("div", recursive=False)
    if not divs:
        return None
    added_div = divs[0]
    name_tag  = added_div.find("a")
    if not name_tag:
        return None
    player_name = name_tag.get_text(strip=True)

    # Team name from anchor with class Tst-team-name
    team_tag = team_cell.find("a", class_="Tst-team-name")
    if not team_tag:
        return None
    team_name = team_tag.get_text(strip=True)

    # Date text (everything after team name in the cell)
    cell_text = team_cell.get_text(separator=" ", strip=True)
    date_text = cell_text.replace(team_name, "").strip()

    return player_name, team_name, date_text


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        cookies = json.loads(SESSION_FILE.read_text())
        await context.add_cookies(cookies)

        page = await context.new_page()

        keeper_adds = []   # (player_name, team_name, date)
        count = 0

        print("Paginating through 2005 add transactions to find Sep 6 keepers...")
        while True:
            url = f"{LEAGUE_URL}?transactionsfilter=add&count={count}"
            print(f"  Fetching count={count} ...")
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(3.5)
            html  = await page.content()
            soup  = BeautifulSoup(html, "html.parser")
            table = soup.find("table", class_="Tst-transaction-table")

            if not table:
                print("  No table found — done.")
                break

            rows = table.find_all("tr")
            if not rows:
                break

            page_has_sep = False
            for tr in rows:
                result = parse_add_row(tr)
                if not result:
                    continue
                player, team, date = result
                if re.search(r"Sep\s+6\b", date):
                    page_has_sep = True
                    keeper_adds.append((player, team, date))
                    print(f"    KEEPER: {player:28s} → {team:25s} ({date})")

            # Check for "Next 25" link
            next_link = soup.find("a", string=re.compile(r"Next", re.I))
            if not next_link:
                print("  No next page — done.")
                break

            count += 25

        await browser.close()

    if not keeper_adds:
        print("\nNo Sep 6 keeper adds found. Check pagination or date format.")
        return

    print(f"\nFound {len(keeper_adds)} keeper adds.")

    # Load existing draft picks
    existing = list(csv.DictReader(open(DRAFT_PATH)))

    # Check none already exist for 2005 / round 15 / is_keeper
    already = [r for r in existing
               if r["season"] == "2005" and r["is_keeper"].lower() == "true"]
    if already:
        print(f"WARNING: {len(already)} 2005 keeper rows already exist — aborting to avoid duplicates.")
        for r in already:
            print(f"  {r}")
        return

    # Determine next available overall_pick slot in round 15 for 2005
    # 12 teams × 14 rounds = 168; R15 picks = 169–180
    num_teams = 12
    new_rows = []
    for i, (player, team, date) in enumerate(keeper_adds, start=1):
        new_rows.append({
            "season":       2005,
            "round":        15,
            "pick_in_round": i,
            "overall_pick": (14 * num_teams) + i,
            "team_name":    team,
            "player_name":  player,
            "is_keeper":    True,
        })

    all_rows = existing + [dict(r) for r in new_rows]
    # Re-sort: season, round, overall_pick
    all_rows.sort(key=lambda r: (str(r["season"]), str(r["round"]).zfill(2), str(r["overall_pick"]).zfill(3)))

    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=DRAFT_FIELDS)
    w.writeheader()
    w.writerows(all_rows)
    DRAFT_PATH.write_text(out.getvalue())

    print(f"\nAdded {len(new_rows)} keeper rows to draft_picks.csv:")
    for r in new_rows:
        print(f"  R{r['round']} pick {r['pick_in_round']:2d}  {r['player_name']:28s}  {r['team_name']}")


if __name__ == "__main__":
    asyncio.run(main())
