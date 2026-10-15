# Consolation games don't count — site-wide ruling, 2026-10-14

## The ruling

The commissioner, on 2026-10-14: **consolation games don't count**, and the site must be
consistent about it. This was already the rule for career totals (ruled 2026-09-07: "consolation
games don't count. they never did.") and for every museum page built on `utils/data.py`
(Rivalries, managers, franchises, history). The one exception was The Program, which since
2026-09-15 had counted every meeting in its lifetime series. That exception is gone.

What counts everywhere: **regular-season games plus championship-bracket playoff games**,
including the 3rd-place game. A playoff-week game counts only when `playoff_games.csv` lists it
in the championship bracket.

## Status

- **Museum: live.** The corrected copy, rebuilt facts and recap footnote deployed 2026-10-14
  (Worker version `7caf0f79-a7b9-4bc5-9e05-7e83b1f5d2cb`). Every corrected note and cold open was
  checked live on Weeks 1–6.
- **Show: in production.** Eight replacement lines approved by the owner on 2026-10-14. Retake
  requests pushed to the FFL Show repo (`3f16cff`), with Grok recording and Codex re-cutting (see
  The Show below). The published videos are unchanged until those cuts are approved and deployed.
- **5th-place game: ruled.** It doesn't count in any season (see the data gap below).

## What changed in the museum

- `scripts/build_program.py`: new `championship_games()` and `counted_game()`. `load_history()`
  (series for both Program tabs) and `week_in_history()` now skip consolation and unbracketed
  playoff-week games. Career totals already followed the rule and are unchanged.
- `scripts/build_recap.py` docstring and the recap footnote (`app/program/recap-view.tsx`) now
  state the rule.
- Rebuilt facts and briefs for the Week 1–6 previews and Week 1–5 recaps. The "playoffs" split on
  each card now counts only championship-bracket games.
  - Week 3's career totals and Milestone Watch also changed: its facts file had been built before
    Week 2's results were added, and the rebuild picked them up. Its published copy doesn't cite
    them.
- Corrected the published copy (below). An automated check confirmed that every win–loss record
  cited in a note matches the rebuilt facts (23 of 23), and each streak, "last N" and lead claim
  was checked against the game-by-game log.
- Docs: `docs/PROGRAM.md` (what counts toward a series), `docs/DATA_GUIDE.md` (consolation section,
  series rule, Known Gaps), `README.md`.

## Copy changes in published issues

Only notes whose facts changed are listed. Everything else in each issue stands.

### Week 1 preview

- **Cold open**
  - was: Four of the six openers are dead-even lifetime series, and a fifth is separated by a single game. Twenty-five years of history, and Week 1 starts with almost nobody ahead.
  - now: Two of the six openers are dead-even lifetime series, and three more are separated by a single game. Twenty-five years of history, and Week 1 starts with almost nobody ahead.
- **Brian Clark – Thomas**
  - was: Tom led this thing by five once. Clark answered with seven straight. Twenty-five years later it's 15–15, and somebody spends the winter ahead.
  - now: Tom led this thing by four once. Clark answered with seven straight. Twenty-five years later Clark leads 15–14, and Tom has won the last three.
- **Kevin O'Boyle – Kevin Swanson**
  - was: No two managers have met more. Forty-two games, a championship between them, and after a quarter century O'Boyle is still chasing Swanson.
  - now: No two managers have met more. Forty games, a championship between them, and after a quarter century O'Boyle is still chasing Swanson.
- **Fadi – Steve Swanson**
  - was: Dead level after 26 games, but the momentum is one way — Fadi hasn't beaten Steve since September 2024, and opens the season staring at the streak.
  - now: Fadi leads 13–12 after 25 games, but the momentum is one way — he hasn't beaten Steve since September 2024, and opens the season staring at a three-game streak.

### Week 1 recap

- **Kevin O'Boyle – Kevin Swanson**
  - was: The luckiest win of the week: Swanson's 77.88 was only the ninth-best score in the league. O'Boyle's best possible lineup scored 108.95. The series now stands 24–19, Swanson.
  - now: The luckiest win of the week: Swanson's 77.88 was only the ninth-best score in the league. O'Boyle's best possible lineup scored 108.95. The series now stands 23–18, Swanson.

### Week 2 preview

- **Shawn – Thomas**
  - was: Thirty-eight meetings and Shawn is two up, but Tom has taken three of the last five. Both opened with a loss — Shawn managing 96.5 percent of his roster, Tom scoring 69.18 against an 85.49 projection.
  - now: Thirty-six meetings and Shawn is two up, but Tom has taken three of the last five. Both opened with a loss — Shawn managing 96.5 percent of his roster, Tom scoring 69.18 against an 85.49 projection.
- **Evan – Steve Swanson**
  - was: Evan leads 16–14 and has won four of the last five, including the last by 21. Steve opened by beating his projection 35.62, more than anyone; Evan by winning the week's biggest blowout.
  - now: Dead even at 13–13, and Evan has won four of the last five, including the last by 21. Steve opened by beating his projection 35.62, more than anyone; Evan by winning the week's biggest blowout.

### Week 2 recap

- **Shawn – Thomas**
  - was: Shawn's 107.33 topped the league and would have beaten all eleven teams, with Goff's 30.89 never leaving the bench. He snapped Tom's two-game run and leads the series 21–18.
  - now: Shawn's 107.33 topped the league and would have beaten all eleven teams, with Goff's 30.89 never leaving the bench. He snapped Tom's two-game run and leads the series 20–17.
- **Evan – Steve Swanson**
  - was: The week's narrowest game, 96.04–94.31. Evan started the quarterback of the week, Josh Allen at 38.41, and lost anyway: Isaiah Likely's 4.15 sat behind DJ Moore's −0.05. Evan leads 16–15.
  - now: The week's narrowest game, 96.04–94.31. Evan started the quarterback of the week, Josh Allen at 38.41, and lost anyway: Isaiah Likely's 4.15 sat behind DJ Moore's −0.05. Steve takes a 14–13 series lead.

### Week 3 preview

- **Eric – Thomas**
  - was: Eight meetings, 4–4. Tom took the last one by 1.11 points, the closest they've ever played, and has won three of the last five. Eric once led this young series by two.
  - now: Seven meetings, Tom up 4–3. He took the last by 1.11 points, the closest they've ever played, and has won three of the last five. Neither has ever led by more than a game.
- **Douglas – Steve Swanson**
  - was: Doug beat Steve for the 2020 title and owns the biggest blowout in the series, 49.18 points in 2024. Steve leads 10–9 anyway, and won the last one 89.53–61.29.
  - now: Doug beat Steve for the 2020 title and owns the biggest blowout in the series, 49.18 points in 2024. Steve leads 9–7 anyway, and won the last one 89.53–61.29.
- **Evan – Fadi**
  - was: Thirty-five meetings, two of them for the championship: Evan won in 2012, Fadi in 2024. Fadi has won four of the last five, leads 18–17, and once beat Evan by 101.93 points.
  - now: Thirty-two meetings, two of them for the championship: Evan won in 2012, Fadi in 2024 by 0.12 points. Fadi has won four of the last five, and the series is dead even at 16–16.
- **Jeff – Kevin Swanson**
  - was: Swanson leads 10–4 and once led by seven. But Jeff has won three of the last five, the last by 48.28 — the biggest blowout in the series. He owns the closest game too, by 0.70.
  - now: Swanson leads 10–3 and once led by eight. Jeff took the last one by 48.28 — the biggest blowout in the series, and only his third win in thirteen meetings.
- **Dominic – Kevin O'Boyle**
  - was: They've met twice for the title, and Dominic won both, in 2011 and 2021. O'Boyle leads the series 16–13 all the same, and won the last one by 47.71.
  - now: They've met twice for the title, and Dominic won both, in 2011 and 2021. O'Boyle leads the series 14–13 all the same, but Dominic won the last one, 76.17–55.41.

### Week 3 recap

- **Brian Clark – Shawn**
  - was: Clark left 41.08 points on his bench, the most in the league. Brock Purdy's 31.64 sat behind Jalen Hurts's 8.31, and that one swap wins it. Shawn has won two straight; Clark leads 20–14.
  - now: Clark left 41.08 points on his bench, the most in the league. Brock Purdy's 31.64 sat behind Jalen Hurts's 8.31, and that one swap wins it. Shawn has won two straight; Clark leads 19–14.
- **Douglas – Steve Swanson**
  - was: The week's narrowest win, by 6.12. Doug was projected to lose and beat his projection by 12.29. Steve had Michael Wilson's 15.95 on the bench behind Jaylen Waddle's 4.2. Series even, 10–10.
  - now: The week's narrowest win, by 6.12. Doug was projected to lose and beat his projection by 12.29. Steve had Michael Wilson's 15.95 on the bench behind Jaylen Waddle's 4.2. Steve leads 9–8.
- **Jeff – Kevin Swanson**
  - was: Swanson scored 101.95, second-best in the league, and lost to the only team that topped it. Jeff went 27.43 over projection, led by Jahmyr Gibbs's 29.7. Swanson still leads the series 10–5.
  - now: Swanson scored 101.95, second-best in the league, and lost to the only team that topped it. Jeff went 27.43 over projection, led by Jahmyr Gibbs's 29.7. Swanson still leads the series 10–4.
- **Eric – Thomas**
  - was: The week's biggest blowout, 87.44–52.03. Eric's Drake Maye was projected for 15.07 and scored −1.12, the dud of the week. Tom has won two straight and takes a 5–4 lead.
  - now: The week's biggest blowout, 87.44–52.03. Eric's Drake Maye was projected for 15.07 and scored −1.12, the dud of the week. Tom has won two straight and leads 5–3.
- **Evan – Fadi**
  - was: Evan was projected for 84.58, more than Fadi, and scored 48.28: the week's low, 36.3 under projection, and short of all eleven other teams. Fadi has won two straight and leads 19–17.
  - now: Evan was projected for 84.58, more than Fadi, and scored 48.28: the week's low, 36.3 under projection, and short of all eleven other teams. Fadi has won two straight and takes a 17–16 lead.
- **Dominic – Kevin O'Boyle**
  - was: The luckiest win: Dominic's 74.41 was only eighth-best. O'Boyle had the quarterback of the week, Tyler Shough at 24.9, and Brock Bowers's 16.8 on the bench behind Dalton Schultz's 3.0. O'Boyle leads 16–14.
  - now: The luckiest win: Dominic's 74.41 was only eighth-best. O'Boyle had the quarterback of the week, Tyler Shough at 24.9, and Brock Bowers's 16.8 on the bench behind Dalton Schultz's 3.0. Series even, 14–14.

### Week 4 preview

- **Cold open**
  - was: Three weeks of division games are done. Week 4 sends every team across the line for the first time this season: a 2013 title-game rematch, a series dead even at 7–7, and an eleven-game lead that has never been wider.
  - now: Three weeks of division games are done. Week 4 sends every team across the line for the first time this season: a 2013 title-game rematch, a series dead even at 7–7, and a ten-game lead that has never been wider.
- **Evan – Kevin Swanson**
  - was: Evan beat Swanson for the 2013 title. Swanson took their last meeting, 99.05–59.15 in Week 16 last year, and leads 16–15 over 31 games — one of them decided by 0.02 points.
  - now: Evan beat Swanson for the 2013 title and leads 15–14 over 29 games, one of them decided by 0.02 points. Swanson took their last meeting, 82.33–57.32 in Week 14 last year.
- **Douglas – Thomas**
  - was: Doug once led this series by six and still holds a 9–5 edge. But Tom has won the last two, and owns its biggest blowout — 69.06 points in 2022.
  - now: Doug once led this series by five and still holds an 8–5 edge. But Tom has won the last two, and owns its biggest blowout — 69.06 points in 2022.
- **Eric – Steve Swanson**
  - was: Only the sixth meeting, and lately it has been all Eric: three straight, the last 86.64–47.37 in Week 15 last year. Steve opened this young series 2–0.
  - now: Only the fifth meeting, and lately it has been all Eric: three straight, the last 86.64–47.37 in Week 15 last year. Steve won the first, in 2023.
- **Fadi – Kevin O'Boyle**
  - was: Twenty-seven meetings since 2002, and O'Boyle leads 19–8, the widest the gap has ever been. He once won six straight, and took their closest game by 0.71 points in 2015.
  - now: Twenty-six meetings since 2002, and O'Boyle leads 18–8, the widest the gap has ever been. He once won five straight, and took their closest game by 0.71 points in 2015.

### Week 4 recap

- **Fadi – Kevin O'Boyle**
  - was: The unluckiest loss: Fadi's lineup was perfect and beat its projection by 26.8. O'Boyle beat projection by 27.57, and the 119.37 is the seventh-best Week 4 score in league history. O'Boyle leads 20–8.
  - now: The unluckiest loss: Fadi's lineup was perfect and beat its projection by 26.8. O'Boyle beat projection by 27.57, and the 119.37 is the seventh-best Week 4 score in league history. O'Boyle leads 19–8.
- **Eric – Steve Swanson**
  - was: The week's biggest blowout, by 25.99, and it didn't have to happen: Steve's best lineup scored 91.74. Romeo Doubs's 17.9 sat behind D'Andre Swift's 2.7. Eric has won four straight and leads 4–2.
  - now: The week's biggest blowout, by 25.99, and it didn't have to happen: Steve's best lineup scored 91.74. Romeo Doubs's 17.9 sat behind D'Andre Swift's 2.7. Eric has won four straight and leads 4–1.
- **Douglas – Thomas**
  - was: Tom started the tight end and the kicker of the week, Sam LaPorta and Will Reichard, and lost. Doug won with Brian Robinson's 21.85 benched behind Jacory Croskey-Merritt's 3.5. Doug leads 10–5.
  - now: Tom started the tight end and the kicker of the week, Sam LaPorta and Will Reichard, and lost. Doug won with Brian Robinson's 21.85 benched behind Jacory Croskey-Merritt's 3.5. Doug leads 9–5.
- **Evan – Kevin Swanson**
  - was: The week's narrowest win, by 8.11. Swanson's best possible lineup scored 83.15, four hundredths more than Evan's 83.11. Tetairoa McMillan's 28.6, the receiver of the week, carried Evan. Series even, 16–16.
  - now: The week's narrowest win, by 8.11. Swanson's best possible lineup scored 83.15, four hundredths more than Evan's 83.11. Tetairoa McMillan's 28.6, the receiver of the week, carried Evan. Evan leads 16–14.

### Week 5 preview

- **Cold open**
  - was: Eric and Jeff are 2–2 and meet for the fifth time. Brian Clark is one game behind Evan in their series, and one behind Kevin Swanson in the all-time wins race, 194–193. Clark plays Evan this week; Swanson plays Fadi.
  - now: Eric and Jeff are 2–2 and meet for the fifth time. Brian Clark is two games behind Evan in their series, and one behind Kevin Swanson in the all-time wins race, 194–193. Clark plays Evan this week; Swanson plays Fadi.
- **Dominic – Steve Swanson**
  - was: Dominic beat Steve for the 2008 title and leads the series 16–13. Steve has won three of the last five, including this same week a year ago: 104.98–82.58 in Week 5.
  - now: Dominic beat Steve for the 2008 title and leads the series 15–12. Steve has won three of the last five, including this same week a year ago: 104.98–82.58 in Week 5.
- **Douglas – Shawn**
  - was: Shawn leads 8–6 and once won four straight, 2019 to 2022. Doug has taken three of the last five, and the last one was ugly: 89.45–36.24, a 53.21-point beating.
  - now: Shawn leads 8–4, his biggest edge ever, and once won four straight, 2019 to 2022. Doug took two in a row in 2023; Shawn has answered with two of his own, the last 89.72–71.57.
- **Kevin O'Boyle – Thomas**
  - was: Tom has won five straight, matching his 2013–15 run as the longest in the series; one more sets the record. O'Boyle owns the biggest blowout, 70.08 points in 2017. Tom leads 17–14.
  - now: Tom has won four straight; one more ties the longest run in the series, five, which both men own. O'Boyle owns the biggest blowout, 70.08 points in 2017. Tom leads 16–14.
- **Brian Clark – Evan**
  - was: Evan once led this series by six; it's down to 15–14. Clark has won four of the last five, the last 73.6–70.48, and took their closest game by 0.53 in 2023. One more evens it.
  - now: Evan once led this series by six; it's down to 15–13. Clark has won three of the last five, the last 73.6–70.48, and took their closest game by 0.53 in 2023.
- **Fadi – Kevin Swanson**
  - was: Swanson leads 17–14 and has won four of the last five. Fadi took the most recent, 88.72–54.07 last year, and owns the series' biggest blowout: 82.45 points in 2008.
  - now: Swanson leads 16–13 and has won four of the last five. Fadi took the most recent, 88.72–54.07 last year, and owns the series' biggest blowout: 82.45 points in 2008.

### Week 5 recap

- **Kevin O'Boyle – Thomas**
  - was: Tom beat his projection by 48.99, with the 49ers' 18.0 the defense of the week. The 61.13 margin was the week's biggest blowout. Tom has won six straight and leads 18–14.
  - now: Tom beat his projection by 48.99, with the 49ers' 18.0 the defense of the week. The 61.13 margin was the week's biggest blowout. Tom has won five straight, tying the series record, and leads 17–14.
- **Brian Clark – Evan**
  - was: Evan's best possible lineup scored 115.7 and wins it: Isaiah Likely's 22.2 sat on the bench behind Mike Washington Jr.'s 1.0 at flex. Clark has won two straight and evens the series, 15–15.
  - now: Evan's best possible lineup scored 115.7 and wins it: Isaiah Likely's 22.2 sat on the bench behind Mike Washington Jr.'s 1.0 at flex. Clark has won two straight and trails 15–14.
- **Fadi – Kevin Swanson**
  - was: The week's narrowest win, by 2.7, and the luckiest: Fadi's 83.22 was only eighth-best. Jameson Williams's 15.35 sat on Swanson's bench behind Tee Higgins's 2.1. Fadi has won two straight; Swanson leads 17–15.
  - now: The week's narrowest win, by 2.7, and the luckiest: Fadi's 83.22 was only eighth-best. Jameson Williams's 15.35 sat on Swanson's bench behind Tee Higgins's 2.1. Fadi has won two straight; Swanson leads 16–14.
- **Douglas – Shawn**
  - was: Doug was projected for 82.54 and scored 56.25, 26.29 under: the furthest below projection in the league. Shawn's 97.97 was fifth-best, with Trey McBride's 13.8 the tight end of the week. Shawn leads 9–6.
  - now: Doug was projected for 82.54 and scored 56.25, 26.29 under: the furthest below projection in the league. Shawn's 97.97 was fifth-best, with Trey McBride's 13.8 the tight end of the week. Shawn leads 9–4.
- **Dominic – Steve Swanson**
  - was: Dominic's 55.31 was the week's low, short of all eleven other teams. Steve started his best possible lineup, led by Christian Watson's 22.15, the receiver of the week. Dominic leads 16–14.
  - now: Dominic's 55.31 was the week's low, short of all eleven other teams. Steve started his best possible lineup, led by Christian Watson's 22.15, the receiver of the week. Dominic leads 15–13.

### Week 6 preview

- **Kevin O'Boyle – Shawn**
  - was: O'Boyle beat Shawn for the 2015 title. Shawn has won the last three, one by 0.32 points and the latest 105.28–70.71 in last year's consolation bracket. His 20–13 lead has never been bigger.
  - now: O'Boyle beat Shawn for the 2015 title. Shawn has won the last two, the latest by 0.32 points, the closest game they've ever played. His 18–12 lead has never been bigger.
- **Dominic – Fadi**
  - was: Dominic beat Fadi for the 2007 title and owns the series' biggest blowout: 139.89–56.62 in 2011. Fadi has won three straight since, and his 18–12 lead has never been wider.
  - now: Dominic beat Fadi for the 2007 title and owns the series' biggest blowout: 139.89–56.62 in 2011. Fadi has won three straight since, and his 17–12 lead has never been wider.
- **Brian Clark – Kevin Swanson**
  - was: Tied at 194 career wins; the winner takes the all-time lead. Clark has won four straight, matching the series' longest run, and leads 19–14, his biggest edge ever. Swanson owns the biggest blowout: 70.22 in 2007.
  - now: Tied at 194 career wins; the winner takes the all-time lead. Clark has won four straight, matching the series' longest run, and leads 18–13, his biggest edge ever. Swanson owns the biggest blowout: 70.22 in 2007.
- **Douglas – Jeff**
  - was: Doug won the first seven, 2017 to 2020, including a 98.03-point demolition. Jeff has taken three of the last five, the latest 97.56–82.42, and the seven-game lead is down to four.
  - now: Doug won the first seven, 2017 to 2020, including a 98.03-point demolition. Jeff has taken four of the last five, the latest 97.56–82.42, and the seven-game lead is down to three.

## The Show: published videos with now-outdated series claims

These are spoken or on screen in released videos. The museum can't change them; correcting them
needs a re-record or re-render in the FFL Show project. They were accurate under the old count.

**Episode 1 (Weeks 1–3, released Oct 4)**
- "pulled the lifetime series even at ten games apiece" / on screen SERIES 10–10 (Douglas–Steve) →
  Steve leads 9–8.
- "Guinness leads This Is How We Do 19 to 8, their widest lead ever" / on screen 8–19 → 18–8
  (still the widest).
- "Mean Machine 22 leads Fuzzy Bears 9 to 5" / on screen 9–5 → 8–5.

**Week 5 Weekly Slate (V007, released Oct 8)**
- "Mini Ditkas lead their lifetime series, seventeen wins to fourteen" → 16–13.
- "Mean Machine won their last meeting by fifty-three points, in week seventeen last season" →
  that was a consolation game; the last counted meeting was Shawn's 89.72–71.57 win in Week 13
  of 2025.
- "Good Times leads their lifetime series by one win" → by two, 15–13.
- "Fuzzy Bears has won their last five meetings" → four.

Still correct: Shawn ending a five-game losing streak against Kittle, the 7–7 Clark–Jeff tie,
Guntry Club's three straight over Bears, and the 2013 title rematch.

The Week 6 Slate hasn't been scripted yet. Its tracker says to reconcile against current Museum
data, which now follows the ruling.

## Data gap: placement games without a bracket, 2021–2025

Each 2021–2025 season has 5 playoff-week games in `weekly_matchups.csv` that `playoff_games.csv`
doesn't list. They're the 6-team format's other placement games: consolation round 1 (Week 15),
the game between the two championship quarterfinal losers (Week 16), and lower placement games
(Week 17). `fetch_yahoo_data.py`'s `scrape_playoffs()` keeps only the round types the 2001–2020
format used, so it dropped the consolation `quarterfinal`, any championship-page `place_5`, and the
`place_9`/`place_11` games. The championship bracket itself is complete: 6 games a season, the
right count for the format.

These games count nowhere today, which is correct for consolation games. To label them, keep every
round type in `scrape_playoffs()` and re-run it for 2021–2025 only (10 bracket pages) with a
logged-in Yahoo session.

**What they are**, by seed and week: two consolation quarterfinals (Week 15), the 11th-place game
(Week 16), the game between the two championship quarterfinal losers (Week 16), and the
consolation semifinal losers' game (Week 17). Four are plainly consolation games. The quarterfinal
losers' game is the 5th-place game: from 2002 to 2020 Yahoo filed that game in the consolation
bracket in all 19 seasons, and it never counted.

**Yahoo's labels** (probe run 2026-10-14, `scripts/probe_playoff_brackets.py`): four of the five
are on the consolation page (`quarterfinal` ×2, `place_11`, `place_9`) and don't count. The
quarterfinal losers' game is `place_5` **on the championship page**. Yahoo moved it there with the
2021 format.

**Ruling (commissioner, 2026-10-14): the 5th-place game doesn't count**, in any season and whatever
bracket Yahoo files it under. It never counted from 2002 to 2020, and the museum never counted it from
2021 either; only Yahoo's label changed. No data or page changes. For the record, the games it would
have added: 2021 Kevin Swanson over Shawn, 2022 Shawn over Fadi, 2023 Douglas over Kevin
Swanson, 2024 Dominic over Steve Swanson, 2025 Brian Clark over Steve Swanson. Kevin Swanson and
Brian Clark would each gain one career win, so their 194–194 tie stands.

## The Show

Corrections for the published videos are written up in the FFL Show project, in its retake format
(exact lines for Grok, picture changes for Codex, release steps):
`weekly/2026-week-05/CONSOLATION_CORRECTION_RETAKE.md` and
`episodes/001-rivalry-round-one/CONSOLATION_CORRECTION_RETAKE.md`, each with a
`consolation-correction-request.json`. The new wording was approved by the owner on 2026-10-14.

The Week 5 release verifier (`scripts/verify-weekly-show-release.mjs`) was retired the same day.
See `docs/SHOW_HUB.md`.
