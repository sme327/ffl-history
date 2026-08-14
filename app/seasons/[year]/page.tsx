import { seasonDetail, seasonIndex, slugify } from "@/lib/data";

export function generateStaticParams() {
  return seasonIndex.map((s) => ({ year: String(s.season) }));
}

export default async function SeasonPage({
  params,
}: {
  params: Promise<{ year: string }>;
}) {
  const { year } = await params;
  const season = seasonDetail(year);
  if (!season) return <h1>Season not found</h1>;

  const champ = season.champion;

  return (
    <>
      <div className="eyebrow">{season.season} Season</div>
      <h1>{season.title ?? season.season}</h1>
      {season.hook && <p style={{ fontStyle: "italic" }}>{season.hook}</p>}
      {season.narrative && <p style={{ color: "var(--text)" }}>{season.narrative}</p>}

      <div className="grid cols-2" style={{ marginTop: "1.25rem" }}>
        {champ && (
          <div className="champion-card">
            <div className="champion-emoji">{champ.emoji}</div>
            <div className="champion-season">🏆 {season.season} Champion 🏆</div>
            <div className="champion-team">{champ.team}</div>
            <div className="champion-manager">
              <a href={`/managers/${slugify(champ.manager)}`}>{champ.manager}</a>
            </div>
            <div className="champion-score">
              {champ.score.toFixed(2)} – {champ.runner_up_score.toFixed(2)} over{" "}
              {champ.runner_up_team}
            </div>
          </div>
        )}
        {season.nfl_context.length > 0 && (
          <div className="card">
            <div className="eyebrow">NFL in {season.season}</div>
            {season.nfl_context.map((line) => (
              <div key={line} style={{ padding: "0.35rem 0", borderBottom: "1px solid var(--border)" }}>
                🏈 {line}
              </div>
            ))}
            {season.nfl_league_links.length > 0 && (
              <div style={{ marginTop: "0.6rem" }}>
                <div className="eyebrow" style={{ marginBottom: "0.2rem" }}>On our rosters</div>
                {season.nfl_league_links.map((link) => (
                  <div key={link.player} className="muted" style={{ fontSize: "var(--step--1)" }}>
                    <a href={`/players/${slugify(link.player)}`}>{link.player}</a>
                    {" — "}
                    {link.managers.map((m, i) => (
                      <span key={m.manager}>
                        {i > 0 && ", "}
                        <a href={`/managers/${slugify(m.manager)}`}>{m.manager}</a>
                        {m.kept && " (kept)"}
                      </span>
                    ))}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      <h2>Final Standings</h2>
      <div className="scroll-x">
        <table>
          <thead>
            <tr>
              <th>Result</th><th>Team</th><th>Manager</th>
              <th>W-L</th><th className="num">Points For</th><th className="num">RS Finish</th>
            </tr>
          </thead>
          <tbody>
            {season.standings.map((row) => (
              <tr key={row.team}>
                <td className={row.result.includes("Champion") ? "gold" : "muted"}>{row.result}</td>
                <td>{row.emoji} {row.team}</td>
                <td>
                  {row.manager === "—" ? (
                    <span className="muted">—</span>
                  ) : (
                    <a href={`/managers/${slugify(row.manager)}`}>{row.manager}</a>
                  )}
                </td>
                <td>{row.wins}-{row.losses}</td>
                <td className="num">{row.points_for.toFixed(2)}</td>
                <td className="num muted">#{row.rs_rank}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {season.bracket.rounds.length > 0 && (
        <>
          <h2>Playoff Bracket</h2>
          <div
            className="bracket"
            style={{ gridTemplateColumns: `repeat(${season.bracket.rounds.length}, 1fr)` }}
          >
            {season.bracket.rounds.map((round) => (
              <div className="bracket-round" key={round.type}>
                <div className="eyebrow">{round.label}</div>
                <div className="bracket-games">
                {round.games.map((game) => (
                  <div className="matchup" key={`${game.team_1}-${game.team_2}`}>
                    {[
                      [game.seed_1, game.team_1, game.score_1] as const,
                      [game.seed_2, game.team_2, game.score_2] as const,
                    ].map(([seed, team, score]) => (
                      <div
                        key={team}
                        className={`matchup-team${game.winner === team ? " winner" : ""}`}
                      >
                        <span>{seed ? `#${seed} ` : ""}{team}</span>
                        <span>{score.toFixed(1)}</span>
                      </div>
                    ))}
                  </div>
                ))}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      <h2>Top Scorers</h2>
      <div className="scroll-x">
        <table>
          <thead>
            <tr><th className="num">Rank</th><th>Team</th><th>Manager</th><th className="num">Total Points</th></tr>
          </thead>
          <tbody>
            {season.top_scorers.map((s) => (
              <tr key={s.team}>
                <td className="num muted">#{s.rank}</td>
                <td>{s.emoji} {s.team}</td>
                <td>
                  {s.manager === "—" ? <span className="muted">—</span> :
                    <a href={`/managers/${slugify(s.manager)}`}>{s.manager}</a>}
                </td>
                <td className="num gold">{s.points_for.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
