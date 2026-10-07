import {
  EPISODES,
  ShowEpisode,
  ShowPreview,
  currentPreview,
  episodeHref,
  latestEpisode,
  pastPreviews,
  previewHref,
  releasedLabel,
  weeksLabel,
  withVersion,
} from "./catalog";
import { ShowFooter, ShowTopbar } from "./watch-view";

export const metadata = {
  title: "Across the Line · {insert witty name here} Museum",
  description:
    "The animated fantasy football show about the {insert witty name here} league. Weekly previews and four full episodes a season, with Graham Keeper and Kate Hedges.",
  openGraph: {
    title: "Across the Line",
    description: "Real scores. Questionable decisions. Weekly previews and full episodes with Graham Keeper and Kate Hedges.",
    url: "https://iwnh.sme327.com/show",
    type: "website",
    images: [{ url: "https://iwnh.sme327.com/show/studio-poster-v001.webp", width: 1920, height: 1080, alt: "Graham Keeper and Kate Hedges at the Across the Line studio desk" }],
  },
};

/** A large clickable card for one of the two "now" slots. */
function NowCard({
  slot,
  href,
  poster,
  title,
  dek,
  meta,
  badge,
}: {
  slot: string;
  href: string;
  poster?: string;
  title: string;
  dek?: string;
  meta: string;
  badge?: string;
}) {
  return (
    <a className="atl-now-card" href={href}>
      <div className="atl-now-slot">{slot}</div>
      <div className="atl-now-thumb">
        {poster && <img src={poster} alt="" loading="lazy" />}
        <span className="atl-play" aria-hidden="true">▶</span>
        {badge && <span className="atl-badge">{badge}</span>}
      </div>
      <div className="atl-now-body">
        <h2>{title}</h2>
        {dek && <p>{dek}</p>}
        <span className="atl-now-meta">{meta}</span>
      </div>
    </a>
  );
}

function PreviewSlot({ preview }: { preview: ShowPreview | null }) {
  if (!preview) {
    return (
      <div className="atl-now-card atl-now-empty">
        <div className="atl-now-slot">This week</div>
        <div className="atl-now-thumb">
          <img src="/show/studio-poster-v001.webp" alt="" loading="lazy" />
          <span className="atl-soon">Next preview coming soon</span>
        </div>
        <div className="atl-now-body">
          <h2>A short look at every matchup</h2>
          <p>Before kickoff, every week between episodes.</p>
          <a className="atl-now-meta" href="/program">Meanwhile: The Program →</a>
        </div>
      </div>
    );
  }
  return (
    <NowCard
      slot="This week"
      href={previewHref(preview)}
      poster={preview.poster}
      title={preview.title}
      dek={preview.dek}
      meta={[preview.runtime, preview.released && `Released ${releasedLabel(preview.released)}`].filter(Boolean).join(" · ")}
      badge="New"
    />
  );
}

function EpisodeSlot({ episode }: { episode: ShowEpisode | null }) {
  if (!episode) return null;
  return (
    <NowCard
      slot="Latest episode"
      href={episodeHref(episode)}
      poster={episode.poster}
      title={`Episode ${episode.number}: ${episode.title}`}
      dek={episode.dek}
      meta={[weeksLabel(episode), episode.runtime, episode.released && `Released ${releasedLabel(episode.released)}`].filter(Boolean).join(" · ")}
    />
  );
}

export default function ShowHubPage() {
  const latest = latestEpisode();
  const preview = currentPreview();
  const past = pastPreviews();

  return (
    <div className="atl-page">
      <ShowTopbar />

      <header className="atl-masthead">
        <div className="atl-masthead-copy">
          <div className="atl-kicker">Fantasy football · Unnecessarily serious coverage</div>
          <h1>Across <span>the Line</span></h1>
          <p className="atl-tagline">Real scores. Questionable decisions. With Graham Keeper &amp; Kate Hedges.</p>
        </div>
      </header>

      <section className="atl-now" aria-label="Watch now">
        <PreviewSlot preview={preview} />
        <EpisodeSlot episode={latest} />
      </section>

      <section className="atl-season" aria-labelledby="season-title">
        <div className="atl-section-heading">
          <h2 id="season-title">The season</h2>
          <span>Four full episodes, with weekly previews in between.</span>
        </div>
        <ol className="atl-season-track">
          {EPISODES.map((e) => {
            const live = e.status === "published";
            const inner = (
              <>
                <span className="atl-season-dot" aria-hidden="true" />
                <strong>Episode {e.number}</strong>
                <span>{live ? e.title : "Coming"}</span>
                <small>{e.weeks ? weeksLabel(e) : "Weeks TBA"}</small>
              </>
            );
            return (
              <li key={e.number} className={live ? "is-live" : "is-planned"}>
                {live ? <a href={episodeHref(e)}>{inner}</a> : <div>{inner}</div>}
              </li>
            );
          })}
        </ol>
      </section>

      {past.length > 0 && (
        <section className="atl-archive" aria-labelledby="previews-title">
          <details>
            <summary>
              <h2 id="previews-title">Past weekly previews</h2>
              <span>{past.length} {past.length === 1 ? "preview" : "previews"}</span>
            </summary>
            <ul>
              {past.map((p) => (
                <li key={p.week}>
                  <a href={previewHref(p)}>
                    <strong>Week {p.week}</strong>
                    <span>{p.dek ?? p.title}</span>
                    <small>{p.runtime}</small>
                  </a>
                </li>
              ))}
            </ul>
          </details>
        </section>
      )}

      <section className="atl-review-note" aria-label="About the show">
        <div>
          <div className="atl-kicker">About the show</div>
          <h2>Every number, checked.</h2>
          <p>
            Across the Line covers the {"{insert witty name here}"} league with real scores from
            The Program, a 25-season archive, and two hosts who take it far too seriously.
            Every number on screen is checked against the museum.
          </p>
        </div>
        <div className="atl-review-actions">
          {latest?.video && (
            <a href={withVersion(latest.video, latest.version)} download className="atl-download">
              Download the latest episode <span aria-hidden="true">↓</span>
            </a>
          )}
          <span>Best viewed with sound on.</span>
        </div>
      </section>

      <ShowFooter />
    </div>
  );
}
