# UI / Visual Review — 2026-08-20

**Status (2026-08-20, same day):** all five §13 questions answered by the owner — the league *is* literally named "{insert witty name here}", night-gallery lighting chosen, parchment (Option B) confirmed, only a few draft-day photos exist, room regeneration approved. **Phase 1 (§12) is implemented and verified** against screenshots of Home, Champions, Rivalries, and Timeline: material tiers live, gold re-rationed, warm-white lighting, typography pass (Source Sans 3 body, Playfair on lore/taglines), emoji purge completed, chrome bugs fixed, plus one item found during verification — the Dynasties grid rendered seven ornate frames at once and now features only the top dynasty. Phases 2–3 are blocked on the `ASSETS-NEEDED-2026-08-20.md` deliveries; Phase 4 is open.

Scope: every visual layer of the site, reviewed piece by piece — background imagery, surface/frame system, lighting, typography, color, iconography, chrome, charts, layout rhythm — against the chosen theme, **"The Museum, Lit Properly"** (`SKIN-CONCEPTS-2026-08-19.md` §1). Grounded in the actual asset files in `public/museum/` (all 9 rooms viewed, chrome/medallion/badge SVG sources read) and the live CSS (`app/globals.css`).

Companion doc: `ASSETS-NEEDED-2026-08-20.md` — the graphics-team brief for everything below that needs new or revised art.

---

## 1. The verdict: the theme drifted from "lit properly" to "gilded everywhere"

The concept spec was explicit about restraint:

> *"a thin inset border, a subtle engraved-texture background (3–5% opacity, not a photo), corner rivets as small decorative marks"* … *"warm spotlight highlight `#fff6e0` used sparingly as a literal light pool behind hero elements"*

What shipped instead:

- The same ornate brass `plaque-frame.svg` is applied via `border-image` to **nine different CSS rules** — every card, every stat tile, every nav card, every table wrapper, every timeline card, every timeline ledger — at 7px, 9px, and 10px widths. A four-number stat tile and the reigning champion's trophy case wear the same heavy gold frame.
- The "lighting" is one 16%-opacity radial pool tiled every 900px, plus text-shadows on headings. The room backdrops themselves are **near-black** (see §3), and the page scrim darkens to 92% opacity by the bottom of every page. The site is not lit; it's dark with gold trim.

These two facts compound each other. Because the environment is so dark, the gold frames are the brightest thing on every screen, so they *become* the design. In a real museum, light carries the hierarchy and frames are rare (they mark the artifacts); here frames are universal and light is scarce — exactly inverted.

**The fix is not "remove the gold."** The brass/navy language is right for the brief. The fix is a *material hierarchy* (frames become rare and meaningful) and a *real lighting pass* (warmth and luminance come from light, not from gilding). Both are detailed in §12.

---

## 2. Surface & frame system (`.card`, `.scroll-x`, `.champion-card`, timeline)

**What's there:** one material — top-lit navy gradient + `plaque-frame.svg` border-image + drop shadow — reused for every surface on the site. Frame width (7/9/10px) is the only hierarchy signal.

**Problems**

- **Frame inflation.** When everything is framed, nothing is. The champion card's 10px frame vs. a stat tile's 7px frame is not a legible difference; both read "big gold frame."
- **The frame art itself is chunky.** `plaque-frame.svg` is a filled brass slab with rivets, sliced at 29%/9%. At 7px on a small card it renders as a thick mustard band, closer to a picture-frame-store sample than museum brasswork. Museum casework is thin: hairline brass rails, glass, shadow.
- **Tables in trophy frames.** Framing `.scroll-x` fixed the "unstyled debug table" seam (round-2 review §2, correctly), but a 195-row matchup ledger in the same ornate case as a championship plaque is a category error the earlier review already named (§4): *display case ≠ reading-room ledger*. The Option-B parchment material was specced (`VISUAL-ASSETS-2026-08-19.md` §4) and never commissioned — it's still the right call.

**Direction — four material tiers, replacing one-frame-fits-all:**

| Tier | Content | Material |
|---|---|---|
| 1. Framed artifact (rare — a handful per page max) | Reigning champion, featured timeline events, season champion, era medallion hero | Refined ornate frame (new art, slimmer than current), full spotlight halo |
| 2. Display case (default card) | Plaques, DNA cards, trivia, storylines | 1px brass hairline + glass top-highlight + shadow. **No border-image.** |
| 3. Wall label / plinth | Metric tiles, mini-champs, nav cards | **No frame at all.** Open on the wall: large numeral, thin brass baseline rule, letterpress label — museum wall-label typography (this is literally what the concept spec asked for) |
| 4. Ledger / archive | All data tables, timeline event ledgers | Parchment "lit page" material (Option B), dark-ink text, thin ruled lines, no brass frame |

Tier 3 is the biggest single de-gilding win: the home page alone currently renders ~13 framed boxes above the fold ~— metrics, recent champions, legends — that would all become open wall labels.

---

## 3. Background images — rooms and textures

All 9 room backdrops reviewed at full size. Craft quality is genuinely good (consistent palette, believable materials, correct empty-center composition for content overlay), and the `position: fixed` full-width implementation is the right architecture. But:

- **They are all nearly black.** Trophy Room, Archive Library, History Corridor, The Vault, War Room — measured visually, ~85–95% of each canvas sits near `#050a12`. Combined with the scrim (which reaches 92% black), on most screens the "room" is invisible except a faint glow at the very top. The theme's entire premise — *a lit space* — is not delivered by the imagery.
- **Same-y composition.** Every room is the same recipe: symmetrical dark-wood shelving at the edges, brass trophy, void in the middle. Nine rooms; one mood. The Arena was specced with a red-orange undertone to make Rivalries feel *hot* and shipped in the same amber as everything else (already logged in `VISUAL-ASSETS-2026-08-19.md` §3 — still open).
- **Portrait Gallery's frames are empty.** Rows of vacant gilt frames read as "abandoned museum," which is eerie rather than nostalgic — and it repeats the site's own problem (frames with nothing in them).
- **Textures:** `gallery-wall-tile.webp` is a near-black navy pinstripe — effectively invisible, contributing nothing but bytes. `navy-walnut-panel.png` is documented in `public/museum/README.md` as "kept for reference" but is actually **load-bearding in the nav** (`globals.css:69`). `trophy-case-side-panels.webp` (home hero) is 900×480 while every other room is 2200×640, so Home's backdrop runs at a different scale rhythm than every other page.

**Direction:** re-light the rooms, don't re-concept them (see assets doc A3). Target: "evening gallery with the lamps on" — dark walls are fine, but light pools should occupy a meaningful fraction of the canvas and reach the mid-frame, ambient floor ~3× brighter, warm (#fff6e0-family) rather than orange-brown. Vary each room's key light so the nine rooms are distinguishable at a glance (corridor = runway of pools, arena = hot red-amber rim, library = green-shaded lamp glow…). Fill the Portrait Gallery's frames with dark suggestive silhouettes.

---

## 4. Lighting (CSS layer)

- Body light pool: `rgba(212,175,55,0.16)` radial, 260px, every 900px — a gold *tint*, not light. The concept called for warm white (`#fff6e0`). Gold-tinted light on navy reads as sepia haze; warm-white light reads as illumination.
- Heading "glow" is a text-shadow on the letters themselves — objects glowing, not light falling on them. Fine as a garnish, but it's currently the *only* lighting on 90% of scroll depth.
- The scrim gradient (12% → 92% black) actively fights the theme: the deeper you scroll, the darker the museum gets. Cap it around 75–80% and let the re-lit rooms breathe through.
- Nothing on the site casts *downward* light: no cone/pool above the champion card, no lit-from-above table surfaces. Tier-1 artifacts should sit under a visible light source (CSS radial or a small overlay asset — see A4).

---

## 5. Typography

- **Bebas Neue does everything.** h1, h2, h3, metric values, champion team, mini-champ years, nav-card titles, timeline titles, teaser — all the same condensed all-caps display voice, differing only in size. That uniformity is the typographic version of the frame problem. Keep Bebas for h1/h2 and hero numerals; let h3s, card titles, and years fall back to weighted Inter (or the body face that replaces it) so display type regains meaning.
- **Playfair Display is imported and used zero times.** `--serif` is defined at `globals.css:22` and never referenced. Either deploy it exactly where the concept said — plaque quotes, lore pull-quotes, `.identity` lines, narrative intros — or drop the import (it costs a render-blocking font fetch on every page). Recommendation: deploy it. The serif voice is the cheapest "museum placard" win available, and the narrative layer is the product per `CLAUDE.md`.
- **Body face:** concept recommended swapping Inter for a warmer humanist sans (Source Sans 3 / Public Sans). Low cost, real warmth gain, and the footer plaque already (aspirationally) names Source Sans 3. Recommended.
- **Scale floor is too low.** Body is 0.875rem, but the site leans hard on 0.7–0.78rem micro-type (nav links 0.72rem, champion-season 0.7rem, hero subtitle 0.78rem) with 4–6px letterspacing. Museum wall text is set generously; bump the floor to ~0.8rem and give body copy `--step-0: 0.9375rem`.
- `tabular-nums` is applied only to `td.num`. Extend to `.metric-value`, scores, and year pills.

---

## 6. Color

- **Gold means nothing anymore.** 31 uses of `--gold`/`--gold-dim` in the CSS: links, all h1s, metric values, pills, brand, borders, hovers, ticks. When gold marks everything, it can't mark champions. Re-ration it: gold = *achievement* (titles, winners, records) + interactive accent (links/hovers). Headings and metric values move to warm white / bone (`#f3ead8`-family); structural borders move to a desaturated brass-gray.
- **Two competing golds.** CSS uses `#d4af37`; the concept spec and every SVG asset use the warmer brass `#c9a24b` ramp (`#fff0a8 → #c9a24b → #7f5b18`). Pick the asset brass (it's the better, warmer one) and update the CSS variables so UI chrome and art match.
- **Surface fills mismatch:** asset SVGs hard-code `#101c2a`/`#172535` interiors vs. CSS `--surface: #0f1b2d`. Close enough to be invisible today, but worth unifying in the token pass since the README claims code is the color source of truth.
- Missing entirely: the **warm spotlight white** `#fff6e0` the concept made the signature of the theme. It should become a first-class token (`--light`) used for light pools, top-highlights, and tier-1 halos.

---

## 7. Iconography — medallions, badges, event/exhibit/position icons

The system is real (67 hand-differentiated vector pieces, zero emoji-font dependency, programmatic naming — all good). Critiques:

- **One template, 67 times.** Everything is the same navy disc + brass ring + brass line-art. At 1em (table cells, chron rows) medallions render as identical dark coins — the identity the system exists to carry disappears exactly where it's used most. Each manager already has an accent color (the ring stroke, e.g. `#EF4444`); at small sizes that 2px ring is the only differentiator and it's ~4% of the area. Ask for small-size variants (fill the disc with the manager color, simplify linework) — see A6.
- **Text-as-Arial inside art:** franchise badges caption "F01" and position icons "QB" in `font-family="Arial"`. Convert to outlined paths (they currently render in whatever the OS serves and will never match the site's type).
- **Copy-paste boilerplate:** every SVG carries an unused `<filter id="shadow">` and a duplicate `id="brass"` gradient. Harmless as `<img>`, an ID-collision landmine if any are ever inlined; also pure bytes. Strip in the next art pass.
- **Emoji stragglers:** after the whole de-emoji effort, `app/page.tsx` still renders `🏆` literals (champion-season line, `"🏆".repeat(...)` on mini-champ cards) and the nav burger is a `☰` character. Replace with the existing trophy icon asset / an SVG burger.

---

## 8. Chrome & site furniture

- **`wordmark.svg` is orphaned** — referenced nowhere in app code (nav renders text). It also contains the literal text `{insert witty name here}`, as do `layout.tsx`'s `<title>`, the nav brand, and the Home h1. The domain (`iwnh.sme327.com`) suggests "Insert Witty Name Here" may genuinely be the league's name — **question 1 for the owner**, because the answer decides the entire nameplate/wordmark commission (A5). If it *is* the name, it deserves a designed, engraved-brass treatment that makes the joke look intentional; if it's a placeholder, it's currently shipping in the page title of every route.
- **Two chrome assets render black-on-navy (effectively invisible):**
  - `divider-cap.svg` uses `fill="currentColor"`, but it's consumed as a CSS `background-image` (`globals.css:194`) where `currentColor` can't inherit → the diamond caps paint black.
  - `nav-active-tick.svg` also strokes `currentColor` and is consumed via `<img>` (`nav-links.tsx:31`) → black on dark navy.
  Hard-code brass fills in both files (or inline them).
- **Footer plaque is a picture of text.** `footer-plaque.svg` sets its line in Source Sans 3, which can never load in an `<img>` context → every visitor gets Arial. Rebuild the footer as HTML/CSS (brass-ruled strip, real text, selectable, localizable); keep only the ornaments as art.
- `stat-diamond.svg` auto-appends to **every** `.metric` — ornament-by-default, same disease as the frames. Keep it for tier-1 moments only.

---

## 9. Charts

Server-rendered SVG with CSS-var colors — right architecture, no notes on the approach. Two theme notes: (1) charts inherit whatever surface they sit on, so when tables move to the parchment tier, decide chart placement deliberately (recommendation: charts are *exhibit graphics* — they stay on dark case material, tier 2); (2) era-band fills and line colors should draw from the re-rationed palette (§6) so gold in a chart means "champion," matching the rest of the site.

---

## 10. Layout & rhythm

- Home is five consecutive `cols-4` card grids. With tier-3 de-framing this mostly self-resolves, but the page would still benefit from one asymmetric moment (the concept's "champion as lede") so the scroll isn't grid–divider–grid–divider.
- Round-2 review items **3** (table material) and **5** (uniform-grid audit: Champions trivia, History stat blocks) are still open and are absorbed into this plan (Phases 2 and 4).
- `.wrap` at 1280px, sticky nav, hamburger breakpoint: all fine.

---

## 11. Housekeeping (not visual, found during review — cheap to clear)

1. `utils/styles.py` — the archived Streamlit stylesheet has reappeared untracked at its old path (the live copy lives in `archive/streamlit-site/`). Delete.
2. `public/museum/README.md` inaccuracies: claims "nothing in this folder is unused" (wordmark.svg is), and lists `navy-walnut-panel.png` as superseded/reference (it's live in the nav).
3. Playfair import (see §5) — resolve either direction.
4. `dist/client 3`, `dist/client 4`, `dist/server 3/4` duplicate build dirs are cruft.
5. `.champion-emoji` class name is legacy of the emoji era; rename in the tier pass.

---

## 12. The plan

### Phase 0 — Decisions (owner input, blocks the art)
The five questions at the end of this doc — league name, lighting direction, parchment confirmation, photography availability, room-regeneration appetite.

### Phase 1 — De-gild and re-light in CSS (no new assets, 1 session, biggest visible change)
1. Implement the four material tiers (§2) with existing means: tier 2 = 1px brass hairline; tier 3 = frameless wall labels with baseline rule; tier 4 = interim calm dark ledger (Option A look via CSS only) until the parchment texture arrives. `border-image` survives only on tier 1 (champion card, `.event-featured`, `.card-feature`).
2. Lighting pass: light pools go warm-white and stronger; scrim capped ~78%; tier-1 artifacts get a radial light-cone halo; hover states brighten (light response) instead of border-color swaps.
3. Palette re-ration (§6): one brass, `--light` token, gold reserved for achievement + links; headings/metrics to warm white.
4. Typography pass (§5): Bebas restricted to h1/h2/hero numerals; Playfair deployed on pull-quotes/`.identity`/narrative intros; type floor raised; tabular-nums extended. (Body-face swap to Source Sans 3 rides along if approved.)
5. Bug sweep: divider caps + nav tick recolored, footer rebuilt as HTML, emoji stragglers replaced, housekeeping list (§11).

### Phase 2 — Material system, asset-backed (needs graphics: A1, A2, A7)
Parchment ledger material lands on all tables + timeline ledgers with dark-ink text theme; refined thin-rail artifact frame replaces `plaque-frame.svg` on tier 1; wall tile v2 behind everything.

### Phase 3 — Rooms re-lit + persona (needs graphics: A3, A4, A5; owner answers)
Nine re-lit room backdrops (distinct per-room light signatures, Arena heat, filled Portrait Gallery), hero spotlight, nameplate/wordmark + monogram. This is the phase that delivers "well lit" and "its own persona."

### Phase 4 — Editorial hierarchy (no assets)
Close round-2 item 5: Champions trivia and History stat blocks get tiered treatment; Home gets its asymmetric champion lede; audit every page top-to-bottom against the tier table.

### Acceptance checks
- Count framed elements per viewport: **≤2** ornate frames visible on any screen (today: often 8+).
- Screenshot each room's page at 50% scroll: the room must still be visibly *a room* (today: flat navy).
- Gold appears only on: titles/champions/records, links, tier-1 frames.
- A league member can identify any manager's medallion at 16px.

---

## 13. Questions for the owner (with recommendations)

1. **Is the league actually named "{insert witty name here}"?** (The domain `iwnh.sme327.com` suggests yes.) If yes → commission the engraved nameplate treatment so it reads as the intentional joke it is (A5). If no → the real name is the single most important missing asset on the site.
2. **Which "well lit"?** (a) Dramatic night-gallery — dark walls, strong warm spotlights (recommended: it preserves all existing art direction and the navy/brass system, just turns the lamps on), or (b) genuinely bright daytime museum (bigger pivot, contradicts the shipped navy palette).
3. **Confirm parchment (Option B) for tables** — carried open since the last review. Recommended: yes; Phase 1 ships the safe dark interim either way.
4. **Does any real league photography exist** (an actual trophy, draft-day photos, old score printouts)? Even 6–10 objects, treated as gold-duotone engravings (A8), would do more for *persona* than any generated art.
5. **Room regeneration appetite:** re-lighting means regenerating or repainting 9 large images (A3). Comfortable re-running that commission, or should Phase 3 start with CSS-side brightening (weaker, but free) on the existing files?
