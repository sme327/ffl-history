import { franchiseIndex, franchiseProfile, slugify, managerIconPath, franchiseBadgePath } from "@/lib/data";

export function generateStaticParams() {
  return franchiseIndex.map((f) => ({ id: f.id }));
}

export default async function FranchisePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const franchise = franchiseProfile(id);
  if (!franchise) return <h1>Franchise not found</h1>;

  const t = franchise.totals;
  // Career totals across every steward — the franchise's own record, not any
  // one manager's.
  const allTimeWins = franchise.stewards.reduce((sum, s) => sum + s.wins, 0);
  const allTimeLosses = franchise.stewards.reduce((sum, s) => sum + s.losses, 0);
  const played = allTimeWins + allTimeLosses;
  const winPct = played ? (allTimeWins / played).toFixed(3).replace(/^0/, "") : "—";

  return (
    <>
      <div className="eyebrow">Franchise {franchise.franchise_id} · established {franchise.established}</div>
      <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
        <img
          src={franchiseBadgePath(franchise.franchise_id)}
          alt=""
          style={{ width: "4.5rem", height: "4.5rem", flexShrink: 0 }}
        />
        <h1 style={{ margin: 0 }}>THE {franchise.current_manager.toUpperCase()} FRANCHISE</h1>
      </div>

      <div className="card plaque">
        <div className="eyebrow">The Story of the Franchise</div>
        <p style={{ color: "var(--text)" }}>{franchise.story}</p>
      </div>

      <div className="grid cols-4" style={{ marginTop: "1.25rem" }}>
        {[
          [t.championships, "Championships"],
          [t.finals_apps, "Finals Apps"],
          [t.playoff_apps, "Playoff Apps"],
          [t.winning_seasons, "Winning Seasons"],
          [`${allTimeWins}-${allTimeLosses}`, "All-Time Record"],
          [winPct, "All-Time Win %"],
          [t.longest_playoff_streak, "Longest PO Streak"],
          [t.seasons, "Seasons"],
          [t.runner_ups, "Runner-Ups"],
          [t.third_places, "Third Places"],
        ].map(([value, label]) => (
          <div className="card metric" key={String(label)}>
            <div className="metric-value">{value}</div>
            <div className="metric-label">{label}</div>
          </div>
        ))}
      </div>

      <h2>Franchise Lineage</h2>
      <div className="grid cols-2">
        {franchise.stewards.map((s) => (
          <div className="card" key={s.manager} style={{ borderLeft: `4px solid ${s.color}` }}>
            <h3>
              <img src={managerIconPath(s.manager)} alt="" className="mgr-icon" />{" "}
              <a href={`/managers/${slugify(s.manager)}`}>{s.manager}</a>
              {s.manager === franchise.best_steward && (
                <span className="pill" style={{ marginLeft: "0.5rem" }}>Most successful</span>
              )}
            </h3>
            <div className="gold">
              {s.start_season}–{s.end_season === Math.max(...franchise.seasons) ? "Present" : s.end_season}
              {" · "}{s.seasons} season{s.seasons === 1 ? "" : "s"}
            </div>
            <div className="muted">
              {s.wins}-{s.losses} · {s.playoff_apps} playoff appearances
              {s.championships > 0 && ` · ${"🏆".repeat(s.championships)} ${s.championship_years.join(", ")}`}
            </div>
          </div>
        ))}
      </div>

      <h2>Top Rivals</h2>
      <div className="scroll-x">
        <table>
          <thead>
            <tr><th>Opponent</th><th className="num">Games</th><th>W-L</th><th className="num">Playoffs</th></tr>
          </thead>
          <tbody>
            {franchise.rivals.map((r) => (
              <tr key={r.opponent}>
                <td><img src={managerIconPath(r.opponent)} alt="" className="mgr-icon" /> <a href={`/managers/${slugify(r.opponent)}`}>{r.opponent}</a></td>
                <td className="num muted">{r.games}</td>
                <td className="gold">{r.wins}-{r.losses}</td>
                <td className="muted">
                  {r.playoff_games > 0
                    ? `${r.playoff_wins}-${r.playoff_games - r.playoff_wins}`
                    : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2>Era Breakdown</h2>
      <div className="scroll-x">
        <table>
          <thead>
            <tr>
              <th>Steward</th><th>Years</th><th className="num">Seasons</th>
              <th>Record</th><th className="num">Win %</th>
              <th className="num">Playoffs</th><th>Titles</th>
            </tr>
          </thead>
          <tbody>
            {franchise.stewards.map((steward) => {
              const played = steward.wins + steward.losses;
              return (
                <tr key={steward.manager}>
                  <td>
                    <img src={managerIconPath(steward.manager)} alt="" className="mgr-icon" />{" "}
                    <a href={`/managers/${slugify(steward.manager)}`}>{steward.manager}</a>
                  </td>
                  <td className="muted">
                    {steward.start_season}–
                    {steward.end_season === Math.max(...franchise.seasons) ? "Present" : steward.end_season}
                  </td>
                  <td className="num muted">{steward.seasons}</td>
                  <td>{steward.wins}-{steward.losses}</td>
                  <td className="num">
                    {played ? (steward.wins / played).toFixed(3).replace(/^0/, "") : "—"}
                  </td>
                  <td className="num">{steward.playoff_apps}</td>
                  <td className="gold">
                    {steward.championships > 0 ? "🏆".repeat(steward.championships) : "—"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <h2>Franchise Achievements</h2>
      <div className="grid cols-3">
        {[
          ["🏆", t.championships, "Championship Seasons",
           franchise.championship_seasons.join(" · ") || "—"],
          ["🥈", t.runner_ups, "Runner-Up Seasons",
           franchise.runner_up_seasons.join(" · ") || "—"],
          ["🥉", t.third_places, "Third-Place Finishes",
           franchise.third_place_seasons.join(" · ") || "—"],
          ["🔥", t.longest_playoff_streak, "Best Playoff Streak",
           "Consecutive postseason appearances"],
          ["📈", t.winning_seasons, "Winning Seasons",
           `Out of ${t.seasons} total seasons`],
          ["🏟️", t.playoff_apps, "Total Playoff Appearances",
           `${Math.round((t.playoff_apps / t.seasons) * 100)}% of all seasons`],
        ].map(([icon, value, label, detail]) => (
          <div className="card" key={label as string}>
            <div style={{ display: "flex", gap: "0.75rem", alignItems: "flex-start" }}>
              <span style={{ fontSize: "1.5rem" }}>{icon as string}</span>
              <div>
                <div className="metric-value" style={{ fontSize: "var(--step-2)" }}>{value as number}</div>
                <div className="metric-label">{label as string}</div>
                <div className="muted" style={{ fontSize: "var(--step--1)" }}>{detail as string}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <h2>Franchise Records</h2>
      <div className="grid cols-3">
        {franchise.peaks.best_record && (
          <div className="card">
            <div className="eyebrow">Best Season Record</div>
            <h3 className="gold">
              {franchise.peaks.best_record.wins}-{franchise.peaks.best_record.losses}
            </h3>
            <p style={{ margin: 0 }}>
              {franchise.peaks.best_record.manager} ·{" "}
              <a href={`/seasons/${franchise.peaks.best_record.season}`}>
                {franchise.peaks.best_record.season}
              </a>
            </p>
          </div>
        )}
        {franchise.peaks.most_points && (
          <div className="card">
            <div className="eyebrow">Most Points in a Season</div>
            <h3 className="gold">{franchise.peaks.most_points.points_for.toFixed(1)}</h3>
            <p style={{ margin: 0 }}>
              {franchise.peaks.most_points.manager} ·{" "}
              <a href={`/seasons/${franchise.peaks.most_points.season}`}>
                {franchise.peaks.most_points.season}
              </a>
            </p>
          </div>
        )}
        {franchise.peaks.best_week && (
          <div className="card">
            <div className="eyebrow">Best Single Week</div>
            <h3 className="gold">{franchise.peaks.best_week.points.toFixed(2)}</h3>
            <p style={{ margin: 0 }}>
              {franchise.peaks.best_week.manager} ·{" "}
              <a href={`/seasons/${franchise.peaks.best_week.season}`}>
                {franchise.peaks.best_week.season}
              </a>{" "}
              Week {franchise.peaks.best_week.week}
            </p>
          </div>
        )}
      </div>

      <h2>Franchise Milestones</h2>
      <div className="card">
        <div className="chron-row">
          <div className="chron-mgr">Championships</div>
          <div className="chron-years">
            {franchise.championship_seasons.length
              ? franchise.championship_seasons.map((year) => (
                  <a className="year-pill gold-pill" key={year} href={`/seasons/${year}`}>{year}</a>
                ))
              : <span className="muted">None yet</span>}
          </div>
        </div>
        <div className="chron-row">
          <div className="chron-mgr">Runner-up</div>
          <div className="chron-years">
            {franchise.runner_up_seasons.length
              ? franchise.runner_up_seasons.map((year) => (
                  <a className="year-pill" key={year} href={`/seasons/${year}`}>{year}</a>
                ))
              : <span className="muted">None</span>}
          </div>
        </div>
        <div className="chron-row">
          <div className="chron-mgr">Playoff seasons</div>
          <div className="chron-years">
            {franchise.playoff_seasons.map((year) => (
              <a className="year-pill" key={year} href={`/seasons/${year}`}>{year}</a>
            ))}
          </div>
        </div>
      </div>

      {franchise.legends.length > 0 && (
        <>
          <h2>Franchise Legends</h2>
          <div className="grid cols-3">
            {franchise.legends.map((player) => (
              <div className="card" key={player.player_name}>
                <h3>
                  <a href={`/players/${slugify(player.player_name)}`}>{player.player_name}</a>{" "}
                  <span className="pill">{player.position}</span>
                </h3>
                <div className="muted">
                  Drafted {player.draft_count}×
                  {player.keeper_count > 0 && ` · kept ${player.keeper_count}×`}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      <h2>Season by Season</h2>
      <div className="scroll-x">
        <table>
          <thead>
            <tr><th>Season</th><th>Steward</th><th>Team</th><th>Record</th><th className="num">Points For</th></tr>
          </thead>
          <tbody>
            {[...franchise.season_records].reverse().map((r) => (
              <tr key={r.season}>
                <td className="gold"><a href={`/seasons/${r.season}`}>{r.season}</a></td>
                <td><a href={`/managers/${slugify(r.manager)}`}>{r.manager}</a></td>
                <td>{r.team_name}</td>
                <td>{r.wins}-{r.losses}</td>
                <td className="num">{r.points_for.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
