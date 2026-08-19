import "./globals.css";
import { site } from "@/lib/data";
import { NavLinks } from "@/app/components/nav-links";

export const metadata = {
  title: "{insert witty name here} Museum",
  description: `${site.subtitle} — a digital museum of a fantasy football league running since ${site.founded}.`,
  icons: {
    // Real PNGs, not an SVG emoji: browsers rasterise SVG favicons without
    // reliably resolving a colour-emoji font, so the tab falls back to a default.
    icon: [
      // Browsers request /favicon.ico regardless of what is declared here; a
      // 404 there leaves them showing whatever icon they had cached.
      { url: "/favicon.ico", sizes: "any" },
      { url: "/favicon-32.png", sizes: "32x32", type: "image/png" },
      { url: "/icon.png", sizes: "512x512", type: "image/png" },
    ],
    shortcut: "/favicon-32.png",
    apple: "/apple-touch-icon.png",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <nav className="nav">
          <div className="nav-inner">
            <a className="nav-brand" href="/">{"{insert witty name here}"}</a>
            <input type="checkbox" id="nav-toggle" className="nav-toggle" hidden />
            <label className="nav-burger" htmlFor="nav-toggle" aria-label="Toggle navigation">☰</label>
            <NavLinks />
          </div>
        </nav>
        <main className="wrap">{children}</main>
        <footer className="site-footer">
          <img
            src="/museum/chrome/footer-plaque.svg"
            alt={`Est. ${site.founded} · A private collection · Report a misfiled exhibit`}
            className="footer-plaque"
          />
        </footer>
      </body>
    </html>
  );
}
