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

### Option A — Static rewrite on Cloudflare (recommended)

Port to the same stack as My Concert Archive: vinext / React on a Cloudflare Worker, data precomputed to JSON at build time, routes replacing dropdowns.

- **Cost:** $0 forever. Free tier isn't even approached.
- **Never sleeps.** Loads in tens of milliseconds.
- **You already have the template.** The concert archive is this exact shape — a read-only archive over static data, with routes for entities. Same problem, already solved once in your own portfolio.
- **Effort:** real. See the estimate below.

### Option B — Self-host Streamlit on Fly.io or Render

Containerize the app as-is, point `iwnh.sme327.com` at it.

- **Cost:** ~$5–7/month (~$60–85/year).
- **No sleeping**, custom domain works, **code unchanged**.
- **Effort:** an evening. A Dockerfile and a deploy.
- Keeps every limitation of the current architecture, and the ~1 hour of deploy config is thrown away if you later do Option A.

### Option C — Reverse-proxy Streamlit Cloud behind a Worker

**Not recommended.** Streamlit needs a WebSocket (`/_stcore/stream`) and performs host/XSRF checks that fight proxying. Even if you get it working, the app still sleeps, because it's still running on Community Cloud. You'd add fragility and fix nothing.

### Recommendation

**Option A**, unless you want it live next week — in which case **Option B now, Option A later** is a legitimate sequence. B is cheap enough that treating it as a bridge isn't wasteful.

Do not do C.

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

## Phase 2 — Port the data layer to a build step

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

The bulk of the work. `utils/styles.py` (886 lines) already has the right instinct — `metric_card()`, `section_header()`, `html_table()`, `avatar_html()` — but most markup bypasses those helpers and inlines styles directly. The port is the moment to invert that: a real stylesheet with real class names, and components that take data.

`utils/narratives.py` (478 lines) is pure static content — `NFL_CONTEXT` and friends — and converts to JSON almost mechanically.

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

Option A is honestly a multi-session project. Rough shape of the 9,585 lines:

| Work | Share | Notes |
|---|---|---|
| Data layer port (`utils/data.py`, 1,262 lines) | ~20% | Highest risk, protected by Phase 1 fixtures |
| Presentation port (pages + `styles.py`, ~7,800 lines) | ~60% | Bulk of it; mostly mechanical, tedious |
| Routing, build, deploy | ~20% | Well-trodden — the concert archive is the template |

Option B is one evening.

---

## Risk summary

| Step | Risk | Mitigation |
|---|---|---|
| Repo has untracked pipeline scripts | Total loss of the scraper if the laptop dies | **Commit them today**, before any migration work |
| Porting 1,262 lines of derivations | Silent correctness drift — wrong champions, wrong records | Phase 1 golden-file fixtures as the acceptance gate |
| Porting 698 inline styles | Visual regressions, inconsistency carried forward | Rebuild on a stylesheet rather than transcribing |
| Rivalry route explosion | Hundreds of near-empty pages | Generate only pairs with real head-to-head history |
| Stale link on the landing page | Card points at the retired Streamlit URL | Phase 6, cross-repo — easy to forget |
| Data refresh workflow | Scrape → commit → rebuild is more steps than today | Document it in README; it's still simpler than a live server |

---

## What doesn't change

`data/` stays the source of truth. `fetch_yahoo_data.py` keeps scraping Yahoo the same way. `DATA_GUIDE.md` remains the authoritative record of era quirks and stays accurate through the port. The museum vision in `CLAUDE.md` is untouched — if anything, routes serve it better than dropdowns, because an exhibit you can link to is an exhibit people actually share.
