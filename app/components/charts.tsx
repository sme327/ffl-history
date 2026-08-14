/**
 * Server-rendered SVG charts.
 *
 * The Streamlit build used Plotly, which costs roughly 3MB of client JavaScript
 * and a hydration pass for what are, on this site, static pictures of settled
 * history. Nothing here needs to respond to a click — so these render on the
 * server as plain SVG: no dependency, no client bundle, and full control over
 * type and colour so the charts look like the rest of the museum.
 *
 * The trade is hover tooltips. Labels are drawn on instead.
 */

type Band = { start: number; end: number; label: string; color: string };
type SeasonPoint = { season: number; avg: number; high: number; low: number };

const AXIS = "var(--border)";
const INK = "var(--muted)";

export function ScoringEvolution({
  points,
  bands,
  championPoints,
}: {
  points: SeasonPoint[];
  bands: Band[];
  championPoints: { season: number; points_for: number }[];
}) {
  const width = 900;
  const height = 320;
  const pad = { top: 24, right: 16, bottom: 32, left: 52 };

  const seasons = points.map((p) => p.season);
  const minSeason = Math.min(...seasons);
  const maxSeason = Math.max(...seasons);
  const maxValue = Math.max(...points.map((p) => p.high));
  const minValue = Math.min(...points.map((p) => p.low));

  const x = (season: number) =>
    pad.left +
    ((season - minSeason) / (maxSeason - minSeason)) *
      (width - pad.left - pad.right);
  const y = (value: number) =>
    height -
    pad.bottom -
    ((value - minValue) / (maxValue - minValue)) *
      (height - pad.top - pad.bottom);

  const rangeArea = [
    ...points.map((p) => `${x(p.season)},${y(p.high)}`),
    ...[...points].reverse().map((p) => `${x(p.season)},${y(p.low)}`),
  ].join(" ");
  const averageLine = points.map((p) => `${x(p.season)},${y(p.avg)}`).join(" ");

  const ticks = [minValue, (minValue + maxValue) / 2, maxValue];

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label="Average, high and low weekly scoring by season, with league eras shaded"
      style={{ width: "100%", height: "auto", display: "block" }}
    >
      {bands.map((band) => (
        <g key={band.label}>
          <rect
            x={x(band.start) - 4}
            y={pad.top}
            width={Math.max(x(Math.min(band.end, maxSeason)) - x(band.start) + 8, 0)}
            height={height - pad.top - pad.bottom}
            fill={band.color}
            opacity={0.07}
          />
          <text
            x={x(band.start) + 2}
            y={pad.top - 8}
            fill={band.color}
            fontSize="11"
            opacity={0.85}
          >
            {band.label}
          </text>
        </g>
      ))}

      {ticks.map((value) => (
        <g key={value}>
          <line
            x1={pad.left}
            x2={width - pad.right}
            y1={y(value)}
            y2={y(value)}
            stroke={AXIS}
          />
          <text x={8} y={y(value) + 4} fill={INK} fontSize="11">
            {Math.round(value)}
          </text>
        </g>
      ))}

      <polygon points={rangeArea} fill="var(--gold)" opacity={0.1} />
      <polyline
        points={averageLine}
        fill="none"
        stroke="var(--gold)"
        strokeWidth={2.5}
      />
      {points.map((p) => (
        <circle key={p.season} cx={x(p.season)} cy={y(p.avg)} r={3} fill="var(--gold)" />
      ))}
      {championPoints.map((c) => (
        <text
          key={c.season}
          x={x(c.season)}
          y={y(c.points_for) + 4}
          fontSize="11"
          textAnchor="middle"
        >
          ★
        </text>
      ))}

      {points
        .filter((_, i) => i % 4 === 0 || i === points.length - 1)
        .map((p) => (
          <text
            key={p.season}
            x={x(p.season)}
            y={height - 10}
            fill={INK}
            fontSize="11"
            textAnchor="middle"
          >
            {p.season}
          </text>
        ))}
    </svg>
  );
}

export function TitleBars({
  entries,
}: {
  entries: { manager: string; titles: number }[];
}) {
  const max = Math.max(...entries.map((e) => e.titles), 1);

  return (
    <div className="grid" style={{ gap: "0.35rem" }}>
      {entries.map((entry) => (
        <div
          key={entry.manager}
          style={{ display: "grid", gridTemplateColumns: "9rem 1fr 2rem", alignItems: "center", gap: "0.5rem" }}
        >
          <span style={{ fontSize: "var(--step--1)" }}>{entry.manager}</span>
          <span
            style={{
              background: "var(--gold)",
              height: 14,
              borderRadius: 3,
              width: `${(entry.titles / max) * 100}%`,
              minWidth: 4,
            }}
          />
          <span className="gold num" style={{ fontSize: "var(--step--1)", textAlign: "right" }}>
            {entry.titles}
          </span>
        </div>
      ))}
    </div>
  );
}

export function PositionShareBar({
  counts,
  colors,
}: {
  counts: Record<string, number>;
  colors: Record<string, string>;
}) {
  const order = ["RB", "WR", "QB", "TE", "DEF", "K"];
  const total = order.reduce((sum, pos) => sum + (counts[pos] ?? 0), 0);
  if (!total) return null;

  return (
    <>
      <div style={{ display: "flex", height: 18, borderRadius: 4, overflow: "hidden" }}>
        {order.map((pos) => {
          const share = (counts[pos] ?? 0) / total;
          if (!share) return null;
          return (
            <div
              key={pos}
              title={`${pos} ${Math.round(share * 100)}%`}
              style={{
                width: `${share * 100}%`,
                background: colors[pos] ?? "var(--faint)",
                color: "#000",
                fontSize: 10,
                fontWeight: 700,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {share >= 0.1 ? pos : ""}
            </div>
          );
        })}
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.6rem", marginTop: "0.35rem" }}>
        {order
          .filter((pos) => counts[pos])
          .map((pos) => (
            <span key={pos} style={{ fontSize: "var(--step--1)", color: colors[pos] }}>
              {pos}: {Math.round(((counts[pos] ?? 0) / total) * 100)}% ({counts[pos]})
            </span>
          ))}
      </div>
    </>
  );
}
