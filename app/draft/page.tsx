import { PositionShareBar, PositionTrends } from "@/app/components/charts";
import { draftCenter, draftExtras, slugify, managerIconPath } from "@/lib/data";
import { Trophies } from "@/app/components/icons";

export const metadata = { title: "Draft Center · {insert witty name here} Museum" };

const POSITION_COLORS: Record<string, string> = {
  RB: "#22C55E", WR: "#3B82F6", QB: "#EF4444",
  TE: "#F59E0B", DEF: "#8B5CF6", K: "#6B7280",
};

export default function DraftPage() {
  const { legends, manager_dna: dna, round_one, totals } = draftCenter;
  const { positionTrends, records } = draftExtras;

  return (
    <>
      <div className="room-photo" style={{ backgroundImage: "url(/museum/rooms/war-room.webp)" }} />
      <div className="room-scrim" />
      <div className="room-title">
        <div className="eyebrow">How were contenders built?</div>
        <h1>DRAFT CENTER</h1>
        <p>25 years of picks, patterns, and obsessions.</p>
      </div>

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
                    display: "flex", alignItems: "center", justifyContent: "center",
                  }}
                >
                  <img src={managerIconPath(d.manager)} alt="" style={{ width: 12, height: 12 }} />
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>

      <h2>Draft DNA</h2>
      <p>
        Every manager has tells. This is 25 years of first-pick evidence — the
        player each manager took with their earliest live selection. In 2003,
        2011 and 2013 every team kept a player at round-one cost, so live
        drafting began in round two; those years count too.
      </p>
      <div className="grid cols-2">
        {dna.map((entry) => (
          <div className="card" key={entry.manager} style={{ borderTop: `3px solid ${entry.color}` }}>
            <div style={{ display: "flex", alignItems: "baseline", gap: "0.5rem" }}>
              <span style={{ fontSize: "1.4rem" }}>
                <img src={managerIconPath(entry.manager)} alt="" className="mgr-icon" />
              </span>
              <h3 style={{ margin: 0 }}>
                <a href={`/managers/${slugify(entry.manager)}`}>{entry.manager}</a>
              </h3>
              {entry.championships > 0 && <span className="gold"><Trophies count={entry.championships} /></span>}
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

      <h2>Position Trends</h2>
      <p style={{ marginTop: "-0.5rem" }}>
        How first-round strategy shifted: the rise of zero-RB, the TE premium,
        the quarterback golden age.
      </p>
      <div className="card">
        <PositionTrends rows={positionTrends} colors={POSITION_COLORS} />
      </div>

      <h2>First Picks</h2>
      <div className="grid cols-2">
        <div className="card">
          <div className="eyebrow">Most Taken With a First Pick</div>
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
          <div className="eyebrow">Most Opening Picks of a Draft</div>
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
      <h2>Draft Records</h2>
      <div className="grid cols-3">
        {[
          ["Most Drafted Players", records.most_drafted_players],
          ["Most Managers to Own One Player", records.most_mgrs_one_player],
          ["Most Kept Players", records.most_kept_players],
        ].map(([label, entries]) => (
          <div className="card" key={label as string}>
            <div className="eyebrow">{label as string}</div>
            {(entries as [string, number][]).slice(0, 5).map(([name, count], i) => (
              <div
                key={name}
                style={{ display: "flex", justifyContent: "space-between", padding: "0.25rem 0", borderBottom: "1px solid var(--border)" }}
              >
                <span>
                  <span className={i < 3 ? "gold" : "muted"}>{i + 1}.</span>{" "}
                  <a href={`/players/${slugify(name)}`}>{name}</a>
                </span>
                <span className="gold">{count}×</span>
              </div>
            ))}
          </div>
        ))}
      </div>

      <h2>Draft Hall of Fame &amp; Shame</h2>
      <div className="grid cols-2">
        {[
          ["Earliest QB Ever Taken", records.earliest_qb?.[0]],
          ["Earliest TE Ever Taken", records.earliest_te?.[0]],
          ["Earliest K Ever Taken", records.earliest_k?.[0]],
          ["Earliest DEF in Round 1", records.earliest_def_r1?.[0]],
        ].map(([label, pick]) =>
          pick ? (
            <div className="card" key={label as string}>
              <div className="eyebrow">{label as string}</div>
              <h3 className="gold">
                <a href={`/players/${slugify((pick as any).player_name)}`}>
                  {(pick as any).player_name}
                </a>
              </h3>
              <p style={{ margin: 0 }}>
                <a href={`/seasons/${(pick as any).season}`}>{(pick as any).season}</a>
                {" · pick #"}{(pick as any).overall_pick}
                {" · "}{(pick as any).manager}
              </p>
            </div>
          ) : null,
        )}
      </div>
    </>
  );
}
