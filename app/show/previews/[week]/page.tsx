import { PREVIEWS, findPreview } from "../../catalog";
import { WatchView } from "../../watch-view";

// URLs read /show/previews/week-5.
const weekOf = (slug: string) => Number(slug.replace(/^week-/, ""));

export function generateStaticParams() {
  return PREVIEWS.filter((p) => p.status === "published").map((p) => ({ week: `week-${p.week}` }));
}

export async function generateMetadata({ params }: { params: Promise<{ week: string }> }) {
  const { week } = await params;
  const p = findPreview(weekOf(week));
  if (!p) return { title: "Across the Line · {insert witty name here} Museum" };
  const title = `Across the Line · ${p.title}`;
  const url = `https://iwnh.sme327.com/show/previews/week-${p.week}`;
  return {
    title,
    description: p.dek,
    alternates: { canonical: url },
    openGraph: {
      title,
      description: p.dek,
      url,
      type: "video.other",
      images: p.poster ? [{ url: `https://iwnh.sme327.com${p.poster}`, width: 1920, height: 1080 }] : [],
    },
  };
}

export default async function PreviewPage({ params }: { params: Promise<{ week: string }> }) {
  const { week } = await params;
  const p = findPreview(weekOf(week));
  if (!p) return <h1>Preview not found</h1>;
  return <WatchView item={p} />;
}
