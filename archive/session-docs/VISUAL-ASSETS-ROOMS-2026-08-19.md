# Page Room Backgrounds — Asset Brief

Ten distinct "rooms," one per section of the site, so each part of the museum feels like its own place while still reading as the same building. Companion to `VISUAL-ASSETS-2026-08-19.md` (icons/medallions/badges — done, live) and `VISUAL-ASSETS-REVISIONS-2026-08-19.md` (the corrected versions of those). This is a new, separate commission: environment images, not icons.

---

## 1. Why this shape, not 10 infinite backgrounds

Pages on this site scroll from a few hundred pixels (a short index page) to several thousand (a dense manager profile with tables). A single image can't be both a beautiful, detailed "establishing shot" *and* seamlessly tile for an arbitrary, unknowable length — those are two different jobs, and asking one image to do both is how you get either a gorgeous top that trails into an awkward stretch, or a tileable pattern too plain to feel like "a place."

So this brief is two asset types:

1. **Ten room scenes (§3)** — one per section, shown once at the top of that section's pages, doing the emotional work of "you have arrived somewhere specific."
2. **One shared tileable wall (§4)** — plain by comparison, continues the same wood/brass material underneath every room's scene for however far the page scrolls, so the room never visibly "runs out."

This is the same logic that already worked for Home: `trophy-case-side-panels.webp` is the room scene, `navy-walnut-panel.png` is the tileable wall. Home is done. This brief is building the other nine.

---

## 2. Shared art direction — read this before building any single room

Every room must look like it belongs to the same building as the existing Home hero image, or switching sections will feel like switching sites, not walking to a new wing.

| | |
|---|---|
| **Wood tone** | Match the existing dark walnut in `trophy-case-side-panels.webp` — same stain color, same grain direction and scale. If the two images sit side by side, the wood should be indistinguishable in material. |
| **Light** | Warm, overhead, ~2700–3000K (the same amber recessed spotlights already established), never cool/blue, never flat/shadowless. Every room has visible light *sources* (fixtures), not just ambient brightness — that's what sold the original image. |
| **Metal** | Brass/bronze only, matching the `#c9a24b`–`#7f5b18` gradient already used throughout the icon system. No chrome, no silver, no gold that reads more yellow than brass. |
| **Floor** | Consistent across rooms unless the room concept below calls for a deliberate variation (e.g., a red runner in the Trophy Room) — same dark wood or dark stone as the baseline. |
| **Camera** | Eye-level, symmetrical or near-symmetrical composition, looking straight into the room — not an angled/dramatic camera tilt. This is what makes it feel architectural rather than illustrated. |
| **Text-legibility zone** | Every room needs a darker, simpler horizontal band through its vertical center — this is where the page's eyebrow/title/intro text will sit on top of the image. Push detail and brightness toward the top, bottom, and sides; keep the middle calm. (This is exactly how the existing hero image already works — dark gap in the middle, detail at the edges.) |
| **Aspect ratio** | Wide banner, roughly **2200×640px** (taller than Home's 900×480 since these need to carry a page header, not just a hero) |
| **Format** | WebP. **Hard ceiling: 200KB per image.** The very first version of the Home image shipped as a 1.4MB PNG and had to be redone — don't repeat that. Compress before delivery, not after. |
| **Naming** | `public/museum/rooms/{room-slug}.webp` — slugs given per room below. |

---

## 3. The ten rooms

### 3a. Champions — The Trophy Room
**Route:** `/champions` · **Question:** "Who won?" · **Slug:** `trophy-room`

The most opulent room in the building — champions earn the grandest space. A hall receding into the distance, trophy cases lining both walls under individual spotlights, a dark red runner rug down the center aisle toward a vanishing point. Trophies/cups visible in the cases (silhouetted, not legible detail — this is atmosphere, not another icon). This should feel like the payoff room, the one everything else points toward.

### 3b. Timeline — The History Corridor
**Route:** `/timeline` · **Question:** "What happened?" · **Slug:** `history-corridor`

A long hallway lined with evenly-spaced framed plaques receding into perspective — a hall of years, not a hall of trophies. Slightly more subdued and aged than the Trophy Room: a hint of sepia in the light, less red/more brown. A thin brass strip inlaid in the floor running the length of the hall reads as a literal timeline if noticed, but shouldn't be a literal ruler with numbers — just a suggestion.

### 3c. League History — The Archive Library
**Route:** `/history` · **Question:** "How did the league evolve?" · **Slug:** `archive-library`

A study, not a hallway — this page is analytical, not celebratory ("This is not a statistics page. It's a history page," per the page's own copy). Tall bookshelves of bound ledgers on both walls, a heavy leather-topped table, maybe a brass-armed reading lamp. Quieter, more scholarly light than the ceremonial rooms — this is where someone goes to research, not to be dazzled.

### 3d. Season Archive — The Chronicle Vault
**Routes:** `/seasons`, `/seasons/:year` · **Question:** "What happened in a specific year?" · **Slug:** `chronicle-vault`

A wall of uniform, identically-bound yearbooks or ledgers, one per season — 25 matching spines side by side, suggesting "pick a year, open the book." Warm single-lamp lighting, more intimate/close than the grand halls, since this room's job is choosing one specific year, not surveying everything at once.

### 3e. Managers — The Portrait Gallery
**Routes:** `/managers`, `/managers/:slug` · **Question:** "Who are these people?" · **Slug:** `portrait-gallery`

A gallery wall of evenly-spaced ornate frames under individual track lighting, parquet floor. **Leave the frames atmospheric/silhouetted, not populated with faces** — there's no real photography of the league's managers, and the manager medallions already carry personality elsewhere on the page. This room is about the *feeling* of a hall of fame, not a literal portrait of anyone specific.

### 3f. Franchises — The Dynasty Wing
**Routes:** `/franchises`, `/franchises/:id` · **Question:** "What happened to this seat over time?" · **Slug:** `dynasty-wing`

Built around the idea of a *seat* that outlasts whoever holds it — a row of tall, ornate high-back chairs along a wall, each beneath its own brass nameplate (blank/atmospheric, not lettered), suggesting succession and institutional continuity rather than any one person. A hint of heraldic banner or crest shapes hanging above, echoing the franchise badge system already built.

### 3g. Draft Center — The War Room
**Routes:** `/draft`, `/players/:slug` · **Question:** "How were contenders built?" · **Slug:** `war-room`

The one room that should feel *working*, not ceremonial — this is where decisions get made, not where they're commemorated. A large table scattered with draft boards/index cards, a corkboard wall with strings connecting names (a "detective board" read), desk lamps rather than overhead spotlights. Slightly cooler/more tense lighting than the other rooms — still warm-toned, but tighter, more focused pools of light rather than grand overhead wash.

### 3h. Keeper Hall — The Vault
**Routes:** `/keepers`, `/keepers/:manager` · **Question:** "Who couldn't let go?" · **Slug:** `the-vault`

A bank-vault room: a heavy circular vault door, slightly ajar, safe-deposit boxes lining the walls floor to ceiling. Dimmer and more secure-feeling than any other room — this is about things too valuable to release. The one room where less light is correct; let shadows do more of the work here than elsewhere.

### 3i. Rivalries — The Arena
**Route:** `/rivalries` · **Question:** "Who still hates each other?" · **Slug:** `the-arena`

The most dramatic, highest-contrast room. Two facing pedestals or podiums lit from opposite sides, suggesting a standoff — a checkered or divided floor pattern reinforcing confrontation. **This is the one room allowed to break the pure amber palette**: mix in a warm red-orange undertone to the lighting (still brass fixtures, still the same wood) so this room reads as hotter, tenser than the rest, the way a rivalry should.

### 3j. Home — no new asset needed
Already built and live (`trophy-case-side-panels.webp`). Listed here only so the set reads as complete — Home is the lobby every other room's language derives from.

---

## 4. The shared tileable wall

**Slug:** `gallery-wall-tile.png` (or `.webp` if the tool supports lossless/near-lossless tiling export)

A simple, vertically-repeating strip of the same wood paneling — no furniture, no props, just wall, subtle baseboard, and the faint light-falloff pattern already established in `navy-walnut-panel.png`. This sits behind every page **below** that section's room scene, carrying the material down through however long the page runs.

- Must tile with **zero visible seam** top-to-bottom at whatever height it's exported at (test by tiling it 4× in a row before delivery).
- Should read as clearly *plainer* than the room scenes — it's the hallway between exhibits, not another exhibit.
- Small file size matters even more here since it repeats: target **under 60KB**.

This can most likely reuse/extend the existing `navy-walnut-panel.png` rather than being built fully from scratch — flag that to whoever's building it as a starting point.

---

## 5. Do you need to give me mockups?

**Not required.** The Home hero image was delivered from a written brief alone — no mockup — and it came back excellent and exactly on-target. The room descriptions in §3 are written at the same level of specificity that brief was.

**Worth considering anyway, given the stakes:** this is a 10-image commission, much bigger than the one-image hero. If you want a cheap insurance check before committing to all ten, generate just **two** first — Trophy Room and The Arena, since they're the most different from each other (opulent/ceremonial vs. dramatic/tense) — and confirm both land before the remaining eight get built. That catches a systemic misread (wrong wood tone, wrong light temperature, wrong mood) after 2 images instead of after 10.

---

## 6. What happens after these exist

Once delivered to `public/museum/rooms/` and `public/museum/textures/gallery-wall-tile.png` (or similar), the implementation work is:

1. Add a room-scene header band to every page that doesn't already have one (currently only Home has a `.hero`-style wrapper — the other 14 routes just have bare `eyebrow` + `h1` + intro text at the top, no image band at all).
2. Wire the shared tileable wall into the page body behind everything, below each room's header band.
3. Verify on **every** section, at both short and long page lengths, before calling it done — given the history in this thread, that verification step is not optional and I'll do it before reporting anything as live.

---

## Status: delivered, built, and live (2026-08-19)

All 9 rooms plus the shared tileable wall were delivered, QA'd against §2's shared art direction and the per-room size/format ceilings, and wired into all 15 routes (all 9 rooms + Home).

**One deliberate change from the plan above:** step 1's "header band" approach — the room image boxed into a bordered, rounded card near the top of the page — shipped first, but read as "a picture in a title box," not an actual place, and was called out as such. The corrected version replaces that with `position: fixed` room photos shown at their true aspect ratio: the image stays behind the page content for the entire scroll instead of scrolling away after the first screenful. Verified with a real `window.scrollTo()` simulation (not just a tall composite screenshot, which wouldn't have proven the fix) on both Home and Champions before shipping.

Two items flagged in §3's room-by-room QA are still open, not blocking: The Arena never got its intended red-orange tint (still reads as the same amber as every other room), and the wall tile's relationship to the pre-existing `navy-walnut-panel.png` was never fully confirmed as a distinct design pass rather than a near-duplicate.
