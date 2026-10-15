import { recapIndex } from "@/lib/data";

/**
 * Across the Line: everything the show has released or planned.
 *
 * This file is the only thing to edit when a new episode or weekly preview
 * ships (see docs/SHOW_HUB.md). The hub (/show), each item's own page, and
 * the "This Week" / "Latest Episode" slots all derive from it.
 *
 * Status:
 *   published  live on the site
 *   draft      prepared but hidden; flip to published on release day
 *   planned    an upcoming episode, shown dimmed on the season track (no link)
 */

export const SHOW_SEASON = 2026;

export type ShowSegment = { title: string; detail: string; type: string };

type ItemBase = {
  title: string;
  /** One line under the title. */
  dek?: string;
  status: "published" | "draft" | "planned";
  /** ISO date (YYYY-MM-DD) the item went live. */
  released?: string;
  /** Display runtime, e.g. "7:45". */
  runtime?: string;
  /** Files under public/. `version` busts browser caches when a file is replaced. */
  video?: string;
  /** A separate WebVTT track. Leave unset when captions are burned into the video, or they show twice. */
  captions?: string;
  poster?: string;
  version?: string;
  summary?: string;
  segments?: ShowSegment[];
  /** The Program issue this item pairs with, e.g. "2026-week-05". */
  programSlug?: string;
  /** Visible correction line, e.g. "Corrected Oct 6: …". Never silently edit a release. */
  correction?: string;
};

export type ShowEpisode = ItemBase & {
  kind: "episode";
  number: number;
  /** Weeks covered, inclusive. Omit until decided for planned episodes. */
  weeks?: [number, number];
};

export type ShowPreview = ItemBase & {
  kind: "preview";
  /** The week being previewed. */
  week: number;
};

export type ShowItem = ShowEpisode | ShowPreview;

export const EPISODES: ShowEpisode[] = [
  {
    kind: "episode",
    number: 1,
    weeks: [1, 3],
    title: "Rivalry Round One",
    dek: "The Standings Are Lying",
    status: "published",
    released: "2026-10-04",
    runtime: "7:45",
    video: "/show/pilot-review.mp4",
    // Correction candidate V034 has burned-in captions; do not duplicate them.
    poster: "/show/studio-poster-v001.webp",
    version: "20261014-v034-consolation-720p",
    correction: "Corrected Oct 14: head-to-head history excludes consolation games.",
    summary:
      "Three weeks of division games, and every division finished with the exact same standings. Graham Keeper and Kate Hedges explain what that hides.",
    segments: [
      { title: "Coach’s Challenge", detail: "One lineup swap, one overturned ruling.", type: "Cold open" },
      { title: "The Standings, Corrected", detail: "Same record. Very different roads.", type: "League recap" },
      { title: "Kittle Watch", detail: "A tight end. An ongoing situation.", type: "Developing story" },
      { title: "The Evidence Locker", detail: "The bench has entered the conversation.", type: "Official findings" },
      { title: "One Last Item", detail: "Graham files the week’s benches.", type: "Closing" },
    ],
  },
  { kind: "episode", number: 2, title: "Episode 2", status: "planned" },
  { kind: "episode", number: 3, title: "Episode 3", status: "planned" },
  { kind: "episode", number: 4, title: "Episode 4", status: "planned" },
];

export const PREVIEWS: ShowPreview[] = [
  {
    kind: "preview",
    week: 5,
    title: "Week 5 Weekly Slate",
    dek: "Week 4 review · Week 5 preview",
    status: "published",
    released: "2026-10-08",
    video: "/show/previews/2026-week-05.mp4",
    // Captions are burned into the approved release; do not show them twice.
    poster: "/show/studio-poster-v001.webp",
    version: "20261014-slate2-v008-consolation",
    runtime: "4:39",
    correction: "Corrected Oct 14: series, streaks and last meetings exclude consolation games; Game 3 historical scores corrected.",
    summary:
      "Six Week 4 results, the Box Score, cross-division progress, Ramirez’s Second Opinion, and all six Week 5 previews.",
    programSlug: "2026-week-05",
  },
];

// ---------------------------------------------------------------- helpers

const isLive = (i: ShowItem) => i.status === "published";

export const publishedEpisodes = () => EPISODES.filter(isLive).sort((a, b) => a.number - b.number);
export const publishedPreviews = () => PREVIEWS.filter(isLive).sort((a, b) => a.week - b.week);

export function latestEpisode(): ShowEpisode | null {
  const eps = publishedEpisodes();
  return eps[eps.length - 1] ?? null;
}

/** A preview's games have been played once the museum has that week's recap. */
export function previewPlayed(p: ShowPreview): boolean {
  return recapIndex.some((r) => r.season === SHOW_SEASON && r.week === p.week);
}

/** The newest published preview whose week is still to be played, else null. */
export function currentPreview(): ShowPreview | null {
  const live = publishedPreviews().filter((p) => !previewPlayed(p));
  return live[live.length - 1] ?? null;
}

/** Every other published preview, newest first. */
export function pastPreviews(): ShowPreview[] {
  const cur = currentPreview();
  return publishedPreviews()
    .filter((p) => p !== cur)
    .reverse();
}

export const episodeHref = (e: ShowEpisode) => `/show/episodes/${e.number}`;
export const previewHref = (p: ShowPreview) => `/show/previews/week-${p.week}`;
export const itemHref = (i: ShowItem) => (i.kind === "episode" ? episodeHref(i) : previewHref(i));

export const weeksLabel = (e: ShowEpisode) =>
  e.weeks ? (e.weeks[0] === e.weeks[1] ? `Week ${e.weeks[0]}` : `Weeks ${e.weeks[0]}–${e.weeks[1]}`) : "Weeks TBA";

export const withVersion = (path: string | undefined, version?: string) =>
  path && version ? `${path}?v=${version}` : path;

export function releasedLabel(iso?: string) {
  if (!iso) return "";
  const d = new Date(`${iso}T12:00:00Z`);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "UTC" });
}

export const findEpisode = (n: number) => EPISODES.find((e) => e.number === n && isLive(e)) ?? null;
export const findPreview = (w: number) => PREVIEWS.find((p) => p.week === w && isLive(p)) ?? null;
