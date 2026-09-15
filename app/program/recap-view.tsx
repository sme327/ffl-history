import { Recap, RecapPlayer, site, slugify, managerIconPath, managerIconSmPath } from "@/lib/data";
import { awardPairs, bestWorst, gameFacts, ordinal, performanceRows, pts, recordLines, seriesLine, type AwardCard } from "@/lib/recap";
import { shortName } from "@/lib/program-names";
import { ProgramIssuePills, ProgramTabs } from "./program-tabs";

const DIVISION_ICON: Record<string, string> = { Rock: "🪨", Paper: "📄", Scissors: "✂️" };

function Manager({ name }: { name: string }) {
  return (
    <>
      <img src={managerIconSmPath(name)} alt="" className="mgr-icon" />{" "}
      <a href={`/managers/${slugify(name)}`}>{shortName(name)}</a>
    </>
  );
}

function initials(name: string): string {
  return name
    .split(" ")
    .map((w) => w[0])
    .slice(0, 2)
    .join("");
}

/** A player as a placard: headshot (a team logo for a defense) with the
 * manager's medallion pinned to it, the points as the exhibit, the NFL game
 * beneath. */
function PlayerPlacard({ recap, label, player, note }: { recap: Recap; label: string; player: RecapPlayer; note?: string }) {
  const isDef = player.position === "DEF";
  return (
    <div className="card recap-player-card">
      <div className={`recap-photo${isDef ? " logo" : ""}`}>
        {player.photo ? <img src={player.photo} alt={player.name} /> : <span className="recap-photo-fallback">{initials(player.name)}</span>}
        <img className="recap-photo-badge" src={managerIconSmPath(player.team)} alt="" />
      </div>
      <div className="recap-label">{label}</div>
      <div className="recap-player-name">{player.name}</div>
      <div className="recap-detail">
        {recap.managers[player.team].team} · <Manager name={player.team} />
      </div>
      <div className="recap-value">{pts(player.points)}</div>
      <div className="recap-game">
        {player.opponent || player.nfl_team || ""}
        {player.projected != null && <> · proj {pts(player.projected)}</>}
      </div>
      {note && <p className="identity recap-note">{note}</p>}
    </div>
  );
}

/** League award cards carry numbers only — never a written note — so every
 * card in a pair keeps the same shape (commissioner, 2026-09-15). */
function AwardSide({ recap, cards }: { recap: Recap; cards: AwardCard[] }) {
  if (cards.length === 0) return <div />;
  return (
    <div className="recap-award-side">
      {cards.map((c) => (
        <div className="card recap-award" key={`${c.id}-${c.team}-${c.player?.name ?? ""}`}>
          <div className="recap-award-head">
            {c.player ? (
              <span className="recap-award-photo">{c.player.photo ? <img src={c.player.photo} alt="" /> : initials(c.player.name)}</span>
            ) : (
              <img className="recap-award-medal" src={managerIconPath(c.team)} alt="" />
            )}
            <span className="recap-label">{c.label}</span>
          </div>
          <div className="recap-award-row">
            <span className="recap-award-name">{c.player ? c.player.name : recap.managers[c.team].team}</span>
            <span className="recap-award-value">{c.value}</span>
          </div>
          <div className="recap-award-row recap-award-ref">
            <span>
              <Manager name={c.team} /> · {c.refLabel}
            </span>
            <span>{c.ref}</span>
          </div>
          <div className="recap-detail">{c.detail}</div>
        </div>
      ))}
    </div>
  );
}

export function RecapView({ recap }: { recap: Recap }) {
  const copy = recap.copy;
  const note = (id: string) => copy?.awards?.[id];
  const M = recap.managers;
  const records = recordLines(recap);
  const games = [...recap.games].sort((x, y) => y.margin - x.margin);
  const perf = performanceRows(recap);

  return (
    <>
      <div className="room-photo" style={{ backgroundImage: "url(/museum/rooms/the-arena.webp)" }} />
      <div className="room-scrim" />
      <div className="program-masthead">
        <div className="eyebrow">The Recap · {recap.season} Season · Week {recap.week}</div>
        <h1>THE PROGRAM</h1>
        {copy?.theme && <div className="program-issue-line">{copy.theme}</div>}
      </div>
      <ProgramTabs slug={recap.slug} week={recap.week} active="recap" />

      <div className="program-open">
        {copy?.cold_open?.length ? (
          copy.cold_open.map((para) => <p key={para.slice(0, 40)}>{para}</p>)
        ) : (
          <p>Every Week {recap.week} final, every lineup judged in hindsight, and what it all did to the lifetime series.</p>
        )}
      </div>

      <div className="recap-bestworst">
        {bestWorst(recap).map((b) => (
          <div className={`card recap-bw ${b.id === "highest_score" ? "best" : "worst"}`} key={`${b.id}-${b.team}`}>
            <div className="recap-label">{b.label}</div>
            <img className="recap-bw-medal" src={managerIconPath(b.team)} alt="" />
            <div className="recap-bw-team">{M[b.team].team}</div>
            <div className="recap-detail">
              <Manager name={b.team} /> · {b.line}
            </div>
            <div className="recap-value recap-bw-score">{b.score}</div>
            {note(b.id) && <p className="identity recap-note">{note(b.id)}</p>}
          </div>
        ))}
      </div>

      <h2>The Finals</h2>
      <div className="program-grid">
        {games.map((g) => {
          const key = [g.a, g.b].sort().join("|");
          const [w, l] = g.winner === g.b ? [g.b, g.a] : [g.a, g.b];
          const tw = recap.teams[w];
          const tl = recap.teams[l];
          const facts = gameFacts(recap, g);
          const divA = M[w].division;
          const divB = M[l].division;
          return (
            <div className="card program-card" key={key}>
              <div className="program-tag">
                <span>
                  Final · Week {recap.week} · {DIVISION_ICON[divA] ?? divA}
                  {divA !== divB && <> · {DIVISION_ICON[divB] ?? divB}</>}
                </span>
                <span>by {pts(g.margin)}</span>
              </div>
              <h3>
                {M[w].team} <span className="muted">def.</span> {M[l].team}
              </h3>
              <div className="program-managers">
                <Manager name={w} />
                <span> · </span>
                <Manager name={l} />
              </div>
              <div className="program-record">
                {pts(tw.actual)}–{pts(tl.actual)}
              </div>
              <div className="program-record-label">{seriesLine(recap, g)} lifetime</div>
              <div className="recap-lines">
                <span>
                  {shortName(w)}: proj {pts(tw.projected)} · best {pts(tw.optimal)}
                </span>
                <span>
                  {shortName(l)}: proj {pts(tl.projected)} · best {pts(tl.optimal)}
                </span>
              </div>
              {facts.length > 0 && (
                <ul className="program-facts">
                  {facts.map((line) => (
                    <li key={line}>{line}</li>
                  ))}
                </ul>
              )}
              {copy?.notes?.[key] && <p className="identity program-note">{copy.notes[key]}</p>}
            </div>
          );
        })}
      </div>
      {copy?.kicker && <p className="identity program-kicker">{copy.kicker}</p>}

      <h2>Lineups in Hindsight</h2>
      <div className="card recap-perf">
        <div className="recap-perf-legend">
          <span>
            <i className="swatch fill" /> scored
          </span>
          <span>
            <i className="swatch track" /> best possible lineup
          </span>
          <span>
            <i className="swatch tick" /> starters&rsquo; projection
          </span>
        </div>
        {perf.map((r) => (
          <div className="recap-perf-row" key={r.team}>
            <span className="recap-perf-rank">{r.rank}</span>
            <img className="recap-perf-medal" src={managerIconPath(r.team)} alt="" />
            <div className="recap-perf-main">
              <div className="recap-perf-name">
                <strong>{M[r.team].team}</strong>
                <span className="muted">{shortName(r.team)}</span>
              </div>
              <div
                className="recap-perf-bar"
                role="img"
                aria-label={`${M[r.team].team}: ${r.actual} of a possible ${r.optimal}, projected ${r.projected}`}
              >
                <span className="track" style={{ width: `${r.trackPct}%` }} />
                <span className="fill" style={{ width: `${r.fillPct}%` }} />
                {r.tickPct != null && <span className="tick" style={{ left: `${r.tickPct}%` }} />}
              </div>
              <div className="recap-perf-label">
                <strong>{r.actual}</strong> of {r.optimal} max · <span className="pct">{r.efficiency}</span>
                <span className="proj"> · proj {r.projected}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <h2>Players of the Week</h2>
      <div className="recap-players recap-players-6">
        {Object.entries(recap.players_of_week).flatMap(([pos, rows]) =>
          rows.map((p) => <PlayerPlacard key={`${pos}-${p.name}`} recap={recap} label={pos} player={p} note={note(`${pos}_of_week`)} />),
        )}
      </div>

      <h2>Benchwarmers of the Week</h2>
      <div className="recap-players">
        {Object.entries(recap.bench_best).flatMap(([pos, rows]) =>
          rows.map((p) => (
            <PlayerPlacard key={`${pos}-${p.name}`} recap={recap} label={`${pos} · bench`} player={p} note={note(`${pos}_bench`)} />
          )),
        )}
      </div>

      <h2>League Awards</h2>
      <div className="recap-award-pairs">
        {awardPairs(recap).map((pair, i) => (
          <div className="recap-award-pair" key={i}>
            <AwardSide recap={recap} cards={pair.left} />
            <AwardSide recap={recap} cards={pair.right} />
          </div>
        ))}
      </div>

      {records.length > 0 && (
        <>
          <h2>For the Record</h2>
          <div className="program-history">
            <div className="scroll-x">
              <table>
                <thead>
                  <tr>
                    <th>Mark</th>
                    <th className="num">Points</th>
                    <th>What happened</th>
                  </tr>
                </thead>
                <tbody>
                  {records.map((r) => (
                    <tr key={r.text}>
                      <td className="mark">{r.tag}</td>
                      <td className="num gold pts">{r.value}</td>
                      <td>{r.text}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      <h2>Standings</h2>
      <div className="program-history">
        <div className="scroll-x">
          <table>
            <thead>
              <tr>
                <th className="num">#</th>
                <th>Team</th>
                <th>Manager</th>
                <th>Div</th>
                <th className="num">W–L</th>
                <th className="num">PF</th>
              </tr>
            </thead>
            <tbody>
              {recap.standings.map((s, i) => (
                <tr key={s.manager}>
                  <td className="num">{ordinal(i + 1)}</td>
                  <td>{M[s.manager].team}</td>
                  <td>
                    <span style={{ color: site.managerColors[s.manager] ?? "inherit" }}>●</span>{" "}
                    <a href={`/managers/${slugify(s.manager)}`}>{s.manager}</a>
                  </td>
                  <td title={`${s.division} Division`}>{DIVISION_ICON[s.division] ?? s.division}</td>
                  <td className="num">
                    {s.wins}–{s.losses}
                    {s.ties ? `–${s.ties}` : ""}
                  </td>
                  <td className="num">{pts(s.points_for)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <p className="recap-footnote">
        Best possible lineup: the highest-scoring legal lineup from each roster&rsquo;s starters and bench (IR
        excluded). Projections are Yahoo&rsquo;s original pregame numbers. Lifetime series count every meeting,
        playoffs and consolation games included. Player photos via Sleeper.
      </p>
      <ProgramIssuePills slug={recap.slug} />
    </>
  );
}
