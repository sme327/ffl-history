import { findEpisode } from "../catalog";
import { WatchView } from "../watch-view";

// The pilot's original link, already shared with the league. It keeps working
// and shows Episode 1; the canonical address is /show/episodes/1.
export const metadata = {
  title: "Across the Line · Episode 1: Rivalry Round One",
  alternates: { canonical: "https://iwnh.sme327.com/show/episodes/1" },
  openGraph: {
    title: "Across the Line · Episode 1: Rivalry Round One",
    description: "Real scores. Questionable decisions. Graham Keeper and Kate Hedges recap Weeks 1–3.",
    url: "https://iwnh.sme327.com/show/episodes/1",
    type: "video.episode",
    images: [{ url: "https://iwnh.sme327.com/show/studio-poster-v001.webp", width: 1920, height: 1080 }],
  },
};

export default function PilotPage() {
  const ep = findEpisode(1);
  if (!ep) return <h1>Episode not found</h1>;
  return <WatchView item={ep} />;
}
