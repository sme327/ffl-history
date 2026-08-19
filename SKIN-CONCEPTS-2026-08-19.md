# Re-Skin Concepts — 2026-08-19

Eight visual directions for **{insert witty name here}** (the brand name is permanent — a deadpan joke, confirmed, keep it exactly as-is in every concept). Companion to `SITE-REVIEW-2026-08-19.md`, which explains *why* a re-skin is the top recommendation: the current design is disciplined but visually uniform — all fifteen routes share one rhythm (eyebrow → title → metric cards → content cards → table), there's zero imagery anywhere, and nothing distinguishes "the Trophy Room" from "a spreadsheet of manager stats" except the words on the page.

**Every concept below is mocked against the same page — Home — so they can be compared side by side.** Home currently contains, top to bottom: a hero with the brand name and tagline, a reigning-champion feature card, a 4-up stat strip (seasons / active members / different champions / matchups played), a "Recent Champions" row (one small card per recent season), a "League Legends" row (top titleholders plus the title-drought callout), a "League Storylines" section (four narrative cards: most championships, best regular season, most trips without a title, all-time scoring leader), a 3-up "Explore the Exhibits" grid (six destination cards — Trophy Room, Timeline, Keeper Hall, Draft Legends, Manager Files, Franchise Files), and a closing teaser line with a call-to-action into Champions.

For each concept below: mood/references, palette (with hex values), typography, what specifically changes in each Home section, the imagery requirement, and an honest tradeoff. A design that works for Home should be sanity-checked against a dense page (Rivalries' full matchup table, League History's ten-column stat table) before sign-off — a direction that only works for hero moments isn't a full skin, and every one of these needs to still host a scrollable data table without falling apart.

Photography needs are called out explicitly per concept, since some directions require it and some deliberately don't — per your steer, this set is intentionally mixed.

---

## Quick comparison

| # | Name | Mood in three words | Photography | Primary colors |
|---|---|---|---|---|
| 1 | The Museum, Lit Properly | warmer, dimensional, same bones | Optional (object photos) | Navy, brass gold, warm white |
| 2 | The Sports Desk | editorial, confident, magazine | **Required** (people, moments) | Off-white, ink black, one accent red |
| 3 | NFL Films Grain | cinematic, weathered, mythic | **Required** (can be low-res/archival) | Sepia brown, grain black, faded gold |
| 4 | Stat Sheet Zine | scrappy, handmade, loud | None — illustration/type only | Newsprint cream, marker orange, halftone black |
| 5 | The Broadcast | live, kinetic, confident | Optional (silhouettes/cutouts) | Broadcast blue, hot accent, white-on-dark |
| 6 | Trading Card Program | nostalgic, collectible, warm paper | **Required** (portrait-style crops) | Cream paper, forest green, card-frame gold |
| 7 | Locker Room App | bold, modern, high-contrast | **Required** (cutout portraits) | Near-black, electric accent, bone white |
| 8 | Podcast Cover | flat, saturated, character-driven | None — illustration only | Duotone pair (pick 2 saturated hues) |

---

## 1. The Museum, Lit Properly

**Pitch:** Keep everything the current design gets right — the navy/gold museum concept genuinely fits `CLAUDE.md`'s "Hall of Fame" brief — and fix the one thing wrong with it: it's flat. Real museums use light, material, and depth. This one doesn't have to pivot; it has to get lit.

**References:** the Basketball / Rock & Roll Hall of Fame's actual physical exhibit design (spotlighting, dark walls, warm pools of light on the object being celebrated), ESPN's "The Ocho"-era trophy-case graphics, a nice hotel lobby's dark-wood-and-brass materiality.

**Palette:** `--bg: #0a1420` (kept, slightly cooled) · `--surface: #14202f` · brass gold `#c9a24b` (warmer than the current `#d4af37`) · warm spotlight highlight `#fff6e0` used sparingly as a literal light pool behind hero elements · keep `--muted`/`--faint` roughly as-is.

**Type:** Keep Bebas Neue for display — it's already doing the "engraved brass plaque" job well. Swap Inter for a slightly warmer humanist sans (**Source Sans 3** or **Public Sans**) for body copy, so it reads less like a dashboard font. Actually *use* the currently-unused Playfair Display: apply it to plaque quotes and lore pull-quotes specifically (see review S13/S16), nowhere else — that restraint is what makes it feel special when it appears.

**Home page changes:**
- Hero: add a subtle radial "spotlight" gradient behind the brand name (warm white fading to navy), like a single hanging light over an exhibit case. The hero background is no longer flat navy.
- Reigning champion card: give it a literal brass plate treatment — a thin inset border, a subtle engraved-texture background (a very faint repeating diagonal linen or brushed-metal texture, 3–5% opacity, not a photo), corner rivets as small decorative marks.
- Stat strip: add a thin brass baseline under each number, like museum wall-label typography — small caps label under a large serif or condensed numeral.
- Recent Champions / League Legends: unchanged structurally, but each card gets a very subtle drop shadow and a 1px inner highlight to read as a raised object rather than a flat rectangle.
- Exhibit grid: this is the best opportunity for restrained photography — six small square "case" thumbnails (a trophy, a stack of draft cards, a torn ticket, a folded jersey, an old photo, a gavel) rendered in gold-duotone so they read as engravings, not photos. If no photography is sourced, keep as-is with icons, just lit better.
- Footer (new, per review S10): a genuine museum placard strip — "Est. 2001 · A private collection · Report a misfiled exhibit →".

**Imagery:** optional. Works with zero new photography (it's mostly a lighting/material pass on the existing system) but improves further with 6–10 object photos (an actual trophy if one exists, a printed bracket, an old draft board) treated as gold-duotone engravings.

**Tradeoff:** the safest option — lowest risk, least differentiation. If the goal is "feel like a destination next to sports blogs," this is a smaller step than concepts 2, 5, 6, or 7. Good as a fallback if a bigger pivot turns out to be too much work, not the pick if you want to close the gap in one move.

---

## 2. The Sports Desk

**Pitch:** Drop the dark museum entirely. Go light, editorial, and confident — the way a real sports desk (a section front, not a stats page) presents a story: a dominant photo, a bold headline, a tight deck, and data used as evidence rather than wallpaper.

**References:** The Athletic's game-story layout, The Ringer's NFL vertical, ESPN's feature-story templates (not the scores app — the long-read pages), Sports Illustrated's website circa its best editorial years.

**Palette:** off-white background `#f7f5f0` (not pure white — slightly warm, like newsprint stock) · ink `#14151a` for text · one loud accent color pulled from the league's own identity if one exists (a team color, a draft-night t-shirt color) — if nothing canonical exists, a confident red `#c8102e` or a deep field green `#0b3d2e`, used *only* for links, the accent rule under the masthead, and one callout per section, never as a background.

**Type:** A strong grotesque display face for headlines — **Archivo Black** or **Anton** (bolder, more "sports section" than Bebas Neue's thin condensed look) — paired with a workhorse serif or sans for body text: **Source Serif 4** for long-form narrative blocks (season hooks, lore, plaques) and **Inter** (already in use) for stats and tables, so the reading experience shifts register between "story" and "data" the way a real sports page does.

**Home page changes:**
- Hero becomes a masthead: brand name set small and confident top-left (like a publication nameplate), a large photo-led headline treatment where the champion of the moment leads — "reigning champion" isn't a card anymore, it's the lede: a big photo (or, if none exists, a bold color-block portrait silhouette) with the manager's name as a huge headline and the season stat line as a deck underneath.
- Stat strip becomes a horizontal "ticker rail" — a thin bordered strip of numbers styled like a box score, not four separate cards.
- Recent Champions becomes a horizontal scrolling "recap strip," each card a small photo thumbnail + caption, like a photo gallery rail under a story.
- League Storylines becomes actual magazine-style story cards — each with a small kicker label, a bold headline, and a 2-3 line deck, laid out asymmetrically (one large lead card, three smaller ones) instead of four equal-weight cards.
- Exhibit grid becomes a "Sections" nav strip, styled like a publication's section front links (Trophy Room / Timeline / Keeper Hall / etc.), text-forward with small icon marks, not big centered cards.
- Footer: a real masthead footer — section links, "About this archive," last-updated date, correction link.

**Imagery:** **required** for this concept to land — it's built around photography leading the page. Needs: current champion photo or portrait, a handful of draft-night/league photos for the recap strip. If genuinely no usable photos exist across 25 years, this concept should be deprioritized in favor of 4, 8, or a lighter version of 1.

**Tradeoff:** the strongest "sits next to a sports blog" result of the eight, but it's also the biggest lift — it needs real photography sourced and curated, and it's the furthest from the current brand feel (dark, trophy-case, night-at-the-museum) toward something brighter and more newsroom. Worth prototyping first on Home before committing further.

---

## 3. NFL Films Grain

**Pitch:** Lean into myth-making. NFL Films built the entire modern language of "this game matters" — slow-motion, film grain, a narrator's gravity, sepia-toned history. This concept treats every season like a chapter of a documentary, which maps directly onto `CLAUDE.md`'s "League History Documentary" reference point — it's the one explicitly named in your own brief.

**References:** NFL Films title cards and season-in-review specials, ESPN's *30 for 30* poster/title design, ESPN's *The Last Dance* title sequence, ken-burns-style archival documentary framing.

**Palette:** warm sepia-brown `#2b2117` background · aged parchment `#e8dcc0` for card surfaces · faded film gold `#c19a4e` for accents (deliberately duller/dustier than the current bright `#d4af37` — this should look like an old photograph, not a new one) · deep vignette black `#0d0a07` for hero backgrounds.

**Type:** A classic film-title serif or slab for display — **Bitter** or **Oswald** at heavier weights for numerals (evokes stenciled scoreboard/title-card numerals), body text in a plain, slightly warm serif like **Lora** to read like narration captions.

**Home page changes:**
- Hero: full-bleed dark background with a subtle grain/noise texture overlay (CSS-generated or a lightweight tiled noise PNG) and a vignette. Brand name set like a documentary title card — centered, letter-spaced, with a thin horizontal rule above and below like an old film credit.
- Reigning champion card: styled as a "chapter card" — season number treated like a title-card chapter marker ("CHAPTER TWENTY-FIVE"), champion name and team in large stenciled type, photo (if available) treated in high-contrast sepia duotone with visible grain.
- Recent Champions: a horizontal filmstrip — literal sprocket-hole styling optional but on-brand — each season a "frame."
- League Storylines: reframe as narrated captions — each stat card gets a small "quote-mark" or film-slate icon and reads like a voiceover line ("The benchmark everyone is chasing.") rather than a stat callout, leaning harder into the copy that's already there.
- Exhibit grid: six "reels" — square cards with a corner label like a film can ("REEL 3 — KEEPER HALL"), grain texture on hover.
- Footer: a closing-credits treatment — "Produced by 25 years of bad waiver decisions."

**Imagery:** **required** for full effect, but forgiving of quality — this is the one concept where low-resolution, poorly-lit, or old phone-camera photos from actual draft nights become an asset instead of a liability, because grain and sepia treatment hide exactly those flaws. If any photos exist from this league's history at all, even bad ones, this is the concept that wants them most.

**Tradeoff:** highest potential emotional payoff — it's the most "documentary," most aligned with your own CLAUDE.md language, and most forgiving of imperfect source photography. Risk is technical: film grain/noise textures need to be done efficiently (CSS `background-blend-mode` or a single small tiled texture, not a large image) to not hurt load time, and sepia-on-everything can get monotonous across 15 routes if not varied by era (suggest the four "Eras" already defined in League History each get a slightly different grain/tint treatment).

---

## 4. Stat Sheet Zine

**Pitch:** No photography, no polish — go the other direction entirely. A scrappy, fan-made zine aesthetic: photocopied stat sheets, marker annotations, halftone dots, torn-paper edges. This is the "made by the league, for the league" energy of a printed fantasy football preview 'zine passed around a draft party.

**References:** *The Fantasy Footballers* and *Draft Sharks* print-era zine graphics, riso-print gig posters, old-school fanzine culture (photocopied, stapled, hand-annotated), skate/punk flyer design applied to a stat sheet.

**Palette:** newsprint cream `#f0ead6` background · halftone black `#1a1a1a` · one loud marker color per section (rotate between a highlighter yellow `#f4d035`, a sharpie orange `#e8622c`, and a ballpoint blue `#2a4d8f` used as annotation color, not structural color) — deliberately inconsistent/handmade rather than a single locked accent.

**Type:** A bold condensed sans with personality for headlines — **Anton** or **Bungee** — paired with a monospace or typewriter face for stats (**Space Mono** or **IBM Plex Mono**), which sells the "photocopied stat sheet" read far better than a clean sans would.

**Home page changes:**
- Hero: the brand name rendered like a rubber-stamped or hand-lettered zine masthead, slightly rotated/imperfect, with a halftone-dot texture behind it instead of a flat background.
- Reigning champion card: styled like a torn-out magazine clipping taped to the page (a subtle rotation, a drop shadow like a physical object, "tape" corner marks as a decorative CSS element).
- Stat strip: rendered like a typewritten stat line, monospace, with hand-drawn-style circles or underlines (SVG squiggle) around the standout numbers instead of card borders.
- League Storylines: styled as margin annotations — sticky-note or index-card look, slightly different rotation per card, marker-color underlines on the key phrase in each blurb.
- Exhibit grid: six cards styled like ticket stubs or trading-card cutouts with a torn/perforated edge (CSS clip-path), each in a different marker color.
- Footer: a "xeroxed at 2am" credit line, deliberately informal.

**Imagery:** none required. This is the strongest "zero photography" option of the set — everything is typographic and textural (halftone patterns, torn-edge shapes, tape/pin decorative elements) rather than photographic, which makes it the lowest-risk option if you confirm no usable photos exist.

**Tradeoff:** the most personality-forward and cheapest to source (no photography pipeline at all), and it fits the "occasionally ruined by a waiver wire mistake" tone in the existing tagline extremely well. Risk: it can undercut the "museum"/Hall-of-Fame framing in `CLAUDE.md` if pushed too far toward joke-y — this works best if the *irreverent* energy is reserved for chrome (borders, textures, marginalia) while the actual record-keeping (tables, plaques) stays legible and serious. Also the busiest option to keep performant and accessible — halftone/texture overlays need to stay decorative-only, never reduce text contrast.

---

## 5. The Broadcast

**Pitch:** Borrow the visual language of a live sports broadcast graphics package — the score bug, the lower third, the ticker — and apply it to a static archive. This gives every page a kinetic, "this matters right now" energy even though it's 25-year-old history, and it's a genre none of the other concepts touch.

**References:** ESPN/NFL Network score-bug and stat-overlay design, RedZone's channel graphics, *NFL Films* GameDay Morning-style lower thirds, modern esports broadcast overlays (which have pushed this genre furthest visually in the last decade).

**Palette:** broadcast navy-black `#0b0e14` · one hot accent — broadcast red `#ff3b30` or a signature electric color if you want to differentiate from every other sports property's red — used exclusively for "live"-style badges and the score-bug elements · clean white `#ffffff` for primary numerals, high contrast throughout (this one should look sharp and technical, not warm).

**Type:** A tight, technical grotesque built for on-screen data — **Barlow Condensed** or **Titillium Web** — used at both display and body sizes, since broadcast graphics rarely mix serif/display combos the way editorial layouts do. Keep everything feeling like it was built for a screen, not a page.

**Home page changes:**
- Hero: styled like a broadcast open — the brand name treated as a channel bug/ident in a corner, with the reigning champion presented as a full-width "score bug" style banner (team name, manager, score line, right where a live game's score would sit), not a centered card.
- Stat strip: rendered as a literal ticker — a horizontal scrolling or evenly-spaced strip with thin separator lines and small colored tags, mimicking a bottom-of-screen stats ticker.
- Recent Champions: presented as a "highlights reel" rail — small rectangular cards styled like broadcast highlight thumbnails, each with a bold season-number badge in the corner (like a score-bug clock).
- League Storylines: each becomes a "graphic package" card — a bold stat number rendered huge and technical (like a broadcast's on-screen stat callout), label beneath in small caps, accent-colored corner tab.
- Exhibit grid: six cards styled like channel/section idents — bold single-color tabs (each exhibit gets its own accent color, like ESPN's sport-specific brand colors) rather than one uniform gold treatment.
- Footer: styled like a channel sign-off — "This has been {insert witty name here}. Same time next season."

**Imagery:** optional. Works well with zero photography (broadcast graphics are mostly typographic/geometric), but gains a lot from small circular or clipped manager photo cutouts used the way broadcasts show a player headshot next to their stat line — even low-quality photos work here since broadcast graphics crop tight and small.

**Tradeoff:** the most kinetic and "alive" feeling of the eight, and a good fit if the site's audience skews toward people who watch football broadcasts more than they read sports blogs. Risk: broadcast graphics are built to be glanced at for two seconds, not read for ten minutes — this look can start to feel exhausting across a long page with a lot of prose (lore, plaques, narrative). If chosen, plan to dial back the "ticker" intensity specifically on text-heavy sections (Keeper Lore, manager plaques) so long-form reading doesn't fight the chrome around it.

---

## 6. Trading Card Program

**Pitch:** Every fan of a 25-year-old league has a mental image of an old game-day program or a stack of trading cards. This concept treats every manager, franchise, and season like a collectible — cream card stock, foil-style borders, portrait-oriented "cards" instead of rectangular dashboard cards.

**References:** 1980s–90s Topps/Score football card design, vintage NFL game-day programs, a printed yearbook page, museum trading-card exhibit cases.

**Palette:** cream card stock `#f2ead9` · deep forest green `#1c3d2e` (a color the current palette doesn't use at all, giving real differentiation) as the primary structural color · card-frame gold `#b8933f` for borders and foil accents · a muted red `#8a2e2e` as a rare second accent (team-color-card energy).

**Type:** A serif with real character for names/headlines — **Playfair Display** (already imported and unused — this is the concept that finally gives it a real job) at large sizes for manager/season names, a clean sans (**Inter**, already in use) for stat lines, mimicking a card's front (serif name) versus back (sans stats) split.

**Home page changes:**
- Hero: the brand name framed like a program cover — a bordered rectangle with corner ornaments, "Program · Est. 2001" as a subtitle where the current hero-subtitle sits.
- Reigning champion card: reframed as a literal trading card — portrait-oriented, a foil-style double border, the manager's photo (or a color-blocked silhouette with initials if no photo exists) filling the top two-thirds, stat line and season on a "card back" strip at the bottom.
- Recent Champions: a "collection" row — small vertical trading cards in a row, like a card binder page, each with a thin foil border and card-number-style season badge in the corner.
- League Legends: styled explicitly as a "starting lineup" or "all-star roster" card set, forest green background, gold player-name-style banners.
- Exhibit grid: six cards presented as program sections/tabs, each with a small custom icon in an embossed-looking circular badge rather than a floating emoji.
- Footer: styled like the back cover of a program — sponsor-style credit blocks repurposed as fun stats ("Printed annually since 2001. Circulation: everyone in the group chat.").

**Imagery:** **required** to hit the "trading card" read fully — ideally portrait-style crops of each manager (even casual photos work if cropped consistently). Without photography this degrades gracefully into colored silhouette cards with initials, which is still a legitimate, differentiated look, just less collectible-feeling.

**Tradeoff:** the strongest "nostalgic collectible" feeling and the best use of forest green as genuine differentiation from every gold/navy sports property. It's also the concept most dependent on being able to get a *consistent* photo per manager (24 of them) — a program with photos for twelve managers and silhouettes for twelve others will look unfinished rather than intentional, so this one lives or dies on photo-gathering follow-through.

---

## 7. Locker Room App

**Pitch:** The current design's dark palette is closer to a native sports app than it looks — this concept pushes it the rest of the way into that world deliberately: bold, high-contrast, big confident numerals, portrait cutouts on color blocks, the visual energy of ESPN's app or Bleacher Report rather than a website.

**References:** the ESPN app's player-card and stat-leader screens, Bleacher Report's bold editorial cards, modern athlete-brand sites (Nike/Jordan Brand athlete pages), NBA 2K/Madden player-card UI (a familiar visual grammar for anyone who plays those games).

**Palette:** near-black `#0d0d0f` · bone white `#f5f3ee` for primary text · one electric accent, ideally *not* gold (to differentiate hardest from the current identity) — an electric lime `#c6f135` or a hot cyan `#2de0ff` used for numerals, active states, and highlight bars only.

**Type:** A big, confident grotesque built for large numerals — **Archivo Expanded** or **Space Grotesk** at heavy weights for stat numbers, a tighter sans (**Inter**, kept) for body copy. This concept should feel like it was designed screen-first, numerals-first.

**Home page changes:**
- Hero: the reigning champion becomes a full "player card" moment — a large color-blocked portrait cutout (photo with background removed, or a bold flat silhouette if no photo exists) on one side, giant stat numerals on the other, exactly like an app's featured-athlete screen.
- Stat strip: numerals get dramatically larger and bolder relative to labels — this concept should make the current `.metric-value` feel timid by comparison; labels shrink to small caps underneath.
- Recent Champions / League Legends: small circular portrait-cutout avatars (or bold initial-monogram badges in the accent color if no photo) replace the emoji entirely — this is the concept where dropping emoji for a real avatar system matters most, since app-native design rarely uses emoji as primary iconography.
- League Storylines: reframed as "cards" with a bold colored corner tab and one enormous number as the focal point of each, minimal supporting text — app UI trusts the number to carry the card.
- Exhibit grid: six large tap-target cards, bold single accent-colored icon marks (custom simple line icons, not emoji) rather than centered text blocks.
- Footer: minimal, app-style — small utility links only, no flourish.

**Imagery:** **required** for the full effect (portrait cutouts are central to this look), but degrades reasonably to bold initial-monogram badges in the accent color if photography isn't available — that's actually a legitimate, common pattern in real sports apps for players without a photo on file, so it won't look like a placeholder.

**Tradeoff:** the most "modern app," least "museum" of the eight — it trades the Hall-of-Fame warmth for something sharper and more contemporary. Best fit if the goal is to feel like a *product* people check in on, less like an archive people visit occasionally. Worth weighing against `CLAUDE.md`'s explicit instruction that the site should *not* feel like a generic sports app — this concept needs a genuinely distinctive accent color and typographic voice to avoid drifting into exactly the ESPN-fantasy-app territory the brief warns against.

---

## 8. Podcast Cover

**Pitch:** Sports podcast branding solved the "flat, bold, no photography needed" problem years ago — big flat-illustrated character marks, saturated duotone, chunky confident type, built to be a thumbnail at 60x60px and still read at full size. Apply that same design language to the site itself.

**References:** *Pardon My Take*, *Fantasy Footballers*, *The Ringer NFL Show*, *Bill Simmons Podcast* cover art and episode-graphic systems — all built around flat illustration, two-or-three-color palettes, and type that reads instantly small.

**Palette:** a locked duotone pair rather than a full palette — pick two saturated, high-contrast hues (for example, deep purple `#3d2b6b` + hot orange `#ff7a1a`, or navy `#12213f` + acid yellow `#f2d100`) and build everything from tints/shades of just those two plus black and white. This is the most disciplined, most instantly-recognizable-as-a-thumbnail option of the set.

**Type:** One extremely bold, slightly rounded display face for everything, headline and label alike — **Fredoka** at heavy weight, or **Baloo 2** — the opposite instinct from the current condensed/serious Bebas Neue. Body copy in a plain, high-legibility sans (**Inter**) kept small and out of the way; this concept wants type to be either huge and flat-colored or quiet and functional, nothing in between.

**Home page changes:**
- Hero: the brand name becomes a flat, illustrated logo lockup — a simple graphic mark (a trophy, a helmet, a football rendered as flat shapes in the two duotone colors) sits next to the wordmark, the way every podcast cover pairs an icon with a title.
- Reigning champion card: illustrated rather than photographic — a simple flat character/avatar representing the champion (could be built from a small library of interchangeable flat illustrated "manager" avatars, reused across the whole site) on a bold duotone background block, no attempt at photorealism.
- Stat strip: rendered as bold flat numeral blocks, each stat its own solid-color tile (alternating the two duotone hues), white numerals, no borders or subtlety — meant to be scannable in half a second, like an episode-art callout.
- League Storylines: each becomes a flat "episode card" — bold color block, one big illustrated icon, short punchy headline, the copy trimmed tighter than it is today to fit the format's energy.
- Exhibit grid: six flat icon tiles, each a different bold color from an extended palette built off the two-hue base (tints/shades, not new hues), simple geometric icons instead of emoji.
- Footer: minimal, playful — "New chapter every season. Subscribe to nothing, this is just a website."

**Imagery:** none required — this is the other fully illustration-driven option alongside concept 4, but where the Zine direction is deliberately messy/handmade, this one is deliberately clean/flat/vector. Needs a small illustrated icon/avatar system built once (a football, a trophy, a whistle, simple flat manager avatar shapes) and reused everywhere, which is a bounded, one-time illustration job rather than an ongoing photography pipeline.

**Tradeoff:** the most instantly modern and shareable (this is the look that survives being screenshotted into a group chat at thumbnail size, which matters given the product's own primary distribution channel), and the cleanest zero-photography option that doesn't read as scrappy the way the Zine does. Risk: it's the furthest in *tone* from "Hall of Fame" — it reads as fun and current more than prestigious and permanent, so it's the one most worth checking against `CLAUDE.md`'s "should NOT feel like a betting application or generic analytics dashboard" line; podcast-cover energy avoids the dashboard problem entirely but needs a restrained hand to still feel like it's honoring 25 years of history rather than just branding a new show.

---

## Suggested next step

Don't commission all eight. Pick two or three that feel right on read — one closer to the current identity (1 or 3), one further from it (2, 6, or 7), and one no-photography option (4 or 8) as a hedge — and have the graphics team mock up just the hero + reigning-champion-card + stat-strip portion of Home for each (not the full page) before committing further. That's enough surface area to feel the type, color, and material choices without paying for three or four full-page comps up front.
