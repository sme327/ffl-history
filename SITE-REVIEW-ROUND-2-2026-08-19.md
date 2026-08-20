# Site Review, Round 2 — 2026-08-19

**Status (2026-08-19): the table-framing fix (§5, items 1–2) is done and live.** The findings below describe the site as it was found, at the start of this review — read §5 for current status on every recommendation, including what's still open.

Full UI/UX pass on the live site (`iwnh.sme327.com`) after the re-skin work: room backdrops, manager medallions, franchise badges, card frames, ambient lighting. Scope: does this read as an actual museum, or a site with museum decoration applied on top of an unchanged structure. Grounded in full-page screenshots of every top-level section, not spot checks.

**Direct answer to the question that prompted this: it's both, and the split is precise, not vague.** Everything built from `.card` — stat tiles, plaques, DNA cards, trivia cards, the reigning champion — is genuinely re-architected. Everything built from a raw `<table>` — and there's more of that on this site than there is of `.card` — never got touched. The costume seam is exactly at that boundary, and it's visible on every single page that has a table, which is most of them.

---

## 1. What's actually working — say this plainly first

- **The fixed room backdrops are the real thing.** Verified with an actual scroll test earlier this session: the photo genuinely stays behind the content as you scroll, on every section. This is architecture, not decoration — it's the single best thing on the site now.
- **Manager medallions and franchise badges carry real identity.** Twenty-four distinct, hand-differentiated icons, correctly colored, correctly reused everywhere a person or seat is referenced. This is the kind of detail a real museum has and a template doesn't.
- **The card frame system (`border-image` on `plaque-frame.svg`) is doing real work** on everything it touches — stat tiles, DNA cards, trivia cards, plaques all read as objects in cases, not divs.
- **The ambient lighting (ceiling-light pools every 900px, glow on every h2) is subtle but real** — it's the thing that makes scrolling feel like moving through a lit space rather than a page.

None of this needs to be redone. The gap is specifically what's described below.

---

## 2. The central finding: every data table on the site is unstyled

`app/globals.css` — the entire table styling, verified just now:

```css
table { width: 100%; border-collapse: collapse; font-size: var(--step--1); }
th, td { padding: 0.5rem 0.7rem; text-align: left; border-bottom: 1px solid var(--border); }
th { color: var(--muted); text-transform: uppercase; letter-spacing: 2px; font-weight: 600; }
tbody tr:hover { background: rgba(212, 175, 55, 0.04); }
```

This is **the pre-re-skin table style, untouched by any commit this entire session.** Every round of work — the frame system, the room backdrops, the border-image cards — touched `.card` and its relatives. Nothing ever touched `table`. And tables are not a minor part of this site:

| Page | Table | Approx. rows |
|---|---|---|
| Champions | Every Final | 25 |
| League History | All-Time Manager Stats | 24, 10 columns wide |
| Rivalries | Championship Game Record | 24 |
| Rivalries | Franchise Rivalries | 10 |
| Rivalries | **Every Matchup** | **195** |
| Keeper Hall | Player Keeper Timelines | ~15 |
| Keeper Hall | Most Kept | 20 |
| Draft Center | First Picks (×2) | 10 each |
| Manager profile | Season by Season, Head to Head | varies |
| Franchise profile | Top Rivals, Season by Season | varies |
| Season detail | Final Standings, Top Scorers | 12 each |
| Player page | Ownership | varies |

Rivalries' "Every Matchup" table alone is **195 rows of plain text on a flat background**, and it's roughly 80% of that page's total height. Scroll to it and every trace of the museum — the frame, the case, the lit room — disappears. It looks like a debug view.

This is the single highest-leverage fix available right now, larger in visual impact than anything else in this document, and it doesn't require new assets — it requires applying the frame system that already exists to an element type it was never pointed at.

---

## 3. The secondary finding: uniform treatment has created a different flatness

This one's subtler and worth naming even though it's not as visually loud as the table gap.

Every `.card` on the site — regardless of what it holds — gets the exact same frame, same weight, same size logic. A "5× Dominic" championship count gets the identical brass frame as a "Highest Winning Score" trivia fact, which gets the identical frame as "Most Runner-Up Finishes." A real museum doesn't do this: the founding trophy sits in a spotlit case: the attendance ledger sits on an open reading table. Presentation weight signals significance. Right now every fact on this site has equal visual weight, which is a subtler version of the same "dashboard wearing a costume" problem — it's just template repetition with better materials.

**Timeline is the clearest example.** The page is **24,610px tall** — one of the longest pages on the site — because all 160+ events, spanning 25 years, render as the same small left-bordered card, one after another, with only a minor size bump (`.event-major`) for high-importance ones. There's no equivalent of "this is the moment worth stopping at" versus "this is a footnote you can skim." The historical spine of the league currently reads as a very long, gently-varying list rather than a curated walk through four eras.

**Draft DNA is a partial counter-example worth learning from** — 24 manager cards, but each carries a distinct color, archetype label, and position-share bar, so even though the frame is identical, the *content* differentiates them enough that the repetition reads less flatly than, say, Champions' identical-looking Trivia grid.

---

## 4. Do we need new assets? Mostly no — this is an architecture gap, not a content gap

**For the table fix (§2): no new assets needed.** `plaque-frame.svg` already exists, is already proven via `border-image` on cards, and can be pointed at tables — either the whole table wrapped in a framed panel, or (better, given how wide and tall these tables are) a lighter treatment: the frame around the table container, with `thead`/row styling pulling from the same brass/gold palette already established. This is a CSS task, achievable with what's already built.

**One asset that would genuinely deepen the "real museum, not costume" feeling: a distinct material for reference/catalog content.** Real museums vary material by content type — a display case is glass and brass; a reading room's card catalog is wood and paper, not gilt. Right now every surface on this site — whether it's a trophy plaque or a 195-row data table — is asked to use the *same* brass-display-case language. Giving tables their own, calmer material (a parchment or ledger-paper toned panel, worn brass rules instead of full ornate frames) would let the site distinguish "here is a treasured artifact" from "here is the reference archive," which is itself a curatorial statement, not just decoration. This would want one new texture asset (a subtly aged paper/ledger tone, tileable) — small, cheap, high-leverage, unlike the room photos which were a large commission.

**For the hierarchy/pacing gap (§3): no new assets, an editorial and layout decision.** This is about *choosing* which content gets the full ornate treatment and which gets something quieter — using restraint as a tool, the way a curator decides what goes in the lit case versus the open shelf. Timeline specifically would benefit from a genuinely larger, more distinct treatment for high-importance events (championships, dynasties) versus a compact list-row treatment for routine ones, rather than the current one-card-fits-all with a minor size bump.

---

## 5. Prioritized recommendations

| # | Action | New assets? | Impact | Status |
|---|---|---|---|---|
| 1 | Frame/style every `<table>` on the site using the existing `plaque-frame.svg` system | No | Highest — this is the most visible remaining "costume" seam, present on ~10 pages | ✅ **Done 2026-08-19** — `.scroll-x` (the shared wrapper every standalone table uses) now gets the same `border-image` frame as `.card`, plus a brass rule under `th` and a faint zebra tint on `tbody`. One CSS change covered all 9 pages, no JSX edits. |
| 2 | Specifically address Rivalries' 195-row "Every Matchup" table — it's the single worst offender | No (covered by #1, called out separately for size) | High | ✅ **Done 2026-08-19** — verified the frame holds without distortion at the top of the table and ~150 rows down; also checked the League History 10-column table on desktop and a 390px mobile viewport. |
| 3 | Give tables their own calmer "reference archive" material, distinct from card display-cases | Yes — one small tileable texture | Medium — turns a fix into a real curatorial choice | ⬜ Open — tables currently reuse the exact `.card` display-case material (§4's original framing); still worth a distinct, calmer texture if the fully-uniform look feels too heavy at table scale once you've lived with it |
| 4 | Rework Timeline's event hierarchy — real size/prominence difference for high-importance events, not just a border tweak | No | Medium — addresses the site's single longest, most repetitive page | ✅ **Done 2026-08-19** — the 39 "high" events (championships, dynasties) each get a full framed `.event-featured` card; the other 121 collapse into a compact `.event-ledger` (one line each) per season. Page height dropped from 24,610px to 14,843px (~40%). Verified on desktop and a 390px mobile viewport. |
| 5 | Audit other uniform-grid pages (Champions Trivia, League History stat blocks) for the same opportunity — not urgent, lower payoff than Timeline | No | Low–Medium | ⬜ Open |

Items 1–2 shipped and are live on `iwnh.sme327.com`, verified against the deployed CSS, not just the dev server. Items 3–5 are the open work — 3 is the one place a new (small, cheap) asset would help; 4 and 5 are layout/editorial decisions, no commissioning needed.
