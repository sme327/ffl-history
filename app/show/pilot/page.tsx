export const metadata = {
  title: "Across the Line — Pilot Review",
  description: "A work-in-progress pilot from the {insert witty name here} Museum.",
};

export default function PilotReviewPage() {
  return (
    <>
      <div
        className="room-photo"
        style={{ backgroundImage: "url(/museum/rooms/entrance-hall.webp)" }}
      />
      <div className="room-scrim" />

      <header className="show-review-header">
        <div className="eyebrow">A SME327 Production · Pilot Review</div>
        <h1>Across the Line</h1>
        <div className="show-review-title">Rivalry Round One: The Standings Are Lying</div>
        <p>
          A work-in-progress animated pilot from the {"{insert witty name here}"} Museum.
        </p>
      </header>

      <section className="show-player-case" aria-label="Across the Line pilot video">
        <div className="show-player-label">
          <span>Pilot Review</span>
          <span>6:45 · October 2, 2026</span>
        </div>
        <video className="show-player" controls preload="metadata" playsInline>
          <source src="/show/pilot-review.mp4?v=20261002-v004" type="video/mp4" />
          Your browser does not support embedded video. You can use the download link below.
        </video>
      </section>

      <div className="show-review-notes">
        <div>
          <div className="eyebrow">Review Cut</div>
          <h2>What you’re watching</h2>
          <p>
            Graham Keeper and Kate Hedges recap the first three weeks of divisional
            matchups, with Kittle Watch, the Evidence Locker, and a look ahead to Week 4.
            This updated review cut uses the approved host designs and current voices;
            character animation and further visual polish are still in development.
          </p>
        </div>
        <div className="show-review-actions">
          <a className="teaser-cta" href="/show/pilot-review.mp4?v=20261002-v004" download>
            Download review cut
          </a>
          <div className="muted">Best viewed with sound on.</div>
        </div>
      </div>
    </>
  );
}
