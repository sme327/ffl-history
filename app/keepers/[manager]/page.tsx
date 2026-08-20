import {
  keeperChainsFor, keeperDnaFor, managerFromSlug, managerIndex, slugify, managerIconPath,
} from "@/lib/data";
import { Trophies } from "@/app/components/icons";

export function generateStaticParams() {
  return managerIndex.map((m) => ({ manager: m.slug }));
}

export default async function ManagerKeepersPage({
  params,
}: {
  params: Promise<{ manager: string }>;
}) {
  const { manager: slug } = await params;
  const manager = managerFromSlug(slug);
  if (!manager) return <h1>Manager not found</h1>;

  const dna = keeperDnaFor(manager);
  const chains = keeperChainsFor(manager).sort(
    (a, b) => b.streak_len - a.streak_len || b.score - a.score,
  );

  return (
    <>
      <div className="room-photo" style={{ backgroundImage: "url(/museum/rooms/the-vault.webp)" }} />
      <div className="room-scrim" />
      <div className="room-title">
        <div className="eyebrow">Keeper Hall</div>
        <h1>
          <img src={managerIconPath(manager)} alt="" className="mgr-icon" /> {manager}
        </h1>
        <p>
          <a href={`/managers/${slug}`}>← Back to {manager}’s profile</a>
        </p>
      </div>

      {dna ? (
        <>
          <div className="card" style={{ borderTop: `3px solid ${dna.color}` }}>
            <div className="eyebrow">{dna.dna}</div>
            <p>{dna.dna_blurb}</p>
          </div>

          <div className="grid cols-4" style={{ marginTop: "1rem" }}>
            {[
              [dna.keeper_count, "Keepers"],
              [`${(dna.keeper_rate * 100).toFixed(1)}%`, "Keeper Rate"],
              [dna.longest_streak, "Longest Streak"],
              [dna.titles, "Titles With Keepers"],
            ].map(([value, label]) => (
              <div className="card metric" key={String(label)}>
                <div className="metric-value">{value}</div>
                <div className="metric-label">{label}</div>
              </div>
            ))}
          </div>

          <h2>Couldn’t Let Go</h2>
          <div className="card">
            <p style={{ margin: 0 }}>
              Kept{" "}
              <a href={`/players/${slugify(dna.favourite.player)}`}>
                {dna.favourite.player}
              </a>{" "}
              {dna.favourite.count}× — more than any other player. Longest
              unbroken run:{" "}
              <a href={`/players/${slugify(dna.longest_streak_player)}`}>
                {dna.longest_streak_player}
              </a>{" "}
              at {dna.longest_streak} straight seasons.
            </p>
          </div>
        </>
      ) : (
        <p>No keeper history recorded for {manager}.</p>
      )}

      <h2>Keeper Chains</h2>
      {chains.length === 0 ? (
        <p>No multi-season keeper runs.</p>
      ) : (
        <div className="grid cols-2">
          {chains.map((chain) => (
            <div className="card" key={`${chain.player_name}-${chain.seasons[0]}`}>
              <h3>
                <a href={`/players/${slugify(chain.player_name)}`}>
                  {chain.player_name}
                </a>{" "}
                <span className="pill">{chain.position}</span>
              </h3>
              <div className="gold">
                {chain.streak_len} straight seasons · score {chain.score.toFixed(1)}
              </div>
              <div className="muted">{chain.seasons.join(" · ")}</div>
              {chain.titles > 0 && (
                <div className="gold">
                  <Trophies count={chain.titles} /> won while kept
                </div>
              )}
              {chain.multi_manager && (
                <div className="muted">
                  Passed through {chain.franchise_id}: {chain.all_managers.join(" → ")}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </>
  );
}
