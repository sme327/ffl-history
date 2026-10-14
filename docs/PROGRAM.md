# The Program — preview and recap

One issue per NFL week, two tabs. Each tab is its own URL, so each is a link the
commissioner can send to the league.

| Tab | URL | When | Built by |
|---|---|---|---|
| **Preview** | `/program/2026-week-NN` | Wednesday or Thursday | `scripts/build_program.py --week N` + hand copy |
| **Recap** | `/program/2026-week-NN/recap` | Tuesday morning, after Monday night | `scripts/fetch_week_lineups.py` → `scripts/build_recap.py --week N` + approved copy |

`/program` opens on the newest published tab: the finished week's Recap from Tuesday until the next
week's preview exists *with its copy*, then that preview. The logic is `programLanding()` in
`app/program/program-tabs.tsx`. Back Issues pills link every week's newest tab.

Decided 2026-09-15 by the commissioner:
- a Recap for both museum leagues (this one and Dynasty 22)
- it lives inside The Program
- it comes out Tuesday mornings
- Claude drafts the copy and the commissioner approves it
- the league gets a link

## The Recap's contents

Computed in `scripts/build_recap.py`, with the awards in `scripts/recap_engine.py`. The engine is
**byte-identical** with Dynasty 22's copy; fix both or neither.

The page is laid out top to bottom. The layout was redesigned 2026-09-15 after Sleeper's app report,
using the same structure as Dynasty 22 in this museum's own materials.

1. **Best Team / Worst Team.** Two placards with manager medallions.
2. **The Finals.** One placard per game:
   - both scores
   - each side's projection and best possible lineup
   - the lifetime series after the game
   - fact lines: "coulda won", a single bench swap that would have flipped it, and streaks snapped,
     extended, taken or evened
3. **Lineups in Hindsight.** Every team ranked by score as a brass bar on one shared scale, the league's
   highest possible score. The fill is what they scored, the track their best possible lineup, and the
   tick their starters' projection.
4. **Players of the Week.** QB, RB, WR, TE, K, DEF. Photo placards: headshot (a team logo for a defense),
   the manager's medallion pinned on, points, and the NFL game ("@ CAR").
5. **Benchwarmers of the Week.** QB, RB, WR, TE.
6. **League Awards.** Matched pairs of two-number cases:
   - Best / Worst Managed: score vs. max points
   - Unluckiest Loss / Luckiest Win: score vs. the opponent
   - Biggest Blowout / Narrowest Victory: winner vs. loser
   - Overachiever / Below Expectation: score vs. the starters' projection
   - Worst Lineup in Hindsight: score vs. max points
   - Dud of the Week: points vs. projection
7. **For the Record.** Archive ranks, shown only when notable.
8. **Standings.** With division marks.

**Photos.** `scripts/photos.py` downloads each featured player's picture once, into `public/players/`
(headshots) or `public/nfl/` (defense logos).
- Yahoo player IDs are matched to Sleeper IDs through the `yahoo_id` in Sleeper's public player list,
  which is cached in `.local/`. A name-plus-team match is the fallback. The logic is the Espinosa
  Clubhouse's.
- Headshots come from `sleepercdn.com`. A player with no match shows initials.
- Per-position colors are deliberately not used.

Ties share an award.

### Definitions

- **Best possible lineup.** The highest-scoring legal lineup (QB, 2 RB, 2 WR, TE, W/R/T, K, DEF)
  from the week's starters and bench.
  - IR slots are excluded.
  - It is solved exactly, including players eligible at more than one position.
  - A slot may be left empty rather than start a negative score.
  - Kicker and defense points are Yahoo's own, never re-scored.
- **Projection.** Yahoo's original pregame projection, the "Proj" column on the matchup page.
- **Integrity checks.** `fetch_week_lineups.py` refuses to write unless:
  - all 12 teams appear once
  - each has 9 starter rows
  - starters sum to Yahoo's score and projections sum to "Orig Proj"

  `build_recap.py` checks the sums again against `results_2026.csv`.

## What counts toward a lifetime series

**Regular-season games plus championship-bracket playoff games. Consolation games don't count.**
The commissioner ruled on 2026-10-14 that this holds everywhere on the site ("consolation games
don't count", first ruled 2026-09-07 for career totals). It replaced the 2026-09-15 decision to
count every meeting in Program series. The Program now uses the same games as the Rivalries room,
the career win totals and every other museum page.

- **Which games count.** `build_program.counted_game()`. A playoff-week game counts only when
  `playoff_games.csv` lists it in the championship bracket. That excludes the consolation bracket
  and also the unbracketed placement games that Yahoo schedules for eliminated teams in 2021–2025
  (see `docs/DATA_GUIDE.md` → Known Gaps).
- **Where it applies.** Series records and the "regular season · playoffs" split on each card,
  streaks, longest runs, biggest leads, last / closest / biggest / highest / lowest meetings, the
  recap's series lines, and "Week N in the Archive". So "playoffs" on a card now means championship
  playoffs only.
- **Back issues.** Weeks 1–6 previews and Weeks 1–5 recaps were rebuilt on 2026-10-14, and 41
  published notes and 3 cold opens were corrected to match. Each change is listed in
  `docs/reviews/CONSOLATION-RULING-2026-10-14.md`.
- **Writing copy.** A game in a playoff week isn't automatically a playoff game. Before writing
  "playoffs", check its bracket in `playoff_games.csv`; the facts JSON's `playoff` flag now means
  championship bracket.

`build_program.load_history(team2mgr, managers, before_week)` serves both tabs. It only ever counts
weeks before the issue's own.

## Copy

- **File.** `data/program/2026-week-NN-recap-copy.json`
- **Fields.** `theme`, `cold_open`, `notes` (keyed `"MgrA|MgrB"`, names sorted), `awards` (keyed `QB_of_week`, `RB_bench`, …, for player cards only; League Award cards take no written notes, decided 2026-09-15, so every card in a pair keeps the same shape and a note can't pass for the full explanation), and `kicker`.
- **Contract.** The same as the preview's (`build_program.py` docstring):
  - Every claim must trace to the week's `-recap-brief.md`.
  - Notes run about 25–35 words.
  - Dramatic is good; unverifiable is not.
- **Drafts.** `"draft": true` means not yet approved. `build_recap.py --site` skips it, so a deploy
  can't ship it. The same flag works for preview copy files.
- **Drafts don't expire.** An unapproved draft just sits there, committed, and the week passes
  without it. That happened to the Week 5 preview (drafted 2026-10-06, approved 2026-10-13 after
  the week was played). Before each deploy, check `grep -l '"draft"' data/program/*-copy.json`
  and ask the commissioner about anything still waiting.
- **Late approval.** Approved preview copy still ships after its week, as a back issue. Every line is a
  pregame line, so it reads correctly as an archive. `/program` still opens on the newest tab.
- **"Playoff" in the facts JSON includes consolation games.** `is_playoff` covers both brackets, so a
  card's `record_po`, `playoff_meetings` and `last.playoff` count consolation games. Before a note
  says "playoffs", check `data/playoff_games.csv` for `bracket`. Doug–Shawn's 2025 Week 17
  meeting has `playoff: true`, but it was the 7th-place consolation game.

## Tuesday runbook

1. `python3 scripts/fetch_week_lineups.py --week N`. This runs on the Mac and needs a live Yahoo session.
2. `python3 scripts/build_recap.py --week N`
3. Claude drafts `2026-week-NN-recap-copy.json` with `"draft": true`. The commissioner approves or edits it.
4. Remove `"draft"`, run `npm run deploy`, commit, and send the league `/program/2026-week-NN/recap`.
5. Wednesday or Thursday: `python3 scripts/build_program.py --week N+1`. Claude drafts
   `2026-week-NN-copy.json` with `"draft": true`, and the commissioner approves it. Then remove
   `"draft"`, deploy, and commit. `/program` flips to the preview once its copy ships.
6. After any deploy, load the live page and confirm the copy is there. A deploy skips a draft without
   any error.

## Status

- **Week 5 (2026).** The preview copy ("Tiebreakers") was approved and deployed 2026-10-13, after the
  week, as a back issue (`8ab8f13`). The recap is committed (`2128b6e`).
- **Week 6 (2026).** The preview facts and draft copy are committed (`4504f0e`). The copy is **still
  awaiting approval**.
