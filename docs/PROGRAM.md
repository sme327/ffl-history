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

- **The Finals.** One placard per game:
  - both scores
  - each side's projection and best possible lineup
  - the lifetime series after the game
  - fact lines: "coulda won", a single bench swap that would have flipped it, and streaks snapped,
    extended, taken or evened
- **The Awards.**
  - Highest and Lowest Scorer
  - Biggest Blowout and Narrowest Victory
  - Best and Worst Managed: actual ÷ best possible lineup
  - Worst Lineup in Hindsight: the most points left on the bench
  - Overachiever and Below Expectation: starters vs. their original projections
  - Luckiest Win and Unluckiest Loss: the week's score against the other eleven teams
- **Players of the Week.** The top-scoring starter at QB, RB, WR, TE, K and DEF.
- **Best on the Bench.** The top bench QB, RB, WR and TE.
- **Dud of the Week.** The starter furthest below his projection.
- **For the Record.** Archive ranks, shown only when notable: a top-3 score for that week number,
  a top-10 score or margin since 2001, or a career high or low.
- **Standings.** Record and points for, with division marks.

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

**Every meeting, consolation games included.** The commissioner decided this on 2026-09-15; a
brief same-day ruling to drop consolation games was reversed before anything shipped. It is the
same count the Week 1 preview uses. It differs from the Rivalries room and the career win totals,
which both exclude consolation games, so three Week 1 series (O'Boyle–Swanson, Clark–Tom,
Fadi–Steve) read one game heavier here than on their Rivalries pages.

`build_program.load_history(team2mgr, managers, before_week)` serves both tabs. It only ever counts
weeks before the issue's own.

## Copy

- **File.** `data/program/2026-week-NN-recap-copy.json`
- **Fields.** `theme`, `cold_open`, `notes` (keyed `"MgrA|MgrB"`, names sorted), `awards` (keyed
  like the award ids, plus `QB_of_week`, `RB_bench`, `dud`, and so on), and `kicker`.
- **Contract.** The same as the preview's (`build_program.py` docstring):
  - Every claim must trace to the week's `-recap-brief.md`.
  - Notes run about 25–35 words.
  - Dramatic is good; unverifiable is not.
- **Drafts.** `"draft": true` means not yet approved. `build_recap.py --site` skips it, so a deploy
  can't ship it. The same flag works for preview copy files.

## Tuesday runbook

1. `python3 scripts/fetch_week_lineups.py --week N`. This runs on the Mac and needs a live Yahoo session.
2. `python3 scripts/build_recap.py --week N`
3. Claude drafts `2026-week-NN-recap-copy.json` with `"draft": true`. The commissioner approves or edits it.
4. Remove `"draft"`, run `npm run deploy`, commit, and send the league `/program/2026-week-NN/recap`.
5. Wednesday or Thursday: `python3 scripts/build_program.py --week N+1`, write the copy, and deploy.
   `/program` flips to the preview.
