# Site Review — 2026-08-19

**Scope:** folder structure, documentation, file hygiene, UI/UX, and content, across the whole repository — the live Next.js/vinext museum in `app/`, the Python data pipeline that feeds it, and the docs that explain both.

**Not covered:** code-level correctness (see `PRODUCT-REVIEW-2026-08-13.md`, which already did that pass and is still mostly accurate — this review doesn't repeat its findings, only notes where the codebase has moved since). No changes were made to any file while producing this review — it is observation only.

---

## 1. Overall impression

The prior product review called this "a genuinely good project... good in the way that's hardest to fake." That's still true, and the five weeks since then closed real gaps: the site is fully ported off Streamlit onto a fast, server-rendered Next.js/Cloudflare Worker stack (`app/`, 3,071 lines), every route has tests-backed data behind it, the NFL-context factual errors got an editorial pass, font sizing has a floor, and the missing entry points (Keeper Hall, Draft Center, Rivalries, Franchises, Players) all exist now.

What's left is less about correctness and more about **arrival experience**: two full copies of the site sit in the repo side by side, the docs describe the half of the project that's now secondary, and the UI — while clean, disciplined, and fast — reads as one long spreadsheet wearing a nice font rather than a destination. That last point is the one you already flagged, and it's the subject of the companion document, `SKIN-CONCEPTS-2026-08-19.md`.

---

## 2. Folder & repository structure

### S1 — Two complete, independent implementations of the same site live in the repo

```
app.py, pages/*.py, utils/*.py     10,694 lines   Streamlit — the original
app/, lib/data.ts                   3,071 lines   Next.js/vinext — the port
```

Both are fully wired, both read from the same `data/` CSVs (via different paths — Streamlit reads CSVs directly through `utils/data.py`; the Next.js site reads pre-built JSON in `build/data/` via `lib/data.ts`), and both are currently *live* per `SELF-HOSTING-PLAN.md`'s explicit strategy of keeping Streamlit running as a fallback until the port is verified.

That's a deliberate, documented decision, not an oversight — but the plan's own Phase 6 checklist (`npx wrangler login`, deploy, attach `iwnh.sme327.com`, update the landing page's `FANTASY_APP_URL`, retire or keep Streamlit) doesn't show a completion marker the way Phases 2–4 do. Worth a direct check: **has cutover actually happened?** If yes, the plan doc and this review are both slightly stale and the Streamlit half becomes the next thing to archive (not delete — the plan is explicit that it protects a working fallback). If no, that's the single highest-leverage next step, since everything else in this review is downstream of "which site is the real one."

**Recommendation:** once cutover is confirmed, move `app.py`, `pages/`, and the Streamlit-only parts of `utils/` (`styles.py` — `data.py` and `narratives.py` are still load-bearing, they feed the Python build script) into an `archive/streamlit-site/` alongside the existing `archive/` migration scripts, with a one-line note on why they're kept. A future contributor opening this repo cold currently has no way to know which of the two UIs is canonical without reading git log.

### S2 — Repo hygiene is clean

`.gitignore` is thorough and correctly excludes build output (`build/`, `dist/`, `.next/`, `.wrangler/`), Python bytecode, IDE noise (`.idea/`), the Yahoo session cookie, and the large re-downloadable NFL reference file. `git status --ignored` confirms nothing sensitive or generated is tracked. This is worth naming explicitly since the prior review's F1 (untracked pipeline scripts) was a real risk and it's fully resolved — the whole pipeline, `CLAUDE.md`, and `DATA_GUIDE.md` are all in version control now.

### S3 — No deployment config committed at the project root

`wrangler.toml` / `wrangler.jsonc` doesn't exist at the repo root — only a generated copy inside the gitignored `dist/server/`. `worker/index.ts` and `vite.config.ts` presumably carry the Cloudflare project name and routing, but there's no single file a new contributor (or you, in six months) can open to see "this deploys to Worker X, attached to domain Y." Low urgency, but worth a five-minute pass to make sure the deploy config that exists is the one you intend to keep using — Worker project names and custom-domain bindings are exactly the kind of thing that's invisible until the day you need to redeploy from a different machine.

---

## 3. Documentation

### S4 — `README.md` documents the pipeline, not the product

The README is excellent for what it covers: scripts, data files, coverage, known gaps. But it was written for the Streamlit era and has no mention of `app/`, `lib/data.ts`, `npm run dev`/`build`/`deploy`, or the Next.js/Cloudflare stack at all. Someone cloning this repo today to work on the actual live site has to piece the workflow together from `package.json` and `SELF-HOSTING-PLAN.md`'s Phase 2–4 notes rather than the file whose entire job is "here's how this project works."

**Recommendation:** add a short section — "Running the site" — pointing at `npm run dev` / `npm run data` / `npm run deploy`, and a one-line pointer to `SELF-HOSTING-PLAN.md` for the full architecture story. Ten minutes of work, and it's the difference between the README describing the *back office* versus the *whole building*.

### S5 — `CLAUDE.md`'s page-ownership list has drifted slightly from what's shipped

The vision doc's page-by-page ownership section doesn't mention `/players/:slug` or `/keepers/:manager` as their own destinations, even though both exist, are cross-linked from Managers and Keeper Hall, and directly serve the doc's own "Player Histories" and "Ownership Trees" priorities. This isn't a defect — `CLAUDE.md` is a vision document, not a sitemap — but since it's the file that's supposed to arbitrate "does this belong," it's worth a short addition once these pages stabilize, so the next feature decision is measured against the site as it actually is.

### S6 — `SELF-HOSTING-PLAN.md`'s cutover phase is the one open thread in an otherwise very well-tracked migration

Covered in S1. Flagging again here specifically as a **documentation** issue: the plan is unusually good at marking phases done inline (✅ **done (2026-08-13)**), which makes the *absence* of that marker on Phase 5/6 informative. If cutover happened outside of what's reflected in the doc, update it — the whole value of this plan is that it's an accurate log, and a stale "what remains" list undercuts that.

### S7 — What's genuinely excellent and should stay exactly as-is

- `DATA_GUIDE.md` remains the standout artifact in this entire project. Twenty-five years of scraper archaeology, documented well enough that a stranger could verify every decision. Nothing here needs touching.
- `PRODUCT-REVIEW-2026-08-13.md` is a real, working audit trail — findings are marked done inline as they're resolved, which is exactly the pattern `SELF-HOSTING-PLAN.md` also uses. Keep using this pattern for future reviews, including this one.
- The three-document structure (vision → data methodology → migration plan) is a genuinely good separation of concerns. Don't collapse it into one file.

---

## 4. UI / UX

The design system itself is disciplined: CSS custom properties for the whole palette and type scale (`app/globals.css`), no inline style literals scattered across ten files the way the Streamlit original had, server-rendered SVG charts instead of a 3MB client chart library, a CSS-only hamburger menu with no client JavaScript. The engineering judgment behind the *system* is sound. The findings below are about what the system produces on the page, not how it's built.

### S8 — Every one of the fifteen routes shares the identical visual rhythm

Home, Champions, Rivalries, Draft Center, Keeper Hall, League History, every Franchise and Manager and Season page — all of them resolve to the same sequence: `eyebrow` → `h1` → intro `<p>` → `.grid.cols-4` metric cards → one or more `.grid.cols-2`/`.cols-3` content-card sections → a `.scroll-x` table. This is real internal consistency, and it's why the site never feels broken or ad hoc. But it also means there is currently **no visual signal that distinguishes "the Trophy Room" from "a spreadsheet of manager stats."** A reader who has been on three pages has seen the entire visual vocabulary of the site. Nothing about the layout itself tells you Champions is a celebration and History is an analysis — only the copy does.

This is the structural reason the site doesn't yet read like a destination next to a sports blog or a podcast site: those properties differentiate their sections visually — a recap page looks different from a stats page which looks different from a rankings page — even when the underlying content system is just as consistent under the hood. Right now every section here uses the same three building blocks in the same order.

This is the core problem the re-skin should solve, and it's covered in depth in `SKIN-CONCEPTS-2026-08-19.md`.

### S9 — There is no imagery anywhere on the site

`public/` contains only favicon assets. Zero photographs, zero illustrations, zero team logos. The entire visual vocabulary is: gold-on-navy typography, thin gold borders, and emoji (🏆 📅 🔑 📋 👤 🏟️) standing in for iconography. Emoji render inconsistently across platforms (Apple, Windows, and Android all draw them differently, and some older Windows fonts render them as flat monochrome glyphs), which undercuts the otherwise premium "museum" framing — a hall-of-fame plaque shouldn't have its visual identity depend on which phone you're reading it on.

This is not a criticism of the current build — a text-and-data museum with excellent editorial voice is a completely valid product. But it's directly relevant to your re-skin goal: a site that wants to sit next to sports blogs and podcast pages typically leans on *some* combination of photography, custom illustration, or a real iconography system, because that's a large part of what makes those properties feel like destinations rather than interfaces. See the skin concepts document for options ranging from "keep it text-driven" to "build around photography."

### S10 — No footer, no site-wide orientation

`app/layout.tsx` renders `<nav>` and `<main className="wrap">` and nothing else — there's no `<footer>`. Most pages simply end after their last table (a few, like Home, add a `.teaser` closing section, but that's page-specific, not site-wide). There's nowhere on the site that says what this project is, who built it, when it was last updated, or how to report a correction — which matters here specifically because the prior product review's biggest correctness bugs (`d865496`, `63b4355`) were caught by *league members reading the site*, not by tooling. A standing "found something wrong? tell us" link is cheap and turns your readers into the QA process you're already relying on informally.

### S11 — The nav has no indication of which section you're currently in

`.nav a:not(.nav-brand)` styles hover and nothing else — there's no `.active` class, no `aria-current="page"`, no visual distinction for the current route. On a 10-item nav (soon to be more if Search or other future routes land), a reader who followed a link from a group chat into `/rivalries/adam-vs-fadi` has no way to tell from the nav bar itself that they're inside Rivalries versus, say, Franchises. Small fix, meaningful orientation improvement.

### S12 — No search, on a site with hundreds of linkable pages

`CLAUDE.md` names Search as a long-term priority, and there's currently no search anywhere — not in the nav, not on any index page. With ~195 rivalry pages, 24 manager pages, 12 franchise pages, 25 season pages, and player pages growing as the site's Player Histories ambition develops, findability depends entirely on already knowing the site's structure well enough to browse to what you want. That's fine for the ten people who built this league's history and already know every name; it's a real barrier for a spouse, a kid, or a new league member trying to find "that one trade everyone still talks about" without knowing which manager or season it's filed under.

Not urgent relative to the visual work, but worth keeping on the roadmap — even a simple client-side fuzzy search over a pre-built name/title index (no server needed, given the whole site is already static-friendly) would meaningfully raise the ceiling on how this site gets used over time.

### S13 — A declared font is imported and never used

`app/globals.css` imports and declares `--serif: "Playfair Display", Georgia, serif;` (`:root`, line 22), but no rule anywhere in the stylesheet actually applies `var(--serif)`. The font is fetched on every page load (part of the single Google Fonts `@import`) for zero visual effect. Either use it somewhere deliberate — a serif treatment reads well for pull-quotes or plaque text, which is exactly the kind of differentiation S8 is asking for — or drop it from the import to save a font-weight fetch.

### S14 — Wide tables rely on raw horizontal scroll on mobile

`.scroll-x { overflow-x: auto; }` is applied to every data table, including some genuinely wide ones — the League History page's "All-Time Manager Stats" table has ten columns. This doesn't break anything (the prior review's F11 concern about `layout="wide"` breaking on mobile doesn't apply here; the grid system already reflows), but scrolling a ten-column table sideways on a phone is a real reading tax. Given the product's own framing — a link shared in a group chat is the primary distribution channel — worth deciding deliberately whether some of the denser tables (History, Rivalries' "Every Matchup") get a mobile-specific condensed view (fewer columns, expandable rows) rather than inheriting the desktop table as-is.

### S15 — What's working, and should be protected in any re-skin

- **The question-framed page structure directly implements `CLAUDE.md`.** "Who won?" "Who still hates each other?" "How did the league evolve?" as literal eyebrow copy above every `h1` is a rare case of a vision document's own language shipping verbatim in the product. Any re-skin should keep this pattern, not just the palette.
- **Cross-linking is thorough and genuinely rewards exploration.** Every manager name, season, player, and franchise ID is a link, consistently, across all fifteen routes. This is the mechanical foundation of the "oh wow, I forgot about that" experience `CLAUDE.md` asks for, and it's already well built.
- **The restraint on interactivity is a feature, not a gap.** Server-rendered SVG instead of a chart library, no client JS beyond the CSS-only nav toggle, 484KB total — this is a fast site for readers on old phones on a group-chat link, which is exactly the audience. Don't let a re-skin add client-side weight it doesn't need.
- **"This is not a statistics page. It's a history page."** (League History's intro copy) is the single best sentence on the site — it's the editorial thesis of `CLAUDE.md` stated in the reader's own voice. More of this, everywhere.

---

## 5. Content

### S16 — The narrative/lore layer is still the thing `CLAUDE.md` wants most and has the least of

The prior product review (F6) called this the highest-leverage work in the project. Since then:

- `manual_timeline_events.csv` has grown from 8 rows to **10 events** across 25 seasons — real progress, still thin.
- `MANAGER_IDENTITY` in `utils/narratives.py` has hand-written one-line descriptors for **13 of 24 managers** (54%) — the other 11, including some long-tenured members, fall back to auto-generated plaque prose.
- The suggested `manager_lore.csv` / `franchise_lore.csv` pattern from the prior review wasn't adopted; instead, identity lines and rivalry plaques live as hardcoded Python dicts in `narratives.py`. That's a reasonable architectural choice (it keeps everything in one file rather than spawning a fourth CSV format), but it does mean adding lore currently requires editing Python rather than filling in a spreadsheet row — a higher barrier for the "let league members contribute their own memories" idea the prior review floated.
- Keeper Hall's "Keeper Lore" section is a real, working example of the pattern at its best — short, specific, hand-written entries per notable player, clearly labeled "written down, not computed." This is the model to replicate everywhere else: Rivalries, Franchises, and the remaining 11 managers are the natural next targets, since they're the pages the eyebrow copy already promises this kind of writing to ("Who still hates each other?" is a question a stat table cannot actually answer).

This isn't a new finding so much as a status check: the gap the prior review flagged as the highest-value work in the project is real, quantifiable, and still open. It's also independent of the re-skin — good lore reads well in any visual system, and a re-skin is a natural moment to design a container for it (a pull-quote treatment, a plaque module) that makes the hand-written content look distinct from the generated stats around it, which reinforces S8's point about needing more visual variety in the first place.

### S17 — What's working in the copy

- The NFL-context factual errors flagged in the prior review (F4 — the 2003/2004 Manning mixup, the Owens sequencing error) were fixed in `1cd6034`. Worth a light re-check of the remaining ~21 seasons not originally spot-checked, but the process that caught this is working.
- Season hooks (`SEASON_HOOKS`) are a good, cheap pattern — one sharp line per season, tied to real NFL history where it lands ("LaDainian Tomlinson. Need anything else?"), and this is exactly the kind of writing S16 wants more of elsewhere.
- The home page's self-aware tagline ("Occasionally ruined by a waiver wire mistake") and the "{insert witty name here}" brand itself are a consistent, deliberate register — a friend-group museum that doesn't take itself too seriously while still building a genuinely rigorous archive underneath. That tone is worth protecting explicitly as a brief constraint on the re-skin: whatever visual direction gets chosen should be able to hold a joke, not just a trophy case.

---

## 6. Prioritized recommendations

| # | Action | Effort | Why |
|---|---|---|---|
| 1 | Confirm cutover status; update `SELF-HOSTING-PLAN.md`'s Phase 5/6 accordingly | 15 min | Everything else depends on knowing which site is canonical (S1, S6) |
| 2 | Add a "Running the site" section to `README.md` covering the Next.js stack | 20 min | The README currently documents only the back office (S4) |
| 3 | Add `<footer>` with attribution, last-updated, and a "report a correction" link | 30 min | Cheapest fix for the site's real QA process (S10) |
| 4 | Add active-state styling to the nav (`.active` / `aria-current`) | 15 min | Orientation on a 10+ item nav (S11) |
| 5 | Either apply `var(--serif)` somewhere deliberate or drop the font import | 10 min | Unused font weight fetched on every page (S13) |
| 6 | Re-skin the visual system — see companion doc | multi-session | The core ask; addresses S8, S9, S15 |
| 7 | Once re-skin lands, design a distinct "lore" module (pull-quote/plaque) | half day | Gives S16's hand-written content a visual home distinct from stat cards |
| 8 | Resume the lore-writing effort: remaining 11 manager identities, franchise lore, more timeline events | ongoing | Still the single highest-value content work per the prior review (S16) |
| 9 | Archive the Streamlit implementation once cutover is confirmed | half day | Removes 10,694 lines of parallel-maintenance risk (S1) |
| 10 | Scope a lightweight client-side search over names/titles | multi-session | No entry point into ~250+ pages beyond browsing (S12) |

Items 1–5 are all achievable in an afternoon. Item 6 is the big one, and it's the subject of the companion document.

---

## 7. Companion document

Visual direction options — five to eight full concepts, each described in enough detail for a design/graphics team to mock up, all rendered against the Home page for a fair side-by-side comparison — are in **`SKIN-CONCEPTS-2026-08-19.md`**.
