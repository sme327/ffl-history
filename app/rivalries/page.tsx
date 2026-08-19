import { franchiseIndex, franchiseRivalries, rivalriesView, rivalryIndex, slugify, managerIconPath, franchiseBadgePath } from "@/lib/data";

export const metadata = { title: "Rivalries · {insert witty name here} Museum" };

export default function RivalriesPage() {
  const { totals, title_records, eliminations, hall_of_pain } = rivalriesView;
  const top = rivalryIndex.slice(0, 10);
  const franchiseNames = new Map(franchiseIndex.map((f) => [f.id, f.currentManager]));
  const topFranchisePairs = [...franchiseRivalries]
    .sort((a, b) => b.games - a.games || a.fid_a.localeCompare(b.fid_a))
    .slice(0, 10);

  return (
    <>
      <div className="room-photo" style={{ backgroundImage: "url(/museum/rooms/the-arena.webp)" }} />
      <div className="room-scrim" />
      <div className="room-title">
        <div className="eyebrow">Who still hates each other?</div>
        <h1>RIVALRIES</h1>
        <p>The emotional center of 25 years of competition.</p>
      </div>

      <div className="grid cols-4">
        {[
          [totals.pairs, "Matchups"],
          [totals.managers, "Managers"],
          [totals.finals, "Title Games"],
          [totals.playoff_eliminations, "Playoff Eliminations"],
        ].map(([value, label]) => (
          <div className="card metric" key={String(label)}>
            <div className="metric-value">{value}</div>
            <div className="metric-label">{label}</div>
          </div>
        ))}
      </div>

      <h2>Top Rivalries</h2>
      <div className="grid cols-2">
        {top.map((r) => (
          <div className="card" key={r.slug}>
            <h3>
              <a href={`/managers/${slugify(r.mgr_a)}`}>{r.mgr_a}</a>
              <span className="muted"> vs </span>
              <a href={`/managers/${slugify(r.mgr_b)}`}>{r.mgr_b}</a>
            </h3>
            <div className="gold">
              {r.rs_a_wins}–{r.rs_b_wins} in {r.rs_games} regular season games
            </div>
            <div className="muted">
              {r.pl_games > 0 && `${r.pl_games} playoff meeting${r.pl_games === 1 ? "" : "s"} · `}
              {r.close_games} game{r.close_games === 1 ? "" : "s"} decided by under a score ·{" "}
              {r.first_meeting}–{r.last_meeting}
            </div>
          </div>
        ))}
      </div>

      <h2>Championship Game Record</h2>
      <div className="scroll-x">
        <table>
          <thead>
            <tr><th>Manager</th><th className="num">Titles</th><th className="num">Losses</th><th className="num">Finals</th></tr>
          </thead>
          <tbody>
            {title_records.map((t) => (
              <tr key={t.manager}>
                <td><img src={managerIconPath(t.manager)} alt="" className="mgr-icon" /> <a href={`/managers/${slugify(t.manager)}`}>{t.manager}</a></td>
                <td className="num gold">{t.wins}</td>
                <td className="num muted">{t.losses}</td>
                <td className="num">{t.apps}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2>Playoff Executioners</h2>
      <div className="grid cols-2">
        <div className="card">
          <div className="eyebrow">Most Eliminations Delivered</div>
          {eliminations.by_executioner.slice(0, 8).map((e, i) => (
            <div key={e.manager} style={{ display: "flex", justifyContent: "space-between", padding: "0.25rem 0", borderBottom: "1px solid var(--border)" }}>
              <span>{i + 1}. <img src={managerIconPath(e.manager)} alt="" className="mgr-icon" /> <a href={`/managers/${slugify(e.manager)}`}>{e.manager}</a></span>
              <span className="gold">{e.total}</span>
            </div>
          ))}
        </div>
        <div className="card">
          <div className="eyebrow">Most Times Eliminated</div>
          {eliminations.by_victim.slice(0, 8).map((e, i) => (
            <div key={e.manager} style={{ display: "flex", justifyContent: "space-between", padding: "0.25rem 0", borderBottom: "1px solid var(--border)" }}>
              <span>{i + 1}. <img src={managerIconPath(e.manager)} alt="" className="mgr-icon" /> <a href={`/managers/${slugify(e.manager)}`}>{e.manager}</a></span>
              <span className="muted">{e.total}</span>
            </div>
          ))}
        </div>
      </div>

      <h2>Hall of Pain</h2>
      <div className="grid cols-2">
        <div className="card">
          <div className="eyebrow">Worst Head-to-Head</div>
          {hall_of_pain.worst_matchups.slice(0, 6).map((m) => (
            <div key={`${m.loser}-${m.winner}`} style={{ padding: "0.3rem 0", borderBottom: "1px solid var(--border)" }}>
              <a href={`/managers/${slugify(m.loser)}`}>{m.loser}</a>
              <span className="muted"> lost {m.losses}× to </span>
              <a href={`/managers/${slugify(m.winner)}`}>{m.winner}</a>
            </div>
          ))}
        </div>
        <div className="card">
          <div className="eyebrow">Closest Championship Loss</div>
          <h3 className="gold">
            {hall_of_pain.closest_final.loser_manager} · {hall_of_pain.closest_final.season}
          </h3>
          <p>
            Lost the title by {hall_of_pain.closest_final.margin.toFixed(2)} points to{" "}
            {hall_of_pain.closest_final.winner_manager}. The cruelest margin in
            league history.
          </p>
          <p>
            <a href={`/seasons/${hall_of_pain.closest_final.season}`}>
              See the {hall_of_pain.closest_final.season} season →
            </a>
          </p>
        </div>
      </div>
      <h2>Franchise Rivalries</h2>
      <p style={{ marginTop: "-0.5rem" }}>
        Franchises are institutions — these are the seats that have met most
        often, whoever was holding them.
      </p>
      <div className="scroll-x">
        <table>
          <thead>
            <tr>
              <th>Franchise</th><th>Opponent</th>
              <th className="num">Games</th><th>Record</th><th className="num">Win %</th>
            </tr>
          </thead>
          <tbody>
            {topFranchisePairs.map((pair) => (
              <tr key={`${pair.fid_a}-${pair.fid_b}`}>
                <td>
                  <img src={franchiseBadgePath(pair.fid_a)} alt="" className="mgr-icon" />{" "}
                  <a href={`/franchises/${pair.fid_a}`}>{pair.fid_a}</a>{" "}
                  <span className="muted">{franchiseNames.get(pair.fid_a)}</span>
                </td>
                <td>
                  <img src={franchiseBadgePath(pair.fid_b)} alt="" className="mgr-icon" />{" "}
                  <a href={`/franchises/${pair.fid_b}`}>{pair.fid_b}</a>{" "}
                  <span className="muted">{franchiseNames.get(pair.fid_b)}</span>
                </td>
                <td className="num muted">{pair.games}</td>
                <td className="gold">{pair.a_wins}-{pair.b_wins}</td>
                <td className="num">{Math.round(pair.a_pct * 100)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2>Every Matchup</h2>
      <p style={{ marginTop: "-0.5rem" }}>
        All {totals.pairs} manager pairings, ranked by rivalry score. The
        Streamlit explorer was a pair of dropdowns; here every matchup is on the
        page, and every name links to its manager.
      </p>
      <div className="scroll-x">
        <table>
          <thead>
            <tr>
              <th>Matchup</th><th className="num">Games</th><th>Record</th>
              <th className="num">Playoffs</th><th className="num">Close</th>
              <th className="num">Span</th><th className="num">Score</th>
            </tr>
          </thead>
          <tbody>
            {rivalryIndex.map((r) => (
              <tr key={r.slug}>
                <td>
                  <a href={`/managers/${slugify(r.mgr_a)}`}>{r.mgr_a}</a>
                  <span className="muted"> vs </span>
                  <a href={`/managers/${slugify(r.mgr_b)}`}>{r.mgr_b}</a>
                </td>
                <td className="num muted">{r.rs_games}</td>
                <td className="gold">{r.rs_a_wins}–{r.rs_b_wins}</td>
                <td className="num">{r.pl_games || "—"}</td>
                <td className="num">{r.close_games}</td>
                <td className="num muted">{r.first_meeting}–{r.last_meeting}</td>
                <td className="num gold">{r.rivalry_score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
