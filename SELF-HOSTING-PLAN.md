# Moving The Long Game to `iwnh.sme327.com` — Proposed Plan

**Date:** 2026-08-13
**Current hosting:** `insertwittynamehere.streamlit.app` (Streamlit Community Cloud, deployed from `github.com/sme327/ffl-history`)
**Target hostname:** `iwnh.sme327.com`
**Goal:** A permanent home on a domain you own, that doesn't sleep, doesn't depend on a free tier's goodwill, and costs nothing to keep running.

---

## Where the domain stands today

`sme327.com` is already on Cloudflare — nameservers moved 2026-08-12, zone active, DNS verified. The landing page runs as a Cloudflare Pages project on the apex. Adding `iwnh.sme327.com` is a subdomain on a zone you already control, so **there is no DNS project here**. That part is a five-minute step at the end.

The entire difficulty of this migration is that Streamlit can't run on Cloudflare.

---

## The key insight: this is a static site wearing a Streamlit costume

Streamlit exists to put interactive Python in front of users. This app barely uses it that way. Measured across `app.py` and the nine pages:

| Signal | Count | What it means |
|---|---|---|
| `st.markdown(..., unsafe_allow_html=True)` | 376 | The app is a **hand-written HTML generator** |
| Inline `style="..."` attributes | 698 | The design is already CSS, just embedded in Python strings |
| `st.columns` | 67 | Layout only — no interactivity |
| `selectbox` / `radio` / `multiselect` | **13** | The entire interactive surface, across 10 pages |
| Data writes | **0** | Completely read-only |

And every one of those 13 controls does the same thing: **pick an entity.** Choose a season. Choose a manager. Choose a franchise. Choose a rivalry.

That is not interactivity. That is a URL.

A dropdown that switches between 25 seasons is a worse version of `/seasons/2009` — worse because it can't be bookmarked, linked in a group chat, or indexed. Converting those dropdowns to routes doesn't just make the app portable; it makes it a better museum. "Hey, remember this" with a link straight to the exhibit is the entire point of the product per `CLAUDE.md`.

So this is **static site generation**, not a reimplementation. The data layer already computes everything at load time and caches it (20 `@st.cache_data` functions). Moving that computation from request-time to build-time is a change of when, not what.

---

## Options

### Option A — Rewrite the presentation layer on Cloudflare ✅ **chosen**

Port to the same stack as My Concert Archive and the Draft Room: vinext / React on a Cloudflare Worker, with the **data layer staying in Python** and emitting JSON at build time. Routes replace dropdowns.

- **Cost:** $0 forever. The free tier isn't approached.
- **Never sleeps.** Loads in tens of milliseconds.
- **One stack across the portfolio.** Three projects, one set of idioms, one deploy story.
- **The riskiest code is never rewritten.** Era-specific keeper rules, franchise lineage, playoff bracket reconstruction — all stay in pandas where they're already correct.
- **Room for the roadmap.** Search, Player Histories, Ownership Trees and the rest of `CLAUDE.md`'s future priorities are client-side features. This stack supports them; exported HTML fights them.
- **Effort:** real, but it's a *presentation* rewrite. See the estimate below.

### Option B — Static-export the Python (considered, rejected)

Stub out `streamlit`, import the app, capture the HTML it generates, write files — the same trick `build.py` uses in `sme327-landing`. Technically viable: only 5 Streamlit DOM selectors appear in `styles.py`, Plotly exports to standalone HTML natively, and `st.columns` can be emulated with grid wrappers.

Rejected because it **ports the technical debt rather than paying it down**. The 698 inline styles and 376 `unsafe_allow_html` calls survive intact and become load-bearing for the build. It also creates a bespoke stub harness that only this project uses, and leaves you authoring against a framework you're no longer really running.

Faster to reach, worse to live in.

### Option C — Self-host Streamlit on Fly.io or Render

Containerize as-is, point `iwnh.sme327.com` at it. ~$5–7/month, code unchanged, an evening of work. Kept on the record as the emergency path if the domain is needed before the rewrite lands — not the plan.

### Option D — Reverse-proxy Streamlit Cloud behind a Worker

**Do not.** Streamlit needs a WebSocket (`/_stcore/stream`) and performs host/XSRF checks that fight proxying. Even working, the app still sleeps, because it's still on Community Cloud. Adds fragility, fixes nothing.

---

## Open questions to settle first

1. **Does this move under `ffl.sme327.com`, or stand alone at `iwnh.sme327.com`?** If the FFL hub gets built, this could live at `ffl.sme327.com/iwnh` instead — one Pages/Worker project, one deploy, one set of shared styling. Standing alone is simpler now; consolidating is cheaper long-term. This plan assumes standalone.
2. **How often does the data actually change?** If it's once a year after the season ends, the build-time model is strictly better. If you want in-season weekly updates, decide now whether that's a manual scrape-and-push or a scheduled job.
3. **Does the rewrite adopt the design as-is, or is it a redesign?** Porting 698 inline styles verbatim is faster but carries the existing inconsistencies forward. Rebuilding on a real stylesheet is more work and a better result. Recommend the latter — see §4 of the product review.

---

## Phase 0 — Prerequisites

- **Fix the repo first.** `fetch_yahoo_data.py`, `build_player_positions.py`, `inspect_yahoo_page.py`, `CLAUDE.md`, `DATA_GUIDE.md`, and `archive/` are **untracked**. The entire data pipeline exists only on one laptop. Commit these before anything else — see the product review, finding **F1**. This is a genuine blocker: you cannot rebuild the data from a clone of the repo as it stands.
- Cloudflare account — ✅ done.
- `wrangler` authenticated to your account (`npx wrangler login`).
- Decide Option A vs B.

## Phase 1 — Freeze the data contract

This is the phase that protects the project, and it's worth doing **even if you never migrate**.

- Add golden-file tests against the current Streamlit app's derived outputs: champions per season, all-time manager records, keeper chains, franchise stewardship periods, rivalry head-to-heads, playoff results.
- Capture them as JSON fixtures from the app **as it exists today**, while it's the source of truth.
- These become the acceptance criteria for the port: the new site is correct when it reproduces them exactly.

Without this, a rewrite of 1,262 lines of pandas derivations is an unverifiable leap. With it, it's a refactor with a pass/fail gate. The git log shows three separate human-discovered correctness bugs (`Fix Mike Williams 20yr career`, `Fix Evan vs Fadi rivalry plaque`, `Fix home page to acknowledge Clark & Fadi both went 12-1`) — that's the failure mode this prevents.

## Phase 2 — Port the data layer to a build step ✅ **done (2026-08-13)**

`scripts/build_site_data.py` emits 270 JSON files (2.5 MB) into `build/data/`, one per future route:

```
site.json  champions.json  timeline.json  draft.json  keepers.json
player-ownership.json  franchise-rivalries.json  playoff-eliminations.json
managers/index.json + 24    franchises/index.json + 12
seasons/index.json + 25     rivalries/index.json + 195
manifest.json
```

Every frame is checked against `tests/fixtures/` **before** it is written — the build exits non-zero rather than emit history the test suite hasn't approved (verified by corrupting a fixture and confirming the refusal). Slugs are stable and apostrophe-safe: `Kevin O'Boyle` → `kevin-oboyle`, rivalries → `dominic-vs-kevin-oboyle`.

### Phase 4 status (2026-08-13)

All ten pages have had their derivations extracted into `utils/data.py` and
`utils/narratives.py`, every one verified against the original inline logic and
covered by fixtures. Six pages are also fully rewired to consume them; four
still run their own copy and are listed as pending in the table above and in
the build output. **No derivation logic remains undiscovered** — the audit is
complete even where the rewiring is not.

### What Phase 2 uncovered

**Not all derivations live in `utils/data.py`.** Seven of ten pages call `load_all()` and compute from raw frames themselves, so that logic is covered by neither the JSON build nor the fixtures:

| Page | Logic still trapped in the page |
|---|---|
| `app.py` | home storylines: best season, title droughts, top scorer |
| `champions.py` | title-game context, dynasty framing |
| `franchise_profiles.py` | per-franchise season tables, lineage narrative |
| `league_history.py` | era summaries, competitive-balance trends |
| `rivalries.py` | elimination/heartbreak sections |

Each needs lifting into `utils/data.py` with fixtures added, before that route can render from JSON alone. This is the real remaining work in the data layer, and it's best done **page by page during Phase 4** — extract the logic, add its fixture, then port the presentation. Doing it that way keeps every step verified instead of front-loading a large untested refactor.

`build/` is gitignored; regenerate with `python3 scripts/build_site_data.py`.

---

## Phase 2 (original scope, for reference) — Port the data layer to a build step

- Translate `utils/data.py` into a build-time script that reads the 15 CSVs and emits JSON artifacts — one per route, plus shared indexes.
- Language choice: **keep it in Python.** `pandas` already does this work correctly, the derivations are subtle (era-specific keeper rules, franchise seat lineage, playoff bracket reconstruction), and rewriting them in TypeScript is pure risk for no gain. The build runs Python, emits JSON, and the site reads JSON. Your concert archive already mixes a Python data pipeline with a TypeScript front end.
- Validate every artifact against the Phase 1 fixtures.
- `data/ref_nfl_players.csv` (25K rows) is build-time only and already gitignored — it never ships.

## Phase 3 — Route design

Replace all 13 controls with URLs:

| Route | Replaces | Pages |
|---|---|---|
| `/` | `app.py` | 1 |
| `/champions` | `champions.py` | 1 |
| `/timeline` | `league_timeline.py` | 1 |
| `/history` | `league_history.py` | 1 |
| `/draft` | `draft_center.py` | 1 |
| `/keepers` | `keeper_hall.py` | 1 |
| `/seasons/:year` | `season_archive.py` dropdown | 25 |
| `/managers`, `/managers/:slug` | `manager_profiles.py` dropdown | 25 |
| `/franchises`, `/franchises/:id` | `franchise_profiles.py` dropdown | 13 |
| `/rivalries`, `/rivalries/:a-vs-b` | `rivalries.py` dropdowns | ~100–280 |

Roughly 350 pages at the high end — nothing for a static generator, and every one of them becomes linkable and indexable.

For rivalries, generate only pairs that actually played each other; a full 24×24 cross product is mostly empty matchups.

## Phase 4 — Port the presentation

The bulk of the work. `utils/styles.py` (886 lines) already has the right instinct — `metric_card()`, `section_header()`, `html_table()`, `avatar_html()` — but most markup bypasses those helpers and inlines styles directly. The port is the moment to invert that: a real stylesheet with real class names, and components that take data. Expect this layer to **shrink**, not transfer — 698 inline style attributes collapse into a few dozen classes.

`utils/narratives.py` (478 lines) is pure static content — `NFL_CONTEXT` and friends — and converts to JSON almost mechanically.

**Port in order of ascending difficulty, not importance.** The goal early on is to establish the component vocabulary, so start where the page is simple and the patterns are obvious:

| Order | Page | Lines | Why here |
|---|---|---|---|
| ~~1~~ | ~~`season_archive.py`~~ | 338 | ✅ **Logic extracted 2026-08-13** → `get_season_detail()`, fixture-covered for all 25 seasons, page is now presentation-only. Presentation port pending the site scaffold |
| ~~2~~ | ~~`league_timeline.py`~~ | 324 | ✅ **Logic extracted 2026-08-13** → `get_timeline_view()` + `group_timeline_by_season()`, verified across 192 filter combinations |
| ~~3~~ | ~~`app.py` (home)~~ | 319 | ✅ **Logic extracted 2026-08-13** → `get_home_view()`; also retired the hardcoded best-season prose (review F3) |
| ~~4~~ | ~~`league_history.py`~~ | 511 | ✅ **Logic extracted 2026-08-13** → `get_league_history_view()`; Plotly ports cleanly once the figure is fed data instead of frames |
| ~~5~~ | ~~`champions.py`~~ | 577 | ✅ **Logic extracted 2026-08-13** → `get_champions_view()`; seven unstable rankings given explicit tie-breaks |
| ~~6~~ | ~~`manager_profiles.py`~~ | 636 | ✅ **Logic extracted 2026-08-13** → `get_manager_profile()` + `manager_h2h_highlights()`; plaque copy moved to narratives |
| 7 | `draft_center.py` | 896 | ⚠️ **Derivations extracted 2026-08-13** → `get_draft_center_view()` + `get_draft_loyalty_board()`, fixture-covered. **Page rewiring still pending** — the page runs on its own inline copy for now |
| 8 | `franchise_profiles.py` | 966 | ⚠️ **Derivations extracted 2026-08-13** → `get_franchise_profile()` + `narratives.franchise_story()`, fixture-covered. **Page rewiring pending** |
| 9 | `keeper_hall.py` | 1,177 | ⚠️ **Derivations extracted 2026-08-13** → `get_keeper_hall_view()`, fixture-covered. **Page rewiring pending** — worth redesigning rather than transcribing, since it still has no entry points (review F7) |
| 10 | `rivalries.py` | 1,215 | ⚠️ **Derivations extracted 2026-08-13** → `get_rivalries_view()` + `get_head_to_head_losses()`, fixture-covered. **Page rewiring pending** |

**Keep the Streamlit app running the whole time.** Side-by-side visual diffing is the only practical way to catch regressions in a design this dense, and it means an unfinished rewrite never costs you a working site. Cut over only at parity.

Mobile is a design decision to make *here*, not to port. The current `layout="wide"` plus fixed column counts is a desktop assumption, and the primary distribution channel for this site is a link in a group chat (see product review, F11).

## Phase 5 — Deploy and attach the domain

- `wrangler deploy`, verify on the `*.workers.dev` URL first.
- Attach `iwnh.sme327.com` as a Custom Domain. Cloudflare writes the DNS record and issues the certificate automatically — the zone is already yours.
- Spot-check every route, including a few `/seasons/:year`, `/managers/:slug`, and a 404.

## Phase 6 — Cutover and cleanup

- **Update the landing page.** `streamlit_app.py` in `sme327-landing` has `FANTASY_APP_URL = "https://insertwittynamehere.streamlit.app"` — it becomes `https://iwnh.sme327.com`. Easy to forget; it's in a different repo.
- Decide the fate of the Streamlit deploy: retire it, or keep it running as a staging copy. There's no way to redirect from `*.streamlit.app`, so anyone with a bookmark keeps landing on the old one until it's taken down.
- Update `README.md` to describe the new build-and-deploy flow.

---

## Effort estimate

A multi-session project, but smaller than "rewrite 9,585 lines of Python in TypeScript" suggests — because most of it isn't rewritten:

| Component | Lines | What happens | Risk |
|---|---|---|---|
| `utils/data.py` | 1,262 | **Stays Python.** Becomes a build script emitting JSON | Low — protected by Phase 1 fixtures |
| `utils/narratives.py` | 478 | Static dicts → JSON | Trivial |
| `utils/styles.py` | 886 | → real stylesheet; expect it to shrink | Low |
| `app.py` + `pages/` | ~6,600 | The genuine rewrite: HTML strings → JSX | Medium, mechanical |
| Routing, build, deploy | new | Concert archive is the template | Low |

The riskiest logic in the project — 25 years of era-specific keeper rules, franchise seat lineage, playoff bracket reconstruction — **is never rewritten at all.**

The real failure mode is abandonment: a half-finished port sitting beside a Streamlit app that still works. Phase 1 fixtures, ascending-difficulty ordering, and keeping Streamlit live are all specifically there to prevent that.

---

## Risk summary

| Step | Risk | Mitigation |
|---|---|---|
| ~~Repo has untracked pipeline scripts~~ | ~~Total loss of the scraper if the laptop dies~~ | ✅ Resolved 2026-08-13 (`97deb37`) |
| Rewrite stalls half-finished | Weeks spent, still on Streamlit | Port ascending-difficulty; keep Streamlit live; ship nothing until parity |
| Porting 1,262 lines of derivations | Silent correctness drift — wrong champions, wrong records | Phase 1 golden-file fixtures as the acceptance gate |
| Porting 698 inline styles | Visual regressions, inconsistency carried forward | Rebuild on a stylesheet rather than transcribing |
| Rivalry route explosion | Hundreds of near-empty pages | Generate only pairs with real head-to-head history |
| Stale link on the landing page | Card points at the retired Streamlit URL | Phase 6, cross-repo — easy to forget |
| Data refresh workflow | Scrape → commit → rebuild is more steps than today | Document it in README; it's still simpler than a live server |

---

## What doesn't change

`data/` stays the source of truth. `fetch_yahoo_data.py` keeps scraping Yahoo the same way. `DATA_GUIDE.md` remains the authoritative record of era quirks and stays accurate through the port. The museum vision in `CLAUDE.md` is untouched — if anything, routes serve it better than dropdowns, because an exhibit you can link to is an exhibit people actually share.
