import { EPISODES, findEpisode } from "../../catalog";
import { WatchView } from "../../watch-view";

export function generateStaticParams() {
  return EPISODES.filter((e) => e.status === "published").map((e) => ({ number: String(e.number) }));
}

export async function generateMetadata({ params }: { params: Promise<{ number: string }> }) {
  const { number } = await params;
  const ep = findEpisode(Number(number));
  if (!ep) return { title: "Across the Line · {insert witty name here} Museum" };
  const title = `Across the Line · Episode ${ep.number}: ${ep.title}`;
  const url = `https://iwnh.sme327.com/show/episodes/${ep.number}`;
  return {
    title,
    description: ep.summary,
    alternates: { canonical: url },
    openGraph: {
      title,
      description: ep.summary,
      url,
      type: "video.episode",
      images: ep.poster ? [{ url: `https://iwnh.sme327.com${ep.poster}`, width: 1920, height: 1080 }] : [],
    },
  };
}

export default async function EpisodePage({ params }: { params: Promise<{ number: string }> }) {
  const { number } = await params;
  const ep = findEpisode(Number(number));
  if (!ep) return <h1>Episode not found</h1>;
  return <WatchView item={ep} />;
}
