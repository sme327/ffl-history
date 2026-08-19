# Visual Asset Inventory — "Museum, Lit Properly"

Every graphic/visual asset needed to re-skin all 15 routes of **{insert witty name here} Museum** in the chosen direction: a lit trophy-case aesthetic — brass plaques, spotlight lighting, engraved medallions — evolving the current navy/gold system rather than replacing it. Grounded in a full pass over `app/`, `lib/data.ts`, `utils/data.py`, and `utils/narratives.py`, not just the Home page mockup.

Companion to `SITE-REVIEW-2026-08-19.md` and `SKIN-CONCEPTS-2026-08-19.md`.

---

## 1. Art direction reference

One page, so every asset the graphics team produces matches without a chat thread to reconstruct it from.

| | |
|---|---|
| **Materials** | Brushed brass / bronze (engraved relief, not flat fill), dark walnut wood grain, deep navy wall, warm parchment (used sparingly, for Playfair Display pull-quotes only) |
| **Palette** | `#0a1420` bg · `#14202f` surface · brass `#c9a24b` · warm spotlight highlight `#fff6e0` · existing `--muted`/`--faint` unchanged |
| **Lighting** | A single warm spotlight per hero moment — radial gradient, soft falloff, never a hard-edged pool. No lighting on secondary/list content; save it for one focal point per page. |
| **Line work** | Engraved (inset/debossed), not printed. Icons should read as if cut into metal — subtle inner shadow + highlight edge, not a flat glyph. |
| **Typography carried over unchanged** | Bebas Neue (display), Inter (body). Playfair Display — currently imported and unused (site review S13) — gets its first real job here: plaque quotes and lore pull-quotes only, nowhere else. |
| **What does NOT change** | The brand name, the question-framed eyebrows, the cross-linking, the restrained no-client-JS approach. This is a materials/lighting pass, not a content or IA rewrite. |

---

## 2. Site-wide chrome (needed on every page)

| Asset | Description | Format | Priority |
|---|---|---|---|
| Wordmark lockup | "{insert witty name here}" set in the engraved-brass treatment for the nav bar — small, so detail must hold at ~24px height | SVG | Tier 1 |
| Nav active-state mark | Small brass underline/tick for the current section (site review S11 — nav currently has no active state) | CSS + tiny SVG tick | Tier 1 |
| Page background material | Dark navy/walnut panel texture, tileable, subtle (3–5% opacity over `--bg`) | Tileable WebP/PNG, ≤40KB | Tier 1 |
| Spotlight/vignette gradient | The hero lighting effect | **CSS only — no asset file.** Radial gradient token, not an image. | Tier 1 |
| Divider cap ornament | Small rivet/fleur mark at each end of the existing `.divider` hairline | SVG (currentColor, tintable) | Tier 2 |
| Footer plaque | New site-wide footer (site review S10 recommended adding one) — small brass plate: "Est. 2001 · A private collection · Report a misfiled exhibit →" | SVG frame + CSS | Tier 1 |
| Trophy-case side panels | The flanking bookshelf/pillar imagery from the Home mockup — helmet, trophy, books, football in lit alcoves | SVG/WebP, **desktop/tablet only** — see §6, drop entirely below ~900px rather than shrink | Tier 3 (polish) |
| Favicon | Already football-themed (`Use football favicon across museum pages`, current commit) | **No change needed** | — |

---

## 3. Reusable component assets

These map directly to existing CSS classes in `app/globals.css` — one asset each covers every page that uses the component, not a per-page rebuild.

| Component class | Where it's used today | New asset needed |
|---|---|---|
| `.plaque` / `.champion-card` | Reigning champion (Home, every Season page), manager Hall of Fame plaque, franchise "Story of the Franchise," rivalry plaques | **One** brass nameplate frame — inset border, corner rivets, engraved-texture fill. Built as a reusable CSS/SVG frame, not redrawn per page. |
| `.card` / `.card-feature` | Every content card, all 15 routes (dozens of instances per page) | A subtle raised-object treatment: 1px inner highlight + soft drop shadow. **CSS only**, no image asset — this is the "lit properly" fix from the review, achieved without new files. |
| `.metric` / `.metric-value` | Every stat strip, all 15 routes | Engraved numeral backing — a thin brass baseline rule under each number. CSS + one small SVG divider glyph (the "◆" diamond already used in the mockups). |
| `.nav-card` (Home exhibit grid) | Home only, 6 tiles | See §4 — Exhibit Icon Set |
| `.chron-row` / `.year-pill` | Championship Timeline (Champions page), Keeper Hall timelines, Franchise Milestones | No new asset — existing pill styling reads fine in brass/gold, just recolor via existing CSS variables |
| `.matchup` / bracket | Every Season page with a playoff bracket | Brass corner-frame treatment per matchup box, winner row gets a small embossed check/tick. CSS + one tiny SVG tick mark. |
| `.event` / `.event-major` | Timeline page (all 160+ events) | See §4 — Event-Type Icon Set |
| Charts (`app/components/charts.tsx`) | League History (scoring evolution, title bars), Draft Center (position share/trends), Keeper Hall (position share) | **No new image assets** — these are server-rendered SVG in code. Needs a re-theme spec instead: brass/gold line color, rivet-dot markers instead of plain circles, museum palette instead of the current bright chart-color set. Hand this to whoever touches `charts.tsx`, not the graphics team. |

---

## 4. Icon & medallion sets (the real content of this project)

This is where the site's existing personality already lives — 24 managers, 4 eras, 15 timeline event types all already have an assigned emoji and, mostly, a color. The job here is translating each into an engraved brass medallion, not inventing new iconography from scratch.

### 4a. Exhibit grid icons — 6, Home page

Replace the emoji currently standing in for each destination:

| Exhibit | Current emoji | Route |
|---|---|---|
| Trophy Room | 🏆 | `/champions` |
| Timeline | 📅 | `/timeline` |
| Keeper Hall | 🔑 | `/keepers` |
| Draft Legends | 📋 | `/draft` |
| Manager Files | 👤 | `/managers` |
| Franchise Files | 🏟️ | `/franchises` |

**Tier 1** — these six are the highest-visibility icons on the site (Home page, first thing every visitor sees) and unlock the whole "Explore the Exhibits" section.

### 4b. League Era medallions — 4, History + Timeline pages

Already defined in `utils/narratives.py` (`LEAGUE_ERAS`) with names, colors, and emoji — translate each 1:1:

| Era | Years | Existing color | Existing emoji |
|---|---|---|---|
| The Founding Era | 2001–2004 | `#D4AF37` (gold) | 🏛️ |
| The Workhorse Era | 2005–2009 | `#22C55E` (green) | 🐎 |
| The Keeper Revolution | 2010–2015 | `#A78BFA` (purple) | 🔑 |
| The Modern Era | 2016–Present | `#3B82F6` (blue) | ⚡ |

Build as brass medallions with a thin tinted ring in each era's existing color, so the color-coding readers already associate with each era carries over. **Tier 2.**

### 4c. Timeline event-type icon set — 15, Timeline page (and anywhere events surface)

Already defined in `utils/narratives.py` (`TIMELINE_EVENT_META`) with a color per type:

| Type | Emoji | Color | Type | Emoji | Color |
|---|---|---|---|---|---|
| championship | 🏆 | `#D4AF37` | collapse | 📉 | `#EF4444` |
| dynasty | 👑 | `#F5C518` | rivalry | ⚔️ | `#FB923C` |
| runner_up | 🥈 | `#A7B0BC` | draft | 📋 | `#818CF8` |
| steward_change | 🔄 | `#60A5FA` | keeper | 🔒 | `#A78BFA` |
| record | ⚡ | `#F59E0B` | rule_change | 📜 | `#9CA3AF` |
| milestone | 🏛️ | `#34D399` | alumni | 👤 | `#6B7280` |
| heartbreak | 💔 | `#F87171` | note | 📝 | `#9CA3AF` |
| breakthrough | 🎯 | `#10B981` | | | |

This is the single largest icon set (15 marks) but also the most repeated across the site — every one of the 160+ timeline events uses one. **Tier 2**, and worth doing right: this is the set readers will see most often.

### 4d. Manager sigil medallions — 24, Managers/Franchises/Keeper Hall/Draft/Rivalries

Every manager already has a personal emoji sigil, defined in `MANAGER_COLORS`/`MANAGER_EMOJI` in `utils/data.py` — this is existing brand IP, not a blank slate:

| Manager | Sigil | Manager | Sigil | Manager | Sigil |
|---|---|---|---|---|---|
| Shawn | 🐝 | Douglas | ⚙️ | Byron | 🏛️ |
| Fadi | 👑 | Jeff | ⚽ | Dan | 📖 |
| Brian Clark | 🍺 | Eric | ⛳ | Dale | 🌪️ |
| Kevin O'Boyle | 🍺 | Jamie | 😇 | Bryan Kearney | 💪 |
| Kevin Swanson | 🧔 | Mike | 🍻 | BV | ❓ |
| Thomas | 🐻 | Joe Tyszko | 🌽 | Adam | 🎯 |
| Evan | 🎉 | Robby | 🎸 | Nick Blaettler | 🐱 |
| Steve Swanson | 🐻 | Rob | ⚔️ | | |

**This is the asset that most directly serves the site's actual purpose.** It sidesteps the whole photography question raised earlier — no real photos needed, no stock models, no fabricated likenesses — and it's more personal than a generic avatar system would be, because these sigils presumably already mean something to the league (inside jokes, nicknames). Translate each into a brass medallion in the manager's existing `MANAGER_COLORS` accent, replacing the emoji everywhere it currently appears (profile hero, championship timeline rows, franchise steward cards, executioner/victim lists on Rivalries, keeper DNA cards).

**Flag before production:** two pairs currently share an emoji — Brian Clark and Kevin O'Boyle both use 🍺, and Thomas and Steve Swanson both use 🐻. Worth a quick decision on whether that's intentional (a shared joke) or should get a secondary distinguishing mark before 24 unique medallions get commissioned as 22 unique + 2 duplicated pairs.

**Tier 3** — highest individual asset count (24 items) but each is reused many times across the site, so it's high-leverage once done. Sequence after 4a/4b/4c since those unlock more pages per asset produced.

### 4e. Franchise badges — 12, new asset category (Franchises, Rivalries)

**Added 2026-08-19** — a category the original inventory didn't cover. The gap it fills is real: right now, the only thing that distinguishes F01 from F07 on `/franchises`, `/rivalries`' "Franchise Rivalries" table, or anywhere else a franchise ID appears is the text string itself (`F01`, `F02`...). There is no visual identity for the *seat* — only for the person currently sitting in it. That's worth fixing, because it's a distinction `CLAUDE.md` itself draws explicitly: **"Franchises are not managers. Franchises are institutions."**

**The core design decision: a franchise badge must not change when its steward changes.** F04 has had five different stewards (Dale → Joe Tyszko → Nick Blaettler → Bryan Kearney → Eric). If the badge were built from whoever currently holds the seat, it would need to be redesigned four times in the site's history and would tell readers nothing about the seat's continuity — only about its current occupant, which the manager sigil already covers. The badge should instead be anchored to the franchise's **founding steward** — the person who established the seat in 2001, 2002, or 2003 — so the crest represents the institution's origin and stays fixed forever, the same way a real franchise's identity outlives any single owner or coach.

**One color-system constraint worth flagging before this gets designed:** `MANAGER_COLORS` already assigns 24 distinct, fairly saturated hues across the whole color wheel to individual managers (§4d) — that's close to the practical ceiling for how many hues a reader can reliably tell apart at a glance. Laying a *second*, unrelated 12-color system on top of that for franchises — using hue alone — risks a reader not being able to tell whether a colored ring means "this is Fadi's personal color" or "this is F06's franchise color," since both would be competing for the same visual channel. **Recommendation: keep franchise badges in a single consistent metal (brass, matching the site's material system) and differentiate by emblem, numeral, and shape/border — not by a second rainbow of hues.** Reserve saturated color exclusively for the manager-identity system it already belongs to.

**What makes each of the 12 badges unique:**

1. **Emblem** — derived from the founding steward's own sigil (see table below), rendered in the same engraved-brass style as the manager medallions, but set inside a badge frame rather than a plain circle, so it reads as "crest," not "person."
2. **Numeral** — the franchise ID (F01–F12) incorporated directly into the badge, e.g. as a small engraved plate at the base, the way a stadium banner shows a retired number.
3. **Frame shape by founding cohort** — a subtle structural cue tying each badge to when its seat entered the league:
   - **F01–F09** (2001, founding members): a round medallion frame.
   - **F10–F11** (2002 expansion): a shield frame.
   - **F12** (2003 expansion): a hexagonal frame — the seat that completed the league at 12 teams.

| Franchise | Established | Founding steward | Founding sigil | Full lineage | Current steward | Titles |
|---|---|---|---|---|---|---|
| F01 | 2001 | Adam | 🎯 | Adam → Douglas (2015) | Douglas | — |
| F02 | 2001 | Brian Clark | 🍺 | Brian Clark (unbroken) | Brian Clark | — |
| F03 | 2001 | Byron | 🏛️ | Byron → Dominic (2005) | Dominic | — |
| F04 | 2001 | Dale | 🌪️ | Dale → Joe Tyszko (2003) → Nick Blaettler (2010) → Bryan Kearney (2021) → Eric (2023) | Eric | — |
| F05 | 2001 | Dan | 📖 | Dan → Evan (2004) | Evan | — |
| F06 | 2001 | Fadi | 👑 | Fadi (unbroken) | Fadi | — |
| F07 | 2001 | Jamie | 😇 | Jamie → Mike (2006) → BV (2010) → Robby (2011) → Jeff (2017) | Jeff | — |
| F08 | 2001 | Rob | ⚔️ | Rob → Steve Swanson (2007) | Steve Swanson | — |
| F09 | 2001 | Shawn | 🐝 | Shawn (unbroken) | Shawn | — |
| F10 | 2002 | Kevin O'Boyle | 🍺 | Kevin O'Boyle (unbroken) | Kevin O'Boyle | — |
| F11 | 2002 | Kevin Swanson | 🧔 | Kevin Swanson (unbroken) | Kevin Swanson | — |
| F12 | 2003 | Thomas | 🐻 | Thomas/Tom Masterson, joined as "Tupa" (unbroken) | Thomas | — |

*(Titles column left blank here — pull current championship counts per franchise from `franchiseIndex`/`franchiseProfile` in `lib/data.ts` before finalizing, since those change season to season.)*

**One more duplicate to flag, distinct from the manager-sigil duplicates in §4d:** F02's and F10's founding stewards — Brian Clark and Kevin O'Boyle — share the 🍺 sigil. Since these badges are keyed to *founding* steward specifically (not current), this is a fresh collision even after resolving the §4d duplicates, and needs its own decision: differentiate via the frame shape (F02 is a round 2001 frame, F10 is a shield 2002 frame, so they're not fully identical) plus, if that's not enough, a secondary small mark on one of the two.

**Optional enhancement, not required:** a thin secondary ring in the *current* steward's personal `MANAGER_COLORS` hue, small enough to read as a detail rather than the badge's main identity — gives a reader who knows the sigil system a way to spot "oh, this seat changed hands" at a glance, without compromising the brass-only rule above. Worth prototyping once, not committing to blind.

Used on: `/franchises` (index grid), `/franchises/:id` (header), `/rivalries`' "Franchise Rivalries" table (currently the only place two franchise IDs appear side by side with zero visual distinction). **Tier 3** — sequence alongside manager sigils, since both are identity-system work and benefit from being designed in the same pass.

### 4f. Position icon set — 6, Draft Center + Keeper Hall

`POSITION_COLORS` is already defined (and currently duplicated verbatim in both `app/draft/page.tsx` and `app/keepers/page.tsx` — worth deduping into a shared constant when this ships, a code note more than a design one):

QB `#EF4444` · RB `#22C55E` · WR `#3B82F6` · TE `#F59E0B` · DEF `#8B5CF6` · K `#6B7280`

Currently rendered as plain colored `.pill` tags — functional, low visual risk. Optional small engraved glyphs (helmet-silhouette variants per position) would fit the material system but aren't load-bearing. **Tier 4 / optional polish.**

---

## 5. Page-by-page checklist

| Route | Hero/unique asset needed | Reused from §2–4 |
|---|---|---|
| `/` (Home) | Trophy-case side panels (desktop only) | Wordmark, plaque frame, stat plate, exhibit icons ×6, manager sigils (Legends row) |
| `/champions` | — | Plaque frame, stat plate, manager sigils, event icons (finals) |
| `/timeline` | — | Era medallions ×4, event-type icons ×15 (the whole page) |
| `/history` | — | Era medallions ×4, chart re-theme |
| `/seasons`, `/seasons/:year` | — | Plaque frame (champion card), bracket frame, manager sigils |
| `/managers`, `/managers/:slug` | — | Plaque frame, manager sigils, chart re-theme (season trends) |
| `/franchises`, `/franchises/:id` | — | Plaque frame, **franchise badges ×12**, manager sigils (stewards), event icons |
| `/draft` | — | Position icons (optional), manager sigils (drafters), chart re-theme |
| `/rivalries` | — | Manager sigils (executioners/victims), **franchise badges ×12** (Franchise Rivalries table), plaque frame (closest-loss callout) |
| `/keepers`, `/keepers/:manager` | — | Manager sigils, position icons (optional), chart re-theme |
| `/players/:slug` | — | Position pill (existing, no change) |

No route needs a bespoke one-off hero asset beyond what's already listed in §2–4 — the whole site runs on the reusable set. That's deliberate: it's what keeps this from becoming a 15-page illustration commission.

---

## 6. Mobile/responsive notes

Per the earlier discussion on this concept's mobile behavior:

- **Desktop/tablet-only, drop below ~900px rather than shrink:** trophy-case side panels (§2). This is the one piece of the concept that's inherently a wide-canvas trick.
- **Scales cleanly at any size, no special handling:** plaque frame, stat plate, all icon/medallion sets (SVG, vector), spotlight gradient (CSS).
- **Watch file weight on mobile:** any raster texture (wood grain, brass fill) should ship as compressed WebP, sized per breakpoint, and the page background texture in particular should stay under ~40KB — the site currently ships 484KB of JS total and loads instantly from a group-chat link on a phone; a heavy texture image is the one thing in this plan that could quietly undo that.

---

## 7. Delivery specs

- **Icons & medallions (§4a–4f):** SVG, single-color where possible using `currentColor` or a CSS-maskable fill, so hover/active states and dark/light variants don't require separate exported files. Target a consistent artboard size (suggest 64×64) so they drop into the existing `nav-card-icon`/`chron-mgr` sizing without per-instance scaling. Franchise badges (§4e) are the exception — they're a frame containing an emblem, not a single flat glyph, so treat them as small compositions (suggest a 96×96 or 128×128 artboard) rather than forcing them into the same box as the plain icons.
- **Plaque frame, stat plate, divider ornaments, footer plate (§2–3):** SVG or CSS-built (border-image / clip-path) in preference to raster where the shape allows — these repeat dozens of times per page and should stay cheap.
- **Textures (background panel, trophy-case renders):** WebP, tileable where applicable, compressed, with explicit size budgets per §6.
- **Naming/folder convention:** suggest `public/museum/icons/`, `public/museum/textures/`, `public/museum/medallions/manager-{slug}.svg`, `public/museum/badges/franchise-{id}.svg` — matching the site's existing `slugify()` convention so a future engineer can map a manager or franchise ID to their asset file programmatically rather than hand-wiring imports.
- **Color handoff:** every hex value referenced above already exists in `utils/data.py` / `utils/narratives.py` — hand the graphics team that source rather than re-transcribing swatches by hand, so a future palette tweak in code doesn't silently desync from the art files. Franchise badges are the one asset in this document with **no existing color source** — the brass-only/cohort-frame-shape approach in §4e is deliberately designed around that gap rather than inventing a new 12-color palette to fill it.

---

## 8. Build order

| Tier | Unlocks | Asset count |
|---|---|---|
| **1** | Home page + site-wide nav/footer/chrome | Wordmark, nav active-state, background texture, footer plate, plaque frame, stat plate, exhibit icons ×6 |
| **2** | Timeline + League History | Era medallions ×4, event-type icons ×15, divider ornaments |
| **3** | Managers, Franchises, Keeper Hall, Draft, Rivalries | Manager sigil medallions ×24 (resolve the §4d duplicate pair first) + franchise badges ×12 (resolve the §4e duplicate pair first) — design in the same pass, they share a visual language |
| **4 (polish)** | Full-site refinement | Trophy-case side panels (desktop), position icons, chart re-theme |

Tier 1 alone is enough to get a real, full-page prototype in front of you (site review's own suggestion was hero + champion card + stat strip — Tier 1 covers that and the full Home page). Tiers 2–3 are where the site's actual content — 25 years of eras, events, and specific people — starts carrying real weight in the new material system, which is the part worth not rushing.
