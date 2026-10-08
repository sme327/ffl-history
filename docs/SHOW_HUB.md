# Across the Line: show hub

The museum hosts the animated show *Across the Line* (Graham Keeper and Kate Hedges). This page covers how its pages are laid out and how to ship a new weekly preview or episode.

## Current Week 5 release: V007

The owner authorized deployment after trimming Decision to Watch. Graham 116 now ends at “leading scorer”; Kate 116 is unchanged. The score card shows SHOUGH 14.13 START / STROUD 14.28 BENCH and stays through Kate's full response. Its stamp remains the actual data-check time, **THU 10:11 AM PT**. No projection gap is spoken or tested.

The clean V007 export is **4:41.200, 1280×720, 30 fps, 20,758,353 bytes (19.80 MiB)**. The catalog uses `20261008-slate2-v007` and `4:41`. The manifest binds its checksum and records explicit deployment authorization. The branch already merged main's Week 4 recap `f60ca86` via `58e7175`.

Deploy from this checkout with `FFL_VERIFY_WEEK5_LINEUPS=1 npm run deploy`. The opt-in gate runs after the full build and immediately before upload: fresh Yahoo selections must still show Kittle/Stevenson starting, Waddle starting/Wilson benched, and Shough starting/Stroud benched. It writes a sanitized final-check report and stops upload on any failure. Raw Yahoo pages and session data stay ignored in the show checkout. The final check does not pretend the displayed projections were captured later than their stamp.

After deployment run `node scripts/verify-weekly-show-release.mjs https://iwnh.sme327.com --live`; verify the hub's This week / Latest episode slots, actual playback and seeking, then merge show-hub into Museum main and push. Preserve prior Worker version `bcc35893-80e0-4375-9016-d8c3a4b1524a` for rollback. The pilot in this branch is V033, not V031; verify its known hash and playback.

Before the merge, the original main checkout's dirty work was saved in retained stash `07ccd67d30fa61a44adbd5d6e057f332512c1a38`. Restore its three unrelated Week 5 Program drafts afterward. Do not apply the overlapping old CSS/pilot-route changes over the approved hub; they remain recoverable in the retained stash. Do not stage the deployment checkout's `node_modules` symlink.

### Video seeking repair

The first V007 upload (`c17e22db-2d97-4c3f-9e50-6597047a19e9`) served the correct movie but ignored Range requests: HTTP 200, and the browser could play but could not seek ahead. This failed release QA and was not merged to main. `worker/video-range.ts` now streams single byte ranges for show videos only. `vite.config.ts` routes the preview MP4s and pilot movie through the Worker before the static asset handler. All other routes retain asset-first behavior. There are no new paid storage resources, secrets or domain changes.

The internal asset binding omits a length in this runtime; the two checksummed release files use their verified byte lengths in the release manifest. Keep those lengths updated with future movie replacements. The slice streams to a [FixedLengthStream](https://developers.cloudflare.com/workers/runtime-apis/streams/transformstream/#fixedlengthstream), so its actual bytes and Content-Length agree. Source streams are cancelled after the interval and promises are attached to the request lifetime. No entire movie is buffered. Routing follows Cloudflare's [selective Worker-first configuration](https://developers.cloudflare.com/workers/static-assets/routing/worker-script/#run-worker-first-for-selective-paths).

`node scripts/test-video-range.mjs`, generated binding types, type checking and local Workers-runtime QA pass. Local Week 5 prefix and pilot suffix requests return HTTP 206 with correct bytes. Repeat live range checks and browser playback/seek after the repair deployment; do not waive the production range guard.

## Historical V006 release preparation (superseded)

The owner approved Weekly Slate V005 and requested the clean 720p release on October 8. **Do not deploy until the owner says go.** Week 5 is marked `published` only in the prepared local branch; it is not live yet. The branch includes the Week 4 recap through merge `58e7175`, containing main's `f60ca86`.

The video belongs at `public/show/previews/2026-week-05.mp4`, with burned-in captions and no separate VTT track. The catalog uses runtime `4:47`, release date `2026-10-08`, and version `20261008-slate2-v006`. The matching Week 5 Program draft is outside this branch; the player suppresses that link until its issue exists in the built Program index.

Local type checking, history-data generation and the complete vinext build passed. Cloudflare's local preview serves `/show`, `/show/previews/week-5`, both pilot URLs and the Week 4 recap successfully. It serves the clean 20,918,660-byte release as `video/mp4` with the expected hash. The release is 4:46.933, 1280×720 at 30 fps, with all 38 takes and no lineup cuts. The final lineup check is October 8 at 8:48 AM Pacific. Evidence is in `docs/releases/weekly-slate-2026-week-05.json` and `docs/releases/weekly-slate-2026-week-05-local-qa.json`.

The local Miniflare asset handler returns a full 200 response to Range requests. **Production byte-range seeking remains unverified**, explicitly recorded in QA; check the new public video's HTTP 206 response and browser seeking after authorized deployment. No production-serving changes were made to work around this local limitation. The verifier is strict by default; `--allow-local-no-range` records this exception without marking the range check passed.

The original main checkout's uncommitted pilot and Week 5 Program edits are preserved separately and must not be reset or overwritten. If deployment is delayed, refresh the lineup check and rebuild any changed exchange before going live. The show repository's `weekly/2026-week-05/RELEASE_BUILD_NOTES.md` holds the release evidence and checkout path. This preparation is local only, with no push or deployment.

The branch's pilot MP4 already matches the verified live V033 delivery: SHA-256 `7efaea2692c49d8fb51e51b52718c6a531deddd7a62d3d1831f9126ca773e383`, 24,291,141 bytes. Its stale V031 catalog comment/cache version is corrected to V033; the media itself is unchanged.

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
6. **Check locally:** `npm run typecheck`, then `npm run build`. Use the built Cloudflare preview for media checks (`wrangler dev --local --config dist/server/wrangler.json`); the generic Node preview may use the wrong MP4 content type. Open `/show` and `/show/previews/week-N`. For Week 5, `node scripts/verify-weekly-show-release.mjs http://127.0.0.1:4186 --allow-local-no-range` records local evidence and the pending production-range check.
7. **Hold for owner authorization.** A local catalog value of `published` is not permission to deploy. Commit the staged release; do not deploy or push until explicitly authorized. If lineups have become stale, refresh them and replace changed exchanges before deployment.
8. **Ship only after “go”:** `npm run deploy`, then verify the new public page, content type, bytes/hash, and byte-range seeking before reporting it live. Preserve the previous deployment for rollback.

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
