import { playerHistory, playerIndex, slugify } from "@/lib/data";

export function generateStaticParams() {
  return playerIndex.map((p) => ({ slug: p.slug }));
}

export default async function PlayerPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const player = playerHistory(slug);
  if (!player) return <h1>Player not found</h1>;

  return (
    <>
      <div className="eyebrow">Player History</div>
      <h1>{player.playerName}</h1>
      <p>
        {player.position && <span className="pill">{player.position}</span>}{" "}
        {player.firstSeason}–{player.lastSeason} · owned by{" "}
        {player.owners.length} manager{player.owners.length === 1 ? "" : "s"}
      </p>

      <div className="grid cols-3">
        {[
          [player.totalDrafts, "Times Drafted"],
          [player.totalKeepers, "Times Kept"],
          [player.totalSeasons, "Roster Seasons"],
        ].map(([value, label]) => (
          <div className="card metric" key={String(label)}>
            <div className="metric-value">{value}</div>
            <div className="metric-label">{label}</div>
          </div>
        ))}
      </div>

      {player.chains.length > 0 && (
        <>
          <h2>Keeper Runs</h2>
          <div className="grid cols-2">
            {player.chains.map((chain) => (
              <div className="card" key={chain.seasons[0]}>
                <h3 className="gold">{chain.streak_len} straight seasons</h3>
                <div className="muted">{chain.seasons.join(" · ")}</div>
                <div>
                  <a href={`/keepers/${slugify(chain.primary_manager)}`}>
                    {chain.primary_manager}
                  </a>
                  {chain.multi_manager && ` → ${chain.all_managers.join(" → ")}`}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      <h2>Ownership</h2>
      <div className="scroll-x">
        <table>
          <thead>
            <tr>
              <th>Manager</th><th className="num">Drafted</th><th className="num">Kept</th>
              <th className="num">Seasons</th><th>Years</th>
            </tr>
          </thead>
          <tbody>
            {player.owners.map((o) => (
              <tr key={o.manager}>
                <td>
                  <a href={`/keepers/${slugify(o.manager)}`}>{o.manager}</a>
                </td>
                <td className="num">{o.draft_count}</td>
                <td className="num gold">{o.keeper_count || "—"}</td>
                <td className="num">{o.total_seasons}</td>
                <td className="muted">{o.seasons.join(" · ")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
