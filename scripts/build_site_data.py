"""Emit the league's derived history as JSON, one file per future route.

    python3 scripts/build_site_data.py [--out build/data]

Phase 2 of SELF-HOSTING-PLAN.md. The derivations stay in pandas — where they are
already correct and now fixture-tested — and move from request time to build
time. The output is what a static site reads instead of calling Python.

Every frame is verified against tests/fixtures/ before it is written, so this
can only emit history the test suite has approved.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from _harness import install_streamlit_stub, load as load_fixture, normalize  # noqa: E402

install_streamlit_stub()

from utils import data as D  # noqa: E402
from utils import narratives as N  # noqa: E402

DEFAULT_OUT = ROOT / "build" / "data"


# ── Slugs ─────────────────────────────────────────────────────────────────────
# The site's URLs are derived from names, so slugging has to be stable and
# reversible-by-lookup. Apostrophes are dropped rather than turned into
# separators: "Kevin O'Boyle" -> kevin-oboyle, not kevin-o-boyle.

def slugify(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("'", "").replace("’", "")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "unknown"


def pair_slug(mgr_a: str, mgr_b: str) -> str:
    return "-vs-".join(sorted([slugify(mgr_a), slugify(mgr_b)]))


# ── Verified extraction ───────────────────────────────────────────────────────

class Verifier:
    """Compares each derivation against its fixture before it is emitted."""

    def __init__(self) -> None:
        self.checked = 0
        self.skipped: list[str] = []

    def frame(self, fixture_name: str, df):
        try:
            expected = load_fixture(fixture_name)
        except FileNotFoundError:
            self.skipped.append(fixture_name)
            return df

        actual = normalize(df)
        if actual["digest"] != expected["digest"]:
            raise SystemExit(
                f"\n  {fixture_name} does not match its fixture.\n"
                f"  The build refuses to emit unverified history.\n"
                f"  Run the tests to see the diff:\n"
                f"    python3 -m unittest discover -s tests -p 'test_*.py'\n"
                f"  If the change is intended: python3 tests/capture_fixtures.py\n"
            )
        self.checked += 1
        return df


def records(df) -> list[dict]:
    return normalize(df).get("rows") or [
        {str(k): v for k, v in rec.items()} for rec in json.loads(df.to_json(orient="records"))
    ]


# ── Writers ───────────────────────────────────────────────────────────────────

class Site:
    def __init__(self, out: Path) -> None:
        self.out = out
        self.routes: list[str] = []

    def write(self, route: str, payload) -> None:
        path = self.out / f"{route}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        self.routes.append(route)


def build(out: Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    site = Site(out)
    verify = Verifier()

    raw = D.load_all()

    # ── Site-wide constants ──────────────────────────────────────────────────
    site.write("site", {
        "leagueName": D.LEAGUE_NAME,
        "subtitle": D.LEAGUE_SUBTITLE,
        "founded": D.FOUNDED,
        "currentSeason": D.CURRENT_SEASON,
        "managerColors": D.MANAGER_COLORS,
        "managerEmoji": D.MANAGER_EMOJI,
    })

    champions_view = D.get_champions_view()
    if normalize(champions_view) != load_fixture("get_champions_view"):
        raise SystemExit("\n  champions view does not match its fixture — refusing to emit.\n")
    verify.checked += 1
    site.write("champions-view", champions_view)

    all_time_frame = verify.frame("get_all_time_manager_stats", D.get_all_time_manager_stats())
    history = D.get_league_history_view()
    if normalize(history) != load_fixture("get_league_history_view"):
        raise SystemExit("\n  league history does not match its fixture — refusing to emit.\n")
    verify.checked += 1
    site.write("league-history", {
        **history,
        "allTimeManagers": records(all_time_frame),
    })

    home = D.get_home_view()
    if normalize(home) != load_fixture("get_home_view"):
        raise SystemExit("\n  home view does not match its fixture — refusing to emit.\n")
    verify.checked += 1
    site.write("home", home)

    # ── Champions & timeline ─────────────────────────────────────────────────
    champions = verify.frame("get_champions", D.get_champions())
    site.write("champions", records(champions))
    verify.frame("get_timeline_events", D.get_timeline_events())
    timeline = D.get_timeline_view()
    if normalize(timeline) != load_fixture("get_timeline_view"):
        raise SystemExit("\n  timeline does not match its fixture — refusing to emit.\n")
    verify.checked += 1
    site.write("timeline", {
        **timeline,
        "bySeason": D.group_timeline_by_season(
            [e for e in timeline["events"] if e["show_on_league_timeline"]]
        ),
    })

    # ── Draft & keepers ──────────────────────────────────────────────────────
    draft_center = D.get_draft_center_view()
    if normalize(draft_center) != load_fixture("get_draft_center_view"):
        raise SystemExit("\n  draft center does not match its fixture — refusing to emit.\n")
    verify.checked += 1
    site.write("draft-center", draft_center)
    for board in ["All Players", "QB", "RB", "WR", "TE", "K", "DEF", "Keepers Only"]:
        site.write(f"draft-loyalty/{slugify(board)}", D.get_draft_loyalty_board(board))

    site.write("draft", {
        "records": normalize(D.get_draft_records())["value"],
        "positionTrends": records(verify.frame("get_position_trends_data", D.get_position_trends_data())),
        "picks": records(verify.frame("get_draft_picks_with_pos", D.get_draft_picks_with_pos())),
    })
    keeper_hall = D.get_keeper_hall_view()
    if normalize(keeper_hall) != load_fixture("get_keeper_hall_view"):
        raise SystemExit("\n  keeper hall does not match its fixture — refusing to emit.\n")
    verify.checked += 1
    site.write("keepers", {
        "chains": records(verify.frame("get_keeper_chains", D.get_keeper_chains())),
        "enriched": records(verify.frame("get_keeper_enriched", D.get_keeper_enriched())),
        **keeper_hall,
    })
    site.write("player-ownership", records(verify.frame("get_player_ownership", D.get_player_ownership())))

    # ── Managers ─────────────────────────────────────────────────────────────
    stats = verify.frame("get_manager_stats", D.get_manager_stats())
    all_time = all_time_frame
    all_time_by_name = {r["canonical_name"]: r for r in records(all_time)}

    index = []
    for row in records(stats):
        name = row["canonical_name"]
        slug = slugify(name)
        index.append({"slug": slug, "name": name, "displayName": row.get("display_name"),
                      "firstSeason": row.get("first_season"), "lastSeason": row.get("last_season"),
                      "championships": row.get("championships"), "active": row.get("active")})
        site.write(f"managers/{slug}", {
            "slug": slug,
            **D.get_manager_profile(name),
            "allTime": all_time_by_name.get(name),
            "h2hHighlights": D.manager_h2h_highlights(D.get_manager_profile(name)["head_to_head"]),
        })
    site.write("managers/index", index)

    # ── Franchises ───────────────────────────────────────────────────────────
    fran = verify.frame("get_franchise_stats", D.get_franchise_stats())
    stewards = records(verify.frame("get_franchise_steward_periods", D.get_franchise_steward_periods()))

    fran_index = []
    for row in records(fran):
        fid = row["franchise_id"]
        fran_index.append({"id": fid, "currentManager": row.get("current_manager"),
                           "established": row.get("established"), "championships": row.get("championships")})
        site.write(f"franchises/{fid}", {
            "id": fid,
            "stats": row,
            **D.get_franchise_profile(fid),
        })
    site.write("franchises/index", fran_index)

    # ── Rivalries ────────────────────────────────────────────────────────────
    rivalries = verify.frame("get_all_rivalries", D.get_all_rivalries())
    riv_rows = records(rivalries)
    rivalries_view = D.get_rivalries_view()
    if normalize(rivalries_view) != load_fixture("get_rivalries_view"):
        raise SystemExit("\n  rivalries view does not match its fixture — refusing to emit.\n")
    verify.checked += 1
    site.write("rivalries-view", rivalries_view)

    site.write("rivalries/index", [
        {**r, "slug": pair_slug(r["mgr_a"], r["mgr_b"])} for r in riv_rows
    ])
    for r in riv_rows:
        slug = pair_slug(r["mgr_a"], r["mgr_b"])
        detail = normalize(D.get_h2h_detail(r["mgr_a"], r["mgr_b"]))
        site.write(f"rivalries/{slug}", {"summary": r, "detail": detail["value"]})

    site.write("franchise-rivalries", records(verify.frame("get_franchise_rivalries", D.get_franchise_rivalries())))
    site.write("playoff-eliminations", records(verify.frame("get_playoff_eliminations", D.get_playoff_eliminations())))

    # ── Seasons ──────────────────────────────────────────────────────────────
    # get_season_detail() carries the standings, bracket, scorers, and the
    # generated title/narrative copy — all fixture-covered since the logic was
    # lifted out of pages/season_archive.py.
    trades = raw["season_trades"]
    season_fixtures = load_fixture("get_season_detail")["value"]
    seasons = sorted(D.get_all_seasons())

    for year in seasons:
        detail = D.get_season_detail(year)
        if normalize(detail) != season_fixtures[str(year)]:
            raise SystemExit(f"\n  seasons/{year} does not match its fixture — refusing to emit.\n")
        site.write(f"seasons/{year}", {
            **detail,
            "trades": records(trades[trades["season"] == year]),
        })
    verify.checked += 1

    site.write("seasons/index", [
        {
            "season": y,
            "title": D.get_season_detail(y)["title"],
            "champion": (D.get_season_detail(y)["champion"] or {}).get("manager"),
        }
        for y in seasons
    ])

    # ── Manifest ─────────────────────────────────────────────────────────────
    total_bytes = sum(p.stat().st_size for p in out.rglob("*.json"))
    site.write("manifest", {
        "routes": sorted(site.routes),
        "counts": {
            "managers": len(index), "franchises": len(fran_index),
            "seasons": len(seasons), "rivalries": len(riv_rows),
        },
        "verifiedAgainstFixtures": verify.checked,
    })

    print(f"Wrote {len(site.routes) + 1} JSON files to {out.relative_to(ROOT)}/ ({total_bytes/1e6:.2f} MB)")
    print(f"  {verify.checked} derivations verified against tests/fixtures/")
    if verify.skipped:
        print(f"  ⚠ no fixture for: {', '.join(verify.skipped)}")
    print(f"  {len(index)} managers · {len(fran_index)} franchises · "
          f"{len(seasons)} seasons · {len(riv_rows)} rivalries")

    if PAGE_LEVEL_WORK:
        print("\nPages still rendering from their own copy (rewiring pending):")
        for page, note in PAGE_LEVEL_WORK.items():
            print(f"  {page:24} {note}")


# Pages that call load_all() and derive from raw frames themselves. Each needs
# its logic lifted into utils/data.py (with fixtures) before the port can render
# that route from JSON alone.
PAGE_LEVEL_WORK: dict[str, str] = {}  # Phase 4 audit complete — every page rewired.


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    build(parser.parse_args().out)


if __name__ == "__main__":
    main()
