import { programIndex, programIssue } from "@/lib/data";
import { IssueView } from "./issue-view";

export const metadata = { title: "The Program · {insert witty name here} Museum" };

// /program is always the latest issue; back issues live at /program/[slug].
export default function ProgramPage() {
  const latest = programIndex[programIndex.length - 1];
  const issue = latest ? programIssue(latest.slug) : null;
  if (!issue) {
    return (
      <>
        <div className="room-title">
          <h1>THE PROGRAM</h1>
          <p>No issues yet — the season hasn&rsquo;t started.</p>
        </div>
      </>
    );
  }
  return <IssueView issue={issue} />;
}
