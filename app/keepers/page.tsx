import { PositionShareBar } from "@/app/components/charts";
import { keeperHall, slugify } from "@/lib/data";

const POSITION_COLORS: Record<string, string> = {
  RB: "#22C55E", WR: "#3B82F6", QB: "#EF4444",
  TE: "#F59E0B", DEF: "#8B5CF6", K: "#6B7280",
};

export const metadata = { title: "Keeper Hall · {insert witty name here} Museum" };

export default function KeeperHallPage() {
  const { totals, notable_chains: chains, manager_dna: dna, most_kept, lore, champions_kept: championsKept, by_season: bySeason } = keeperHall;
  const peakSeason = [...bySeason].sort((a, b) => b.count - a.count || a.season - b.season)[0];
  // The longest run and the highest-scoring run are different questions; the
  // Streamlit page read one row for both.
  const bestChain = [...keeperHall.immortals].sort((a, b) => b.score - a.score || b.streak_len - a.streak_len)[0];
  const topKeeper = dna[0];
  const mostTitles = [...dna].sort((a, b) => b.titles - a.titles || a.manager.localeCompare(b.manager))[0];

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

      <h2>Keeper Lore</h2>
      <p style={{ marginTop: "-0.5rem" }}>
        The players who became institutions — written down, not computed.
      </p>
      <div className="grid cols-2">
        {lore.map((entry) => (
          <div className="card" key={entry.player_name}>
            <h3>
              <a href={`/players/${slugify(entry.player_name)}`}>{entry.player_name}</a>{" "}
              <span className="pill">{entry.position}</span>
              {entry.times_kept > 0 && (
                <span className="gold" style={{ fontSize: "var(--step--1)" }}>
                  {" "}· kept {entry.times_kept}×
                </span>
              )}
            </h3>
            <p style={{ margin: 0 }}>{entry.lore}</p>
          </div>
        ))}
      </div>

      <h2>Keeper Rule Evolution</h2>
      <div className="card">
        <p style={{ marginTop: 0 }}>
          Keepers per season since the rule arrived. The league went from no
          keepers at all to a full slate every year — {peakSeason.count} in{" "}
          <a href={`/seasons/${peakSeason.season}`}>{peakSeason.season}</a>.
        </p>
        <div className="grid" style={{ gap: "0.3rem" }}>
          {bySeason.map((row) => (
            <div
              key={row.season}
              style={{ display: "grid", gridTemplateColumns: "4rem 1fr 2rem", alignItems: "center", gap: "0.5rem" }}
            >
              <a href={`/seasons/${row.season}`} style={{ fontSize: "var(--step--1)" }}>{row.season}</a>
              <span
                style={{
                  background: "var(--gold)", height: 12, borderRadius: 3,
                  width: `${(row.count / peakSeason.count) * 100}%`, minWidth: 4,
                }}
              />
              <span className="gold num" style={{ fontSize: "var(--step--1)", textAlign: "right" }}>
                {row.count}
              </span>
            </div>
          ))}
        </div>
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

      <h2>Players on Championship Rosters</h2>
      <p style={{ marginTop: "-0.5rem" }}>
        Every player kept on a title-winning roster — the common thread in
        championship runs.
      </p>
      <div className="grid cols-3">
        {championsKept.map((player) => (
          <div className="card" key={player.player_name}>
            <h3>
              {"🏆".repeat(player.title_count)}{" "}
              <a href={`/players/${slugify(player.player_name)}`}>{player.player_name}</a>
            </h3>
            <div className="muted">
              {player.managers.join(" / ")} ·{" "}
              {player.seasons.map((year, i) => (
                <span key={year}>
                  {i > 0 && " · "}
                  <a href={`/seasons/${year}`}>{year}</a>
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>

      <h2>Keeper Position Analysis</h2>
      <p style={{ marginTop: "-0.5rem" }}>
        What each manager protects, by position.
      </p>
      <div className="grid cols-2">
        {dna.map((entry) => (
          <div className="card" key={entry.manager}>
            <h3>
              {entry.emoji}{" "}
              <a href={`/keepers/${slugify(entry.manager)}`}>{entry.manager}</a>
            </h3>
            <div className="eyebrow" style={{ marginBottom: "0.4rem" }}>{entry.dna}</div>
            <PositionShareBar counts={entry.position_counts} colors={POSITION_COLORS} />
          </div>
        ))}
      </div>

      <h2>When Great Keeper Runs Ended</h2>
      <p style={{ marginTop: "-0.5rem" }}>
        Every multi-season run that has already finished — and the year the
        manager finally let go.
      </p>
      <div className="grid cols-3">
        {chains
          .filter((chain) => Math.max(...chain.seasons) < Math.max(...keeperHall.keeper_seasons))
          .slice(0, 9)
          .map((chain) => (
            <div className="card" key={`${chain.player_name}-${chain.seasons[0]}`}>
              <h3>
                <a href={`/players/${slugify(chain.player_name)}`}>{chain.player_name}</a>
              </h3>
              <div className="gold">
                {chain.seasons[0]}–{chain.seasons[chain.seasons.length - 1]} ·{" "}
                {chain.streak_len} seasons
              </div>
              <div className="muted">
                Released after{" "}
                <a href={`/seasons/${chain.seasons[chain.seasons.length - 1]}`}>
                  {chain.seasons[chain.seasons.length - 1]}
                </a>{" "}
                by{" "}
                <a href={`/keepers/${slugify(chain.primary_manager)}`}>
                  {chain.primary_manager}
                </a>
              </div>
            </div>
          ))}
      </div>

      <h2>Keeper Records &amp; Superlatives</h2>
      <div className="grid cols-3">
        {[
          ["Longest Single Streak", `${chains[0].streak_len} seasons`,
           `${chains[0].player_name} · ${chains[0].seasons[0]}–${chains[0].seasons[chains[0].seasons.length - 1]}`],
          ["Most Valuable Keeper Run", `Score ${bestChain.score.toFixed(1)}`,
           `${bestChain.player_name} — ${bestChain.titles} title${bestChain.titles === 1 ? "" : "s"} while kept`],
          ["Most Kept Player", `${most_kept[0].count}×`, most_kept[0].player_name],
          ["Most Keepers Named", `${topKeeper.keeper_count}`,
           `${topKeeper.manager} — ${(topKeeper.keeper_rate * 100).toFixed(1)}% of their picks`],
          ["Most Titles With Keepers", `${mostTitles.titles}`, mostTitles.manager],
          ["Busiest Keeper Season", `${peakSeason.count} keepers`, `${peakSeason.season}`],
        ].map(([label, headline, sub]) => (
          <div className="card" key={label}>
            <div className="eyebrow">{label}</div>
            <h3 className="gold">{headline}</h3>
            <p style={{ margin: 0 }}>{sub}</p>
          </div>
        ))}
      </div>

      <h2>Player Keeper Timelines</h2>
      <p style={{ marginTop: "-0.5rem" }}>
        The most-kept players and the seasons they were protected.
      </p>
      <div className="card">
        {most_kept.slice(0, 15).map((player) => {
          const runs = keeperHall.immortals.filter((c) => c.player_name === player.player_name);
          const seasons = [...new Set(runs.flatMap((c) => c.seasons))].sort();
          return (
            <div className="chron-row" key={player.player_name}>
              <div className="chron-mgr">
                <a href={`/players/${slugify(player.player_name)}`}>{player.player_name}</a>
                <span className="pill">{player.position}</span>
              </div>
              <div className="chron-years">
                {seasons.map((year) => (
                  <a className="year-pill gold-pill" key={year} href={`/seasons/${year}`}>{year}</a>
                ))}
              </div>
            </div>
          );
        })}
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
