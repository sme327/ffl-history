# Across the Line: show hub

## Episode 2 — Halftime Adjustments V003, LIVE and verified October 28

[Watch Episode 2](https://iwnh.sme327.com/show/episodes/2) · [Show hub](https://iwnh.sme327.com/show). Published with `npm run deploy` from **7ce53d9**, Worker version **49423fc1-0e2d-4d64-a407-4c7beff52ce7**. All twelve changed assets uploaded successfully. Live HTTP QA passes seven pages × three requests, five exact movie hashes/types, fifteen valid HTTP 206 ranges and five invalid-range HTTP 416s. Browser playback/seek/resume passes all six watch routes, including both pilot URLs. Episode 2 is Latest episode; Weeks 7/6/5 are archived. Older movies remain byte-identical. No remaining release failure. Evidence: `episode02-v003-published.json`, `episode02-v003-live-qa.json`, `episode02-v003-live-browser-qa.json`. Registry deployment metadata was updated after the build; `show-static-pages-current.json` preserves its exact build-time page/registry hashes.

Shawn approved the exact V003 review and directed **“go ahead and publish. approved.”** The clean release changes only removal of the review banner: **8:38.03 / 1280×720 / 24,307,526 bytes / 23.18 MiB**, SHA-256 **a69d80788ab38f70183d436f66a34e929fecacf080324e2b3dcd1289949909b2**. FFL Show `OWNER_APPROVAL_V003.json`, `RELEASE_RENDER_V003.json` and `RELEASE_QA_V003.json` bind the approval, 92 complete takes, unchanged captions/cues, all 12,143 identical AAC packets, continuous timestamps and 30 approved-review picture comparisons. V001/V002/V003 reviews remain preserved.

Live route: **/show/episodes/2**, catalog version **20261028-episode02-v003**; Episode 2 is Latest episode. It covers Weeks 4–7 and replaces the Week 8 weekly. Published full retrospectives now also close covered weekly previews, so Week 7 joins Weeks 6/5 in the archive before a Week 7 Program recap exists. The archived Week 7 note points to Episode 2 rather than a missing recap (verified live). No new weekly preview is published.

The existing bounded MP4 range handler now also handles `/show/episodes/*.mp4`; its slicing algorithm and all four older movie files/versions are unchanged. No storage, dependency, account-plan or compatibility-date changes. A dedicated upload gate verifies owner authorization, clean-cut QA and all five exact movie hashes; this retrospective/schedule preview has no current lineup condition to re-check.

Local typecheck, full build, catalog/range tests and Wrangler dry-run pass. Seven pages × three HTTP checks, all five movie hashes/types, fifteen valid ranges/five invalid ranges, and actual browser play/seek/resume on all six watch routes pass. See `episode02-v003-local-qa.json`, `episode02-v003-local-browser-qa.json` and `episode02-v003-qa-attempts.json`. Initial local preview transport resets resolved by independent **local-only** verifier connections; no hash/status/range assertion was relaxed. Production verification kept the original/default connection policy and passed. Local cancelled-stream warnings during seeking did not prevent play/seek/resume; no production streaming-algorithm fix is claimed. Prior live Worker **1de8979e-7ab8-4a21-9394-4ad9dc2ba0ff** is the rollback reference.

## Week 7 V003 — live and verified, October 25

[Watch Week 7](https://iwnh.sme327.com/show/previews/week-7) · [Show hub](https://iwnh.sme327.com/show).

Shawn approved V002 and directed publication, then explicitly waived further lineup verification. The clean V003 changes **only** removal of the review banner; the approved audio, captions, timing, graphics, lineup values and actual October 24 ~8:35 PM PT stamps remain unchanged. No fresh Yahoo certification is claimed. Both messages are recorded in FFL Show `weekly/2026-week-07/OWNER_APPROVAL_V002.json` and the current media registry. The Week 7 upload gate enforces exact hashes, technical QA and this explicit waiver; it does not call Yahoo.

Published with `npm run deploy` from reconciled `show-hub` source `0767e21`, including local Museum main `20d7a16` (Week 6 recap and Week 7 Program preview). **5:37.533, 1280×720, 20,305,858 bytes / 19.37 MiB**, SHA-256 `a4fbfcba698bc232448ee8ba1bc0157283b56ab132f67e46266d07b9206d8a1e`. Worker version **1de8979e-7ab8-4a21-9394-4ad9dc2ba0ff**. The asset uploader retried two network failures, then completed all 11 changed assets successfully; no release check remains failed.

Live HTTP QA passes six pages × three requests, all four movie hashes/bytes/MP4 types, twelve valid HTTP 206 range requests and four invalid-range HTTP 416 responses. Browser QA passes play/seek/resume for Week 7, Week 6, Week 5, `/show/pilot` and `/show/episodes/1`. The hub places Week 7 in **This week**, Episode 1 in **Latest episode**, and Week 6 / Week 5 in the archive. Previous movies are byte-for-byte unchanged. Evidence: `weekly-slate-2026-week-07-v003-live-qa.json`, `weekly-slate-2026-week-07-v003-live-browser-qa.json`, `weekly-slate-2026-week-07-final-upload-check.json`. The exact build-time page hashes remain in `show-static-pages-current.json`; deployment-status metadata was updated only after live verification.

Verified rollback version before this deployment: **ef91292b-82e7-496c-bcbc-2ada04d90e37**, not the older Week 6-only version in historical notes below.

The museum hosts the animated show *Across the Line* (Graham Keeper and Kate Hedges). This page covers how its pages are laid out and how to ship a new weekly preview or episode.

## Week 6 V004 — LIVE and verified, October 16

Shawn approved the exact cut, then separately said “go.” `npm run deploy` rebuilt all five show pages and ran the Week 6 upload gate immediately before publishing. The **11:47 PM Pacific** Yahoo check passed all spoken roster/count conditions. The exact V004 movie was not changed: **4:48.033, 720p, 17,093,176 bytes**, SHA-256 `e98bb81ec17cad4467cc3ea14df98e360f3366c58d43fc28f134c142960b1c4e`. Its card stamps remain the real 7:58 PM PT source capture. Projections moved slightly after that capture; neither those values nor a gap is spoken.

[Watch Week 6](https://iwnh.sme327.com/show/previews/week-6) · [Show hub](https://iwnh.sme327.com/show). Worker version **5bf2389d-d75d-4952-b580-9af07f3d47b8**, deployed source `85cdc25`. Live verification passed 15 repeated page/hash requests, all three full movie hashes/MP4 types, nine valid HTTP 206 ranges, three invalid-range HTTP 416 responses, and browser playback/seek/resume on Week 6, Week 5, `/show/pilot` and `/show/episodes/1`. Week 6 is This week, Episode 1 remains Latest episode, and Week 5 is archived. V008/V034 media are untouched. No known release check failed.

Evidence: `docs/releases/weekly-slate-2026-week-06-v004-published.json`, `weekly-slate-2026-week-06-final-upload-check.json`, `weekly-slate-2026-week-06-v004-live-qa.json`, and `weekly-slate-2026-week-06-v004-live-browser-qa.json`. Current-registry deployment status was updated after the build; `show-static-pages-current.json` retains its exact build-time registry/page hashes. The earlier staged report remains historical and its false deployment flag is not current status. Previous Worker version `a9b2dadd-a368-4c70-a46e-9879307e22e5` is retained for rollback.

## Historical Week 6 V004 staging (subsequently published above)

Shawn approved the exact V004 cut on October 16: SHA-256 `e98bb81ec17cad4467cc3ea14df98e360f3366c58d43fc28f134c142960b1c4e`, 17,093,176 bytes, 720p, 4:48.033. Evidence: FFL Show `weekly/2026-week-06/OWNER_APPROVAL_V004.json`. Deployment authorization is **not** included in that approval.

Prepared on `show-hub`, reconciled with fetched `origin/main` baseline `c6d59ba`. The local catalog marks Week 6 published at `/show/previews/week-6`, version `20261016-slate-v004`, with Week 7 hidden as a draft. This is local staging only. The current media registry adds its exact hash/bytes and watch route; its deployment fields remain false. Week 5 V008 and pilot V034 movie hashes/versions are unchanged. The five generated pages now put Week 6 in This week, Episode 1 in Latest episode and Week 5 in the archive.

Local checks pass: typecheck, complete data/site build, 15 repeated page requests, all three movie hashes and MP4 types, prefix/suffix/open-range HTTP 206 and invalid-range HTTP 416. Automated browser tests confirm the hub slots/archive and play/seek/resume on all four watch URLs. Reports: `docs/releases/weekly-slate-2026-week-06-v004-local-qa.json`, `weekly-slate-2026-week-06-v004-local-browser-qa.json`, and `weekly-slate-2026-week-06-v004-staged.json`. Browser tests were muted technical checks; human listening acceptance came from Shawn, not the test.

The local runtime logged `Network connection lost` during automated video seeking/navigation. All browser players still advanced after the seek with no media error, and all HTTP checks passed. Likely cause is cancellation of an in-flight video stream (inference); no runtime fix is claimed. The staged report records this warning; repeat functional checks live rather than waiving an actual playback/range failure.

The active branch in `scripts/verify-weekly-deploy-lineups.mjs` stops **before capture/upload** unless both repositories record explicit deployment approval for this exact hash. After go, it checks all media bytes/hashes, runs the isolated Week 6 read-only Yahoo checker after the build, and requires fresh Rodgers/Young, Fuzzy Bears, Mixon and transaction/Move spoken conditions. It logs current card numbers without relabelling the approved movie's actual 7:58 PM PT capture stamps. The old Week 5 opt-in branch remains historical; never run the retired `verify-weekly-show-release.mjs`.

After explicit go: record the actual message in both approval records and enable deployment approval on the Week 6 registry item; reconcile current main, update the catalog release date if the day changed, run `npm run deploy` **without** the old Week 5 flag, and verify `/show`, Week 6, Week 5 and both pilot URLs against the current registry. Browser QA: `python3 scripts/verify-show-browser.py BASE_URL NEW_REPORT_PATH`. HTTP/hash/range QA: `node scripts/verify-corrected-show-release.mjs BASE_URL NEW_REPORT_PATH`. Preserve historical reports. Merge/push only after authorized publication and live QA. Previous live Worker version `a9b2dadd-a368-4c70-a46e-9879307e22e5` remains the rollback target. No Week 6 upload has occurred.

## Live consolation corrections: V008 / V034

The owner approved the exact Week 5 Slate V008 and Pilot V034 cuts, then explicitly said “go” on October 15. Both are deployed and live-verified. Worker version: `a9b2dadd-a368-4c70-a46e-9879307e22e5`; deployed source: `03cab90`. Approval binds the unchanged SHA-256 values in `docs/releases/show-media-current.json`. [Week 5](https://iwnh.sme327.com/show/previews/week-5) · [Pilot](https://iwnh.sme327.com/show/pilot) · [Episode 1](https://iwnh.sme327.com/show/episodes/1).

Live evidence: `docs/releases/consolation-v008-v034-live-qa.json` (four pages × three checks, both full movie hashes/MIME/bytes, six valid 206 range checks and two invalid-range 416 checks) and `consolation-v008-v034-browser-qa.json` (all three players play/seek/resume; hub and expanded archive verified). An upload network retry and the first post-deploy page hash mismatch resolved before final verification. No known failure remains. Deployment status metadata was updated after the build; `show-static-pages-current.json` retains the exact build-time registry hash and generated page hashes. No movie was re-rendered after approval.

`docs/releases/show-media-current.json` is the current media registry: movie paths, exact bytes/hash, catalog versions, watch routes and recorded owner approval. `worker/index.ts` uses its file lengths for range responses rather than V007's historical release report. Preserve that old report and all old live QA.

`scripts/build-show-pages.mjs` now takes its routes and expected catalog versions from this registry and writes `docs/releases/show-static-pages-current.json`. Add future published movie/watch routes to the registry. Other Museum pages retain their existing rendering. `scripts/verify-corrected-show-release.mjs BASE_URL NEW_QA_PATH` checks exact movie bytes/hash, MP4 content type, prefix/suffix/open ranges, invalid-range 416, repeated static pages and the declared hub state. It refuses to overwrite a previous QA report. Browser playback and seeking are separate checks after authorized deployment.

Week 5 has been played and belongs in Past weekly previews, not This Week. The expected current slot is the coming-soon card until another weekly is published; Episode 1 remains Latest Episode. Do not rerun the retired V007 verifier or its old current-lineup upload gate for these historical correction cuts.

After explicit go: reconcile current main, run `npm run deploy` with no old `FFL_VERIFY_WEEK5_LINEUPS=1` flag, verify all four watch/hub routes and both movies, then merge/push the verified source. The current registry and versioned correction staging report bind the movies approved by the owner.

## Correction background: Week 5 Slate (V008) and pilot (V034)

V007 and the pilot V033 state series records under the old count. On 2026-10-14 the commissioner
ruled that consolation games don't count anywhere (`docs/reviews/CONSOLATION-RULING-2026-10-14.md`)
and approved eight replacement lines: five in the Slate, three Kate lines in the pilot. The FFL Show
repo holds the retake briefs and requests (commit `3f16cff`):
`weekly/2026-week-05/CONSOLATION_CORRECTION_RETAKE.md` and
`episodes/001-rivalry-round-one/CONSOLATION_CORRECTION_RETAKE.md`. Grok records; Codex swaps the
takes, fixes the hard-coded card numbers, re-renders and stages both releases. Each cut needs the
owner's ear-check, exact-cut approval and deploy go. Until then the live videos stay as they are.

## Historical Week 5 release: V007 (superseded after V008 deployment)

**Live and verified October 8.** [Watch Week 5](https://iwnh.sme327.com/show/previews/week-5) · [Show hub](https://iwnh.sme327.com/show). Worker version `d49f0a30-6819-41fa-bf14-4d74fffef385`, deployed source `37c4347`. The final Yahoo capture was **11:58 AM Pacific**, and all three spoken configurations passed. Twelve repeat show-page requests match the built HTML; both movie hashes, prefix/suffix/open-range requests and unsatisfiable-range responses pass. Week 5 browser playback and seeking resume correctly, and the unchanged V033 pilot plays. Initial seeking and page-limit failures were repaired before the main-branch handoff. No known release failure remains. See the release manifest, live QA, browser QA and final-lineup report.

The owner authorized deployment after trimming Decision to Watch. Graham 116 now ends at “leading scorer”; Kate 116 is unchanged. The score card shows SHOUGH 14.13 START / STROUD 14.28 BENCH and stays through Kate's full response. Its stamp remains the actual data-check time, **THU 10:11 AM PT**. No projection gap is spoken or tested.

The clean V007 export is **4:41.200, 1280×720, 30 fps, 20,758,353 bytes (19.80 MiB)**. The catalog uses `20261008-slate2-v007` and `4:41`. The manifest binds its checksum and records explicit deployment authorization. The branch already merged main's Week 4 recap `f60ca86` via `58e7175`.

Deploy from this checkout with `FFL_VERIFY_WEEK5_LINEUPS=1 npm run deploy`. The opt-in gate runs after the full build and immediately before upload: fresh Yahoo selections must still show Kittle/Stevenson starting, Waddle starting/Wilson benched, and Shough starting/Stroud benched. It writes a sanitized final-check report and stops upload on any failure. Raw Yahoo pages and session data stay ignored in the show checkout. The final check does not pretend the displayed projections were captured later than their stamp.

After deployment run `node scripts/verify-weekly-show-release.mjs https://iwnh.sme327.com --live` (retired 2026-10-14; see "Retired: the Week 5 release verifier" below); verify the hub's This week / Latest episode slots, actual playback and seeking, then merge show-hub into Museum main and push. Preserve prior Worker version `bcc35893-80e0-4375-9016-d8c3a4b1524a` for rollback. The pilot in this branch is V033, not V031; verify its known hash and playback.

Before the merge, the original main checkout's dirty work was saved in retained stash `07ccd67d30fa61a44adbd5d6e057f332512c1a38`. Restore its three unrelated Week 5 Program drafts afterward. Do not apply the overlapping old CSS/pilot-route changes over the approved hub; they remain recoverable in the retained stash. Do not stage the deployment checkout's `node_modules` symlink.

### Video seeking repair

The first V007 upload (`c17e22db-2d97-4c3f-9e50-6597047a19e9`) served the correct movie but ignored Range requests: HTTP 200, and the browser could play but could not seek ahead. This failed release QA and was not merged to main. `worker/video-range.ts` now streams single byte ranges for show videos only. `vite.config.ts` routes the preview MP4s and pilot movie through the Worker before the static asset handler. All other routes retain asset-first behavior. There are no new paid storage resources, secrets or domain changes.

The internal asset binding omits a length in this runtime; the two checksummed release files use their verified byte lengths in the release manifest. Keep those lengths updated with future movie replacements. The slice streams to a [FixedLengthStream](https://developers.cloudflare.com/workers/runtime-apis/streams/transformstream/#fixedlengthstream), so its actual bytes and Content-Length agree. Source streams are cancelled after the interval and promises are attached to the request lifetime. No entire movie is buffered. Routing follows Cloudflare's [selective Worker-first configuration](https://developers.cloudflare.com/workers/static-assets/routing/worker-script/#run-worker-first-for-selective-paths).

`node scripts/test-video-range.mjs`, generated binding types, type checking and local Workers-runtime QA pass. Local Week 5 prefix and pilot suffix requests return HTTP 206 with correct bytes. Repeat live range checks and browser playback/seek after the repair deployment; do not waive the production range guard.

### Show-page rendering repair

Live verification also caught intermittent HTTP 503 / Cloudflare 1102 failures on the hub and preview. A later check passing did not erase those failures. `scripts/build-show-pages.mjs` now renders exactly four public routes with the installed vinext production server at build time: `/show`, `/show/previews/week-5`, `/show/pilot`, and `/show/episodes/1`. It preflights all four before writing generated HTML into `dist/client`; the existing static asset router serves the clean URLs. The pages regenerate with every deployment, after catalog and Program data changes. Other museum routes remain unchanged SSR. No account-plan or paid-resource change was made.

The live verifier compares these pages against their generated HTML hashes and repeats all four requests three times. Current-snapshot authentication remains outside the build, in the separate final upload gate. Static page generation does not touch the episode, its stamped facts, or either MP4 checksum. Add future published watch routes to this narrow build list.

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
6. **Check locally:** `npm run typecheck`, then `npm run build`. Use the built Cloudflare preview for media checks (`wrangler dev --local --config dist/server/wrangler.json`); the generic Node preview may use the wrong MP4 content type. Open `/show` and `/show/previews/week-N`. (The Week 5 release verifier is retired; see below. Until a general one exists, check the hub slots, playback, content type, bytes/hash and byte-range seeking by hand.)
7. **Hold for owner authorization.** A local catalog value of `published` is not permission to deploy. Commit the staged release; do not deploy or push until explicitly authorized. If lineups have become stale, refresh them and replace changed exchanges before deployment.
8. **Ship only after “go”:** `npm run deploy`, then verify the new public page, content type, bytes/hash, and byte-range seeking before reporting it live. Preserve the previous deployment for rollback.

## Retired: the Week 5 release verifier

`scripts/verify-weekly-show-release.mjs` was the one-time release gate for Week 5 V007. It is
retired as of 2026-10-14 (owner decision) and must not be rerun:

- It expects the Week 5 preview in **This week**, which stopped being true, by design, once the
  Week 5 recap shipped.
- It compares pages against the Week 5 build snapshot, which every later build rewrites.
- A rerun overwrites `docs/releases/weekly-slate-2026-week-05-live-qa.json`, the recorded evidence
  of the V007 release.

Its record of V007 stays in `docs/releases/`. The checks it ran (byte-range seeking, movie and pilot
hashes, burned-in captions only, no dead Program link, repeated build-time page fetches) are the
checklist for the next release. If that release wants a script, write a general one that reads the
release manifest it is shipping and knows a preview leaves **This week** once its recap exists.

`scripts/build-show-pages.mjs` is **not** retired: `npm run build` runs it on every deploy. The
V008/V034 staging change replaces its Week 5 hard-coded routes and old report path with
`show-media-current.json` and `show-static-pages-current.json`, as described above. The recorded
Week 5 release QA remains historical evidence, not a mutable gate for future releases.

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
