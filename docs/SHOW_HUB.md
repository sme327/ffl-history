# Across the Line: show hub

The museum hosts the animated show *Across the Line* (Graham Keeper and Kate Hedges). This page covers how its pages are laid out and how to ship a new weekly preview or episode.

## Pages

| URL | What it is |
|---|---|
| `/show` | **The hub.** It has two "now" slots (**This week**, the current weekly preview, and **Latest episode**), then a four-episode season track and a collapsible archive of past previews. |
| `/show/episodes/N` | One episode: player, summary, rundown, download, and links to what's new. |
| `/show/previews/week-N` | One weekly preview. After that week's games are played, it shows a banner linking to the Program recap. |
| `/show/pilot` | The pilot's original link, already shared with the league. It keeps working and shows Episode 1; its canonical link is `/show/episodes/1`. |

Everything is server-rendered. There is no client JS; the archive uses `<details>`. Each item page has its own title and poster for link previews in the group chat.

## The one file to edit: `app/show/catalog.ts`

`EPISODES` and `PREVIEWS` drive every page. Each entry has a `status`:

- `published`: live.
- `draft`: prepared, but hidden everywhere. Item pages return "not found".
- `planned`: (episodes only) shown dimmed on the season track, with no link.

**This week** shows the newest *published* preview whose week has **not** been played yet. "Played" means the museum has that week's Program recap. So a preview leaves the slot by itself once the Tuesday recap is built and deployed, and drops into **Past weekly previews**. If no preview is current, the slot shows a "Next preview coming soon" card.

**Latest episode** is the highest-numbered published episode.

## Release-day runbook: weekly preview

1. **Video.** Put the file at `public/show/previews/2026-week-NN.mp4`. **It must be under 25 MiB**, the Cloudflare Worker static-asset limit. A 2–3 minute preview at 720p fits easily.
2. **Captions.** If the captions are burned into the video, leave `captions` unset; a separate track would show them twice. If they're not, add `public/show/previews/2026-week-NN.vtt` and set `captions`.
3. **Poster (optional).** Use a frame from the preview, or reuse `/show/studio-poster-v001.webp`.
4. **Catalog.** In `catalog.ts`, update that week's `PREVIEWS` entry:
   - `status: "published"`
   - `released: "YYYY-MM-DD"`
   - `runtime: "m:ss"`
   - check `video`, `poster`, and `programSlug`
   - change `version` whenever a file is replaced, to bust browser caches
5. **Next week.** Add a `draft` entry for the following week, so it's ready.
6. **Check locally:** `npm run typecheck`, then `npm run build`, then `npm run start`. Open `/show` and `/show/previews/week-N`.
7. **Ship:** `npm run deploy`, then commit and push.

## Release-day runbook: episode

Same as a preview, with these changes:
- Use `public/show/episodes/epNN.mp4`. Episode 1 is still served from `public/show/pilot-review.mp4`.
- Fill in `number`, `weeks`, `title`, `dek`, `summary`, and `segments` (the rundown cards).
- Set `status: "published"`. It becomes **Latest episode**, and its season-track dot fills in.

**Episodes and the 25 MiB limit:** a 7–8 minute episode at 720p sits right at the limit. If one won't fit, host it in Cloudflare R2 instead and point `video` at the R2 URL. The hub and pages don't care where the file lives.

## Corrections

Never silently replace a released video. Set `correction` on the item (e.g. `"Corrected Oct 9: Week 5 score for Bears updated after a stat correction."`) and bump `version`. The line appears under the player.

## Open decisions (owner)

- **Episode coverage:** which weeks Episodes 2–4 cover, and whether Episode 4 is the playoffs. Until then the season track shows "Weeks TBA".
- **Preview release day:** for example, Thursday before the first kickoff.
- **Nav link:** whether to add **Show** to the museum's top nav (`app/components/nav-links.tsx`). It's not added yet; the nav is already at eleven items.
