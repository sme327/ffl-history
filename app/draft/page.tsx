import { PositionShareBar } from "@/app/components/charts";
import { draftCenter, slugify } from "@/lib/data";

export const metadata = { title: "Draft Center · The Long Game" };

const POSITION_COLORS: Record<string, string> = {
  RB: "#22C55E", WR: "#3B82F6", QB: "#EF4444",
  TE: "#F59E0B", DEF: "#8B5CF6", K: "#6B7280",
};

export default function DraftPage() {
  const { legends, manager_dna: dna, round_one, totals } = draftCenter;

  return (
    <>
      <div className="eyebrow">How were contenders built?</div>
      <h1>DRAFT CENTER</h1>
      <p>25 years of picks, patterns, and obsessions.</p>

      <div className="grid cols-4">
        {[
          [totals.picks.toLocaleString(), "Total Picks"],
          [totals.real_drafts.toLocaleString(), "Drafted"],
          [totals.keepers, "Kept"],
          [totals.unique_players.toLocaleString(), "Different Players"],
        ].map(([value, label]) => (
          <div className="card metric" key={String(label)}>
            <div className="metric-value">{value}</div>
            <div className="metric-label">{label}</div>
          </div>
        ))}
      </div>

      <h2>The Ones They Couldn’t Quit</h2>
      <div className="grid cols-2">
        {legends.slice(0, 8).map((player) => (
          <div
            className="card"
            key={player.player_name}
            style={{ borderLeft: `4px solid ${POSITION_COLORS[player.position] ?? "var(--faint)"}` }}
          >
            <h3>
              <a href={`/players/${slugify(player.player_name)}`}>{player.player_name}</a>{" "}
              <span className="pill">{player.position}</span>
            </h3>
            <div className="gold">
              {player.total_drafts} drafts · {player.unique_managers} managers ·{" "}
              {player.career_span}-season run
            </div>
            <p>{player.story}</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 3 }}>
              {player.drafters.map((d) => (
                <span
                  key={d.manager}
                  title={`${d.manager} (${d.count}×)`}
                  style={{
                    width: 18, height: 18, borderRadius: "50%", background: d.color,
                    fontSize: 10, lineHeight: "18px", textAlign: "center",
                  }}
                >
                  {d.emoji}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>

      <h2>Draft DNA</h2>
      <p>
        Every manager has tells. This is 25 years of first-round evidence — who
        they were, what they valued, and whether it worked.
      </p>
      <div className="grid cols-2">
        {dna.map((entry) => (
          <div className="card" key={entry.manager} style={{ borderTop: `3px solid ${entry.color}` }}>
            <div style={{ display: "flex", alignItems: "baseline", gap: "0.5rem" }}>
              <span style={{ fontSize: "1.4rem" }}>{entry.emoji}</span>
              <h3 style={{ margin: 0 }}>
                <a href={`/managers/${slugify(entry.manager)}`}>{entry.manager}</a>
              </h3>
              {entry.championships > 0 && <span>{"🏆".repeat(entry.championships)}</span>}
            </div>
            <div className="eyebrow" style={{ color: entry.archetype_color, marginTop: "0.35rem" }}>
              {entry.archetype}
            </div>
            <p style={{ marginTop: "0.2rem" }}>{entry.archetype_blurb}</p>
            <PositionShareBar counts={entry.counts} colors={POSITION_COLORS} />
            <div className="muted" style={{ marginTop: "0.5rem", fontSize: "var(--step--1)" }}>
              Playoff rate {Math.round(entry.playoff_rate * 100)}% · best R1 find:{" "}
              <a href={`/players/${slugify(entry.best_round_one_find)}`}>
                {entry.best_round_one_find}
              </a>
            </div>
          </div>
        ))}
      </div>

      <h2>Round One History</h2>
      <div className="grid cols-2">
        <div className="card">
          <div className="eyebrow">Most Taken in Round 1</div>
          <table>
            <tbody>
              {round_one.most_taken.slice(0, 10).map((p) => (
                <tr key={p.player_name}>
                  <td><a href={`/players/${slugify(p.player_name)}`}>{p.player_name}</a></td>
                  <td className="muted">{p.position}</td>
                  <td className="num gold">{p.count}×</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="card">
          <div className="eyebrow">Most #1 Overall Picks</div>
          <table>
            <tbody>
              {round_one.first_overall.slice(0, 10).map((p) => (
                <tr key={p.player_name}>
                  <td><a href={`/players/${slugify(p.player_name)}`}>{p.player_name}</a></td>
                  <td className="num gold">{p.count}×</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
