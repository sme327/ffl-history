import "./globals.css";
import { site } from "@/lib/data";

export const metadata = {
  title: "The Long Game",
  description: `${site.subtitle} — a digital museum of a fantasy football league running since ${site.founded}.`,
  icons: {
    // Real PNGs, not an SVG emoji: browsers rasterise SVG favicons without
    // reliably resolving a colour-emoji font, so the tab falls back to a default.
    icon: [
      { url: "/favicon-32.png", sizes: "32x32", type: "image/png" },
      { url: "/icon.png", sizes: "512x512", type: "image/png" },
    ],
    shortcut: "/favicon-32.png",
    apple: "/apple-touch-icon.png",
  },
};

const NAV = [
  { href: "/", label: "Home" },
  { href: "/champions", label: "Champions" },
  { href: "/timeline", label: "Timeline" },
  { href: "/history", label: "League History" },
  { href: "/seasons", label: "Seasons" },
  { href: "/managers", label: "Managers" },
  { href: "/franchises", label: "Franchises" },
  { href: "/draft", label: "Draft" },
  { href: "/rivalries", label: "Rivalries" },
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
