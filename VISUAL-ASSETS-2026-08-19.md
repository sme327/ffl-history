# Visual Assets — 2026-08-19

**Single consolidated asset document** — supersedes three earlier dated briefs from today (the original icon/medallion/badge inventory, its round-2 revision brief, and the room-backgrounds brief). All three are complete, delivered, and live; their content is condensed into §2 below rather than kept as three separate historical documents. The one thing actually still needed — a new texture — is specified in full in §3.

For the itemized file-by-file inventory of what's in `public/museum/` today, see `public/museum/README.md`. This document is the design history and the forward-looking brief; that one is the folder manifest.

---

## 1. Status: the re-skin's asset system is complete and live

Every asset commissioned this session shipped, was QA'd against its brief before being wired in, and is verified live on `iwnh.sme327.com`:

- 24 manager sigil medallions, 12 franchise badges, 4 era medallions, 15 timeline event icons, 6 exhibit icons, 6 position icons — all real SVG vector art, zero OS emoji-font dependency.
- 7 chrome pieces (wordmark, footer plaque, plaque-frame, dividers, ticks) — `plaque-frame.svg` in particular is now the single shared frame used on every card *and* every table on the site via CSS `border-image`.
- 9 room backdrops (one per section) plus a shared tileable wall texture — fixed-position backgrounds, confirmed via real scroll simulation to stay visible for a page's entire length, not just its first screenful.

Total footprint: ~90 files, all referenced from code, nothing orphaned.

---

## 2. History, condensed

Three commissioning rounds happened today. Worth recording briefly why, since it explains two items still open (§4):

1. **Round 1 — icons, medallions, badges.** First delivery used a brass-ring-plus-emoji-character template rather than real engraved line art — didn't solve the cross-platform emoji-inconsistency problem the whole exercise existed to fix. Caught in QA before wiring anything in.
2. **Round 2 — the correction.** Redelivered as real vector line art (a bee, a crown, a beer stein, etc., matching each manager's existing sigil), verified with `grep -rl "Emoji"` returning zero files. Also fixed two manager-sigil duplicate pairs and compressed the hero texture from 1.4MB to 12KB.
3. **Round 3 — room backgrounds.** Nine distinct scenes commissioned and delivered correctly on the first pass — QA found only two minor items (below). The *implementation* took two attempts: the first boxed each photo into a small rounded card near the page top, which read as "a picture in a title box," not an actual place. Corrected to `position: fixed`, shown at true aspect ratio, confirmed with a real `window.scrollTo()` test to stay behind the content for the whole scroll.

---

## 3. Open items carried forward — small, not blocking

- **The Arena** (`the-arena.webp`) was supposed to carry a red-orange undertone distinguishing it from the other rooms' amber palette. It shipped in the same amber as everywhere else. Cosmetic; revisit if you want the Rivalries page to feel more visually "hot" than the rest of the site.
- **`gallery-wall-tile.webp` vs. `navy-walnut-panel.png`** — the newer tile was meant to be a refined pass on the older one; whether it's meaningfully distinct was never confirmed side-by-side. Both are still in `public/museum/textures/`; low stakes either way since the current one passed its tiling-seam test.

---

## 4. What's actually needed now: a distinct material for tables

This is the one item from the post-re-skin review (`SITE-REVIEW-2026-08-19.md` §4d) that requires a new asset rather than more CSS.

**The problem it solves:** tables are now framed with the exact same `border-image` brass display-case treatment as every card on the site. That's a real fix for legibility and consistency, but it means a 195-row data table and a single championship plaque currently use identical material. A real museum doesn't do this — a display case is glass and brass; a reading room's ledger is paper and worn leather. Giving tables their own calmer material is a curatorial statement, not decoration: it tells a reader "this is the reference archive" versus "this is a treasured object," which is exactly the distinction Champions vs. History vs. Keeper Hall are already making at the *room* level.

### Two directions — pick one before this gets built

**Option A — Dark ledger (lower risk, smaller change).** Keep the current dark navy/brass palette family, but replace the table's fill material with something that reads as leather-bound or aged-dark-paper rather than lit brass — a subtle dark texture (deep brown/oxblood leather grain, or a very dark aged-paper tone) instead of the warm gold-tinted gradient cards use. No table text recoloring needed; `var(--text)`/`var(--muted)`/`var(--gold)` all still work on a dark fill.

**Option B — Lit page (bigger change, more dramatic, more authentic).** A genuinely light, warm parchment/ledger-paper texture — cream/tan, visible grain, maybe a whisper of foxing — so a table reads as an actual open ledger book lit from above, a bright page in the dark room. This is the more striking, more "real museum" version — a lit reading-room lectern, not just a different-colored box — but it requires a follow-up implementation pass to recolor table text to dark ink tones specifically for that context, since the current light-on-dark palette would be illegible on a light background.

**Recommendation: Option B**, if you're willing to accept the small follow-up implementation cost — it's the version that actually delivers "distinct place, not just a different frame," which is the whole point of this item. Option A is the safe fallback if you'd rather not touch table text colors right now.

### Asset spec (either option)

| | |
|---|---|
| **Format** | Tileable PNG or WebP, no visible seam at 4× repeat (same test the wall tile passed) |
| **Size** | Small — target 256×256px source, similar scale to the existing wall textures |
| **File ceiling** | ≤60KB, matching the budget already used for `navy-walnut-panel.png`/`gallery-wall-tile.webp` |
| **Texture** | Visible paper/leather fiber grain at close range, calm and unpatterned at table-row scale — should read as *material*, not as a busy repeating pattern |
| **Option A color** | Deep oxblood or dark umber leather tone, or near-black aged paper — stays within the site's existing dark palette family |
| **Option B color** | Warm cream/tan parchment, `#e8dcc0`–`#d4c5a0` range (matching the "aged parchment" reference already used for `.identity` styling elsewhere in the design system) |
| **Naming** | `public/museum/textures/ledger-page.webp` (or `-dark.webp` for Option A) |

### Do you need to provide a mockup?

Not required — the same "write a specific, detailed text brief" approach has worked for every asset this session, including the much bigger 9-room commission. Worth doing anyway *only* if you're unsure between Option A and B — a single quick mockup of Option B specifically (the bigger design bet) would confirm it reads as "museum reading room" rather than "clashing light box in a dark page" before committing to the text-recoloring follow-up work.

---

## 5. Delivery conventions (unchanged, for reference)

- SVG for anything vector, single-color where possible via `currentColor` so hover/theme states don't need separate files.
- WebP for anything photographic or textured, with an explicit size ceiling stated up front — the one time this was skipped (the original hero texture), it shipped as a 1.4MB PNG and had to be redone.
- Naming matches the site's `slugify()` output so a future engineer can map an entity to its asset file programmatically rather than hand-wiring imports.
- Every color used across the asset system already exists as a named value in `utils/data.py`/`utils/narratives.py` — hand that source to whoever's building new assets rather than re-picking swatches by eye.
