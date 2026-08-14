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
          <div className="champion-card champion-hero">
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
        <div className="eyebrow">Recent Champions</div>
      </div>
      <div className="grid cols-4">
        {home.recent_champions.map((champion) => (
          <div className="card mini-champ" key={champion.season}>
            <div style={{ fontSize: "1.4rem" }}>{champion.emoji}</div>
            <div className="mini-champ-year">
              <a href={`/seasons/${champion.season}`}>{champion.season}</a>
            </div>
            <div className="mini-champ-team">{champion.team}</div>
            <div className="mini-champ-mgr">
              <a href={`/managers/${slugify(champion.manager)}`}>{champion.manager}</a>
            </div>
            {champion.titles_to_date > 1 && (
              <div className="gold" style={{ fontSize: "var(--step--1)" }}>
                {"🏆".repeat(champion.titles_to_date)} — {champion.titles_to_date}× champ
              </div>
            )}
          </div>
        ))}
      </div>

      <hr className="divider" />

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
      <div className="grid cols-4">
        {storylines.most_championships && (
          <div className="card">
            <div className="eyebrow">Most Championships</div>
            <h3 className="gold">
              {storylines.most_championships.titles}× —{" "}
              {storylines.most_championships.manager}
            </h3>
            <p>
              Won in {storylines.most_championships.years}. The benchmark
              everyone is chasing.
            </p>
          </div>
        )}
        <div className="card">
          <div className="eyebrow">Best Regular Season</div>
          <h3 className="gold">{storylines.best_season.record}</h3>
          <p>{storylines.best_season.summary}</p>
        </div>
        {drought && (
          <div className="card">
            <div className="eyebrow">Most Trips Without a Title</div>
            <h3 className="gold">{drought.playoff_apps} Appearances</h3>
            <p>
              <a href={`/managers/${slugify(drought.manager)}`}>{drought.manager}</a>{" "}
              — the playoffs keep calling. The trophy doesn’t.
            </p>
          </div>
        )}
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
      <div className="section-centre">
        <div className="eyebrow">Museum Destinations</div>
        <h2>Explore the Exhibits</h2>
        <p style={{ marginTop: 0 }}>Every section is a destination. Start anywhere.</p>
      </div>
      <div className="grid three-up">
        {[
          ["🏆", "Trophy Room", "Every champion. Every dynasty. The immortal record of who won and how.", "/champions"],
          ["📅", "Timeline", "The historical spine of the league — every era, every turning point.", "/timeline"],
          ["🔑", "Keeper Hall", "25 years of attachment, loyalty, and the players nobody could let go.", "/keepers"],
          ["📋", "Draft Legends", "The obsessions, the archetypes, and the players everyone had to have.", "/draft"],
          ["👤", "Manager Files", "Career plaques, rivalries, and records for every competitor.", "/managers"],
          ["🏟️", "Franchise Files", "Lineages, stewardship eras, and the franchises that built this league.", "/franchises"],
        ].map(([icon, title, desc, href]) => (
          <a className="card nav-card" key={href} href={href}>
            <div className="eyebrow">Exhibit</div>
            <div className="nav-card-icon">{icon}</div>
            <div className="nav-card-title">{title}</div>
            <div className="nav-card-desc">{desc}</div>
          </a>
        ))}
      </div>

      <div className="teaser">
        <hr className="divider" style={{ maxWidth: 400 }} />
        <div className="teaser-line">
          {stats.seasons} SEASONS.
          <br />
          {stats.unique_champions} DIFFERENT CHAMPIONS.
          <br />
          ONE LEAGUE THAT NEVER QUIT.
        </div>
        <a className="teaser-cta" href="/champions">
          Enter the Trophy Room &rarr;
        </a>
      </div>
    </>
  );
}
