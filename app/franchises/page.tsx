import { franchiseIndex, slugify, franchiseBadgePath } from "@/lib/data";
import { Trophies } from "@/app/components/icons";

export const metadata = { title: "Franchises · {insert witty name here} Museum" };

export default function FranchisesPage() {
  return (
    <>
      <div className="room-photo" style={{ backgroundImage: "url(/museum/rooms/dynasty-wing.webp)" }} />
      <div className="room-scrim" />
      <div className="room-title">
        <div className="eyebrow">What happened to this seat over time?</div>
        <h1>FRANCHISES</h1>
        <p>
          Franchises are not managers. Franchises are institutions — a seat that
          persists as one manager replaces another.
        </p>
      </div>

      <div className="grid cols-3" style={{ marginTop: "1.5rem" }}>
        {franchiseIndex.map((f) => (
          <a className="card" key={f.id} href={`/franchises/${f.id}`}>
            <img src={franchiseBadgePath(f.id)} alt="" style={{ width: "3rem", height: "3rem", marginBottom: "0.4rem" }} />
            <div className="eyebrow">{f.id} · est. {f.established}</div>
            <h3>{f.currentManager}</h3>
            <div className="gold">
              {f.championships > 0 ? <Trophies count={f.championships} /> : "No titles yet"}
            </div>
          </a>
        ))}
      </div>
    </>
  );
}
