import { seasonIndex, slugify } from "@/lib/data";

export const metadata = { title: "Season Archive · {insert witty name here} Museum" };

export default function SeasonsPage() {
  return (
    <>
      <header className="room-header" style={{ backgroundImage: "url(/museum/rooms/chronicle-vault.webp)" }}>
        <div className="eyebrow">What happened in a specific year?</div>
        <h1>SEASON ARCHIVE</h1>
        <p>Every season is its own chapter. Start anywhere.</p>
      </header>

      <div className="grid cols-3" style={{ marginTop: "1.5rem" }}>
        {[...seasonIndex].reverse().map((s) => (
          <a className="card" key={s.season} href={`/seasons/${s.season}`}>
            <div className="eyebrow">{s.season}</div>
            <h3 className="gold">{s.title ?? "—"}</h3>
            <div className="muted">
              {s.champion ? `Champion: ${s.champion}` : "No champion recorded"}
            </div>
          </a>
        ))}
      </div>
    </>
  );
}
