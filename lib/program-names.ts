/** The Program's locker-room voice: cards and recap tiles use short names; the
 * history ledger and Milestone Watch keep full names. Longest keys replace
 * first so "Kevin Swanson" never half-matches through "Swanson". */
const SHORT_NAME: Record<string, string> = {
  "Kevin O'Boyle": "O'Boyle",
  "Kevin Swanson": "Swanson",
  "Brian Clark": "Clark",
  "Steve Swanson": "Steve",
  Thomas: "Tom",
  Douglas: "Doug",
};

export function shortName(name: string): string {
  return SHORT_NAME[name] ?? name;
}

export function shortenNames(text: string): string {
  let out = text;
  for (const full of Object.keys(SHORT_NAME).sort((a, b) => b.length - a.length)) {
    out = out.split(full).join(SHORT_NAME[full]);
  }
  return out;
}

