/**
 * The Recap — the Program's Tuesday tab. Facts come precomputed from
 * scripts/build_recap.py; this module only phrases them. Nothing here
 * invents a claim: every sentence is a template over a value already in the
 * Recap JSON. Dynasty 22's museum carries a sibling of this file — keep the
 * award labels and phrasing in step.
 */

import type { Recap, RecapGame, RecapRecord, RecapSeriesNote } from "./data";
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

export type AwardTile = { id: string; label: string; team: string; value: string; detail: string };

const AWARD_ORDER: [string, string][] = [
  ["highest_score", "Highest Scorer"],
  ["lowest_score", "Lowest Scorer"],
  ["biggest_blowout", "Biggest Blowout"],
  ["narrowest_win", "Narrowest Victory"],
  ["best_managed", "Best Managed"],
  ["worst_managed", "Worst Managed"],
  ["most_left_on_bench", "Worst Lineup in Hindsight"],
  ["overachiever", "Overachiever"],
  ["below_expectation", "Below Expectation"],
  ["luckiest_win", "Luckiest Win"],
  ["unluckiest_loss", "Unluckiest Loss"],
];

export function awardTiles(recap: Recap): AwardTile[] {
  const tiles: AwardTile[] = [];
  const others = Object.keys(recap.teams).length - 1;
  for (const [id, label] of AWARD_ORDER) {
    for (const w of recap.awards[id] ?? []) {
      const key = (w.team ?? w.winner)!;
      const t = recap.teams[key];
      let value = pts(w.value);
      let detail = "";
      switch (id) {
        case "highest_score":
        case "lowest_score":
          detail = `${ordinal(t.score_rank)} of ${others + 1} · ${t.result === "win" ? "won" : t.result === "loss" ? "lost" : "tied"} by ${pts(Math.abs(t.margin))}`;
          break;
        case "biggest_blowout":
        case "narrowest_win": {
          const l = recap.teams[w.loser!];
          value = pts(w.value);
          detail = `${pts(t.actual)}–${pts(l.actual)} over ${nameOf(recap, w.loser)}`;
          break;
        }
        case "best_managed":
        case "worst_managed":
          value = `${w.value.toFixed(1)}%`;
          detail = `${pts(t.actual)} of a possible ${pts(t.optimal)}`;
          break;
        case "most_left_on_bench":
          detail = `points left on the bench — scored ${pts(t.actual)}, could have had ${pts(t.optimal)}`;
          break;
        case "overachiever":
        case "below_expectation":
          value = signed(w.value);
          detail = `${pts(t.actual)} against a ${pts(t.projected)} projection`;
          break;
        case "luckiest_win":
          detail = `won with the ${ordinal(t.score_rank)}-best score — would have beaten ${t.all_play.wins} of ${others}`;
          break;
        case "unluckiest_loss":
          detail = `lost with the ${ordinal(t.score_rank)}-best score — would have beaten ${t.all_play.wins} of ${others}`;
          break;
      }
      tiles.push({ id, label, team: key, value, detail });
    }
  }
  return tiles;
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
