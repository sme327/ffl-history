#!/usr/bin/env python3
"""
inspect_yahoo_page.py

Fetches a Yahoo Fantasy page and prints its HTML structure so we can
write correct parsers for fetch_yahoo_data.py.

Usage:
    python inspect_yahoo_page.py standings 2004
    python inspect_yahoo_page.py draft 2004
    python inspect_yahoo_page.py scoreboard 2004 week=1
    python inspect_yahoo_page.py playoffs 2004
"""

import asyncio
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

LEAGUE_SLUG = "sme327"
BASE_URL = "https://football.fantasysports.yahoo.com"
SESSION_FILE = Path(__file__).parent / ".yahoo_cookies.json"

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


def league_url(year, section="", extra=""):
    year = int(year)
    if year in LEAGUE_IDS:
        lid = LEAGUE_IDS[year]
        base = f"{BASE_URL}/{year}/f2/{lid}"
        if section:
            return f"{base}/{section}"
        return base
    else:
        base = f"{BASE_URL}/league/{LEAGUE_SLUG}/{year}"
        if section:
            return f"{base}/{section}"
        return base


async def ensure_logged_in(context):
    """Navigate to Yahoo login, wait for user, save cookies."""
    if SESSION_FILE.exists():
        cookies = json.loads(SESSION_FILE.read_text())
        await context.add_cookies(cookies)
        # Quick check — try to load a Yahoo page and see if we're logged in
        page = await context.new_page()
        await page.goto("https://www.yahoo.com", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        content = await page.content()
        if 'id="ybar-useremail"' in content or "Sign Out" in content or "sme327" in content.lower():
            print("Already logged in via saved session.\n")
            await page.close()
            return
        await page.close()

    # Need to log in — go to yahoo.com (not the fantasy URL) to avoid bot detection
    page = await context.new_page()
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


async def main():
    section = sys.argv[1] if len(sys.argv) > 1 else "standings"
    year = sys.argv[2] if len(sys.argv) > 2 else "2004"
    extra = sys.argv[3] if len(sys.argv) > 3 else ""

    # Allow passing a full URL directly as section
    if section.startswith("http"):
        url = section
        section = "url"  # safe filename segment
    else:
        year_int = int(year)
        game, lid = LEAGUE_IDS[year_int]
        base = f"{BASE_URL}/{year}/{game}/{lid}"
        if section == "standings":
            url = f"{base}?lhst=stand#leaguehomestandings"
        elif section == "matchups":
            url = f"{base}?matchup_week={extra}&module=matchups&lhst=matchups" if extra else f"{base}/matchup"
        elif section == "playoffs":
            url = f"{base}?module=standings&lhst=playoff#lhstplayoff"
        elif section == "schedule":
            url = f"{base}?module=standings&lhst=sched#lhstsched"
        elif section == "alltime":
            url = f"{base}?module=standings&lhst=alltime#lhstalltime"
        elif section in ("", "home"):
            url = base
        else:
            url = f"{base}/{section}?{extra}" if extra else f"{base}/{section}"

    print(f"Target URL: {url}\n")

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

        await ensure_logged_in(context)

        page = await context.new_page()
        print(f"Navigating to: {url}")
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(4)

        html = await page.content()
        if "Request denied" in html or len(html) < 500:
            print("\nYahoo returned 'Request denied' — IP is rate-limited.")
            print("Wait 15-20 minutes then try again.")
            input("Or navigate manually in the browser to the page above, then press Enter to capture what loaded.")
            html = await page.content()

        final_url = page.url

        out_file = Path(__file__).parent / f"debug_{year}_{section}.html"
        out_file.write_text(html, encoding="utf-8")
        print(f"Saved HTML to: {out_file}")

        soup = BeautifulSoup(html, "html.parser")

        print(f"\nPage title: {soup.title.get_text() if soup.title else '(none)'}")
        print(f"Final URL:  {final_url}")

        print("\n--- Tables found ---")
        for i, table in enumerate(soup.find_all("table")[:8]):
            classes = table.get("class", [])
            id_ = table.get("id", "")
            rows = len(table.find_all("tr"))
            cols = len(table.find_all("th"))
            print(f"  [{i}] id={id_!r} class={classes} rows={rows} cols={cols}")
            headers = [th.get_text(strip=True) for th in table.find_all("th")]
            if headers:
                print(f"       headers: {headers[:12]}")
            # Print first data row as sample
            trs = table.find_all("tr")
            if len(trs) > 1:
                sample = [td.get_text(strip=True) for td in trs[1].find_all(["td", "th"])]
                print(f"       sample:  {sample[:8]}")

        print("\n--- Key divs/sections ---")
        for cls_pattern in ["standings", "draft", "scoreboard", "matchup", "bracket", "team", "player"]:
            els = soup.find_all(class_=re.compile(cls_pattern, re.I))
            if els:
                print(f"  .{cls_pattern}: {len(els)} elements")
                for el in els[:2]:
                    text = el.get_text(strip=True)[:100]
                    print(f"    → {el.name} class={el.get('class')} | {text!r}")

        print("\n--- IDs on page ---")
        for el in soup.find_all(id=True)[:20]:
            print(f"  #{el.get('id')} ({el.name})")

        # Save cookies in case they were refreshed
        cookies = await context.cookies()
        SESSION_FILE.write_text(json.dumps(cookies))

        input("\nPress Enter to close the browser.")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
