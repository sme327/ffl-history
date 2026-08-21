import "./globals.css";
import { site } from "@/lib/data";
import { NavLinks } from "@/app/components/nav-links";

export const metadata = {
  title: "{insert witty name here} Museum",
  description: `${site.subtitle} — a digital museum of a fantasy football league running since ${site.founded}.`,
  icons: {
    // The commissioned "Est. 2001" monogram roundel (A5b).
    icon: [
      // Browsers request /favicon.ico regardless of what is declared here; a
      // 404 there leaves them showing whatever icon they had cached.
      { url: "/favicon.ico", sizes: "any" },
      { url: "/museum/chrome/monogram-32.png", sizes: "32x32", type: "image/png" },
      { url: "/museum/chrome/monogram-512.png", sizes: "512x512", type: "image/png" },
    ],
    shortcut: "/museum/chrome/monogram-32.png",
    apple: "/museum/chrome/monogram-180.png",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <nav className="nav">
          <div className="nav-inner">
            {/* Full nameplate on desktop; below the burger breakpoint the
                monogram takes over so the nav plate doesn't stack directly
                on the hero plate (CSS-only swap — no client logic). */}
            <a className="nav-brand" href="/">
              <img
                src="/museum/chrome/nameplate-nav.svg"
                alt="{insert witty name here}"
                className="nav-plate"
              />
              <img
                src="/museum/chrome/monogram.svg"
                alt="{insert witty name here}"
                className="nav-mono"
              />
            </a>
            <input type="checkbox" id="nav-toggle" className="nav-toggle" hidden />
            <label className="nav-burger" htmlFor="nav-toggle" aria-label="Toggle navigation">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path stroke="currentColor" strokeWidth="2" strokeLinecap="round" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </label>
            <NavLinks />
          </div>
        </nav>
        <main className="wrap">{children}</main>
        {/* Real HTML, not a picture of text: the SVG plaque set its line in a
            font that can never load inside an <img>, so every visitor got
            Arial — and the text was unselectable besides. */}
        <footer className="site-footer">
          <div className="footer-plaque">
            Est. {site.founded} · A private collection · Report a misfiled exhibit
          </div>
        </footer>
      </body>
    </html>
  );
}
