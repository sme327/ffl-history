# Museum visual assets

All imagery for the museum skin. Current design direction and the forward-looking commission list: `UI-VISUAL-REVIEW-2026-08-20.md` and `ASSETS-NEEDED-2026-08-20.md` at the repo root. Historical specs: `VISUAL-ASSETS-2026-08-19.md`.

## Inventory

| Folder | Contents | Count |
|---|---|---|
| `badges/` | Franchise seat crests (F01–F12), keyed to each seat's founding steward | 12 |
| `chrome/` | Site furniture: `artifact-frame.svg` (the tier-1 `border-image`, rendered at 10px — its predecessor `plaque-frame.svg` is retired but kept), `case-corner.svg` (accepted, not yet wired), divider caps, ticks, `spotlight.webp` (the light-cone above the reigning champion), the **A5 nameplates** (`nameplate.svg` hero, `nameplate-nav.svg` nav) and **monogram** (`monogram.svg` + 32/180/512 PNG favicons). `wordmark.svg` and `footer-plaque.svg` remain retired | 16 |
| `icons/events/` | Timeline event-type icons (championship, heartbreak, keeper, etc.) | 15 |
| `icons/exhibits/` | Home page's 6 exhibit-grid icons | 6 |
| `icons/positions/` | QB/RB/WR/TE/DEF/K — vector helmet marks, no photo dependency | 6 |
| `medallions/eras/` | The four league era medallions (Founding, Workhorse, Keeper Revolution, Modern) | 4 |
| `medallions/managers/` | One sigil medallion per manager (`manager-{slug}.svg`), plus a small variant per manager (`manager-{slug}-sm.svg`: accent-filled disc, simplified sigil) for table cells and list rows ≤20px — `managerIconPath()` / `managerIconSmPath()` in `lib/data.ts` | 48 |
| `rooms/` | The distinct background scene for each section (including Home's `entrance-hall.webp`), rendered as a fixed full-width backdrop behind that section's pages. All ten are the **re-lit A3 delivery** (2026-08-21): warm-white light pools, per-room signatures, the Arena's red heat, filled portrait frames | 10 |
| `textures/` | Site-wide tiled wall (`gallery-wall-v2.webp`), the nav's wood panel (`navy-walnut-panel.png` — **live in the nav**, not a leftover), and the table parchment (`ledger-page.webp`, plus the unused dark fallback `ledger-page-dark.webp`) | 4 |

## Conventions

- **Naming:** `manager-{slug}.svg` and `franchise-{id}.svg` match the site's existing `slugify()` output, so a manager or franchise can be mapped to its asset file programmatically (see `managerIconPath()`/`franchiseBadgePath()`/`eventIconPath()`/`eraIconPath()` in `lib/data.ts`).
- **Format:** SVG for everything vector, WebP for photographic content (rooms, textures), each under the size ceilings in the assets brief.
- **No `currentColor` in files consumed as `<img>` or CSS `background-image`** — it can't inherit there and silently renders black (this bit `divider-cap.svg` and `nav-active-tick.svg`, both now hard-coded brass). Reserve `currentColor` for SVG that is inlined in JSX.
- **No `<text>` with system font-families and no unused defs** in new deliveries — see "global conventions" in `ASSETS-NEEDED-2026-08-20.md` (existing files get cleaned in the A6 pass).
- **Color source of truth:** hex values for manager/era/event colors are defined in `utils/data.py` / `utils/narratives.py`; the brass ramp is `#fff0a8 → #c9a24b → #7f5b18`, warm light `#fff6e0`.
