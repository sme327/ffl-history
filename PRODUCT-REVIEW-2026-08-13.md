# The Long Game — Product & Code Review

**Date:** 2026-08-13
**Scope:** `app.py`, 9 pages, `utils/` (data, styles, narratives), `data/` (15 CSVs), repo hygiene, and the product against its own stated vision in `CLAUDE.md`.
**Not covered:** the Yahoo scraper's behavior against live Yahoo (not run), and visual QA on real devices (assessed from code only).

---

## 1. Overall

This is a genuinely good project, and it's good in the way that's hardest to fake: **the data is trustworthy and the reasoning behind it is written down.**

`DATA_GUIDE.md` and the README's data section are the standout artifacts here. Era-by-era keeper detection rules (2001–02 none, 2003 normalized from R1 to R15, 2004–09 inferred from empty round-15 slots, 2010–13 marker-plus-transition handling, 2014+ true cost round). The 2011 draft that Yahoo renders in auction format but is actually snake order. Points-for and points-against reconstructed from weekly matchups for 2001–03 because Yahoo's early standings page swapped the columns. FAAB balances hiding in the `waiver_priority` field from 2011 onward.

That's twenty-five years of accumulated data archaeology, documented well enough that someone else could verify it. Most personal projects have none of this. It's what separates a museum from a spreadsheet.

The product vision in `CLAUDE.md` is also unusually clear — "statistics support stories, statistics should rarely be the final destination" is a real editorial position, and the page-by-page ownership questions ("Who still hates each other?") give every screen a job.

The findings below are about the gap between that standard and the current state of the code.

---

## 2. Correctness & durability

### F1 — The data pipeline is not in version control ⚠️ **highest priority**

`git status` shows these as untracked:

```
?? CLAUDE.md
?? DATA_GUIDE.md
?? build_player_positions.py
?? fetch_yahoo_data.py
?? inspect_yahoo_page.py
?? archive/
```

The CSVs in `data/` are committed, so the *app* survives. But **every script that produces those CSVs exists only on one laptop**, along with the product vision document and the data methodology guide. A clone of `github.com/sme327/ffl-history` cannot regenerate the dataset, and cannot even explain it — `README.md` links to a `DATA_GUIDE.md` that isn't in the repo.

Twenty-five years of scraped, hand-corrected league history is one disk failure away from being a folder of CSVs nobody can rebuild or reason about.

**Fix:** `git add` all six, commit, push. Two minutes. Do it before anything else in this document.

Also add `.idea/` to `.gitignore` — it's currently untracked noise.

### F2 — No tests, in a codebase where correctness is the product

`utils/data.py` is 1,262 lines of derivation: keeper chains, franchise stewardship periods, head-to-head records, playoff eliminations, rivalry scoring, all-time manager stats. There is no `tests/` directory.

The git log shows what that costs:

```
d931dc3 Fix Mike Williams 20yr career, remove franchise codes...
d865496 Fix Evan vs Fadi rivalry plaque: update to reflect 2024 championship
63b4355 Fix home page to acknowledge Clark & Fadi both went 12-1
4b09515 Fix 3 issues from Fadi: trophy room, keeper lore gap, DNA legend
```

Every one of those is a correctness bug found by a human reading the site — one of them found by a *league member*. In a museum, a wrong record isn't a rendering glitch; it's a false claim about someone's life. Fadi noticing his own plaque is wrong is the worst possible QA process.

**Fix:** golden-file tests. Capture the current output of the ~20 derivation functions as JSON fixtures and assert against them. This costs an afternoon, immediately protects the most subtle logic in the project, and — per the self-hosting plan — becomes the acceptance gate if you ever port off Streamlit. Your concert archive already does exactly this.

### F3 — Hardcoded prose inside a dynamically computed branch

`app.py:54–66` correctly detects at runtime whether the best regular season is a tie, then hardcodes the explanation:

```python
_best_szn_desc = (
    f"{_mgr_str} — the only two managers in league history to go {best_szn_record}. "
    f"Clark won the title in 2009. Fadi went 12-1 in 2010 and still lost in the playoffs."
)
```

The names, years, and outcomes are frozen strings inside a branch whose *inputs* are computed. If a third manager ever goes 12-1, the headline updates to name three people and the sentence below still discusses two. If the record itself is broken, the prose describes a record that's no longer the best.

This is the fix for `63b4355` having introduced a latent bug of the same species it fixed.

**Fix:** move the editorial line into `narratives.py`, keyed by season, and select it from the computed result — or generate it from data. The pattern to avoid is *computed number, hardcoded explanation*.

### F4 — Factual errors in the NFL context copy

Spot-checking `narratives.py`'s `NFL_CONTEXT` surfaced two errors in the first four seasons:

- **2003:** "Peyton Manning breaks Dan Marino's single-season TD record with 49." That was the **2004** season — and the 2004 entry states it again, correctly. In 2003 Manning threw 29 touchdowns.
- **2004:** "Terrell Owens catches 77 balls in a Super Bowl before breaking his leg." Garbled — 77 receptions was his regular season; he broke his leg in December, *then* played in Super Bowl XXXIX with 9 catches. The order is reversed and two stats are merged.

I checked four of twenty-five seasons and found two errors, so the base rate is worth taking seriously.

This matters more here than it would elsewhere. The whole premise of `CLAUDE.md` is that this is a museum with an editorial voice — and the NFL context exists specifically to anchor league memories in real football history. A museum placard that misdates a record undermines the exhibits next to it. League members will absolutely notice; several of them lived through these seasons as adults.

**Fix:** a full editorial pass over all 25 seasons of `NFL_CONTEXT`, verified against a reference. It's ~75 bullets — an hour of work, and it makes the most quotable copy on the site trustworthy.

### F5 — `_cache_bust` is a manual counter

`utils/data.py:71` — `_cache_bust = 2  # increment to force re-read when CSV data changes`.

This works exactly as long as you remember. Update a CSV, forget the bump, and the app serves stale data with no error and no signal. Given that data corrections are a routine activity here (see the git log), that's a live foot-gun.

**Fix:** hash the CSVs' mtimes or contents into the cache key so it invalidates itself.

---

## 3. Product — measured against `CLAUDE.md`

### What's working

The museum framing genuinely lands. "EXHIBIT" labels, the Trophy Room, `MANAGER_EMOJI` giving every person a sigil, the closing "25 SEASONS. N DIFFERENT CHAMPIONS. ONE LEAGUE THAT NEVER QUIT." — these are editorial choices, not dashboard defaults. The home page hero even undercuts itself with "Occasionally ruined by a waiver wire mistake," which is exactly the right register for a league of friends.

The "Most Trips Without a Title" card is the best thing on the home page. It's a stat that only means something inside this community, and it puts a person's ongoing disappointment on the front page as a headline. That is the product working.

### F6 — The narrative layer is the stated priority and the biggest gap

`CLAUDE.md` is unambiguous: *"Every significant entity should eventually have a narrative summary... Not just: Record: 184-142. But: 'One of the defining managers of the modern era, known for…'"* It lists Managers, Franchises, Seasons, Players, Rivalries, and Records.

In practice `narratives.py` is 478 lines and is dominated by `NFL_CONTEXT` — real football history, not league mythology. The entity-level prose the vision calls for is largely generated from stats, which produces sentences that are accurate but interchangeable ("more fantasy points than anyone in league history").

The stat cards are already good. The gap is that the *league's own* mythology — the trades people still argue about, the nicknames, why a team is called what it's called — is the one thing that can't be derived from Yahoo, and it's the thing the vision document says matters most.

**Suggestion:** this is a content project, not an engineering one, and it's the highest-leverage work available. A `manager_lore.csv` / `franchise_lore.csv` in the same editorial spirit as `manual_timeline_events.csv` (which already exists and is the right pattern) would let you write mythology incrementally without touching code. Even two or three sentences per manager would transform the profile pages.

Corollary: this is also the part of the project that most benefits from *other people*. Fadi already files bug reports. A form or a shared doc where league members contribute their own memories would produce better copy than you can write alone, and would make them feel like the museum is theirs.

### F7 — Some exhibits have no way in

`keeper_hall.py` (1,177 lines) and `league_history.py` (511 lines) have **zero** interactive controls, while `rivalries.py` (1,215 lines) has three. There's nothing wrong with a linear exhibit — but Keeper Hall is the second-largest page in the project and the vision explicitly names "Keeper dynasties, keeper lore, keeper identity, player attachment" as a destination. Without any entry point for "show me *my* keepers" or "show me this player," a reader has to scroll the whole hall to find themselves.

**Suggestion:** the routes proposed in the self-hosting plan (`/managers/:slug`, and eventually `/players/:name`) solve this structurally. Worth keeping in mind that "Player Histories" and "Ownership Trees" already sit in your own second-tier priority list — they're the natural entry points into Keeper Hall.

---

## 4. Architecture & maintainability

### F8 — 698 inline styles are a maintenance tax you're already paying

Across `app.py`, the pages, and `utils/`, there are **376** `unsafe_allow_html` calls and **698** inline `style="..."` attributes. `utils/styles.py` already provides `metric_card()`, `section_header()`, `html_table()`, `avatar_html()`, and `render_page_footer()` — the right instinct — but most markup bypasses them and re-declares `font-family:'Bebas Neue'`, a gold hex, and a letter-spacing by hand.

Concretely: `#D4AF37` and `'Bebas Neue'` appear dozens of times as literals. Changing the gold, or the display font, is currently a find-and-replace across ten files rather than one edit.

This isn't urgent — it works, and it's a personal project. But it's the single biggest reason the codebase is 9,585 lines, and it's the main thing that will make a future port tedious. If you do nothing else here, moving the color palette and font stack into CSS custom properties in `inject_css()` would pay for itself immediately.

**The upside worth noting:** because the app is already hand-writing HTML and CSS, it is *far* closer to a portable static site than a typical Streamlit app. The costume is thin. That's the core argument in `SELF-HOSTING-PLAN.md`.

### F9 — Data/presentation separation is genuinely good

Worth saying explicitly, since most of this section is criticism: the split between `utils/data.py` (derivations, cached), `utils/narratives.py` (editorial content), and pages (presentation) is clean and consistently followed. Pages import named functions rather than reaching into DataFrames ad hoc. That discipline is why a port is feasible at all, and why the golden-file tests in F2 are straightforward to write.

---

## 5. Accessibility & device support

### F10 — Type is too small in places to read

The smallest declared sizes in the codebase are `0.5rem`, `0.55rem`, and `0.58rem` — **8px to 9.3px**. These are used for section labels and eyebrow text (e.g. `app.py:291`, the "EXHIBIT" label). Combined with uppercase and 3–6px letter-spacing, that's below what many people can comfortably read, and letter-spacing at that size makes it worse rather than better.

Secondary text uses `#A7B0BC` on a dark background, which is fine, but the `#6B7280` used for de-emphasized copy (`app.py:270`) against the dark background is likely under the 4.5:1 contrast threshold.

Your audience is a league that started in 2001. Some of these readers are 25 years older than they were at the first draft, and many will open this on a phone.

**Fix:** set a floor of `0.75rem` (12px) for any real text, reserve smaller sizes for nothing, and check the two greys with a contrast tool. Cheap, and it materially widens who can use the site.

### F11 — Wide layout and fixed column counts on mobile

Every page uses `layout="wide"`, and the home page renders `st.columns(5)` for recent champions plus `st.columns(4)` twice. Streamlit stacks columns on narrow screens, so it won't break — but five stacked champion cards push the "League Legends" section far down, and the museum's visual rhythm (which depends on horizontal grouping) doesn't survive the stack.

**Fix:** worth actually opening on a phone and deciding. If most traffic is league members getting a link in a group chat, mobile *is* the primary experience, not the fallback.

---

## 6. Prioritized recommendations

| # | Action | Effort | Why |
|---|---|---|---|
| 1 | **Commit the untracked pipeline scripts and docs** (F1) | 2 min | Data pipeline currently exists on one machine |
| 2 | Editorial pass over `NFL_CONTEXT` (F4) | ~1 hr | Two errors in four sampled seasons; copy is the product |
| 3 | Golden-file tests for `utils/data.py` (F2) | ~1 afternoon | Stops league members from finding your bugs |
| 4 | Raise minimum font size, check grey contrast (F10) | ~1 hr | Widens the audience; your readers are older now |
| 5 | Fix the hardcoded 12-1 prose (F3) | 15 min | Latent wrong-claim bug |
| 6 | Self-invalidating cache key (F5) | 15 min | Silent stale-data risk during routine edits |
| 7 | Palette + fonts into CSS custom properties (F8) | ~1 hr | Removes the worst of the find-and-replace tax |
| 8 | Start `manager_lore.csv` (F6) | ongoing | The highest-value work in the project |
| 9 | Self-hosting migration | multi-session | See `SELF-HOSTING-PLAN.md` |

Items 1–6 are all achievable in a weekend and would meaningfully raise the floor.

---

## 7. Closing

The thing this project gets right is the thing most projects get wrong: it knows what it is. `CLAUDE.md` states a clear product thesis, the data documentation is rigorous enough to trust, and the site makes editorial choices instead of defaulting to charts. That foundation is why the findings above are mostly about *tightening* rather than *rebuilding*.

The two that matter most aren't technical. **Get the pipeline into git** — the archaeology in `DATA_GUIDE.md` is irreplaceable and it isn't backed up. And **write the lore** — you've built an excellent frame for stories that are, for now, still mostly implied by statistics. The scraping is done. The hard remaining work is remembering.
