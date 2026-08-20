import { managerIndex, managerIconPath } from "@/lib/data";
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
                {/* This page is the portrait gallery — it should show the
                    portraits, not just nameplates. */}
                <div style={{ fontSize: "2.5rem", lineHeight: 1, marginBottom: "0.4rem" }}>
                  <img src={managerIconPath(m.name)} alt="" className="mgr-icon" />
                </div>
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
