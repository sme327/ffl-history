import "./globals.css";
import { site } from "@/lib/data";

export const metadata = {
  title: "The Long Game",
  description: `${site.subtitle} — a digital museum of a fantasy football league running since ${site.founded}.`,
};

const NAV = [
  { href: "/", label: "Home" },
  { href: "/champions", label: "Champions" },
  { href: "/timeline", label: "Timeline" },
  { href: "/seasons", label: "Seasons" },
  { href: "/managers", label: "Managers" },
  { href: "/keepers", label: "Keeper Hall" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <nav className="nav">
          <div className="nav-inner">
            <a className="nav-brand" href="/">THE LONG GAME</a>
            {NAV.map((item) => (
              <a key={item.href} href={item.href}>{item.label}</a>
            ))}
          </div>
        </nav>
        <main className="wrap">{children}</main>
      </body>
    </html>
  );
}
