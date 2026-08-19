import { ScoringEvolution, TitleBars } from "@/app/components/charts";
import { leagueHistory, slugify, eraIconPath, managerIconPath } from "@/lib/data";

export const metadata = { title: "League History · {insert witty name here} Museum" };

export default function HistoryPage() {
  const { eras, era_bands, scoring, balance, records, allTimeManagers } = leagueHistory;

  return (
    <>
      <div className="eyebrow">How did the league evolve?</div>
      <h1>THE EVOLUTION OF THE LEAGUE</h1>
      <p>
        This is not a statistics page. It’s a history page. The numbers exist to
        support the story of how this league changed over 25 years.
      </p>

      <h2>The Four Eras</h2>
      {eras.map((era) => (
        <div
          className="card"
          key={era.short}
          style={{ borderLeft: `5px solid ${era.color}`, marginBottom: "0.75rem" }}
        >
          <div style={{ display: "flex", alignItems: "baseline", gap: "0.75rem", flexWrap: "wrap" }}>
            {eraIconPath(era.short) && (
              <img src={eraIconPath(era.short)!} alt="" style={{ width: "2rem", height: "2rem" }} />
            )}
            <h3 style={{ color: era.color, margin: 0 }}>{era.name}</h3>
            <span className="muted">{era.years}</span>
          </div>
          <div style={{ fontFamily: "var(--display)", fontSize: "var(--step-1)", letterSpacing: 2, margin: "0.4rem 0" }}>
            {era.headline}
          </div>
          <p>{era.body}</p>
          <div className="grid inline-stats">
            {[
              [era.titles_awarded, "Titles"],
              [era.unique_champions, "Unique Champions"],
              [Math.round(era.avg_score), "Avg Weekly PF"],
            ].map(([value, label]) => (
              <div className="metric" key={String(label)}>
                <div className="metric-value" style={{ color: era.color }}>{value}</div>
                <div className="metric-label">{label}</div>
              </div>
            ))}
          </div>
          <div className="muted" style={{ marginTop: "0.5rem" }}>
            {era.champions.map((c, i) => (
              <span key={c.season}>
                {i > 0 && " · "}
                <a href={`/seasons/${c.season}`} style={{ color: era.color }}>{c.season}</a>{" "}
                <img src={managerIconPath(c.manager)} alt="" className="mgr-icon" /> {c.manager}
              </span>
            ))}
          </div>
        </div>
      ))}

      <h2>Scoring Evolution</h2>
      <div className="card">
        <ScoringEvolution
          points={scoring.by_season}
          bands={era_bands}
          championPoints={scoring.champion_points}
        />
        <div className="muted" style={{ fontSize: "var(--step--1)", marginTop: "0.5rem" }}>
          Gold line: league average. Shaded band: season high to low. ★ marks the
          champion’s season total.
        </div>
      </div>

      <div className="grid cols-3" style={{ marginTop: "0.75rem" }}>
        <div className="card">
          <div className="eyebrow">Peak Scoring Era</div>
          <h3 className="gold">{scoring.peak.season}</h3>
          <p>League average {scoring.peak.avg} pts — the most prolific year in history.</p>
        </div>
        <div className="card">
          <div className="eyebrow">Lean Era</div>
          <h3 className="gold">{scoring.lean.season}</h3>
          <p>League average {scoring.lean.avg} pts — the most defensive year on record.</p>
        </div>
        <div className="card">
          <div className="eyebrow">25-Year Scoring Rise</div>
          <h3 className="gold">+{scoring.rise} pts</h3>
          <p>The NFL became a scoring-first league. This league followed.</p>
        </div>
      </div>

      <h2>Competitive Balance</h2>
      <div className="grid cols-4">
        {[
          [balance.unique_champions, "Unique Champions"],
          [balance.playoff_managers_ever, "Made Playoffs"],
          [`${Math.round(balance.diversity_rate * 100)}%`, "Title Diversity"],
          [balance.most_consistent?.appearances ?? 0, `Playoff Trips — ${balance.most_consistent?.manager ?? "—"}`],
        ].map(([value, label]) => (
          <div className="card metric" key={String(label)}>
            <div className="metric-value">{value}</div>
            <div className="metric-label">{label}</div>
          </div>
        ))}
      </div>

      <div className="card" style={{ marginTop: "0.75rem" }}>
        <div className="eyebrow">Championships by Manager</div>
        <TitleBars entries={balance.title_counts} />
        <p style={{ marginTop: "0.75rem" }}>
          The top manager holds {balance.top1_pct}% of all championships. The top
          three account for {balance.top3_pct}%.
        </p>
      </div>

      <h2>By the Numbers</h2>
      <div className="grid cols-3">
        {[
          ["Single-Week Record", `${records.week_high.points} pts`,
           `${records.week_high.manager} · ${records.week_high.season} Wk${records.week_high.week}`],
          ["Biggest Blowout", `+${records.blowout.margin} pts`,
           `${records.blowout.manager} · ${records.blowout.season} Week ${records.blowout.week}`],
          ["Closest Game", `+${records.closest.margin} pts`,
           `${records.closest.manager} edged ${records.closest.loser} · ${records.closest.season}`],
          ["Best Single Season", `${records.best_record.wins}-${records.best_record.losses}`,
           `${records.best_record.manager} · ${records.best_record.season}`],
          ["Most Points in a Season", `${records.best_points.points_for} pts`,
           `${records.best_points.manager} · ${records.best_points.season}`],
          ["Highest-Scoring Season", String(scoring.peak.season),
           `League average ${scoring.peak.avg} pts/team`],
        ].map(([label, headline, sub]) => (
          <div className="card" key={label}>
            <div className="eyebrow">{label}</div>
            <h3 className="gold">{headline}</h3>
            <p style={{ margin: 0 }}>{sub}</p>
          </div>
        ))}
      </div>
      <h2>All-Time Manager Stats</h2>
      <p style={{ marginTop: "-0.5rem" }}>Raw data lives here. The stories live above.</p>
      <div className="scroll-x">
        <table>
          <thead>
            <tr>
              <th>Manager</th><th className="num">Seasons</th><th>RS W-L</th>
              <th className="num">RS PF</th><th className="num">RS PA</th><th>PL W-L</th>
              <th className="num">Playoffs</th><th className="num">Finals</th>
              <th>Titles</th><th className="num">Best/Worst</th>
            </tr>
          </thead>
          <tbody>
            {allTimeManagers.map((m) => (
              <tr key={m.canonical_name}>
                <td>
                  <a href={`/managers/${slugify(m.canonical_name)}`}>{m.canonical_name}</a>
                </td>
                <td className="num muted">{m.seasons}</td>
                <td>{m.rs_wins}-{m.rs_losses}</td>
                <td className="num">{m.rs_pf.toLocaleString(undefined, { maximumFractionDigits: 1 })}</td>
                <td className="num muted">{m.rs_pa.toLocaleString(undefined, { maximumFractionDigits: 1 })}</td>
                <td>{m.pl_wins}-{m.pl_losses}</td>
                <td className="num">{m.playoff_apps}</td>
                <td className="num">{m.finals_apps}</td>
                <td className="gold">{m.championships > 0 ? "🏆".repeat(m.championships) : "—"}</td>
                <td className="num muted">
                  {m.best_finish ? `#${m.best_finish}` : "—"} / {m.worst_finish ? `#${m.worst_finish}` : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
