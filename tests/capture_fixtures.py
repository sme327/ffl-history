"""Capture the current derived outputs of utils/data.py as golden fixtures.

    python3 tests/capture_fixtures.py

Run this deliberately, never automatically. The fixtures record what the app
computes *today*, and tests/test_derivations.py asserts nothing has drifted
since. Regenerating them is how you accept a change — so a diff on
tests/fixtures/ in code review is the signal that league history moved.

Legitimate reasons to regenerate:
  - new season added to data/
  - a data correction (see git log for the running list of those)
  - a derivation was deliberately changed, and the new numbers were eyeballed

If the fixtures change and none of those apply, that's the bug this suite exists
to catch.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _harness import dump, install_streamlit_stub, normalize  # noqa: E402

install_streamlit_stub()

from utils import data as D  # noqa: E402

# Every no-argument derivation. If you add one to utils/data.py, add it here.
GLOBAL_DERIVATIONS = [
    "get_champions",
    "get_manager_stats",
    "get_all_time_manager_stats",
    "get_manager_season_history",  # parameterized — handled below, listed for the audit
    "get_franchise_steward_periods",
    "get_franchise_stats",
    "get_timeline_events",
    "get_draft_picks_with_pos",
    "get_position_trends_data",
    "get_draft_records",
    "get_keeper_chains",
    "get_player_ownership",
    "get_keeper_enriched",
    "get_all_rivalries",
    "get_franchise_rivalries",
    "get_playoff_eliminations",
]

PARAMETERIZED = {"get_manager_season_history", "get_manager_h2h", "get_franchise_legends", "get_h2h_detail"}

# How many rivalries get full game-by-game capture. The pairwise space is 195
# rows; the ones with real history are what the site actually surfaces.
TOP_RIVALRIES = 15


def capture_schema() -> None:
    """Row counts and columns of the raw CSVs — catches a schema change early."""
    payload = {
        key: {"shape": list(df.shape), "columns": [str(c) for c in df.columns]}
        for key, df in sorted(D.load_all().items())
    }
    dump("00_source_schema", {"type": "schema", "value": payload})
    print(f"  00_source_schema           {len(payload)} tables")


def capture_globals() -> None:
    for name in GLOBAL_DERIVATIONS:
        if name in PARAMETERIZED:
            continue
        payload = normalize(getattr(D, name)())
        dump(name, payload)
        shape = payload.get("shape") or payload.get("length") or "—"
        print(f"  {name:26} {shape}")


def capture_by_manager() -> None:
    managers = sorted(D.get_manager_stats()["canonical_name"].tolist())

    for fn_name in ("get_manager_season_history", "get_manager_h2h"):
        fn = getattr(D, fn_name)
        payload = {"type": "dict", "value": {m: normalize(fn(m)) for m in managers}}
        dump(fn_name, payload)
        print(f"  {fn_name:26} {len(managers)} managers")


def capture_by_franchise() -> None:
    franchises = sorted(D.get_franchise_stats()["franchise_id"].tolist())
    payload = {"type": "dict", "value": {f: normalize(D.get_franchise_legends(f)) for f in franchises}}
    dump("get_franchise_legends", payload)
    print(f"  {'get_franchise_legends':26} {len(franchises)} franchises")


def capture_seasons() -> None:
    """Season pages, including the generated title and narrative copy.

    Extracted from pages/season_archive.py — this fixture is what stops the
    editorial voice drifting during the port.
    """
    seasons = sorted(D.get_all_seasons())
    payload = {"type": "dict", "value": {str(s): normalize(D.get_season_detail(s)) for s in seasons}}
    dump("get_season_detail", payload)
    print(f"  {'get_season_detail':26} {len(seasons)} seasons")


def capture_home() -> None:
    """Home page view, including the generated best-season copy that replaced
    a hardcoded sentence naming two managers (product review, F3)."""
    dump("get_home_view", normalize(D.get_home_view()))
    print(f"  {'get_home_view':26} home")


def capture_rivalries_view() -> None:
    """Finals, title records, playoff eliminations and the hall of pain —
    lifted out of pages/rivalries.py, the page that started all of this."""
    dump("get_rivalries_view", normalize(D.get_rivalries_view()))
    dump("get_head_to_head_losses", normalize(D.get_head_to_head_losses()))
    print(f"  {'get_rivalries_view':26} finals + pain")


def capture_keeper_hall() -> None:
    """Immortal keeper chains, championship keepers and per-manager keeper DNA —
    lifted out of pages/keeper_hall.py."""
    dump("get_keeper_hall_view", normalize(D.get_keeper_hall_view()))
    print(f"  {'get_keeper_hall_view':26} chains + DNA")


def capture_franchise_profiles() -> None:
    """Per-franchise history and the generated legacy story —
    lifted out of pages/franchise_profiles.py."""
    ids = sorted(D.get_franchise_stats()["franchise_id"].tolist())
    dump("get_franchise_profile", {"type": "dict",
                                   "value": {f: normalize(D.get_franchise_profile(f)) for f in ids}})
    print(f"  {'get_franchise_profile':26} {len(ids)} franchises")


def capture_draft_center() -> None:
    """Player legends, manager draft DNA and round-one history —
    lifted out of pages/draft_center.py."""
    dump("get_draft_center_view", normalize(D.get_draft_center_view()))
    boards = ["All Players", "QB", "RB", "WR", "TE", "K", "DEF", "Keepers Only"]
    dump("get_draft_loyalty_board", {"type": "dict", "value": {
        f: normalize(D.get_draft_loyalty_board(f)) for f in boards
    }})
    print(f"  {'get_draft_center_view':26} legends + DNA")


def capture_manager_profiles() -> None:
    """Full profile per manager, including the generated Hall of Fame plaque —
    lifted out of pages/manager_profiles.py."""
    directory = D.get_manager_directory()
    dump("get_manager_directory", normalize(directory))
    names = sorted(directory["active"] + directory["former"])
    dump("get_manager_profile", {"type": "dict",
                                 "value": {n: normalize(D.get_manager_profile(n)) for n in names}})
    dump("manager_h2h_highlights", {"type": "dict", "value": {
        n: normalize(D.manager_h2h_highlights(D.get_manager_profile(n)["head_to_head"]))
        for n in names
    }})
    print(f"  {'get_manager_profile':26} {len(names)} managers")


def capture_champions_view() -> None:
    """Leaders, dynasties, trivia and the championship-pain cards —
    lifted out of pages/champions.py."""
    dump("get_champions_view", normalize(D.get_champions_view()))
    print(f"  {'get_champions_view':26} leaders + dynasties")


def capture_league_history() -> None:
    """Eras, scoring evolution, competitive balance and league records —
    lifted out of pages/league_history.py."""
    dump("get_league_history_view", normalize(D.get_league_history_view()))
    dump("get_season_scoring", normalize(D.get_season_scoring()))
    print(f"  {'get_league_history_view':26} eras + records")


def capture_timeline() -> None:
    """Enriched timeline events and the season grouping.

    Extracted from pages/league_timeline.py — covers the event taxonomy
    (icons, colours, labels) and the era assignment as well as the events.
    """
    view = D.get_timeline_view()
    dump("get_timeline_view", normalize(view))
    dump("get_era_by_season", normalize({str(k): v for k, v in D.get_era_by_season().items()}))

    shown = [e for e in view["events"] if e["show_on_league_timeline"]]
    dump("group_timeline_by_season", normalize(D.group_timeline_by_season(shown)))
    print(f"  {'get_timeline_view':26} {view['stats']['total_events']} events")


def capture_rivalry_detail() -> None:
    riv = D.get_all_rivalries().sort_values("rs_games", ascending=False).head(TOP_RIVALRIES)
    pairs = [(row["mgr_a"], row["mgr_b"]) for _, row in riv.iterrows()]
    payload = {
        "type": "dict",
        "value": {f"{a} vs {b}": normalize(D.get_h2h_detail(a, b)) for a, b in pairs},
    }
    dump("get_h2h_detail", payload)
    print(f"  {'get_h2h_detail':26} {len(pairs)} rivalries")


def main() -> None:
    print("Capturing fixtures from data/ ...")
    capture_schema()
    capture_globals()
    capture_by_manager()
    capture_by_franchise()
    capture_seasons()
    capture_home()
    capture_rivalries_view()
    capture_keeper_hall()
    capture_franchise_profiles()
    capture_draft_center()
    capture_manager_profiles()
    capture_champions_view()
    capture_league_history()
    capture_timeline()
    capture_rivalry_detail()
    print("\nWrote tests/fixtures/. Review the diff before committing.")


if __name__ == "__main__":
    main()
