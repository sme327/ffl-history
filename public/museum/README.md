# Museum visual assets

All imagery for the "Museum, Lit Properly" re-skin. Every file here is referenced from `app/globals.css` or inline in a page component — nothing in this folder is unused. Full history and specs: `VISUAL-ASSETS-2026-08-19.md` at the repo root.

## Inventory

| Folder | Contents | Count |
|---|---|---|
| `badges/` | Franchise seat crests (F01–F12), keyed to each seat's founding steward | 12 |
| `chrome/` | Site-wide furniture: nav wordmark, footer plaque, plaque-frame (the `border-image` used on every card/table), dividers, ticks | 7 |
| `icons/events/` | Timeline event-type icons (championship, heartbreak, keeper, etc.) | 15 |
| `icons/exhibits/` | Home page's 6 exhibit-grid icons | 6 |
| `icons/positions/` | QB/RB/WR/TE/DEF/K — vector helmet marks, no photo dependency | 6 |
| `medallions/eras/` | The four league era medallions (Founding, Workhorse, Keeper Revolution, Modern) | 4 |
| `medallions/managers/` | One sigil medallion per manager, `manager-{slug}.svg` | 24 |
| `rooms/` | The distinct background scene for each section (Trophy Room, History Corridor, etc.), rendered as a fixed full-width backdrop behind that section's pages | 9 |
| `textures/` | Site-wide tiled wall (`gallery-wall-tile.webp`), Home's hero scene (`trophy-case-side-panels.webp`), and the original wall tile it superseded (`navy-walnut-panel.png`, kept for reference) | 3 |

## Conventions

- **Naming:** `manager-{slug}.svg` and `franchise-{id}.svg` match the site's existing `slugify()` output, so a manager or franchise can be mapped to its asset file programmatically (see `managerIconPath()`/`franchiseBadgePath()`/`eventIconPath()`/`eraIconPath()` in `lib/data.ts`).
- **Format:** SVG for everything vector (icons, medallions, badges, chrome) — no OS emoji-font dependency anywhere in this tree. WebP for photographic content (rooms, textures), each under the size ceilings set in `VISUAL-ASSETS-2026-08-19.md`.
- **Color source of truth:** every hex value used across this set (manager colors, era colors, event colors) is defined once in `utils/data.py` / `utils/narratives.py`, not re-picked by eye — a future palette change in code should stay in sync with the art automatically.
