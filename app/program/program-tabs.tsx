import { programIndex, recapIndex, programIssue } from "@/lib/data";

/** One week, two tabs: the midweek preview and the Tuesday recap. Real
 * sub-pages (/program/[slug] and /program/[slug]/recap), so each is its own
 * link for the group chat and the museum stays free of client JS. */
export function ProgramTabs({ slug, week, active }: { slug: string; week: number; active: "preview" | "recap" }) {
  const hasPreview = programIndex.some((i) => i.slug === slug);
  const hasRecap = recapIndex.some((i) => i.slug === slug);
  return (
    <nav className="program-tabs" aria-label={`Week ${week}`}>
      {hasPreview ? (
        <a href={`/program/${slug}`} aria-current={active === "preview" ? "page" : undefined}>
          Week {week} Preview
        </a>
      ) : (
        <span className="pending">Preview</span>
      )}
      {hasRecap ? (
        <a href={`/program/${slug}/recap`} aria-current={active === "recap" ? "page" : undefined}>
          Week {week} Recap
        </a>
      ) : (
        <span className="pending">Recap · after Monday night</span>
      )}
    </nav>
  );
}

/** Which issue /program opens on: the finished week's Recap from Tuesday
 * until the next week's preview is published with its copy (Wednesday or
 * Thursday); before any recap exists, the latest preview. */
export function programLanding(): { kind: "preview" | "recap"; slug: string } | null {
  const preview = programIndex[programIndex.length - 1];
  const recap = recapIndex[recapIndex.length - 1];
  if (!recap) return preview ? { kind: "preview", slug: preview.slug } : null;
  if (preview && preview.week > recap.week && programIssue(preview.slug)?.copy) {
    return { kind: "preview", slug: preview.slug };
  }
  return { kind: "recap", slug: recap.slug };
}

/** Every issue so far, newest first; each pill opens that week's newest tab. */
export function ProgramIssuePills({ slug }: { slug: string }) {
  const bySlug = new Map<string, { season: number; week: number; recap: boolean }>();
  for (const i of programIndex) bySlug.set(i.slug, { season: i.season, week: i.week, recap: false });
  for (const i of recapIndex) bySlug.set(i.slug, { season: i.season, week: i.week, recap: true });
  const issues = [...bySlug.entries()].sort((a, b) => b[1].season - a[1].season || b[1].week - a[1].week);
  if (issues.length < 2) return null;
  return (
    <>
      <h2>Back Issues</h2>
      <div className="chron-years">
        {issues.map(([s, i]) => (
          <a
            className={`year-pill${s === slug ? " gold-pill" : ""}`}
            key={s}
            href={i.recap ? `/program/${s}/recap` : `/program/${s}`}
          >
            {i.season} wk {i.week}
          </a>
        ))}
      </div>
    </>
  );
}
