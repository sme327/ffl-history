# Site Review — 2026-08-19

**This is the consolidated, current-state review** — it supersedes two earlier passes written earlier today (a pre-re-skin folder/docs/hygiene/UI review, and a post-re-skin "does this feel like a museum or a costume" pass). Both are folded in here rather than kept as separate point-in-time snapshots, so there's one document that reflects the site as it actually stands, live on `iwnh.sme327.com`.

---

## 1. Overall

The project cleared two different bars today. First, the housekeeping bar: the data pipeline is versioned, the Streamlit-to-Next.js migration is complete and archived cleanly, the docs describe the site that actually exists. Second, the harder bar: **does this read as an actual museum, or a site wearing museum decoration.** After a full re-skin pass and a dedicated review of that pass, the honest answer is — mostly yes now, with two specific, named gaps left, not a vague "needs polish."

What's below is organized by area, each section stating current status plainly rather than re-narrating how it got there.

---

## 2. Folder & repository structure

**Clean.** `git status` shows nothing stray, `.gitignore` correctly excludes all build output, the Yahoo session cookie, and IDE noise. The full data pipeline, `CLAUDE.md`, and `DATA_GUIDE.md` are all versioned — nothing here depends on one laptop.

**Fixed today:** a duplicate `utils/styles.py` kept reappearing as an untracked file at the repo root (byte-identical to the real, archived copy in `archive/streamlit-site/utils/styles.py` — almost certainly an IDE local-history artifact given the project's `.idea/` folder). Deleted; the real copy is safe in the archive.

**`public/museum/`** is now a real asset library — 9 categories, ~90 files, all referenced from code, nothing orphaned. Added a manifest `README.md` inside it today so the inventory doesn't have to be reverse-engineered from `git log`.

**Documentation set consolidated today.** This session produced five dated planning docs (two site reviews, three asset briefs) as work happened in phases — appropriate at the time, clutter now that the work they were scoping is done. Down to two: this file, and `VISUAL-ASSETS-2026-08-19.md` (now including the one still-open asset need). `SKIN-CONCEPTS-2026-08-19.md` is kept as-is — it's the historical record of *why* "Museum, Lit Properly" was chosen over the other seven directions, worth keeping as a decision log, not clutter. `PRODUCT-REVIEW-2026-08-13.md` (data/code correctness) and `SELF-HOSTING-PLAN.md` (hosting migration, marked complete) cover different scope entirely and are untouched.

---

## 3. Documentation

- **README.md** — documents both the data pipeline and the live site's build/deploy flow (`npm run dev`/`build`/`deploy`). Accurate.
- **DATA_GUIDE.md** — unchanged, still the standout artifact in the project: twenty-five years of scraper archaeology, verifiable by a stranger.
- **CLAUDE.md** — still the north star for what belongs on this site. One small drift: its page-ownership list doesn't yet name `/players/:slug` or `/keepers/:manager` as their own destinations, even though both exist and directly serve priorities the doc itself names (Player Histories, Ownership Trees). Cosmetic, not urgent.

---

## 4. UI/UX — the re-skin

### 4a. What's built

The full "Museum, Lit Properly" identity, live on every route:

- A distinct fixed-position room backdrop per section (Trophy Room, History Corridor, Archive Library, Chronicle Vault, Portrait Gallery, Dynasty Wing, War Room, The Vault, The Arena) plus Home's original hero scene — genuinely fixed to the viewport, not scrolling away after the first screenful.
- 24 manager sigil medallions, 12 franchise badges, 4 era medallions, 15 event-type icons, 6 exhibit icons, 6 position icons — all real vector art, zero OS emoji-font dependency anywhere.
- A `border-image`-based frame system (`plaque-frame.svg`) applied consistently to cards, plaques, and — as of today — every data table on the site.
- Site-wide ambient lighting: a recurring light pool every 900px down every page, a glow on every `h1`/`h2`, wood-textured nav.

### 4b. Verified genuinely working, not just claimed

Worth stating plainly because earlier rounds of this same work were reported "done" before they actually were, more than once:

- The fixed room backdrops were confirmed with a **real scroll simulation** (`page.evaluate('window.scrollTo(...)')`), not just a tall composite screenshot — the composite alone wouldn't have proven `position: fixed` was actually working.
- The card/table frame system was checked at both size extremes: a 195-row table (Rivalries' Every Matchup) and a 10-column wide table (League History), on desktop and a 390px mobile viewport.
- Every deploy in this session was verified against the **live server's actual served CSS**, not the deploy log — which caught a real CDN propagation lag once (resolved on its own within ~15 seconds, not a broken build).

### 4c. What a dedicated post-re-skin review found broken, and is now fixed

A full-page (not spot-check) pass across every section surfaced the actual seam between "re-skinned" and "not":

- **Every data table was completely unstyled** — plain hairlines, no frame, no material — while every `.card` had the full treatment. This was the single most visible remaining "costume" moment: scroll to Rivalries' 195-row matchup table (roughly 80% of that page's height) and the museum disappeared entirely. **Fixed**: all 9 pages with tables share one wrapper (`.scroll-x`), so one CSS change framed every table on the site — same border-image system, a brass rule under headers, a faint zebra tint for readability on long tables.
- **Timeline was 24,610px of uniformly-weighted events** — 160 events, from championships to minor footnotes, all rendered as the same card. **Fixed**: the 39 "high" importance events now get the full display-case frame; the other 121 collapse into compact one-line ledger rows, grouped per season. Page height dropped to 14,843px (~40% shorter) with no content removed, just weighted correctly.

### 4d. Still open

- **A distinct "reference archive" material for tables.** Tables now use the frame system, but they reuse the *exact* brass display-case look everything else uses. A real museum varies material by content type — a display case isn't built from the same stuff as a card catalog. This is the one place a new asset would genuinely deepen the "real museum, not costume" feeling rather than just extend what exists. Brief is in `VISUAL-ASSETS-2026-08-19.md` §5.
- **Extend Timeline's hierarchy treatment to other uniform grids** (Champions' Trivia section, League History's stat blocks) — flagged low priority in the review that found it, not done. Worth a look eventually, not urgent.
- **The Arena's missing tint** — the brief asked for a red-orange undertone to distinguish it from the other rooms; it shipped in the same amber as everywhere else. Cosmetic.
- **Whether `gallery-wall-tile.webp` is meaningfully distinct from the texture it replaced** (`navy-walnut-panel.png`, still present in the folder for reference) was never fully confirmed. Low stakes either way — it passed its seam test and reads correctly live.

---

## 5. Content — carried forward from before the re-skin, untouched by it

The re-skin was entirely a presentation-layer effort; nothing this session touched the site's actual editorial content. The gap the original review called the highest-value work in the project is exactly as open as it was before today:

- `manual_timeline_events.csv` has **10 hand-written events across 25 seasons** (unchanged since the last check).
- `MANAGER_IDENTITY` has hand-written one-line descriptors for **13 of 24 managers** (unchanged).
- Keeper Hall's "Keeper Lore" section remains the one place this pattern is done well — short, specific, explicitly labeled "written down, not computed" — and remains the model worth replicating elsewhere (Rivalries and the remaining 11 managers are the natural next targets, since their own eyebrow copy — "Who still hates each other?" — already promises writing a stat table can't deliver).
- **Search** is still absent, still named on `CLAUDE.md`'s own roadmap, still unaddressed.

None of this is a defect introduced by the re-skin — it's the same open item from before, now sitting inside a much better-built room.

---

## 6. Prioritized recommendations

| # | Action | New assets? | Status |
|---|---|---|---|
| 1 | Frame every table on the site | No | ✅ Done |
| 2 | Fix Rivalries' 195-row table specifically | No | ✅ Done |
| 3 | Give tables their own calmer reference-archive material | Yes — brief in `VISUAL-ASSETS-2026-08-19.md` | ⬜ Open |
| 4 | Rework Timeline's event hierarchy | No | ✅ Done |
| 5 | Extend the hierarchy treatment to other uniform-grid pages | No | ⬜ Open, low priority |
| 6 | Resume lore-writing: remaining 11 manager identities, Rivalries plaques, more timeline events | No | ⬜ Open — still the highest-value non-visual work available |
| 7 | Scope a lightweight client-side search | No | ⬜ Open, longer-term |
| 8 | Fix The Arena's missing tint | No | ⬜ Open, cosmetic |

Items 1, 2, and 4 shipped today, verified live. Item 3 is the one place a new asset is actually warranted — its brief is in the companion document. Item 6 remains the single highest-leverage thing nobody's touched: the museum now has a genuinely well-built building; the thing worth doing next is filling it with more of the league's own writing, not more architecture.
