import { managerIndex, managerProfile, slugify } from "@/lib/data";

export function generateStaticParams() {
  return managerIndex.map((m) => ({ slug: m.slug }));
}

export default async function ManagerPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const profile = managerProfile(slug);
  if (!profile) return <h1>Manager not found</h1>;

  const m = profile.metrics;

  return (
    <>
      <div className="eyebrow">{profile.status_label}</div>
      <h1>
        {profile.emoji} {profile.display_name}
      </h1>

      <div className="card plaque" style={{ marginTop: "1rem" }}>
        <div className="eyebrow">Hall of Fame Plaque</div>
        <p>{profile.plaque}</p>
        {profile.identity && <div className="identity">“{profile.identity}”</div>}
      </div>

      <div className="grid cols-3" style={{ marginTop: "1.25rem" }}>
        {[
          [m.championships, "Championships"],
          [m.runner_ups, "Runner-Up Finishes"],
          [m.playoff_apps, "Playoff Appearances"],
          [`${Math.round(m.playoff_rate * 100)}%`, "Playoff Rate"],
          [m.record, "Regular Season Record"],
          [m.win_pct.toFixed(3), "Win Percentage"],
        ].map(([value, label]) => (
          <div className="card metric" key={String(label)}>
            <div className="metric-value">{value}</div>
            <div className="metric-label">{label}</div>
          </div>
        ))}
      </div>

      {/* The entry point Keeper Hall was missing: a way in from the page where
          people already go to find themselves (product review, F7). */}
      <h2>Keepers</h2>
      <div className="card">
        <p style={{ margin: 0 }}>
          {profile.draft
            ? `Draft identity: ${profile.draft.style}. Kept ${profile.draft.most_kept.player} ${profile.draft.most_kept.count}× — more than anyone else on the roster.`
            : "No draft history recorded."}
        </p>
        <p style={{ marginBottom: 0 }}>
          <a href={`/keepers/${slug}`}>
            See every player {profile.name} couldn’t let go →
          </a>
        </p>
      </div>

      <h2>Season by Season</h2>
      <div className="scroll-x">
        <table>
          <thead>
            <tr>
              <th>Season</th><th>Team</th><th>Record</th>
              <th className="num">Points For</th><th className="num">Finish</th><th>Result</th>
            </tr>
          </thead>
          <tbody>
            {profile.seasons.map((s) => (
              <tr key={s.season}>
                <td className="gold">{s.season}</td>
                <td>{s.team_name}</td>
                <td>{s.wins}-{s.losses}{s.ties ? `-${s.ties}` : ""}</td>
                <td className="num">{s.points_for.toFixed(2)}</td>
                <td className="num muted">{s.rank ? `#${s.rank}` : "—"}</td>
                <td className={s.result.includes("Champion") ? "gold" : "muted"}>{s.result}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2>Head to Head</h2>
      <div className="scroll-x">
        <table>
          <thead>
            <tr>
              <th>Opponent</th><th className="num">GP</th><th>W-L</th>
              <th className="num">Win%</th><th className="num">PF</th><th className="num">PA</th>
            </tr>
          </thead>
          <tbody>
            {profile.head_to_head.map((h) => (
              <tr key={h.opp_manager}>
                <td>
                  {h.opp_emoji}{" "}
                  <a href={`/managers/${slugify(h.opp_manager)}`}>{h.opp_manager}</a>
                </td>
                <td className="num muted">{h.games}</td>
                <td className="gold">{h.wins}-{h.losses}</td>
                <td className="num">{Math.round(h.win_pct * 100)}%</td>
                <td className="num">{h.pf.toLocaleString()}</td>
                <td className="num muted">{h.pa.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2>Team Names</h2>
      <div className="grid cols-3">
        {profile.team_names.map((t) => (
          <div className="card" key={`${t.years}-${t.team_name}`}>
            <div className="gold">{t.years}</div>
            <div>{t.team_name}</div>
          </div>
        ))}
      </div>
    </>
  );
}
