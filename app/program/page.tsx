import { programIssue, programRecap } from "@/lib/data";
import { IssueView } from "./issue-view";
import { RecapView } from "./recap-view";
import { programLanding } from "./program-tabs";

export const metadata = { title: "The Program · {insert witty name here} Museum" };

// /program opens on the newest issue — the Tuesday recap until the next
// preview is published, then that preview (programLanding). Every issue keeps
// its own URLs: /program/[slug] (preview) and /program/[slug]/recap.
export default function ProgramPage() {
  const landing = programLanding();
  const recap = landing?.kind === "recap" ? programRecap(landing.slug) : null;
  const issue = landing?.kind === "preview" ? programIssue(landing.slug) : null;
  if (recap) return <RecapView recap={recap} />;
  if (issue) return <IssueView issue={issue} />;
  return (
    <div className="room-title">
      <h1>THE PROGRAM</h1>
      <p>No issues yet — the season hasn&rsquo;t started.</p>
    </div>
  );
}
