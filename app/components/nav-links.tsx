"use client";

import { usePathname } from "next/navigation";

// Labels stay one word where possible — eleven items have to share one line
// on a laptop before the burger takes over.
const NAV = [
  { href: "/", label: "Home" },
  { href: "/program", label: "Program" },
  { href: "/champions", label: "Champions" },
  { href: "/timeline", label: "Timeline" },
  { href: "/history", label: "History" },
  { href: "/seasons", label: "Seasons" },
  { href: "/managers", label: "Managers" },
  { href: "/franchises", label: "Franchises" },
  { href: "/draft", label: "Draft" },
  { href: "/rivalries", label: "Rivalries" },
  { href: "/keepers", label: "Keepers" },
];

// The only client-side JS in the nav: everything else on the site is
// server-rendered, but knowing "which link is the current page" requires
// the pathname, which only exists on the client in the app router.
export function NavLinks() {
  const pathname = usePathname();

  return (
    <div className="nav-links">
      {NAV.map((item) => {
        const active = item.href === "/" ? pathname === "/" : pathname?.startsWith(item.href);
        return (
          <a key={item.href} href={item.href} className={active ? "active" : undefined}>
            {active && (
              <img src="/museum/chrome/nav-active-tick.svg" alt="" className="nav-active-tick" />
            )}
            {item.label}
          </a>
        );
      })}
    </div>
  );
}
