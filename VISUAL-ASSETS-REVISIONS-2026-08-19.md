# Visual Asset Revisions — Round 2

Follow-up to `VISUAL-ASSETS-2026-08-19.md`, after reviewing the completed `assets/` delivery. This is a **narrow, targeted brief** — most of round 1 is approved as-is. Read this alongside the original document; it doesn't replace it, it corrects one specific gap.

---

## 1. What happened in round 1

Coverage was complete — every file in the manifest got produced, correct counts, correct folder structure, correct naming. But nearly every icon/medallion/badge was built from one template: a brass-gradient ring or frame with the **original emoji character dropped in as literal Unicode text** (`<text font-family="Apple Color Emoji,Segoe UI Emoji,sans-serif">🍺</text>`). That still delegates rendering to whatever emoji font the reader's OS happens to have — which is the exact cross-platform inconsistency problem this whole asset system exists to fix (site review, finding S9). It also doesn't match the art direction's "engraved, cut into metal, not a flat glyph" instruction. Full-color emoji rendered flat is close to the opposite of that.

The good news: **this is a narrower fix than it sounds.** The frames, rings, plates, shapes, sizing, and colors are correct throughout — only the glyph sitting inside each frame needs replacing.

---

## 2. Approved as-is — do not touch

- **Frame/ring/plate construction** on every medallion, badge, and icon (the brass gradient, the dark inset circle, the corner rivets on `chrome/plaque-frame.svg`).
- **Franchise badge shapes** — round for F01–F09 (2001 founding), shield for F10–F11 (2002 expansion), hexagon for F12 (2003 expansion). Correct per spec.
- **Franchise numeral plates** (the "F02," "F10," etc. brass tags).
- **Per-manager ring colors**, correctly pulled from `MANAGER_COLORS`.
- **Sizing** — 64×64 for icons/medallions, 96×96 for badges. Consistent throughout.
- **`assets/textures/navy-walnut-panel.png`** — appropriately subtle, correctly sized (36KB), tileable. No changes needed.
- **`assets/textures/trophy-case-side-panels.png`** — content is excellent, exactly matches the reference mockup. Only the file size needs fixing (§4), not the artwork.
- **`assets/icons/positions/*.svg`** (QB/RB/WR/TE/DEF/K) — checked one (`qb.svg`) and it's built correctly: a real vector helmet-silhouette shape with a text label, no emoji dependency at all. **This is the reference example for what "correct" looks like** — if the other position icons match this construction, that whole category is done. Spot-check the remaining five against this one file; if they follow the same pattern, no further work needed here.

---

## 3. The fix: redraw the emblem layer

**What changes:** replace every `<text>emoji</text>` element with actual vector line art — simple, engraved-style icon construction, sized and centered the same way the emoji was. **What doesn't change:** everything in §2. This is a swap of one layer inside an already-correct frame, not a redo of the frame.

**Construction rule:** single or double-stroke line art (matching weight across the whole set), rendered in the brass gradient already defined in each file (`url(#brass)`) or a simple debossed fill — not full-color, not a literal emoji redraw. The goal is a glyph that reads as "cut into the metal," the way `qb.svg`'s helmet already does. **Use `qb.svg` as the literal reference file for construction technique** — it's already in the delivery and it's correct.

**Acceptance test — mechanical and easy to verify:** once this is done, running `grep -rl "Emoji" assets/` should return **zero files**. Right now it returns most of them. That single grep is the pass/fail gate for this round.

### 3a. Manager medallions — 24 glyphs, `assets/medallions/managers/`

Translate the *meaning* of each existing sigil into line art — don't invent new symbolism, just stop depending on the OS font to draw it:

| Manager | Emoji | Draw as | Manager | Emoji | Draw as |
|---|---|---|---|---|---|
| Shawn | 🐝 | Bee | Douglas | ⚙️ | Gear/cog |
| Fadi | 👑 | Crown | Jeff | ⚽ | Soccer ball |
| Brian Clark | 🍺 | Beer stein — **see flag below** | Eric | ⛳ | Golf flag/pin |
| Kevin O'Boyle | 🍺 | Beer stein — **see flag below** | Jamie | 😇 | Smiling face with halo |
| Kevin Swanson | 🧔 | Bearded face | Mike | 🍻 | Clinking beer mugs |
| Thomas | 🐻 | Bear — **see flag below** | Joe Tyszko | 🌽 | Ear of corn |
| Evan | 🎉 | Party popper / confetti burst | Robby | 🎸 | Guitar |
| Steve Swanson | 🐻 | Bear — **see flag below** | Rob | ⚔️ | Crossed swords |
| Dominic | 🏈 | Football | Byron | 🏛️ | Classical column/temple |
| Dan | 📖 | Open book | Dale | 🌪️ | Tornado |
| Bryan Kearney | 💪 | Flexed bicep | BV | ❓ | Question mark |
| Adam | 🎯 | Target/bullseye | Nick Blaettler | 🐱 | Cat face |

**Flag — duplicate pairs (carried over from round 1, still unresolved):** Brian Clark/Kevin O'Boyle (both beer) and Thomas/Steve Swanson (both bear) need a secondary distinguishing mark now that these are being hand-drawn anyway — ring color alone isn't enough for these two pairs specifically, because unlike the era/event/exhibit icons (§3b–3d), manager sigils appear **side by side in lists where telling people apart is the whole point** (Rivalries' executioner/victim tables, franchise steward rows). Suggested fix: keep the same base object but vary its pose/detail — e.g. Brian Clark's stein upright and full, Kevin O'Boyle's tankard tilted/clinking; Thomas's bear standing, Steve Swanson's bear sitting. Any small, consistent variation works — the point is two glyphs that read as clearly different silhouettes at 24px, not just two different ring colors.

### 3b. League Era medallions — 4 glyphs, `assets/medallions/eras/`

| Era | Emoji | Draw as |
|---|---|---|
| The Founding Era | 🏛️ | Classical column/temple |
| The Workhorse Era | 🐎 | Horse |
| The Keeper Revolution | 🔑 | Key |
| The Modern Era | ⚡ | Lightning bolt |

### 3c. Timeline event-type icons — 15 glyphs, `assets/icons/events/`

| Type | Emoji | Draw as | Type | Emoji | Draw as |
|---|---|---|---|---|---|
| championship | 🏆 | Trophy cup | collapse | 📉 | Downward trend arrow |
| dynasty | 👑 | Crown | rivalry | ⚔️ | Crossed swords |
| runner_up | 🥈 | Second-place medal | draft | 📋 | Clipboard |
| steward_change | 🔄 | Circular exchange arrows | keeper | 🔒 | Padlock |
| record | ⚡ | Lightning bolt | rule_change | 📜 | Scroll/parchment |
| milestone | 🏛️ | Classical column | alumni | 👤 | Person silhouette/bust |
| heartbreak | 💔 | Broken heart | note | 📝 | Memo / pencil on paper |
| breakthrough | 🎯 | Target/bullseye | | | |

*(A few of these motifs — column, target, crossed swords, key — repeat concepts also used in §3a/§3b. That's fine and expected; these are separate icon systems that never appear side by side with the manager sigils, so there's no confusion risk the way there is within §3a's duplicate pairs.)*

### 3d. Exhibit grid icons — 6 glyphs, `assets/icons/exhibits/`

| Exhibit | Emoji | Draw as |
|---|---|---|
| Trophy Room | 🏆 | Trophy cup |
| Timeline | 📅 | Calendar |
| Keeper Hall | 🔑 | Key |
| Draft Legends | 📋 | Clipboard |
| Manager Files | 👤 | Person silhouette |
| Franchise Files | 🏟️ | Stadium |

### 3e. Franchise badges — no separate work needed

Once §3a is done, the 12 franchise badges are automatically fixed too — each badge's emblem is just the founding steward's manager icon, composited into the already-correct badge frame (round/shield/hexagon). Don't redraw these separately; just re-render the 12 badge files once the corresponding manager glyph exists. F02 and F10 (the Brian Clark/Kevin O'Boyle pair) will inherit whatever secondary distinguishing mark gets added in §3a.

---

## 4. Texture: compress before this ships

`assets/textures/trophy-case-side-panels.png` is 1.4MB — 82% of the entire assets folder's current weight, for a background element that's explicitly desktop-only decoration (site review's own mobile guidance said keep this lean).

- **Interim fix, already tested:** resizing to 900px width with `sips` got it to 464KB with no visible quality loss. I can commit that version now if you want something smaller in the repo immediately.
- **Real fix:** convert to WebP. This shell doesn't have `cwebp`/ImageMagick available, so it needs a proper tool — `sharp` or `@squoosh/cli` in a one-off Node script, or the original export tool if it supports WebP output. Target: under ~150KB. Do this as part of the same pass as §3, since whoever's touching these files will have the right tooling open anyway.

---

## 5. Wordmark — optional, low priority

`assets/chrome/wordmark.svg` is just the brand text in a gradient fill inside a rounded box — functionally identical to what CSS (`--display` font + `var(--gold)`) already produces without a dedicated asset. Not wrong, just not adding anything. Fine to keep if there's a reason to want it as a fixed asset (e.g., reuse outside the website — social preview image, etc.); otherwise safe to drop and just style the text directly in the nav component. Not blocking anything else in this list.

---

## 6. Integration note — ✅ resolved 2026-08-19

Moved to `public/museum/` (badges/, chrome/, icons/, medallions/, textures/, README.md), matching the original doc's naming convention. The stale round-1 copies at the old `assets/` root were removed once the corrected set was confirmed. Final: 77 files, 344KB total.

---

## 7. Sign-off checklist — ✅ all clear, verified 2026-08-19

- [x] `grep -rl "Emoji" public/museum/` returns nothing
- [x] Brian Clark vs. Kevin O'Boyle medallions are visibly distinct — upright stein vs. rotated tankard, verified by diffing the two files
- [x] Thomas vs. Steve Swanson medallions are visibly distinct — standing bear vs. seated bear with added limb lines
- [x] The 12 franchise badges re-rendered with the fixed manager glyphs — confirmed F02/F10 correctly inherit the Brian Clark/Kevin O'Boyle variants inside their distinct frame shapes
- [x] `trophy-case-side-panels.webp` — 12KB (900×480), well under the ~150KB target
- [x] Position icons — all six remain the correct vector helmet-mark construction, untouched
- [x] `wordmark.svg` — kept; noted for reuse outside live navigation (social graphics, etc.)

**This is ready to build.**
- [ ] `assets/` moved into its final serving location (`public/museum/...` or equivalent)

Once this list is clear, it's ready for the build.
