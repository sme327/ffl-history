import { Recap, RecapPlayer, site, slugify, managerIconSmPath } from "@/lib/data";
import { awardTiles, gameFacts, ordinal, pts, recordLines, seriesLine } from "@/lib/recap";
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

function PlayerPlacard({ recap, label, rows, note }: { recap: Recap; label: string; rows: RecapPlayer[]; note?: string }) {
  if (rows.length === 0) return null;
  return (
    <div className="card recap-placard">
      <div className="recap-label">{label}</div>
      {rows.map((p) => (
        <div className="recap-player" key={`${p.team}-${p.name}`}>
          <div className="recap-value">{pts(p.points)}</div>
          <div className="recap-player-name">{p.name}</div>
          <div className="recap-detail">
            {recap.managers[p.team].team} · <Manager name={p.team} />
            {p.projected != null && <> · proj {pts(p.projected)}</>}
          </div>
        </div>
      ))}
      {note && <p className="identity recap-note">{note}</p>}
    </div>
  );
}

export function RecapView({ recap }: { recap: Recap }) {
  const copy = recap.copy;
  const tiles = awardTiles(recap);
  const records = recordLines(recap);
  const games = [...recap.games].sort((x, y) => y.margin - x.margin);

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
          <p>
            Every Week {recap.week} final, every lineup judged in hindsight, and what it all did to the lifetime
            series.
          </p>
        )}
      </div>

      <h2>The Finals</h2>
      <div className="program-grid">
        {games.map((g) => {
          const key = [g.a, g.b].sort().join("|");
          const [w, l] = g.winner === g.b ? [g.b, g.a] : [g.a, g.b];
          const tw = recap.teams[w];
          const tl = recap.teams[l];
          const facts = gameFacts(recap, g);
          const divA = recap.managers[w].division;
          const divB = recap.managers[l].division;
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
                {recap.managers[w].team} <span className="muted">def.</span> {recap.managers[l].team}
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

      <h2>The Awards</h2>
      <div className="recap-placards">
        {tiles.map((t) => (
          <div className="card recap-placard" key={`${t.id}-${t.team}`}>
            <div className="recap-label">{t.label}</div>
            <div className="recap-value">{t.value}</div>
            <div className="recap-who">
              <Manager name={t.team} /> <span className="muted">· {recap.managers[t.team].team}</span>
            </div>
            <div className="recap-detail">{t.detail}</div>
            {copy?.awards?.[t.id] && <p className="identity recap-note">{copy.awards[t.id]}</p>}
          </div>
        ))}
      </div>

      <h2>Players of the Week</h2>
      <div className="recap-placards">
        {Object.entries(recap.players_of_week).map(([pos, rows]) => (
          <PlayerPlacard key={pos} recap={recap} label={`${pos} of the Week`} rows={rows} note={copy?.awards?.[`${pos}_of_week`]} />
        ))}
      </div>

      <h2>Best on the Bench</h2>
      <div className="recap-placards recap-placards-4">
        {Object.entries(recap.bench_best).map(([pos, rows]) => (
          <PlayerPlacard key={pos} recap={recap} label={`Benchwarmer · ${pos}`} rows={rows} note={copy?.awards?.[`${pos}_bench`]} />
        ))}
      </div>
      {recap.dud.length > 0 && (
        <div className="recap-placards" style={{ marginTop: "1rem" }}>
          <div className="card recap-placard">
            <div className="recap-label">Dud of the Week</div>
            {recap.dud.map((p) => (
              <div className="recap-player" key={p.name}>
                <div className="recap-value">{pts(p.points)}</div>
                <div className="recap-player-name">{p.name}</div>
                <div className="recap-detail">
                  started by <Manager name={p.team} /> · projected {pts(p.projected)}, missed by {pts(p.shortfall)}
                </div>
              </div>
            ))}
            {copy?.awards?.dud && <p className="identity recap-note">{copy.awards.dud}</p>}
          </div>
        </div>
      )}

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
                  <td>{recap.managers[s.manager].team}</td>
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
        playoffs and consolation games included.
      </p>
      <ProgramIssuePills slug={recap.slug} />
    </>
  );
}
