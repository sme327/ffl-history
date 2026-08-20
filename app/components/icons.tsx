/* Inline SVG glyphs for the handful of places that still rendered OS emoji
 * characters (🏆 and friends) after the asset purge. Inline rather than an
 * <img> so they take currentColor — a trophy inherits the gold of whatever
 * line it sits in, with no extra requests.
 */

export function Trophy() {
  return (
    <svg viewBox="0 0 24 24" className="trophy-glyph" aria-hidden="true">
      <path
        fill="currentColor"
        d="M7 3h10v2h4v2c0 2.8-1.9 4.6-4.3 5-.7 1.7-2 2.8-3.7 3v2.5h3V21H8v-3.5h3V15c-1.7-.2-3-1.3-3.7-3C4.9 11.6 3 9.8 3 7V5h4V3zm-2 4c0 1.5.8 2.5 2 2.9V7H5zm14 0h-2v2.9c1.2-.4 2-1.4 2-2.9z"
      />
    </svg>
  );
}

/** A row of trophy glyphs — the replacement for `"🏆".repeat(n)`. */
export function Trophies({ count }: { count: number }) {
  if (count <= 0) return null;
  return (
    <>
      {Array.from({ length: count }, (_, i) => (
        <Trophy key={i} />
      ))}
    </>
  );
}
