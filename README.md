# FFL History — Project Overview

25-year fantasy football league (Yahoo, commissioner: Shawn, league slug `sme327`).
This folder contains the data pipeline that scrapes and normalizes historical league data
for use in a Streamlit history app.

For detailed methodology, data quirks, and the reasoning behind decisions, see **[DATA_GUIDE.md](DATA_GUIDE.md)**.

---

## Scripts

### `fetch_yahoo_data.py`
Main scraper. Uses Playwright (headless Chrome) + BeautifulSoup to pull data directly
from Yahoo Fantasy Football's HTML pages. Requires a saved Yahoo login session.

**Usage:**
```
python fetch_yahoo_data.py                        # all years, all sections
python fetch_yahoo_data.py --year 2010            # single year
python fetch_yahoo_data.py --year 2005 2010       # range of years
python fetch_yahoo_data.py --section transactions # specific section only
```

**Sections:** `standings`, `draft`, `matchups`, `playoffs`, `managers`, `transactions`

**Sessions:** Login is handled interactively on first run and saved to `.yahoo_cookies.json`.
Subsequent runs reuse the saved session. Delete the file to force a fresh login.

**Rate limiting:** Yahoo blocks after ~40 rapid page loads. The scraper uses a 3.5s delay
between requests and auto-pauses 5 minutes on "Request denied" responses.

---

### `inspect_yahoo_page.py`
Diagnostic tool for examining Yahoo page structure — use this when building or debugging
new scrapers. Opens a browser window, fetches a page, and prints its HTML element summary.

**Usage:**
```
python inspect_yahoo_page.py standings 2004
python inspect_yahoo_page.py draftresults 2004
python inspect_yahoo_page.py "https://full.url.here" 2004
```

---

### `build_player_positions.py`
One-time script that builds `data/player_positions.csv` by matching every player name
in `draft_picks.csv` against the nflverse players database (`data/ref_nfl_players.csv`).
Re-run after adding new draft seasons.

**Usage:**
```
python build_player_positions.py
```

Handles team defenses (→ `DEF`), stale Yahoo team suffixes in old player names,
generational suffixes (Jr./Sr./II/III), known nicknames, and a small manual override
list for players absent from nflverse. Coverage: 100% of 1,140 unique drafted players.

---

## Data Files (`data/`)

### `season_standings.csv`
Final regular-season standings for each year.
**Columns:** `season, rank, team_name, wins, losses, ties, points_for, points_against, streak, waiver_priority, moves`
**Coverage:** 2001–2025 (complete)
- `points_for` and `points_against` for **2001–2003** are derived from `weekly_matchups.csv` (sum of team scores and opponent scores respectively) — Yahoo's early standings page displayed PA where the scraper expected PF, so both columns were reconstructed from weekly game data
- `waiver_priority` contains **FAAB remaining balance** (e.g., `$80`) for **2011–2025**; for 2001–2010 it is a numeric priority (1 = highest). The league switched to FAAB waivers in 2011. Use `league_settings.csv` `waiver_type` to branch logic.

---

### `draft_picks.csv`
Every pick from every draft.
**Columns:** `season, round, pick_in_round, overall_pick, team_name, player_name, is_keeper`
**Coverage:** 2001–2025 (complete)
- 2011: Yahoo incorrectly displays this draft in auction format, but picks are in chronological snake order. Parsed with snake correction for even rounds (`pick_in_round = 12 - pos_in_group`).
- `is_keeper` detection by era:
  - **2001–2002**: always `False` — no keeper system yet
  - **2003**: Yahoo entered keepers as round 1 picks; normalized to `round = 15` in the scraper so they don't pollute first-round analysis
  - **2004–2009**: `round == 15` and player not `--empty--` — no Yahoo indicator; empty round-15 slots mean keeper not exercised
  - **2010–2013**: Yahoo "K" marker detected; keepers appearing in R1 (2013 transition year) normalized to R15
  - **2014+**: Yahoo "K" marker; keepers appear at their true cost round (one round earlier than drafted the prior year)
- Keeper cost = the draft round the player is kept at. No separate FAAB cost column — Yahoo's "Keeper Salary" field reflects internal encoding, not a real dollar cost.
- No `player_pos` column — Yahoo's draft results page does not expose position; join to `player_positions.csv` on `player_name` to get position

---

### `player_positions.csv`
Position lookup for every player ever drafted. Built by `build_player_positions.py`.
**Columns:** `player_name, position, match_source`
- `position`: NFL position abbreviation (`QB`, `RB`, `WR`, `TE`, `K`, `DEF`)
- `match_source`: how the position was resolved — `nflverse`, `nflverse_ambiguous`, `nflverse_no_suffix`, `nflverse_nickname`, `defense`, or `manual`
- 1,128 rows; 100% coverage of drafted players
- Join to `draft_picks.csv` on `player_name`

---

### `ref_nfl_players.csv`
Downloaded from [nflverse](https://github.com/nflverse/nflverse-data) — reference file only, not scraped.
Contains ~25K NFL players with `display_name`, `position`, and cross-reference IDs (gsis, pfr, espn, etc.).
Used exclusively as the position lookup source for `build_player_positions.py`.
Re-download periodically to pick up newly added players.

---

### `weekly_matchups.csv`
One row per team per week. Includes both regular season and playoff weeks.
**Columns:** `season, week, team_name, opponent, result, team_score, opponent_score, is_bye, is_playoff`
- `is_bye`: true only for 2001 (9 teams) and 2002 (11 teams) where rotating byes occurred
- `is_playoff`: true for any week at or after the playoff start week for that season
- Playoff start weeks vary: wk 16 (2001), wk 15 (2002–2004, 2021–2025), wk 14 (2005–2020)
- Consolation bracket games for non-playoff teams are **not** captured for most years
**Coverage:** 2001–2025 (complete — all seasons have full week ranges)

---

### `playoff_games.csv`
Game-by-game results for both the championship and consolation brackets.
**Columns:** `season, bracket, week, round, game_type, seed_1, team_1, score_1, seed_2, team_2, score_2, winner`
- `bracket`: `championship` or `consolation`
- `game_type` (championship): `quarterfinal`, `semifinal`, `final`, `3rd_place`
- `game_type` (consolation, 2001–2020): `semifinal`, `5th_place`, `7th_place` — 4 games per year
- `game_type` (consolation, 2021–2025): `semifinal`, `7th_place` — 3 games per year; no 11th/12th place game in 6-team playoff format. Note: `7th_place` in these years is actually the consolation championship (9th place overall); Yahoo reuses the same CSS class regardless of bracket size.
- Consolation seeds reflect each team's original championship seeding
- 281 total rows: 186 championship + 95 consolation
**Coverage:** 2001–2025 (complete)

---

### `season_managers.csv`
Per-season team and manager information.
**Columns:** `season, team_name, manager_name, email, waiver_priority, moves, trades`
- `manager_name` and `email` are the person behind each team that year
- Some early years have `--hidden--` emails; those are patched from `manager_lookup.csv`
**Coverage:** 2001–2025 (complete)

---

### `manager_lookup.csv`
Canonical person-to-email mapping — used to normalize manager identity across years
when the same person used different team names or email addresses.
**Columns:** `email, canonical_name, notes`
- Covers all known managers; Brian Clark and Tom Masterson each used two Yahoo accounts
- Yahoo display names patched: "Psps" → Fadi, "AdamJ" → Adam, "angry cat" → Nick Blaettler

---

### `managers.csv`
Canonical registry of every person who has ever been in the league. One row per person.
**Columns:** `canonical_name, display_name, first_season, last_season, seasons_played, notes`
- 24 rows — 10 active through 2025, 14 former members
- One one-season member without a full name on record: "BV" (2010, friend of Fadi's)

---

### `team_name_history.csv`
Every team name each manager used, by season. One row per manager per season.
**Columns:** `canonical_name, season, team_name`
- 296 rows — derived from `season_managers.csv`
- Sorted by canonical_name then season

---

### `franchise_history.csv`
Tracks which franchise "seat" (F01–F12) each manager held each season. A seat persists when one
manager replaces another; expansion slots were added in 2002 (F10, F11) and 2003 (F12).
**Columns:** `franchise_id, season, manager_name`
- 296 rows (9 franchises × 2001, 11 × 2002, 12 × 2003–2025)
- F01–F09: founding seats (2001); F10–F11: 2002 expansion; F12: 2003 expansion

| Franchise | Lineage |
|-----------|---------|
| F01 | Adam → Douglas (2015) |
| F02 | Brian Clark |
| F03 | Byron → Dominic (2005) |
| F04 | Dale → Joe Tyszko (2003) → Nick Blaettler (2010) → Bryan Kearney (2021) → Eric (2023) |
| F05 | Dan → Evan (2004) |
| F06 | Fadi |
| F07 | Jamie → Mike (2006) → BV (2010) → Robby (2011) → Jeff (2017) |
| F08 | Rob → Steve Swanson (2007) |
| F09 | Shawn |
| F10 | Kevin O'Boyle (joined 2002) |
| F11 | Kevin Swanson (joined 2002) |
| F12 | Thomas/Tom Masterson (joined 2003 as "Tupa") |

---

### `season_trades.csv`
All trades, one row per player received per team. Two rows per 1-for-1 trade; more for multi-player trades.
**Columns:** `season, trade_id, date, team_name, player_name, player_pos, trade_partner`
- `trade_id`: 8-char hash shared by all rows belonging to the same trade
- `team_name`: team that received this player
- `trade_partner`: team that sent this player (and received the other side)
- 2009 and 2014 had 0 trades
- 80 unique trades across 25 seasons; 247 player-rows total
**Coverage:** 2001–2025 (complete)

---

### `season_rosters.csv`
Final week roster snapshots. Currently only has 2001 week 17 data — deferred.
**Columns:** `season, week, team_name, slot, player_name, fantasy_points, starter_status`

---

### `manual_timeline_events.csv`
Hand-authored narrative events for the league timeline. Supplements scraped data with editorial milestones, dynasty markers, heartbreak moments, and franchise transitions that have no structured data source.
**Columns:** `season, event_date, event_type, title, description, manager, franchise_id, team_name, player_name, importance, source, show_on_homepage, show_on_league_timeline, show_on_franchise_page, show_on_manager_page`
- `event_type`: `milestone`, `dynasty`, `heartbreak`, `note`, `rule_change`, `steward_change`, `breakthrough`
- `importance`: `high`, `medium`, `low` — controls display prominence
- `show_on_*` flags: control which pages surface the event
- `source` is always `editorial` for this file (as opposed to scraped events added by other pages)

---

## Other Files

- **`archive/`** — completed one-time migration scripts; kept for documentation of methodology but not intended to be run again
- **`.yahoo_cookies.json`** — saved Yahoo login session; delete to force fresh login
- **`.claude/`** — Claude Code project memory (do not delete)

---

## Known Data Gaps & Pending Work

| Item | Status |
|------|--------|
| 2011 draft picks | Complete — scraped from Yahoo auction-format page with snake correction |
| `roster_moves.csv` | Not yet built — FA adds/drops/waivers from transactions page |
| `league_settings.csv` | Built manually; requires manual updates if league settings change |
| Consolation bracket matchups | Not captured in `weekly_matchups` (only championship bracket) |
| `ref_nfl_players.csv` | Re-download periodically from nflverse for new player coverage |
