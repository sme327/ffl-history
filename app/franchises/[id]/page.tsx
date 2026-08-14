import { franchiseIndex, franchiseProfile, slugify } from "@/lib/data";

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

  return (
    <>
      <div className="eyebrow">Franchise {franchise.franchise_id} · established {franchise.established}</div>
      <h1>THE {franchise.current_manager.toUpperCase()} FRANCHISE</h1>

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
          [t.seasons, "Seasons"],
          [t.longest_playoff_streak, "Best PO Streak"],
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
              {s.emoji}{" "}
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
            <tr><th>Opponent</th><th className="num">Games</th><th>W-L</th><th>Playoffs</th></tr>
          </thead>
          <tbody>
            {franchise.rivals.map((r) => (
              <tr key={r.opponent}>
                <td>{r.emoji} <a href={`/managers/${slugify(r.opponent)}`}>{r.opponent}</a></td>
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
