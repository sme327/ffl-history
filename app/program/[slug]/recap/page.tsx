import { programRecap, recapIndex } from "@/lib/data";
import { RecapView } from "../../recap-view";

export function generateStaticParams() {
  return recapIndex.map((i) => ({ slug: i.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const recap = programRecap(slug);
  return {
    title: recap
      ? `The Recap · ${recap.season} Week ${recap.week} · {insert witty name here} Museum`
      : "The Recap · {insert witty name here} Museum",
  };
}

export default async function RecapPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const recap = programRecap(slug);
  if (!recap) return <h1>Recap not found</h1>;
  return <RecapView recap={recap} />;
}
