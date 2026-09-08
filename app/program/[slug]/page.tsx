import { programIndex, programIssue } from "@/lib/data";
import { IssueView } from "../issue-view";

export function generateStaticParams() {
  return programIndex.map((i) => ({ slug: i.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const issue = programIssue(slug);
  return {
    title: issue
      ? `The Program · ${issue.season} Week ${issue.week} · {insert witty name here} Museum`
      : "The Program · {insert witty name here} Museum",
  };
}

export default async function ProgramIssuePage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const issue = programIssue(slug);
  if (!issue) return <h1>Issue not found</h1>;
  return <IssueView issue={issue} />;
}
