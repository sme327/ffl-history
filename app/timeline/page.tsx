import { timeline, slugify, eventIconPath, eraIconPath, managerIconPath, managerIconSmPath } from "@/lib/data";

export const metadata = { title: "Timeline · {insert witty name here} Museum" };

export default function TimelinePage() {
  const { stats, bySeason } = timeline;

  return (
    <>
      <div className="room-photo" style={{ backgroundImage: "url(/museum/rooms/history-corridor.webp)" }} />
      <div className="room-scrim" />
      <div className="room-title">
        <div className="eyebrow">What happened?</div>
        <h1>LEAGUE TIMELINE</h1>
        <p>The historical spine of the league — every era, every turning point.</p>
      </div>

      <div className="grid cols-4">
        {[
          [stats.total_seasons, "Seasons"],
          [stats.total_events, "Events"],
          [stats.computed_events, "Computed"],
          [stats.editorial_events, "Editorial"],
        ].map(([value, label]) => (
          <div className="card metric" key={String(label)}>
            <div className="metric-value">{value}</div>
            <div className="metric-label">{label}</div>
          </div>
        ))}
      </div>

      {bySeason.map((block) => (
        <section key={block.season}>
          <h2 style={{ display: "flex", alignItems: "baseline", gap: "0.75rem", flexWrap: "wrap" }}>
            <a href={`/seasons/${block.season}`}>{block.season}</a>
            {block.era.name && (
              <span className="pill" style={{ color: block.era.color, borderColor: block.era.color, display: "inline-flex", alignItems: "center", gap: "0.35rem" }}>
                {eraIconPath(block.era.name) && (
                  <img src={eraIconPath(block.era.name)!} alt="" style={{ width: "1rem", height: "1rem" }} />
                )}
                {block.era.name}
              </span>
            )}
            <span className="muted" style={{ fontSize: "var(--step--1)", fontFamily: "var(--body)", letterSpacing: 0 }}>
              {block.count_label}
            </span>
          </h2>

          {block.high.map((event, i) => (
            <div className="event-featured" key={`${event.title}-${i}`}>
              <img
                src={eventIconPath(event.event_type)}
                alt=""
                style={{ width: "2.75rem", height: "2.75rem", flexShrink: 0 }}
              />
              <div>
                <div className="eyebrow" style={{ color: event.color, marginBottom: "0.2rem" }}>
                  {event.importance_label} · {event.label}
                  {event.is_editorial && " · ✦ Editorial"}
                </div>
                <div className="event-featured-title">{event.title}</div>
                {event.description && <p style={{ margin: "0.3rem 0 0" }}>{event.description}</p>}
                {event.manager && (
                  <div className="muted" style={{ marginTop: "0.3rem" }}>
                    <img src={managerIconSmPath(event.manager)} alt="" className="mgr-icon" />{" "}
                    <a href={`/managers/${slugify(event.manager)}`}>{event.manager}</a>
                    {event.franchise_id && ` · ${event.franchise_id}`}
                  </div>
                )}
              </div>
            </div>
          ))}

          {block.other.length > 0 && (
            <div className="event-ledger">
              {block.other.map((event, i) => (
                <div className="event-row" key={`${event.title}-${i}`}>
                  <img src={eventIconPath(event.event_type)} alt="" className="evt-icon" />
                  <span className="event-row-title">{event.title}</span>
                  {event.manager && (
                    <>
                      <span className="muted">—</span>
                      <img src={managerIconSmPath(event.manager)} alt="" className="mgr-icon" />
                      <a href={`/managers/${slugify(event.manager)}`}>{event.manager}</a>
                    </>
                  )}
                  <span className="muted" style={{ marginLeft: "auto", fontSize: "var(--step--1)" }}>
                    {event.label}
                  </span>
                </div>
              ))}
            </div>
          )}
        </section>
      ))}
    </>
  );
}
