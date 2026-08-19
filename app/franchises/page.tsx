import { franchiseIndex, slugify, franchiseBadgePath } from "@/lib/data";

export const metadata = { title: "Franchises · {insert witty name here} Museum" };

export default function FranchisesPage() {
  return (
    <>
      <div className="eyebrow">What happened to this seat over time?</div>
      <h1>FRANCHISES</h1>
      <p>
        Franchises are not managers. Franchises are institutions — a seat that
        persists as one manager replaces another.
      </p>

      <div className="grid cols-3" style={{ marginTop: "1.5rem" }}>
        {franchiseIndex.map((f) => (
          <a className="card" key={f.id} href={`/franchises/${f.id}`}>
            <img src={franchiseBadgePath(f.id)} alt="" style={{ width: "3rem", height: "3rem", marginBottom: "0.4rem" }} />
            <div className="eyebrow">{f.id} · est. {f.established}</div>
            <h3>{f.currentManager}</h3>
            <div className="gold">
              {f.championships > 0 ? "🏆".repeat(f.championships) : "No titles yet"}
            </div>
          </a>
        ))}
      </div>
    </>
  );
}
