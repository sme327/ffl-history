export const metadata = {
  title: "Across the Line — Rivalry Round One",
  description:
    "Graham Keeper and Kate Hedges recap three weeks of fantasy football. Real scores. Questionable decisions. A SME327 production.",
  openGraph: {
    title: "Across the Line — Rivalry Round One",
    description: "Real scores. Questionable decisions. Watch the animated fantasy football pilot with Graham Keeper and Kate Hedges.",
    url: "https://iwnh.sme327.com/show/pilot",
    type: "website",
    images: [{ url: "https://iwnh.sme327.com/show/studio-poster-v001.webp", width: 1920, height: 1080, alt: "Graham Keeper and Kate Hedges at the Across the Line studio desk" }],
  },
};

const episodeFile = "/show/pilot-review.mp4?v=20261005-v033-720p";

export default function PilotReviewPage() {
  return (
    <div className="atl-page">
      <a className="atl-skip" href="#watch">Skip to episode</a>
      <nav className="atl-topbar" aria-label="Show navigation">
        <a className="atl-home" href="/">← Back to the league museum</a>
        <span className="atl-production">A SME327 production</span>
      </nav>

      <header className="atl-masthead">
        <div className="atl-masthead-copy">
          <div className="atl-kicker">Fantasy football · Unnecessarily serious coverage</div>
          <h1>Across <span>the Line</span></h1>
          <p className="atl-tagline">Real scores. Questionable decisions.</p>
        </div>
        <div className="atl-episode-stamp" aria-label="Pilot episode, weeks one to three">
          <span>Pilot episode</span>
          <strong>01</strong>
          <span>Weeks 1–3</span>
        </div>
      </header>

      <section className="atl-broadcast" id="watch" tabIndex={-1} aria-label="Watch Across the Line pilot">
        <div className="atl-player-bar">
          <span><i aria-hidden="true" /> In the studio</span>
          <span>Animated review · V033 · 7:45 · 720p</span>
        </div>
        <video
          className="atl-player"
          controls
          preload="metadata"
          playsInline
          poster="/show/studio-poster-v001.webp"
          aria-label="Rivalry Round One: The Standings Are Lying — pilot review"
        >
          <source src={episodeFile} type="video/mp4" />
          Your browser does not support embedded video. <a href={episodeFile}>Download the episode instead.</a>
        </video>
        <div className="atl-lower-third">
          <div className="atl-episode-label">Episode 01 <span>Weeks 1–3</span></div>
          <div className="atl-episode-title">
            <span>Rivalry Round One</span>
            <h2>The Standings Are Lying</h2>
          </div>
          <div className="atl-host-credit">At the desk<strong>Graham Keeper <span>&amp;</span> Kate Hedges</strong></div>
        </div>
      </section>

      <footer className="atl-footer">
        <span>Across the Line <small> / A SME327 production</small></span>
        <a href="/program">Meet the league →</a>
      </footer>
    </div>
  );
}
