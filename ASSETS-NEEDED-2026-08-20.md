# Assets Needed — Graphics Team Brief — 2026-08-20

Companion to `UI-VISUAL-REVIEW-2026-08-20.md` (the "why" behind every item). This document is the commission list: what to make, exact specs, and priority. Supersedes the open items in `VISUAL-ASSETS-2026-08-19.md` §3–4 (both are folded in here as A1 and part of A3).

**Theme, one line:** *An evening gallery with the lamps on.* Dark navy walls and walnut stay; the light gets real. Warm white (`#fff6e0`) is light; brass (`#c9a24b`) is material; gold marks champions only. Frames are rare — most content sits in thin-railed cases, on open wall labels, or on lit ledger paper.

## Global conventions (unchanged from previous rounds, plus two new rules)

- SVG for vector, WebP for photographic, explicit file-size ceiling per item below. Naming matches `slugify()` output where entity-keyed.
- Color source of truth: the brass ramp `#fff0a8 → #c9a24b → #7f5b18`, navy family `#081120 / #0f1b2d / #1e2d40`, warm light `#fff6e0`, parchment `#e8dcc0–#d4c5a0`. Manager/era/event accent hexes live in `utils/data.py` / `utils/narratives.py`.
- **New rule 1 — no text glyphs in art.** No `<text>` elements with system font-families (current badges/position icons use Arial). All lettering outlined to paths.
- **New rule 2 — no dead boilerplate.** Ship SVGs without unused filters/gradients; every current file carries an unused `<filter id="shadow">` and a duplicated `id="brass"`. IDs must be unique per file (prefix with the asset slug) so files can be inlined safely.

---

## A1 — Ledger paper texture (tables) — **Priority 1, unblocked**

The single confirmed-needed material from the last review, still not commissioned. Turns every data table into a lit page in the dark room ("Option B" — pending final owner confirmation, but spec it now).

| | |
|---|---|
| Purpose | Background material for all data tables and timeline ledgers (tier 4 in the review) |
| Look | Warm cream/tan parchment, visible paper fiber at close range, calm at row scale; a whisper of foxing at edges is welcome, no busy pattern |
| Color | `#e8dcc0`–`#d4c5a0` range |
| Format | Tileable WebP, no visible seam at 4× repeat |
| Size | 256×256 source, ≤60KB |
| File | `public/museum/textures/ledger-page.webp` |
| Also | A dark companion (deep umber leather, same spec) as `ledger-page-dark.webp` — fallback if the light version doesn't sit well in situ |

## A2 — Frame system v2 — **Priority 1, unblocked**

Replaces the one-size-fits-all `plaque-frame.svg` (which stays in place until these land). Two pieces:

**A2a — Artifact frame (tier 1, the only ornate frame on the site).**
- Ornate but *slim*: thin brass rails (rail ≈ 3–4px at render size, not the current 7–10px slab), corner-weighted ornament (rivets/rosettes at corners, near-plain rails between), subtle top-edge highlight as if lit from above.
- Must work as CSS `border-image`: uniform, cleanly sliceable margins; corners that survive `stretch` on the edges; supply viewBox + recommended slice values in the delivery note.
- File: `public/museum/chrome/artifact-frame.svg`, ≤8KB.

**A2b — Case hairline corner set (tier 2, the default card).**
- Optional garnish over a plain CSS 1px brass border: four small corner marks (bracket/rivet, ~10×10 units) usable as a border-image or four positioned backgrounds. Extremely quiet — visible on inspection, invisible at a glance.
- File: `public/museum/chrome/case-corner.svg`, ≤2KB.

## A3 — Room backdrops, re-lit (×9, + 1 variant) — **Priority 2, needs owner sign-off (review Q2/Q5)**

Keep each room's existing composition and palette family; change the *lighting*. Current files average ~90% near-black canvas; the theme is "lit properly."

Targets for every room:
- Light pools reach the mid-frame, not just the top corners; ambient floor roughly 3× brighter than current; key light is warm white `#fff6e0`, not orange-brown.
- Empty center preserved (content overlays it), but the center should read as *lit wall*, not void.
- Format/size unchanged: 2200×640 WebP, ≤60KB each, same filenames (drop-in replacements).

Per-room light signatures (so the nine rooms stop being interchangeable):

| File | Room / page | Signature |
|---|---|---|
| `trophy-room.webp` | Champions | Case downlights, strongest sparkle on brass; the "hero" room |
| `history-corridor.webp` | League History | A runway of ceiling pools receding to depth |
| `chronicle-vault.webp` | Timeline | Slanted archival skylight, dust motes in the beam |
| `portrait-gallery.webp` | Managers | Picture lights over each frame — **and fill the frames**: dark painterly manager-silhouette suggestions, not empty gilt (current file reads "abandoned museum") |
| `dynasty-wing.webp` | Franchises | Banner-lit, columnar, grander scale |
| `war-room.webp` | Draft | Green-gold desk-lamp glow, map board lit hot |
| `the-vault.webp` | Keepers | Interior glow spilling *out* of the open vault door |
| `the-arena.webp` | Rivalries | **Red-orange heat** (the undertone specced in round 3 that shipped amber) — rim light, ~15–20% of canvas warm-red |
| `archive-library.webp` | Seasons | Multiple reading lamps, warmest and coziest room |

**A3b — Home hero scene:** re-lit `trophy-case-side-panels.webp`, redelivered at the standard 2200×640 so Home matches every other room's scale. File: `public/museum/rooms/entrance-hall.webp` (it's a room; it should live with the rooms).

## A4 — Spotlight cone overlay — **Priority 2, unblocked**

A single soft light-cone/pool overlay for tier-1 artifacts (champion card, featured timeline events): warm white radial falling from above, transparent background, very soft edges.
- Format: WebP or PNG with alpha, ~800×600, ≤30KB. File: `public/museum/chrome/spotlight.webp`.
- (If A3 lands well this may end up CSS-only; commission it cheap, treat as experiment.)

## A5 — Nameplate wordmark + monogram — **Priority 1 once the name is confirmed (review Q1)**

The site currently has no designed mark at all (the existing `wordmark.svg` is orphaned and contains raw placeholder text). Assuming the league name is confirmed (likely literally *"{insert witty name here}"* — if so, design it as the deliberate joke: pristine engraved brass plaque, perfectly serious museum typography, absurd text):

- **A5a Nameplate:** engraved-brass horizontal wordmark for nav and hero. Lettering as outlined paths (Bebas-compatible engraving style), subtle bevel/highlight, no drop shadows baked in. SVG, ≤10KB, `public/museum/chrome/nameplate.svg` + a compact nav-height variant `nameplate-nav.svg`.
- **A5b Monogram:** a stamp-scale mark (initials or "Est. 2001" roundel) for favicon, footer, loading states, section dividers. Must read at 16px. SVG ≤4KB, `public/museum/chrome/monogram.svg`, plus 32/180/512 PNG renders for favicons.

## A6 — Medallion & badge small-size variants — **Priority 3, unblocked**

The 24 manager medallions + 12 franchise badges are good at 40px+ but become identical dark coins at table-cell size (the ring of manager color is ~4% of the area).

- **A6a:** For each manager: a simplified small variant — manager accent color as the disc fill, sigil linework in navy or brass, no inner rings. Same viewBox, `manager-{slug}-sm.svg`. Legible at 16px; test against `#0f1b2d`.
- **A6b:** Franchise badges: replace Arial "F01" text with outlined numerals; same for position icons ("QB" etc.).
- **A6c:** While touching every file: strip unused shadow filters, de-duplicate/prefix gradient IDs (global rule 2).

## A7 — Wall tile v2 — **Priority 3, unblocked**

`gallery-wall-tile.webp` is functionally invisible (near-black pinstripe). Wanted: a *barely* warmer fabric/plaster wall material — visible as texture when looked for, silent otherwise. Think dark navy wool or dyed linen with thread-level variation.
- Tileable WebP, 256×256, ≤40KB, `public/museum/textures/gallery-wall-v2.webp`. (Old file retired on landing; `navy-walnut-panel.png` stays — it's live in the nav.)

## A8 — Object photography, gold-duotone set — **Priority: opportunistic (review Q4)**

Only if real league artifacts exist (trophy, draft board, old printouts, league documents). 6–10 photos treated as gold-duotone engravings (navy shadows, brass highlights) for the Home exhibit grid and season-chapter headers. Square crops, 800×800 WebP, ≤80KB each, `public/museum/objects/{slug}.webp`. This is the highest-persona-per-pixel item on the list if the source material exists — a real trophy beats any generated room.

---

## Priority summary

All owner decisions are in (2026-08-20): league name confirmed as literally *"{insert witty name here}"* — design A5 as the deliberate joke; night-gallery lighting and full room regeneration approved for A3; parchment Option B confirmed for A1; A8 is limited to a handful of existing draft-day photos.

**Delivery status (2026-08-21): A1, A3 (all ten rooms incl. entrance hall), A4, and A7 delivered, QA'd (size ceilings, dimensions, alpha, Arena heat, filled portrait frames all verified), and live.** The parchment table material and ink recolor are implemented; the old wall tile and hero texture are retired.

| Item | Status |
|---|---|
| A1 ledger paper | ✅ Delivered & live (light version in use; `-dark` kept as fallback) |
| A2 frame system (artifact frame v2, case corners) | ⬜ **Still needed** — tier-1 cards still use the original chunky `plaque-frame.svg` |
| A3 re-lit rooms | ✅ Delivered & live, all ten |
| A4 spotlight | ✅ Delivered & live over the reigning champion |
| A5 nameplate + monogram | ⬜ **Still needed** — highest-value remaining item; name is confirmed |
| A6 small medallions / de-Arial pass | ⬜ Still needed (batch when convenient) |
| A7 wall tile v2 | ✅ Delivered & live |
| A8 object photos | ⬜ Blocked on owner sourcing draft-day photos |

Delivery QA (same bar as previous rounds): tile seams checked at 4× repeat, size ceilings enforced, `grep` for `font-family` and unused `id=` in every SVG before wiring in.
