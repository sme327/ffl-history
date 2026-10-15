"""List every game on Yahoo's playoff bracket pages, with Yahoo's own round labels. Read-only.

    python3 scripts/probe_playoff_brackets.py              # 2021-2025
    python3 scripts/probe_playoff_brackets.py 2019 2025    # any season range

Why: fetch_yahoo_data.py's scrape_playoffs() keeps only the round types the
2001-2020 format used, so for the 6-team format (2021-) playoff_games.csv is
missing 5 placement games a season (docs/DATA_GUIDE.md -> Known Gaps). This
probe records every bracket box on the championship and consolation pages, so
we can see what those games are and how Yahoo files them before deciding
whether any should count. It changes no data file.

Session: the museum's .yahoo_cookies.json. If Yahoo sends it to the login page,
a visible browser window opens on login.yahoo.com; sign in there and the
probe continues by itself (up to 10 minutes), then saves the refreshed session
back to .yahoo_cookies.json for the next fetch.

Output: raw pages in .local/raw/brackets/, a summary in
.local/raw/brackets/brackets.json, and one line per game on stdout.
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from fetch_yahoo_data import league_url  # noqa: E402

COOKIES = ROOT / ".yahoo_cookies.json"
OUT = ROOT / ".local" / "raw" / "brackets"
PAGES = ("champ", "consolation")


def side(div) -> dict:
    seed = div.find("span", class_="yfa-rank")
    name = div.find("span", class_="Ell")
    link = name.find("a") if name else None
    nums = [s.get_text(strip=True) for s in div.find_all("span", class_="Block")
            if re.match(r"^\d+\.?\d*$", s.get_text(strip=True))]
    return {"seed": seed.get_text(strip=True) if seed else "",
            "team": (link or name).get_text(strip=True) if name else "",
            "score": nums[-1] if nums else "",
            "won": "ahead" in (div.get("class") or [])}


def boxes(html: str, season: int, page: str) -> list[dict]:
    rows = []
    for div in BeautifulSoup(html, "html.parser").find_all("div", class_="bracket"):
        week = re.search(r"week=(\d+)", div.get("data-target", ""))
        sides = [d for d in div.find_all("div", recursive=False)
                 if any(c in (d.get("class") or []) for c in ("No-bdrbot", "Bdrtop"))]
        sides = sides or div.find_all("div", class_=re.compile(r"ahead|behind"))
        rows.append({"season": season, "page": page,
                     "round": [c for c in div.get("class", []) if c != "bracket"],
                     "week": week.group(1) if week else "",
                     "sides": [side(s) for s in sides[:2]]})
    return rows


async def logged_in_page(pw):
    """A page with a working Yahoo session; opens a visible login window if needed."""
    browser = await pw.chromium.launch()
    context = await browser.new_context()
    if COOKIES.exists():
        await context.add_cookies(json.loads(COOKIES.read_text()))
    page = await context.new_page()
    await page.goto(f"{league_url(2025)}?module=standings&lhst=playoff&ptype=champ",
                    wait_until="domcontentloaded")
    if "login.yahoo.com" not in page.url:
        return browser, page

    await browser.close()
    print("Yahoo session expired. Sign in in the browser window that just opened (10 minutes).")
    browser = await pw.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://login.yahoo.com", wait_until="domcontentloaded")
    for _ in range(120):
        await page.wait_for_timeout(5000)
        if "login.yahoo.com" not in page.url:
            break
    else:
        raise SystemExit("No sign-in within 10 minutes; nothing was read.")
    await page.goto(f"{league_url(2025)}?module=standings&lhst=playoff&ptype=champ",
                    wait_until="domcontentloaded")
    if "login.yahoo.com" in page.url:
        raise SystemExit("Still not signed in; nothing was read.")
    COOKIES.write_text(json.dumps(await context.cookies()))
    print("Signed in; session saved to .yahoo_cookies.json.")
    return browser, page


async def main(first: int, last: int) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    async with async_playwright() as pw:
        browser, page = await logged_in_page(pw)
        for season in range(first, last + 1):
            for kind in PAGES:
                await page.goto(f"{league_url(season)}?module=standings&lhst=playoff&ptype={kind}",
                                wait_until="domcontentloaded")
                await page.wait_for_timeout(2500)
                html = await page.content()
                (OUT / f"{season}-{kind}.html").write_text(html, encoding="utf-8")
                found = boxes(html, season, kind)
                print(f"{season} {kind}: {len(found)} bracket boxes")
                rows += found
        await browser.close()
    (OUT / "brackets.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    for r in rows:
        teams = " vs ".join(f"({s['seed']}) {s['team']} {s['score']}{' W' if s['won'] else ''}" for s in r["sides"])
        print(f"{r['season']} {r['page']:11} wk{r['week']:>2} {'.'.join(r['round']):20} {teams}")


if __name__ == "__main__":
    years = [int(a) for a in sys.argv[1:3]] or [2021, 2025]
    asyncio.run(main(years[0], years[-1]))
