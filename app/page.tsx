import { home, site, slugify } from "@/lib/data";

export default function HomePage() {
  const { stats, current_champion: champ, legends, drought, storylines } = home;

  return (
    <>
      <header className="hero">
        <h1>THE LONG GAME</h1>
        <div className="hero-subtitle">{site.subtitle}</div>
        <div className="hero-tagline">
          Built by friendship.&nbsp; Defined by competition.&nbsp; Occasionally
          ruined by a waiver wire mistake.
        </div>
      </header>
      <hr className="divider" />

      {champ && (
        <>
          <div className="section-centre">
            <div className="eyebrow">Reigning Champion</div>
          </div>
          <div className="champion-card">
            <div className="champion-emoji">{champ.emoji}</div>
            <div className="champion-season">🏆 {champ.season} League Champion 🏆</div>
            <div className="champion-team">{champ.team}</div>
            <div className="champion-manager">
              <a href={`/managers/${slugify(champ.manager)}`}>{champ.manager}</a>
              {champ.titles_all_time > 1 && ` · ${champ.titles_all_time}× Champion`}
            </div>
            <div className="champion-score">
              {champ.score.toFixed(2)} – {champ.runner_up_score.toFixed(2)} over{" "}
              {champ.runner_up_team}
            </div>
          </div>
          <hr className="divider" />
        </>
      )}

      <div className="grid cols-4">
        {[
          [stats.seasons, "Seasons"],
          [stats.active_managers, "Active Members"],
          [stats.unique_champions, "Different Champions"],
          [stats.total_games.toLocaleString(), "Matchups Played"],
        ].map(([value, label]) => (
          <div className="card metric" key={String(label)}>
            <div className="metric-value">{value}</div>
            <div className="metric-label">{label}</div>
          </div>
        ))}
      </div>

      <div className="section-centre">
        <div className="eyebrow">All-Time</div>
        <h2>League Legends</h2>
      </div>
      <div className="grid cols-4">
        {legends.slice(0, 4).map((legend) => (
          <div className="card metric" key={legend.manager}>
            <div style={{ fontSize: "1.75rem" }}>{legend.emoji}</div>
            <div className="metric-value">{legend.titles}</div>
            <div className="metric-label">
              Championship{legend.titles === 1 ? "" : "s"}
            </div>
            <div style={{ marginTop: "0.35rem" }}>
              <a href={`/managers/${slugify(legend.manager)}`}>{legend.manager}</a>
            </div>
            <div className="muted" style={{ fontSize: "var(--step--1)" }}>{legend.years}</div>
          </div>
        ))}
        {drought && (
          <div className="card metric">
            <div style={{ fontSize: "1.75rem" }}>{drought.emoji}</div>
            <div className="metric-value" style={{ color: "var(--muted)" }}>
              {drought.playoff_apps}
            </div>
            <div className="metric-label">Playoff trips · 0 titles</div>
            <div style={{ marginTop: "0.35rem" }}>
              <a href={`/managers/${slugify(drought.manager)}`}>{drought.manager}</a>
            </div>
            <div className="muted" style={{ fontSize: "var(--step--1)" }}>Still waiting…</div>
          </div>
        )}
      </div>

      <div className="section-centre">
        <div className="eyebrow">The Numbers Behind the Legend</div>
        <h2>League Storylines</h2>
      </div>
      <div className="grid cols-2">
        <div className="card">
          <div className="eyebrow">Best Regular Season</div>
          <h3 className="gold">{storylines.best_season.record}</h3>
          <p>{storylines.best_season.summary}</p>
        </div>
        <div className="card">
          <div className="eyebrow">All-Time Scoring Leader</div>
          <h3 className="gold">
            {Math.round(storylines.top_scorer.points_for).toLocaleString()} pts
          </h3>
          <p>
            <a href={`/managers/${slugify(storylines.top_scorer.manager)}`}>
              {storylines.top_scorer.manager}
            </a>{" "}
            — more fantasy points than anyone in league history.
          </p>
        </div>
      </div>
    </>
  );
}
