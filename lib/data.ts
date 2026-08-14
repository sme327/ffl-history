/**
 * Typed access to the league history emitted by scripts/build_site_data.py.
 *
 * The Python pipeline stays the source of truth for every derivation — this
 * file only reads what it wrote. Run `npm run data` (or `npm run build`) to
 * regenerate build/data before building the site.
 *
 * Everything is bundled into the Worker at build time: the full archive is
 * ~0.3MB gzipped, far inside the size limit, and bundling means no runtime
 * fetch and no cold-start penalty on a page view.
 */

const files = import.meta.glob("../build/data/**/*.json", {
  eager: true,
  import: "default",
}) as Record<string, unknown>;

/** "../build/data/managers/shawn.json" -> "managers/shawn" */
function routeKey(path: string): string {
  return path.replace("../build/data/", "").replace(/\.json$/, "");
}

const byRoute = new Map<string, unknown>(
  Object.entries(files).map(([path, value]) => [routeKey(path), value]),
);

function read<T>(route: string): T {
  const value = byRoute.get(route);
  if (value === undefined) {
    throw new Error(
      `Missing build/data/${route}.json — run \`npm run data\` to regenerate it.`,
    );
  }
  return value as T;
}

function readMaybe<T>(route: string): T | null {
  return (byRoute.get(route) as T) ?? null;
}

// ── Types ─────────────────────────────────────────────────────────────────────
// Only the fields the site reads. The JSON carries more; these are the contract.

export type Site = {
  leagueName: string;
  subtitle: string;
  founded: number;
  currentSeason: number;
  managerColors: Record<string, string>;
  managerEmoji: Record<string, string>;
};

export type ManagerIndexEntry = {
  slug: string;
  name: string;
  displayName: string;
  firstSeason: number;
  lastSeason: number;
  championships: number;
  active: boolean;
};

export type ManagerSeason = {
  season: number;
  team_name: string;
  wins: number;
  losses: number;
  ties: number;
  points_for: number;
  rank: number | null;
  result: string;
  category: string;
  win_pct: number | null;
};

export type HeadToHead = {
  opp_manager: string;
  opp_emoji: string;
  opp_active: boolean;
  games: number;
  wins: number;
  losses: number;
  win_pct: number;
  pf: number;
  pa: number;
};

export type ManagerProfile = {
  slug: string;
  name: string;
  display_name: string;
  emoji: string;
  color: string;
  active: boolean;
  status_label: string;
  metrics: {
    championships: number;
    runner_ups: number;
    playoff_apps: number;
    seasons_played: number;
    playoff_rate: number;
    record: string;
    win_pct: number;
    finals_apps: number;
  };
  championship_years: number[];
  plaque: string;
  identity: string;
  seasons: ManagerSeason[];
  head_to_head: HeadToHead[];
  team_names: { team_name: string; years: string }[];
  draft: {
    style: string;
    style_color: string;
    keeper_rate: number;
    most_drafted: { player: string; count: number };
    most_kept: { player: string; count: number };
  } | null;
};

export type KeeperChain = {
  player_name: string;
  position: string;
  primary_manager: string;
  all_managers: string[];
  franchise_id: string;
  seasons: number[];
  streak_len: number;
  titles: number;
  playoffs: number;
  score: number;
  multi_manager: boolean;
};

export type KeeperDna = {
  manager: string;
  emoji: string;
  color: string;
  keeper_count: number;
  keeper_rate: number;
  favourite: { player: string; count: number };
  longest_streak: number;
  longest_streak_player: string;
  titles: number;
  dna: string;
  dna_blurb: string;
  position_counts: Record<string, number>;
};

export type KeeperHall = {
  immortals: KeeperChain[];
  notable_chains: KeeperChain[];
  champions_kept: {
    player_name: string;
    position: string;
    title_count: number;
    seasons: number[];
    managers: string[];
  }[];
  manager_dna: KeeperDna[];
  most_kept: { player_name: string; position: string; count: number }[];
  totals: { keepers: number; unique_players: number; chains: number; managers: number };
};

export type PlayerOwnership = {
  player_name: string;
  manager: string;
  franchise_id: string;
  position: string | null;
  draft_count: number;
  keeper_count: number;
  total_seasons: number;
  seasons: number[];
  first_season: number;
  last_season: number;
};

export type HomeView = {
  stats: {
    seasons: number;
    active_managers: number;
    unique_champions: number;
    total_games: number;
  };
  current_champion: {
    season: number;
    manager: string;
    team: string;
    emoji: string;
    score: number;
    runner_up_team: string;
    runner_up_score: number;
    titles_all_time: number;
  } | null;
  legends: { manager: string; titles: number; years: string; emoji: string }[];
  drought: { manager: string; playoff_apps: number; emoji: string } | null;
  storylines: {
    best_season: { record: string; seasons: number[]; summary: string };
    top_scorer: { manager: string; points_for: number };
  };
};

export type ChampionsView = {
  totals: { seasons: number; titles_awarded: number; unique_managers: number };
  manager_leaders: {
    manager: string; emoji: string; championships: number; years: string;
    finals_apps: number; titles: number; runner_ups: number; win_pct: number;
  }[];
  dynasties: {
    manager: string; emoji: string; championships: number; years: string;
    era_desc: string; consecutive: boolean; titles: number; finals_apps: number;
  }[];
  chronological: {
    manager: string; emoji: string; championships: number; year_list: number[];
  }[];
  trivia: Record<string, any>;
  pain: Record<string, any>;
  finals: {
    season: number; emoji: string;
    champion_manager: string; champion_team: string; champion_score: number;
    runner_up_manager: string; runner_up_team: string; runner_up_score: number;
    margin: number;
  }[];
};

export type LeagueHistory = {
  eras: {
    name: string; short: string; years: string; color: string; icon: string;
    headline: string; body: string; titles_awarded: number;
    unique_champions: number; avg_score: number;
    champions: { season: number; manager: string; emoji: string }[];
  }[];
  era_bands: { start: number; end: number; label: string; color: string; fill: string }[];
  scoring: {
    by_season: { season: number; avg: number; high: number; low: number }[];
    champion_points: { season: number; points_for: number }[];
    peak: { season: number; avg: number };
    lean: { season: number; avg: number };
    rise: number;
  };
  balance: {
    unique_champions: number; total_seasons: number; diversity_rate: number;
    playoff_managers_ever: number;
    most_consistent: { manager: string; appearances: number; emoji: string } | null;
    title_counts: { manager: string; titles: number }[];
    top1_pct: number; top3_pct: number;
  };
  records: Record<string, any>;
};

export type SeasonIndexEntry = { season: number; title: string | null; champion: string | null };

export type SeasonDetail = {
  season: number;
  title: string | null;
  hook: string | null;
  narrative: string | null;
  nfl_context: string[];
  champion: {
    manager: string; team: string; emoji: string; score: number; margin: number;
    runner_up_manager: string; runner_up_team: string; runner_up_score: number;
  } | null;
  standings: {
    result: string; team: string; manager: string; emoji: string;
    wins: number; losses: number; ties: number; points_for: number; rs_rank: number;
  }[];
  bracket: {
    rounds: {
      type: string; label: string;
      games: {
        seed_1: number | null; team_1: string; score_1: number;
        seed_2: number | null; team_2: string; score_2: number; winner: string;
      }[];
    }[];
    third_place: unknown | null;
  };
  top_scorers: { rank: number; team: string; manager: string; emoji: string; points_for: number }[];
};

export type TimelineEvent = {
  season: number; icon: string; color: string; label: string;
  importance: string; importance_label: string;
  title: string; description: string;
  manager: string; manager_emoji: string; franchise_id: string;
  is_editorial: boolean; era: { name: string; color: string };
  show_on_league_timeline: boolean;
};

export type Timeline = {
  events: TimelineEvent[];
  stats: {
    total_events: number; total_seasons: number;
    computed_events: number; editorial_events: number;
  };
  bySeason: {
    season: number; era: { name: string; color: string };
    count_label: string; high: TimelineEvent[]; other: TimelineEvent[];
  }[];
};

// ── Accessors ─────────────────────────────────────────────────────────────────

export const site = read<Site>("site");
export const home = read<HomeView>("home");
export const keeperHall = read<KeeperHall>("keepers");
export const managerIndex = read<ManagerIndexEntry[]>("managers/index");
export const playerOwnership = read<PlayerOwnership[]>("player-ownership");
export const championsView = read<ChampionsView>("champions-view");
export const seasonIndex = read<SeasonIndexEntry[]>("seasons/index");
export const timeline = read<Timeline>("timeline");
export const leagueHistory = read<LeagueHistory>("league-history");

export function seasonDetail(year: string | number): SeasonDetail | null {
  return readMaybe<SeasonDetail>(`seasons/${year}`);
}

export function managerProfile(slug: string): ManagerProfile | null {
  return readMaybe<ManagerProfile>(`managers/${slug}`);
}

/** Mirrors slugify() in scripts/build_site_data.py — the two must agree. */
export function slugify(value: string): string {
  return value
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/['’]/g, "")
    .replace(/[^a-zA-Z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .toLowerCase();
}

const slugToManager = new Map(managerIndex.map((m) => [m.slug, m.name]));
export function managerFromSlug(slug: string): string | null {
  return slugToManager.get(slug) ?? null;
}

// ── Keeper views, the entry points Keeper Hall was missing ────────────────────

export function keeperChainsFor(manager: string): KeeperChain[] {
  return keeperHall.immortals.filter((chain) =>
    chain.all_managers.includes(manager),
  );
}

export function keeperDnaFor(manager: string): KeeperDna | null {
  return keeperHall.manager_dna.find((d) => d.manager === manager) ?? null;
}

export type PlayerHistory = {
  playerName: string;
  position: string | null;
  owners: PlayerOwnership[];
  totalDrafts: number;
  totalKeepers: number;
  totalSeasons: number;
  firstSeason: number;
  lastSeason: number;
  chains: KeeperChain[];
};

const ownershipByPlayer = new Map<string, PlayerOwnership[]>();
for (const row of playerOwnership) {
  const rows = ownershipByPlayer.get(row.player_name) ?? [];
  rows.push(row);
  ownershipByPlayer.set(row.player_name, rows);
}

export const playerIndex = [...ownershipByPlayer.keys()]
  .map((name) => ({ name, slug: slugify(name) }))
  .sort((a, b) => a.name.localeCompare(b.name));

const slugToPlayer = new Map(playerIndex.map((p) => [p.slug, p.name]));

export function playerHistory(slug: string): PlayerHistory | null {
  const name = slugToPlayer.get(slug);
  if (!name) return null;

  const owners = [...(ownershipByPlayer.get(name) ?? [])].sort(
    (a, b) =>
      b.total_seasons - a.total_seasons || a.manager.localeCompare(b.manager),
  );
  if (owners.length === 0) return null;

  return {
    playerName: name,
    position: owners.find((o) => o.position)?.position ?? null,
    owners,
    totalDrafts: owners.reduce((sum, o) => sum + o.draft_count, 0),
    totalKeepers: owners.reduce((sum, o) => sum + o.keeper_count, 0),
    totalSeasons: owners.reduce((sum, o) => sum + o.total_seasons, 0),
    firstSeason: Math.min(...owners.map((o) => o.first_season)),
    lastSeason: Math.max(...owners.map((o) => o.last_season)),
    chains: keeperHall.immortals.filter((c) => c.player_name === name),
  };
}
