import { championsView, slugify, managerIconPath, managerIconSmPath } from "@/lib/data";

export const metadata = { title: "Champions · {insert witty name here} Museum" };

export default function ChampionsPage() {
  const { totals, manager_leaders: leaders, dynasties, finals, trivia, pain } = championsView;

  return (
    <>
      <div className="room-photo" style={{ backgroundImage: "url(/museum/rooms/trophy-room.webp)" }} />
      <div className="room-scrim" />
      <div className="room-title">
        <div className="eyebrow">Who won?</div>
        <h1>CHAMPIONS</h1>
        <p>
          {totals.seasons} seasons · {totals.titles_awarded} champions crowned ·
          only {totals.unique_managers} managers have ever lifted the trophy.
        </p>
      </div>

      <h2>Championship Leaders</h2>
      <div className="grid cols-3">
        {leaders.map((m) => (
          <div className="card" key={m.manager}>
            <div style={{ fontSize: "1.75rem" }}>
              <img src={managerIconPath(m.manager)} alt="" className="mgr-icon" />
            </div>
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

      <h2>Championship Timeline</h2>
      <div className="card">
        {championsView.chronological.map((entry) => (
          <div key={entry.manager} className="chron-row">
            <div className="chron-mgr">
              <span style={{ fontSize: "1.1rem" }}>
                <img src={managerIconSmPath(entry.manager)} alt="" className="mgr-icon" />
              </span>
              <a href={`/managers/${slugify(entry.manager)}`}>{entry.manager}</a>
              <span className="muted">({entry.championships})</span>
            </div>
            <div className="chron-years">
              {entry.year_list.map((year) => (
                <a
                  className={entry.championships > 1 ? "year-pill gold-pill" : "year-pill"}
                  key={year}
                  href={`/seasons/${year}`}
                >
                  {year}
                </a>
              ))}
            </div>
          </div>
        ))}
      </div>

      <h2>Dynasties</h2>
      <div className="grid cols-2">
        {/* Only the league's defining dynasty gets the ornate artifact frame —
            seven gilt frames in one grid was the exact "gold everywhere"
            problem this skin pass removed. */}
        {dynasties.map((d, i) => (
          <div className={i === 0 ? "card card-feature" : "card"} key={d.manager}>
            <div style={{ fontSize: "2.25rem" }}>
              <img src={managerIconPath(d.manager)} alt="" className="mgr-icon" />
            </div>
            <h3>
              <a href={`/managers/${slugify(d.manager)}`}>{d.manager}</a>
            </h3>
            <div className="metric-value">{d.championships}</div>
            <p style={{ margin: "0.25rem 0" }}>{d.era_desc}</p>
            <div className="gold">{d.years}</div>
          </div>
        ))}
      </div>

      <h2>Championship Trivia</h2>
      <div className="grid cols-3">
        {[
          ["Biggest Blowout", String(trivia.biggest_blowout.season),
           `${trivia.biggest_blowout.champion_team} won by ${trivia.biggest_blowout.margin.toFixed(2)} pts`],
          ["Closest Title Game", String(trivia.closest_final.season),
           `${trivia.closest_final.champion_team} survived by ${trivia.closest_final.margin.toFixed(2)} pts`],
          ["Most Runner-Up Finishes", trivia.most_runner_up.manager,
           `${trivia.most_runner_up.count}× runner-up — still waiting`],
          ["Highest-Scoring Final", String(trivia.highest_scoring_final.season),
           `${trivia.highest_scoring_final.combined.toFixed(2)} combined points`],
          ["Defensive Masterclass", String(trivia.lowest_scoring_final.season),
           `Only ${trivia.lowest_scoring_final.combined.toFixed(2)} pts combined — ${trivia.lowest_scoring_final.champion_team} edged it`],
          ["Most Finals Appearances", trivia.most_finals.manager,
           `${trivia.most_finals.finals_apps} trips (${trivia.most_finals.titles}W–${trivia.most_finals.runner_ups}L)`],
          trivia.back_to_back
            ? ["Back-to-Back Champion", trivia.back_to_back.manager,
               `Repeated in ${trivia.back_to_back.season} with ${trivia.back_to_back.team}`]
            : ["Back-to-Back", "No Repeat Yet", "Nobody has successfully defended their title"],
          ["Highest Winning Score", String(trivia.highest_winning_score.season),
           `${trivia.highest_winning_score.champion_team} dropped ${trivia.highest_winning_score.champion_score.toFixed(2)} pts`],
          ["The Original", String(trivia.first_champion.season),
           `${trivia.first_champion.champion_team} — ${trivia.first_champion.champion_manager} — the first to hoist it`],
        ].map(([label, headline, sub]) => (
          <div className="card" key={label}>
            <div className="eyebrow">{label}</div>
            <h3 className="gold">{headline}</h3>
            <p style={{ margin: 0 }}>{sub}</p>
          </div>
        ))}
      </div>

      <h2>Championship Pain</h2>
      <div className="grid cols-3">
        <div className="card">
          <div className="eyebrow">Most Runner-Up Finishes</div>
          <h3 className="gold">
            <img src={managerIconSmPath(pain.most_runner_up.manager)} alt="" className="mgr-icon" />{" "}
            {pain.most_runner_up.manager} — {pain.most_runner_up.count}×
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
                  <img src={managerIconSmPath(f.champion_manager)} alt="" className="mgr-icon" />{" "}
                  {f.champion_team}{" "}
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
