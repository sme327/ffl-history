/**
 * The Recap — the Program's Tuesday tab. Facts come precomputed from
 * scripts/build_recap.py; this module only phrases them. Nothing here
 * invents a claim: every sentence is a template over a value already in the
 * Recap JSON. Dynasty 22's museum carries a sibling of this file — keep the
 * award labels and phrasing in step.
 */

import type { Recap, RecapGame, RecapPlayer, RecapRecord, RecapSeriesNote } from "./data";
import { shortName } from "./program-names";

export const FIRST_SEASON = 2001;

export function pts(n: number | null | undefined): string {
  return n == null ? "—" : n.toFixed(2);
}

export function signed(n: number): string {
  return `${n >= 0 ? "+" : "−"}${Math.abs(n).toFixed(2)}`;
}

export function ordinal(n: number): string {
  const mod100 = n % 100;
  if (mod100 >= 11 && mod100 <= 13) return `${n}th`;
  return `${n}${({ 1: "st", 2: "nd", 3: "rd" } as Record<number, string>)[n % 10] ?? "th"}`;
}

function nameOf(_recap: Recap, key: string | undefined | null): string {
  return key ? shortName(key) : "";
}

/** "Shawn leads 6–2" / "Series tied 4–4" — the lifetime line after this week. */
export function seriesLine(recap: Recap, g: RecapGame): string {
  const a = g.series.after[g.a] ?? 0;
  const b = g.series.after[g.b] ?? 0;
  const ties = g.series.after.ties ? `–${g.series.after.ties}` : "";
  if (a === b) return `Series tied ${a}–${b}${ties}`;
  const [lead, hi, lo] = a > b ? [g.a, a, b] : [g.b, b, a];
  return `${nameOf(recap, lead)} leads ${hi}–${lo}${ties}`;
}

export function seriesNoteText(recap: Recap, g: RecapGame, note: RecapSeriesNote): string {
  const loserOf = (team: string) => nameOf(recap, team === g.a ? g.b : g.a);
  switch (note.kind) {
    case "first_meeting":
      return "the first meeting ever between these two";
    case "snapped":
      return `${nameOf(recap, note.team)} snapped ${loserOf(note.team)}'s ${note.length}-game win streak in the series`;
    case "streak":
      return `${nameOf(recap, note.team)} has now won ${note.length} straight in the series`;
    case "took_lead":
      return `${nameOf(recap, note.team)} takes the lifetime lead`;
    case "evened":
      return `${nameOf(recap, note.team)} pulls the series even`;
    case "first_win":
      return `${nameOf(recap, note.team)}'s first win in ${note.games + 1} meetings`;
    case "first_win_since":
      return `${nameOf(recap, note.team)}'s first win over ${loserOf(note.team)} since ${note.season}`;
  }
}

/** The fact lines under a result card, most telling first. */
export function gameFacts(recap: Recap, g: RecapGame): string[] {
  const out: string[] = [];
  if (g.coulda_won) {
    const loser = g.coulda_won.team;
    out.push(`${nameOf(recap, loser)}'s best possible lineup scored ${pts(g.coulda_won.optimal)} — enough to win`);
  }
  if (g.swap_flip) {
    const s = g.swap_flip;
    out.push(`starting ${s.bench} (${pts(s.bench_points)}) over ${s.starter ?? "an empty slot"} (${pts(s.starter_points)}) would have flipped it`);
  }
  for (const note of g.series.notes) out.push(seriesNoteText(recap, g, note));
  return out;
}

/** One side of a league-award card: who, the headline number, and the number
 * it's measured against (max points, projection, the opponent) — the
 * two-number read Sleeper's weekly report uses, plus our one-line detail. */
export type AwardCard = {
  id: string;
  label: string;
  team: string;
  value: string;
  refLabel: string;
  ref: string;
  detail: string;
  player?: RecapPlayer;
};

function card(recap: Recap, id: string, label: string, team: string, ref: { label: string; value: string }, detail: string, value?: string): AwardCard {
  return { id, label, team, value: value ?? pts(recap.teams[team].actual), refLabel: ref.label, ref: ref.value, detail };
}

/** League awards as matched pairs — best beside worst — so each row is one
 * comparison. Ties add a card to their side. */
export function awardPairs(recap: Recap): { left: AwardCard[]; right: AwardCard[] }[] {
  const T = recap.teams;
  const others = Object.keys(T).length - 1;
  const winners = (id: string) => recap.awards[id] ?? [];
  const managed = (id: string, label: string) =>
    winners(id).map((w) => {
      const t = T[w.team!];
      return card(recap, id, label, w.team!, { label: "max points", value: pts(t.optimal) }, `${(t.efficiency ?? 0).toFixed(1)}% of a perfect lineup`);
    });
  const luck = (id: string, label: string, verb: string) =>
    winners(id).map((w) => {
      const t = T[w.team!];
      return card(recap, id, label, w.team!, { label: `vs ${nameOf(recap, t.opponent)}`, value: pts(T[t.opponent].actual) },
        `${verb} with the ${ordinal(t.score_rank)}-best score — would have beaten ${t.all_play.wins} of ${others}`);
    });
  const margin = (id: string, label: string) =>
    winners(id).map((w) =>
      card(recap, id, label, w.winner!, { label: `vs ${nameOf(recap, w.loser)}`, value: pts(T[w.loser!].actual) }, `won by ${pts(w.value)}`),
    );
  const projection = (id: string, label: string) =>
    winners(id).map((w) => {
      const t = T[w.team!];
      const pct = t.projected ? Math.round((100 * Math.abs(w.value)) / t.projected) : 0;
      return card(recap, id, label, w.team!, { label: "starter projection", value: pts(t.projected) },
        `${signed(w.value)} points, ${w.value >= 0 ? "over" : "under"} by ${pct}%`);
    });
  const hindsight = winners("most_left_on_bench").map((w) => {
    const t = T[w.team!];
    return card(recap, "most_left_on_bench", "Worst Lineup in Hindsight", w.team!, { label: "max points", value: pts(t.optimal) },
      `${pts(t.left_on_bench)} points left on the bench, the most in the league`);
  });
  const dud: AwardCard[] = recap.dud.map((p) => ({
    id: "dud",
    label: "Dud of the Week",
    team: p.team,
    value: pts(p.points),
    refLabel: "projected",
    ref: pts(p.projected),
    detail: `started by ${nameOf(recap, p.team)}${p.opponent ? ` ${p.opponent}` : ""} — missed by ${pts(p.shortfall)}`,
    player: p,
  }));
  return [
    { left: managed("best_managed", "Best Managed"), right: managed("worst_managed", "Worst Managed") },
    { left: luck("unluckiest_loss", "Unluckiest Loss", "lost"), right: luck("luckiest_win", "Luckiest Win", "won") },
    { left: margin("biggest_blowout", "Biggest Blowout"), right: margin("narrowest_win", "Narrowest Victory") },
    { left: projection("overachiever", "Overachiever"), right: projection("below_expectation", "Below Expectation") },
    { left: hindsight, right: dud },
  ];
}

/** Best Team / Worst Team — the week's highest and lowest scores, opening the Recap. */
export function bestWorst(recap: Recap): { label: string; id: string; team: string; score: string; line: string }[] {
  const line = (key: string) => {
    const t = recap.teams[key];
    const verb = t.result === "win" ? "beat" : t.result === "loss" ? "lost to" : "tied";
    return `${verb} ${nameOf(recap, t.opponent)} ${pts(t.actual)}–${pts(recap.teams[t.opponent].actual)}`;
  };
  return [
    ...(recap.awards.highest_score ?? []).map((w) => ({ label: "Best Team", id: "highest_score", team: w.team!, score: pts(w.value), line: line(w.team!) })),
    ...(recap.awards.lowest_score ?? []).map((w) => ({ label: "Worst Team", id: "lowest_score", team: w.team!, score: pts(w.value), line: line(w.team!) })),
  ];
}

/** Lineups in Hindsight — every team ranked by score, as bars: the fill is
 * what they scored, the track what their best lineup would have, the tick
 * their starters' projection. All three share one scale (the league's
 * highest possible score), so a short track means a thin roster and a long
 * empty tail means points left on the bench. */
export function performanceRows(recap: Recap) {
  const rows = Object.values(recap.teams).sort((a, b) => b.actual - a.actual);
  const scale = Math.max(...rows.map((t) => Math.max(t.optimal, t.projected ?? 0)));
  const pct = (n: number | null) => (n == null ? null : Math.round((1000 * n) / scale) / 10);
  return rows.map((t, i) => ({
    rank: i + 1,
    team: t.key,
    actual: pts(t.actual),
    optimal: pts(t.optimal),
    projected: pts(t.projected),
    efficiency: `${(t.efficiency ?? 0).toFixed(1)}%`,
    fillPct: pct(t.actual)!,
    trackPct: pct(t.optimal)!,
    tickPct: pct(t.projected),
  }));
}

/** Archive context worth a line — only genuinely notable ranks. */
export function recordLines(recap: Recap, firstSeason = FIRST_SEASON): { tag: string; value: string; text: string }[] {
  const out: { tag: string; value: string; text: string }[] = [];
  const who = (r: RecapRecord) => nameOf(recap, r.team);
  for (const r of recap.records) {
    switch (r.kind) {
      case "high_week":
        if (r.rank <= 3) out.push({ tag: r.rank === 1 ? "week record" : `${ordinal(r.rank)} best`, value: pts(r.value), text: `${who(r)} posts the ${r.rank === 1 ? "" : `${ordinal(r.rank)}-`}highest Week ${r.week} score since ${firstSeason}` });
        break;
      case "low_week":
        if (r.rank <= 3) out.push({ tag: r.rank === 1 ? "week low" : `${ordinal(r.rank)} worst`, value: pts(r.value), text: `${who(r)} posts the ${r.rank === 1 ? "" : `${ordinal(r.rank)}-`}lowest Week ${r.week} score since ${firstSeason}` });
        break;
      case "high_all_time":
        if (r.rank <= 10) out.push({ tag: "all-time", value: pts(r.value), text: `${who(r)}'s score ranks ${ordinal(r.rank)} of ${r.of} regular-season scores since ${firstSeason}` });
        break;
      case "low_all_time":
        if (r.rank <= 10) out.push({ tag: "all-time low", value: pts(r.value), text: `${who(r)}'s score is the ${ordinal(r.rank)}-lowest of ${r.of} regular-season scores since ${firstSeason}` });
        break;
      case "blowout_all_time":
        if (r.rank <= 10) out.push({ tag: "margin", value: pts(r.value), text: `${who(r)}'s win is the ${ordinal(r.rank)}-biggest regular-season margin of ${r.of} games since ${firstSeason}` });
        break;
      case "career_high":
        out.push({ tag: "career high", value: pts(r.value), text: `${who(r)}'s best score ever — the old mark was ${pts(r.previous)}` });
        break;
      case "career_low":
        out.push({ tag: "career low", value: pts(r.value), text: `${who(r)}'s lowest score ever — the old floor was ${pts(r.previous)}` });
        break;
    }
  }
  return out;
}
