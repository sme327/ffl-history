import { keeperHall, slugify } from "@/lib/data";

export const metadata = { title: "Keeper Hall · The Long Game" };

export default function KeeperHallPage() {
  const { totals, notable_chains: chains, manager_dna: dna, most_kept } = keeperHall;

  return (
    <>
      <div className="eyebrow">Who couldn’t let go?</div>
      <h1>KEEPER HALL</h1>
      <p>25 years of attachment, loyalty, and the players nobody could release.</p>

      <div className="grid cols-4">
        {[
          [totals.keepers, "Keepers Named"],
          [totals.unique_players, "Different Players"],
          [totals.chains, "Keeper Runs"],
          [totals.managers, "Managers"],
        ].map(([value, label]) => (
          <div className="card metric" key={String(label)}>
            <div className="metric-value">{value}</div>
            <div className="metric-label">{label}</div>
          </div>
        ))}
      </div>

      {/* Entry points: find yourself, or find a player. */}
      <h2>Find Your Keepers</h2>
      <div className="grid cols-4">
        {dna.map((d) => (
          <a className="card" key={d.manager} href={`/keepers/${slugify(d.manager)}`}>
            <div style={{ fontSize: "1.5rem" }}>{d.emoji}</div>
            <h3>{d.manager}</h3>
            <div className="muted">{d.dna}</div>
            <div className="gold">{d.keeper_count} keepers</div>
          </a>
        ))}
      </div>

      <h2>The Immortals</h2>
      <div className="grid cols-2">
        {chains.slice(0, 8).map((chain) => (
          <div className="card" key={`${chain.player_name}-${chain.seasons[0]}`}>
            <h3>
              <a href={`/players/${slugify(chain.player_name)}`}>{chain.player_name}</a>{" "}
              <span className="pill">{chain.position}</span>
            </h3>
            <div className="gold">
              {chain.streak_len} straight seasons · score {chain.score.toFixed(1)}
            </div>
            <div className="muted">
              <a href={`/keepers/${slugify(chain.primary_manager)}`}>
                {chain.primary_manager}
              </a>{" "}
              · {chain.seasons.join(" · ")}
            </div>
          </div>
        ))}
      </div>

      <h2>Most Kept</h2>
      <div className="scroll-x">
        <table>
          <thead>
            <tr><th>Player</th><th>Pos</th><th className="num">Times Kept</th></tr>
          </thead>
          <tbody>
            {most_kept.slice(0, 20).map((p) => (
              <tr key={p.player_name}>
                <td><a href={`/players/${slugify(p.player_name)}`}>{p.player_name}</a></td>
                <td className="muted">{p.position}</td>
                <td className="num gold">{p.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
