import {
  ShowItem,
  latestEpisode,
  currentPreview,
  itemHref,
  previewPlayed,
  publishedEpisodes,
  releasedLabel,
  weeksLabel,
  withVersion,
} from "./catalog";
import { programIndex, recapIndex } from "@/lib/data";

/** Shared chrome for every show page: back links and the show masthead strip. */
export function ShowTopbar() {
  return (
    <nav className="atl-topbar" aria-label="Show navigation">
      <a className="atl-home" href="/">← Back to the league museum</a>
      <a className="atl-production" href="/show">Across the Line · all episodes</a>
    </nav>
  );
}

export function ShowFooter() {
  return (
    <footer className="atl-footer">
      <span>Across the Line <small> / A SME327 production</small></span>
      <a href="/program">The Program: this week in the league →</a>
    </footer>
  );
}

/** The player plus its lower third. Server-rendered; the only "JS" is the browser's own video controls. */
export function ShowPlayer({ item, priority = false }: { item: ShowItem; priority?: boolean }) {
  const src = withVersion(item.video, item.version);
  const label = item.kind === "episode" ? `Episode ${String(item.number).padStart(2, "0")}` : `Week ${item.week}`;
  const sub = item.kind === "episode" ? weeksLabel(item) : "Weekly preview";
  return (
    <section className="atl-broadcast" id="watch" tabIndex={-1} aria-label={`Watch ${item.title}`}>
      <div className="atl-player-bar">
        <span><i aria-hidden="true" /> {item.kind === "episode" ? "In the studio" : "This week"}</span>
        <span>{[item.runtime, item.released && `Released ${releasedLabel(item.released)}`].filter(Boolean).join(" · ")}</span>
      </div>
      <video
        className="atl-player"
        controls
        preload={priority ? "metadata" : "none"}
        playsInline
        poster={item.poster}
        aria-label={item.dek ? `${item.title}: ${item.dek}` : item.title}
      >
        <source src={src} type="video/mp4" />
        {item.captions && <track kind="captions" src={item.captions} srcLang="en" label="English" />}
        Your browser does not support embedded video. <a href={src}>Download it instead.</a>
      </video>
      <div className="atl-lower-third">
        <div className="atl-episode-label">{label} <span>{sub}</span></div>
        <div className="atl-episode-title">
          <span>{item.dek ? item.title : "Across the Line"}</span>
          <h2>{item.dek ?? item.title}</h2>
        </div>
        <div className="atl-host-credit">At the desk<strong>Graham Keeper <span>&amp;</span> Kate Hedges</strong></div>
      </div>
    </section>
  );
}

/** A full page for one episode or preview: player, rundown, links, and what's next. */
export function WatchView({ item }: { item: ShowItem }) {
  const src = withVersion(item.video, item.version);
  const latest = latestEpisode();
  const preview = currentPreview();
  const played = item.kind === "preview" && previewPlayed(item);
  const pairedProgramAvailable = item.programSlug && programIndex.some((issue) => issue.slug === item.programSlug);
  const recapAvailable = item.programSlug && recapIndex.some((issue) => issue.slug === item.programSlug);
  const coveringEpisode = item.kind === "preview" ? publishedEpisodes().find((e) => e.weeks && e.weeks[0] <= item.week && e.weeks[1] >= item.week) : null;
  const next = [
    preview && preview !== item ? preview : null,
    latest && latest !== item ? latest : null,
  ].filter(Boolean) as ShowItem[];

  return (
    <div className="atl-page">
      <a className="atl-skip" href="#watch">Skip to video</a>
      <ShowTopbar />

      {played && (
        <p className="atl-stale-note">
          Week {item.kind === "preview" && item.week} has been played.{" "}
          {recapAvailable ? <a href={`/program/${item.programSlug}/recap`}>See how it turned out →</a>
            : coveringEpisode ? <a href={itemHref(coveringEpisode)}>See the review in Episode {coveringEpisode.number} →</a> : null}
        </p>
      )}

      <ShowPlayer item={item} priority />

      {item.summary && <p className="atl-summary">{item.summary}</p>}
      {item.correction && <p className="atl-correction">{item.correction}</p>}

      {item.segments && item.segments.length > 0 && (
        <section className="atl-rundown" aria-labelledby="rundown-title">
          <div className="atl-section-heading">
            <h2 id="rundown-title">On the rundown</h2>
          </div>
          <ol className="atl-segments" data-count={item.segments.length}>
            {item.segments.map((s, i) => (
              <li key={s.title}>
                <span className="atl-segment-number" aria-hidden="true">{String(i + 1).padStart(2, "0")}</span>
                <div className="atl-segment-type">{s.type}</div>
                <h3>{s.title}</h3>
                <p>{s.detail}</p>
              </li>
            ))}
          </ol>
        </section>
      )}

      <section className="atl-review-note" aria-label="More">
        <div>
          {pairedProgramAvailable && item.programSlug && (
            <p>
              Pairs with <a href={`/program/${item.programSlug}`}>The Program, Week {item.programSlug.split("-").pop()?.replace(/^0/, "")}</a>.
            </p>
          )}
          {item.captions ? <p>Captions are available from the player’s CC button.</p> : <p>Captions are built into the video.</p>}
        </div>
        <div className="atl-review-actions">
          {src && <a href={src} download className="atl-download">Download video <span aria-hidden="true">↓</span></a>}
          <span>Best viewed with sound on.</span>
        </div>
      </section>

      {next.length > 0 && (
        <section className="atl-up-next" aria-label="Also on Across the Line">
          {next.map((n) => (
            <a key={itemHref(n)} className="atl-up-next-link" href={itemHref(n)}>
              <span>{n.kind === "preview" ? "This week" : "Latest episode"}</span>
              {n.title}
              {n.dek && <small> · {n.dek}</small>}
            </a>
          ))}
          <a className="atl-up-next-link" href="/show"><span>Everything</span>All episodes and previews</a>
        </section>
      )}

      <ShowFooter />
    </div>
  );
}
