import { ProgramIssue, ProgramCard, programIndex, site, slugify, managerIconSmPath } from "@/lib/data";

function noteKey(card: ProgramCard): string {
  return [card.manager_a, card.manager_b].sort().join("|");
}

// Placeholder glyphs until the commissioned division marks land in
// public/museum/ — swap this for an <img> path helper then.
const DIVISION_ICON: Record<string, string> = {
  Rock: "🪨",
  Paper: "📄",
  Scissors: "✂️",
};

// Matchup cards speak in locker-room short names; the history ledger and
// Milestone Watch keep full names. Longest keys replace first so
// "Kevin Swanson" never half-matches through "Swanson".
const SHORT_NAME: Record<string, string> = {
  "Kevin O'Boyle": "O'Boyle",
  "Kevin Swanson": "Swanson",
  "Brian Clark": "Clark",
  "Steve Swanson": "Steve",
  Thomas: "Tom",
  Douglas: "Doug",
};

function shortName(name: string): string {
  return SHORT_NAME[name] ?? name;
}

function shortenNames(text: string): string {
  let out = text;
  for (const full of Object.keys(SHORT_NAME).sort((a, b) => b.length - a.length)) {
    out = out.split(full).join(SHORT_NAME[full]);
  }
  return out;
}

function DivisionMark({ division }: { division: string }) {
  return (
    <span title={`${division} Division`} aria-label={`${division} Division`}>
      {DIVISION_ICON[division] ?? division}
    </span>
  );
}

function recordNumerals(card: ProgramCard): string {
  const { record } = card.facts;
  const ties = record.ties ? `–${record.ties}` : "";
  return `${record[card.manager_a]}–${record[card.manager_b]}${ties}`;
}

function Manager({ name, short }: { name: string; short?: boolean }) {
  return (
    <>
      <img src={managerIconSmPath(name)} alt="" className="mgr-icon" />{" "}
      <a href={`/managers/${slugify(name)}`}>{short ? shortName(name) : name}</a>
    </>
  );
}

export function IssueView({ issue }: { issue: ProgramIssue }) {
  const copy = issue.copy;
  const milestone =
    typeof copy?.milestone === "string"
      ? { value: null, label: null, text: copy.milestone }
      : copy?.milestone ?? null;
  const wih = issue.week_in_history;
  const historyRows =
    copy?.history_lines ??
    [
      ...wih.best.map((r, i) => ({
        year: r.season,
        text: `${r.manager ?? r.team} scores ${r.score.toFixed(2)}`,
        pts: r.score.toFixed(2),
        tag: i === 0 ? "best ever" : `${i + 1}${i === 1 ? "nd" : "rd"} best`,
      })),
      ...(wih.best_losing
        ? [{ year: wih.best_losing.season, text: `${wih.best_losing.manager ?? wih.best_losing.team} scores ${wih.best_losing.score.toFixed(2)} — and loses`, pts: wih.best_losing.score.toFixed(2), tag: "best in defeat" }]
        : []),
      ...(wih.worst
        ? [{ year: wih.worst.season, text: `${wih.worst.manager ?? wih.worst.team} finds the floor`, pts: wih.worst.score.toFixed(2), tag: "worst ever" }]
        : []),
    ];
  const others = programIndex.filter((i) => i.slug !== issue.slug).reverse();

  return (
    <>
      <div className="room-photo" style={{ backgroundImage: "url(/museum/rooms/the-arena.webp)" }} />
      <div className="room-scrim" />
      <div className="program-masthead">
        <div className="eyebrow">{issue.season} Season · Week {issue.week}</div>
        <h1>THE PROGRAM</h1>
        {copy?.theme && <div className="program-issue-line">{copy.theme}</div>}
      </div>
      <hr className="divider" style={{ maxWidth: "420px" }} />

      {copy && (
        <div className="program-open">
          {copy.cold_open.map((para) => (
            <p key={para.slice(0, 40)}>{para}</p>
          ))}
        </div>
      )}

      <h2>The Matchups</h2>
      <div className="program-grid">
        {[...issue.cards].sort((a, b) => b.facts.games - a.facts.games).map((card) => (
          <div className="card program-card" key={noteKey(card)}>
            <div className="program-tag">
              <span>
                {issue.season} · Week {issue.week} · <DivisionMark division={card.division_a} />
                {!card.in_division && (
                  <> · <DivisionMark division={card.division_b} /></>
                )}
              </span>
              <span>{card.facts.first_season ? `since ${card.facts.first_season}` : "first meeting"}</span>
            </div>
            <h3>
              {card.team_a} <span className="muted">vs</span> {card.team_b}
            </h3>
            <div className="program-managers">
              <Manager name={card.manager_a} short />
              <span> · </span>
              <Manager name={card.manager_b} short />
            </div>
            <div className="program-record">{recordNumerals(card)}</div>
            <div className="program-record-label">
              {card.facts.record_rs[card.manager_a]}–{card.facts.record_rs[card.manager_b]} regular season
              {card.facts.record_po[card.manager_a] + card.facts.record_po[card.manager_b] > 0 && (
                <> · {card.facts.record_po[card.manager_a]}–{card.facts.record_po[card.manager_b]} playoffs</>
              )}
            </div>
            {card.facts.record[card.manager_a] + card.facts.record[card.manager_b] > 0 && (
              <div
                className="program-bar"
                title={`${shortName(card.manager_a)} ${card.facts.record[card.manager_a]} · ${shortName(card.manager_b)} ${card.facts.record[card.manager_b]}`}
              >
                <span style={{ flex: card.facts.record[card.manager_a] || 0.5, background: site.managerColors[card.manager_a] ?? "var(--gold)" }} />
                <span style={{ flex: card.facts.record[card.manager_b] || 0.5, background: site.managerColors[card.manager_b] ?? "var(--muted)" }} />
              </div>
            )}
            <ul className="program-facts">
              {card.storylines.map((line) => (
                <li key={line}>{shortenNames(line)}</li>
              ))}
            </ul>
            {copy?.notes?.[noteKey(card)] && (
              <p className="identity program-note">{copy.notes[noteKey(card)]}</p>
            )}
          </div>
        ))}
      </div>
      {copy?.kicker && <p className="identity program-kicker">{copy.kicker}</p>}

      <h2>Week {issue.week} in the Archive</h2>
      <div className="program-archive-span">{site.founded}–{issue.season - 1}</div>
      <div className="program-history">
        <div className="scroll-x">
          <table>
            <thead>
              <tr>
                <th>Mark</th>
                <th className="num">Points</th>
                <th>What happened</th>
                <th className="num">Year</th>
              </tr>
            </thead>
            <tbody>
              {historyRows.map((row) => (
                <tr key={`${row.year}-${row.tag}`}>
                  <td className="mark">{row.tag}</td>
                  <td className="num gold pts">{row.pts}</td>
                  <td>{row.text}</td>
                  <td className="num year">{row.year}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {milestone && (
        <>
          <h2>Milestone Watch</h2>
          <div className="program-milestone">
            {milestone.value && <div className="milestone-value">{milestone.value}</div>}
            {milestone.label && <div className="milestone-label">{milestone.label}</div>}
            <p>{milestone.text}</p>
          </div>
        </>
      )}

      {others.length > 0 && (
        <>
          <h2>Back Issues</h2>
          <div className="chron-years" style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
            {others.map((i) => (
              <a className="year-pill" key={i.slug} href={`/program/${i.slug}`}>
                {i.season} wk {i.week}
              </a>
            ))}
          </div>
        </>
      )}
    </>
  );
}
