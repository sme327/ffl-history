import { managerIndex } from "@/lib/data";
import { Trophies } from "@/app/components/icons";

export const metadata = { title: "Managers · {insert witty name here} Museum" };

export default function ManagersPage() {
  const active = managerIndex.filter((m) => m.active);
  const former = managerIndex.filter((m) => !m.active);

  return (
    <>
      <div className="room-photo" style={{ backgroundImage: "url(/museum/rooms/portrait-gallery.webp)" }} />
      <div className="room-scrim" />
      <div className="room-title">
        <div className="eyebrow">Who are these people?</div>
        <h1>MANAGERS</h1>
        <p>Career records for every competitor in league history.</p>
      </div>

      {[
        ["Active", active] as const,
        ["Former Members", former] as const,
      ].map(([label, group]) => (
        <section key={label}>
          <h2>{label}</h2>
          <div className="grid cols-3">
            {group.map((m) => (
              <a className="card" key={m.slug} href={`/managers/${m.slug}`}>
                <h3>{m.displayName}</h3>
                <div className="muted">
                  {m.firstSeason}–{m.active ? "Present" : m.lastSeason}
                </div>
                <div className="gold">
                  {m.championships > 0
                    ? <Trophies count={m.championships} />
                    : "No titles yet"}
                </div>
              </a>
            ))}
          </div>
        </section>
      ))}
    </>
  );
}
