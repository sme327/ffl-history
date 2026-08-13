# Data Guide — The Long Game

This document covers the methodology, quirks, and reasoning behind every data file in this project. It is intended for anyone building features on top of this data who needs to understand *why* things are the way they are, not just what the columns mean.

---

## Source and Scraping Overview

All data originates from Yahoo Fantasy Football's historical league pages, scraped with Playwright (headless Chrome) and BeautifulSoup. Yahoo does not expose an API for historical data. Everything had to be extracted from rendered HTML, which means the scraper is fragile to Yahoo's markup changes and varies significantly across eras.

Yahoo's URL structure changed over the years:

| Years | Game Prefix |
|-------|-------------|
| 2001–2003 | `f1` |
| 2004–2008 | `f2` |
| 2009–2025 | `f1` |

The league slug is `sme327`. League IDs by year are hardcoded in `LEAGUE_IDS` in `fetch_yahoo_data.py`.

**Rate limiting:** Yahoo blocks scrapers after roughly 40 rapid page loads. A 3.5-second delay runs between every request. On "Request denied" responses, the scraper auto-pauses for 5 minutes. Yahoo session cookies are saved to `.yahoo_cookies.json` after the first login so subsequent runs can reuse the session.

---

## `draft_picks.csv` — 4,440 rows, 2001–2025

The most structurally complex file in the project. Yahoo's draft pages changed format several times over 25 years.

### Draft Format History

**2001 — Autopick:** Yahoo chose all players automatically. There was no live draft. The picks are preserved in Yahoo's system and are included here, but they do not reflect any strategic decision-making by managers.

**2002 — First Live Draft:** Conducted offline (in person or via phone/chat). Yahoo's records exist and are scraped normally using Format B (per-round tables).

**2003–2025 — Snake Draft:** Standard snake format. Yahoo shows one table per round with a "Round N" header. The scraper reads these tables in order, calculates `overall_pick` sequentially, and uses `pick_in_round` as Yahoo reports it.

**2011 — Auction Display Bug:** Yahoo renders the 2011 draft as a flat auction-style table (columns: Pick | Player | Salary | Team) despite the draft being a standard snake draft. The picks are in chronological draft order, which means the snake direction is correct for odd rounds but reversed for even rounds. The scraper detects the auction-format table (via a "Salary" column header), reads picks in order, and applies a snake correction for even rounds: `pick_in_round = 12 - position_in_round`. This is the only year with this bug.

### Keeper System History

The league has run a keeper system since 2003. How Yahoo recorded keepers changed several times.

**2001–2002 — No Keepers:** `is_keeper = False` for all picks. The keeper system did not exist yet.

**2003 — Keepers as Round 1 Artifacts:** The league introduced keepers. Yahoo entered all 12 keepers as each manager's first-round pick in the system, even though they conceptually occupied the 15th-round slot. Because all 12 first-round picks were keepers, there are **no actual first-round picks in 2003** — the draft ran rounds 2 through 15. In the data, these keepers have been **normalized to round 15** so they don't pollute first-round analysis and remain consistent with every other pre-2014 season.

**2004–2009 — Heuristic Detection:** Yahoo did not yet add any visual marker for keepers. The rule was simple: the league used round 15 exclusively for keepers. If a player occupies round 15 and is not `--empty--`, they are a keeper. An `--empty--` in round 15 means a manager chose not to keep anyone that slot. This heuristic is not perfect — if a manager legitimately drafted someone in round 15 (not as a keeper), it would be indistinguishable. In practice this never happened; round 15 was always the designated keeper round.

**2005 — Keepers from Transactions Page:** The 2005 draft page showed all 12 round-15 slots as `--empty--`. The commissioner had entered keepers via the transactions page (as adds) rather than through the draft flow that year. Those `--empty--` rows were removed and replaced with keeper data scraped from the transactions page, filtered to exactly the 12 adds that occurred on September 6 (the keeper entry date). The script `fix_2005_keepers.py` performed this one-time migration.

**2010–2013 — Yahoo "K" Marker Introduced:** Yahoo began displaying a visual "K" badge on keeper players in the draft interface. The scraper detects this via a `<span>` element whose `title` attribute contains the word "keeper" (case-insensitive). The exact title text changed over time — early years used `"This player is a keeper."`, later years shifted to `"Keeper Salary: N"` — but matching on "keeper" as a substring handles both.

2013 was a transition year: Yahoo still entered keepers at round 1 in its system. These keepers appear in round 1 in the raw data but have been **normalized to round 15**, same as 2003.

**2014+ — Keeper Cost Round:** Starting in 2014, Yahoo began placing keepers at their actual cost round. The rule: keeping a player costs the round one earlier than where they were drafted the previous year. If you drafted someone in round 3 last year, you keep them this year in round 2. Yahoo now correctly places the pick at that cost round in the draft results, and `is_keeper = True` is detected by the "K" span.

There is no separate cost column. The round number *is* the cost. Early seasons had an occasional rule allowing a player drafted in round 1 to be kept for a $25–$50 FAAB fee instead of a round, but Yahoo's "Keeper Salary" field reflects internal encoding, not a real dollar amount, so no FAAB cost is tracked here.

### Pre-2014 Keeper Normalization

For all years before 2014, any keeper not already at round 15 is moved there in post-processing:

```
round = 15
overall_pick = (14 × 12) + pick_in_round = 169–180
```

This keeps the analysis consistent: round 15 = keeper round for the entire 2003–2013 era. You can safely look at round 1 picks for any year and trust they are real first-round selections — except 2003, which has no round 1 at all.

### `--empty--` Rows

A small number of rows have `player_name = "--empty--"`. These are round-15 slots where no keeper was exercised (the slot was left empty in Yahoo's draft system). They appear in 2002, 2012, and 2017. They should be excluded from any player-level analysis.

### Position Data

Yahoo's draft results pages do not expose player position. Position comes from a separate join to `player_positions.csv` on `player_name`. Do not assume positions exist on `draft_picks` directly.

---

## `player_positions.csv` — 1,128 rows

Built by `build_player_positions.py` against the nflverse players database (`ref_nfl_players.csv`, ~25K players). Covers every unique player name in `draft_picks.csv` at 100% resolution.

### Matching Logic (4-Tier Fallback)

**1. Direct name match:** Normalize both the Yahoo name and the nflverse `display_name` to lowercase, strip punctuation and extra whitespace, then look up. Handles ~87% of players.

**2. Nickname map:** A small hardcoded dictionary of Yahoo names that differ from nflverse canonical names:

| Yahoo name | nflverse name | Reason |
|---|---|---|
| Beanie Wells | Chris Wells | Nickname vs. legal name |
| Deebo Samuel | Deebo Samuel Sr. | nflverse disambiguates father from son |
| Hollywood Brown | Marquise Brown | Nickname vs. legal name |
| Stephen Hauschka | Steven Hauschka | Minor spelling variant |
| Nyheim Miller-Hines | Nyheim Hines | Yahoo used his full hyphenated surname; nflverse does not |
| Trenton Richardson | Trent Richardson | Yahoo used full legal name |
| Joe Jerevicius | Joe Jurevicius | Yahoo misspelling of the actual last name |

The normalization function strips hyphens and punctuation, so "Nyheim Miller-Hines" and "Nyheim Millerhines" both normalize to the same key, which is then looked up in the map.

**3. Generational suffix stripping:** Strip Jr./Sr./II/III/IV from the end and retry. Handles cases where Yahoo includes a suffix that nflverse omits or vice versa.

**4. Manual overrides:** Four players absent from nflverse entirely (retired before nflverse's coverage window or otherwise missing):

| Player | Position | Note |
|---|---|---|
| Michael Vick | QB | Career predates nflverse coverage |
| Joshua Palmer | WR | Not in nflverse players database |
| Kenneth Gainwell | RB | Not in nflverse players database |
| Kenneth Barber | RB | Not in nflverse players database |

### Defense Detection

If a player name is 1–2 words and one of those words is an NFL team name (e.g., "Patriots", "Ravens", "49ers"), it is assigned `position = DEF`. This handles all 32 NFL team defenses as drafted units.

### `match_source` Values

| Value | Meaning |
|---|---|
| `nflverse` | Unique name match |
| `nflverse_ambiguous` | Multiple players with same name; skill position preferred |
| `defense` | Team defense detected by name |
| `nflverse_no_suffix` | Matched after stripping generational suffix |
| `nflverse_nickname` | Matched via NICKNAME_MAP |
| `manual` | Hardcoded override; not in nflverse |

`nflverse_ambiguous` occurs when the same name exists for multiple players in nflverse (e.g., "A.J. Green"). In those cases the resolver picks the highest-priority fantasy-relevant position (QB > RB > WR > TE > K > DEF). This is almost always correct since fantasy drafts skew heavily toward skill positions.

### Re-running

Re-run `build_player_positions.py` after adding any new draft seasons. The script is fully idempotent — it rebuilds the entire file from scratch each time.

---

## `season_standings.csv` — 296 rows, 2001–2025

One row per team per season. Final regular-season standings only.

### Points For / Points Against (2001–2003)

Yahoo's early standings page displayed columns in an unexpected order — the scraper was reading `points_against` where it expected `points_for`. Rather than trusting incorrect scraped values, both `points_for` and `points_against` for 2001–2003 were reconstructed from `weekly_matchups.csv`:

- `points_for` = sum of `team_score` across all regular-season weeks for that team
- `points_against` = sum of `opponent_score` across all regular-season weeks for that team

This is mathematically equivalent to what Yahoo would show and is more reliable than the mis-parsed standings values.

### `waiver_priority` — Dual Meaning

This column means two different things depending on the era:

| Era | Value format | Meaning |
|---|---|---|
| 2001–2010 | Integer (1–12) | Waiver priority rank; 1 = highest priority |
| 2011–2025 | Dollar string (e.g., `$78`) | FAAB budget remaining at season end |

The league switched from priority-based waivers to FAAB (Free Agent Acquisition Budget) in 2011. Use `league_settings.csv` → `waiver_type` to branch logic: an empty `waiver_type` or "Continual rolling list" means priority; a FAAB-style value means dollar budget.

---

## `weekly_matchups.csv` — 4,573 rows, 2001–2025

One row per team per week. Each game produces two rows (one from each team's perspective).

### Playoff Detection

`is_playoff = True` for any week at or after that season's playoff start week. The start week shifted twice over the league's history:

| Seasons | Playoff Start Week |
|---|---|
| 2001 | Week 16 |
| 2002–2004 | Week 15 |
| 2005–2020 | Week 14 |
| 2021–2025 | Week 15 |

The 2021 shift back to week 15 reflects the NFL extending its regular season to 18 games, which pushed the fantasy playoff window. The scraper derives `is_playoff` purely from the week number against this lookup — it does not parse Yahoo's playoff bracket structure.

### Bye Weeks (2001–2002 Only)

The league started with 9 teams in 2001 and expanded to 11 in 2002. With an odd number of teams, one team had a bye each week. `is_bye = True` marks those rows. Bye weeks don't exist in any other season — from 2003 onward the league had 12 teams and a full schedule every week.

### Consolation Bracket

Consolation bracket games are **not captured** in this file. The scraper only pulled championship bracket matchup data. Consolation games from the playoff period are missing here; they appear in `playoff_games.csv` instead (as game-level results, not week-level matchup rows).

---

## `playoff_games.csv` — 281 rows, 2001–2025

Game-level playoff results for both the championship and consolation brackets.

### Bracket Structure Change (2021)

Before 2021, the league ran an 8-team playoff across both brackets:
- Championship: top 4 seeds — quarterfinals, semifinals, final, 3rd-place game
- Consolation: seeds 5–8 — semifinals, 5th-place game, 7th-place game

Starting in 2021, the league expanded to a 6-team championship bracket (adding a bye round), which changed consolation structure:
- Championship: 6 seeds — quarterfinals (2 games), semifinals, final, 3rd-place game
- Consolation: 3 games instead of 4; no 11th/12th place game in the 6-team format

**Important:** In 2021–2025, the game labeled `game_type = "7th_place"` in the consolation bracket is actually the consolation *championship* (9th place overall). Yahoo reuses the same CSS class regardless of how many teams are in the consolation bracket, so the label is inherited from the markup rather than from the actual game position.

### Seeding

Seeds reflect each team's **original championship seeding** based on regular-season finish. Consolation bracket seeds are not re-seeded; a team listed as seed 6 in consolation was the 6th seed in the original bracket.

---

## `season_managers.csv` — 296 rows, 2001–2025

Per-season record of which person managed which team. One row per team per season.

The `manager_name` field contains the person's canonical name as defined in `manager_lookup.csv`. In early seasons, Yahoo's team manager display varied — some names appeared as Yahoo usernames ("Psps", "AdamJ", "angry cat") rather than real names. These have been corrected:

| Yahoo display | Canonical name |
|---|---|
| Psps | Fadi |
| AdamJ | Adam |
| angry cat | Nick Blaettler |

**Brian Clark** is the only manager with two active Yahoo accounts over the league's life (`shaman3@rocketmail.com` for 2002–2006, `brianjclark13@yahoo.com` for 2001 and 2007–2025). Both accounts resolve to the same canonical name.

**Jamie** (Shawn's ex-wife, seasons 2001–2005) has no email address on record. Her `manager_lookup.csv` entry has a blank email field.

---

## `manager_lookup.csv` — 26 rows

Canonical identity mapping. Every email address that has ever appeared in the league maps to one `canonical_name`. This table is the authoritative source for resolving identity across seasons when team names, email addresses, or Yahoo display names changed.

Use this to join `season_managers.csv` on `email → canonical_name` when you need a consistent person-level identifier across all 25 seasons.

---

## `managers.csv` — 24 rows

One row per unique person. `first_season`, `last_season`, and `seasons_played` are derived values. 10 managers are active through 2025; 14 are former members. **BV** (2010 only, friend of Fadi's) is the only member with no last name on record.

---

## `franchise_history.csv` — 296 rows, 2001–2025

This file captures franchise *seats*, not managers. A franchise is a persistent institution — when a manager leaves and a new one joins their slot, the franchise continues under a new steward.

This distinction matters for questions like "what has happened to this seat over time" versus "what has this person accomplished." The franchise view shows lineage; the manager view shows individual history.

The 12 franchises were added over three years:

| Franchise IDs | Year Added | Reason |
|---|---|---|
| F01–F09 | 2001 | Founding members |
| F10–F11 | 2002 | First expansion (9 → 11 teams) |
| F12 | 2003 | Second expansion (11 → 12 teams) |

F04 has seen the most ownership changes: Dale (2001–2002) → Joe Tyszko (2003–2009) → Nick Blaettler (2010–2020) → Bryan Kearney (2021–2022) → Eric (2023–present).

---

## `team_name_history.csv` — 296 rows, 2001–2025

Every team name every manager used, by season. Derived from `season_managers.csv`. Managers who stayed in the league across 25 seasons have up to 25 distinct team name entries. Many managers changed team names frequently; a few kept the same name for their entire tenure.

---

## `season_trades.csv` — 247 rows, 2001–2025

One row per player received per team per trade. A 1-for-1 trade produces 2 rows (each team receives one player); larger trades produce more.

`trade_id` is an 8-character hash shared by all rows belonging to the same trade. Use it to reconstruct who traded what to whom.

`player_pos` comes directly from Yahoo's trade page and uses Yahoo's own format (`"TEAM - POS"`, e.g., `"TB - WR"`). This is distinct from the position data in `player_positions.csv`. It is generally accurate but uses team abbreviations current at the time of the trade.

Two seasons had zero trades: **2009** and **2014**. These are complete seasons — no trades occurred, not a data gap.

---

## `manual_timeline_events.csv` — 8 rows (and growing)

Hand-authored narrative events that supplement the scraped data. Covers milestones, dynasty completions, heartbreak moments, franchise transitions, and other league history that has no structured data source.

Unlike scraped files, this one is edited by hand. Every row has `source = editorial`.

### Schema

| Column | Purpose |
|---|---|
| `season` | The year the event belongs to |
| `event_date` | Optional specific date (blank for season-level events) |
| `event_type` | `milestone`, `dynasty`, `heartbreak`, `note`, `rule_change`, `steward_change`, `breakthrough` |
| `title` | Short display label |
| `description` | 1–3 sentence narrative; this is the actual content |
| `manager`, `franchise_id`, `team_name`, `player_name` | Attribution — populate whichever are relevant |
| `importance` | `high`, `medium`, `low` — controls display prominence on pages |
| `show_on_*` flags | Four boolean columns controlling which pages surface the event |

### What belongs here vs. what should be derived

If something can be computed from the scraped data (e.g., "most points in a single week," "longest winning streak"), it should be derived at query time rather than hardcoded here. This file is for events that require human context to understand — the kind of thing a league member would remember but a database would never surface on its own.

---

## `league_settings.csv` — 25 rows, 2001–2025

Built manually from Yahoo's settings pages rather than scraped programmatically. Contains one row per season with structural facts about the league that year: number of teams, scoring type, draft type, roster configuration, waiver system, and playoff rules.

`roster_slots` is a comma-separated string of position slots (e.g., `"QB, WR, WR, RB, TE, K, DEF, BN, BN, BN, BN, BN, BN, BN, BN"`). Parse it to understand how many starters vs. bench slots existed in a given year.

`waiver_type` is empty for early seasons when Yahoo had no formal waiver system, "Continual rolling list" for the traditional priority system, and a FAAB-style description for 2011+.

---

## Known Gaps

| Gap | Detail |
|---|---|
| Consolation matchup rows | `weekly_matchups.csv` does not include consolation bracket weeks; only `playoff_games.csv` has consolation results |
| `season_rosters.csv` | Only contains 2001 week 17 data; full roster snapshots were not scraped |
| `roster_moves.csv` | Not built — FA adds, drops, and waiver pickups from the transactions page are not yet captured |
| Standings 2019–2025 | Scraped and complete per the scraper, but verify if re-scraping |
| `ref_nfl_players.csv` | Re-download from nflverse periodically to pick up recent players for future seasons |
