import { championsView, slugify } from "@/lib/data";

export const metadata = { title: "Champions · The Long Game" };

export default function ChampionsPage() {
  const { totals, manager_leaders: leaders, dynasties, finals, trivia, pain } = championsView;

  return (
    <>
      <div className="eyebrow">Who won?</div>
      <h1>CHAMPIONS</h1>
      <p>
        {totals.seasons} seasons · {totals.titles_awarded} champions crowned ·
        only {totals.unique_managers} managers have ever lifted the trophy.
      </p>

      <h2>Championship Leaders</h2>
      <div className="grid cols-3">
        {leaders.map((m) => (
          <div className="card" key={m.manager}>
            <div style={{ fontSize: "1.75rem" }}>{m.emoji}</div>
            <h3 className="gold">{m.championships}× </h3>
            <div>
              <a href={`/managers/${slugify(m.manager)}`}>{m.manager}</a>
            </div>
            <div className="muted">{m.years}</div>
            <div className="muted">
              {m.finals_apps} finals · {Math.round(m.win_pct * 100)}% win rate
            </div>
          </div>
        ))}
      </div>

      <h2>Dynasties</h2>
      <div className="grid cols-2">
        {dynasties.map((d) => (
          <div className="card card-feature" key={d.manager}>
            <div style={{ fontSize: "2.25rem" }}>{d.emoji}</div>
            <h3>
              <a href={`/managers/${slugify(d.manager)}`}>{d.manager}</a>
            </h3>
            <div className="metric-value">{d.championships}</div>
            <p style={{ margin: "0.25rem 0" }}>{d.era_desc}</p>
            <div className="gold">{d.years}</div>
          </div>
        ))}
      </div>

      <h2>Championship Pain</h2>
      <div className="grid cols-3">
        <div className="card">
          <div className="eyebrow">Most Runner-Up Finishes</div>
          <h3 className="gold">
            {pain.most_runner_up.emoji} {pain.most_runner_up.manager} — {pain.most_runner_up.count}×
          </h3>
          <p>Runner-up in {pain.most_runner_up.years.join(", ")}.</p>
        </div>
        <div className="card">
          <div className="eyebrow">Closest Championship Loss</div>
          <h3 className="gold">
            {pain.closest_loss.runner_up_manager} · {pain.closest_loss.season}
          </h3>
          <p>
            Lost by {pain.closest_loss.margin.toFixed(2)} points. The cruelest
            margin in league history.
          </p>
        </div>
        <div className="card">
          <div className="eyebrow">Best Regular Season, No Title</div>
          <h3 className="gold">
            {pain.best_rs_no_title.manager} · {pain.best_rs_no_title.season}
          </h3>
          <p>
            {pain.best_rs_no_title.wins}-{pain.best_rs_no_title.losses} — the best
            that year. Didn’t matter when the playoffs started.
          </p>
        </div>
      </div>

      <h2>Every Final</h2>
      <div className="scroll-x">
        <table>
          <thead>
            <tr>
              <th>Season</th><th>Champion</th><th className="num">Score</th>
              <th>Runner-Up</th><th className="num">Score</th><th className="num">Margin</th>
            </tr>
          </thead>
          <tbody>
            {finals.map((f) => (
              <tr key={f.season}>
                <td className="gold">
                  <a href={`/seasons/${f.season}`}>{f.season}</a>
                </td>
                <td>
                  {f.emoji} {f.champion_team}{" "}
                  <span className="muted">
                    <a href={`/managers/${slugify(f.champion_manager)}`}>{f.champion_manager}</a>
                  </span>
                </td>
                <td className="num">{f.champion_score.toFixed(2)}</td>
                <td>
                  {f.runner_up_team}{" "}
                  <span className="muted">
                    <a href={`/managers/${slugify(f.runner_up_manager)}`}>{f.runner_up_manager}</a>
                  </span>
                </td>
                <td className="num muted">{f.runner_up_score.toFixed(2)}</td>
                <td className="num">{f.margin.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
