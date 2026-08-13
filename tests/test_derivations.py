"""Assert that utils/data.py still produces the recorded league history.

    python3 -m unittest discover -s tests -p 'test_*.py'

These are golden-file tests. They don't encode what the numbers *should* be —
they encode what they *were* when the fixtures were captured, which is the
question that matters for a 25-year archive: did anything change that nobody
meant to change?

Regenerate with `python3 tests/capture_fixtures.py` when a change is intended.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _harness import FIXTURES, install_streamlit_stub, load, normalize  # noqa: E402

install_streamlit_stub()

from utils import data as D  # noqa: E402


class FixtureAssertions(unittest.TestCase):
    maxDiff = 8000

    def assert_matches(self, name: str, actual) -> None:
        path = FIXTURES / f"{name}.json"
        self.assertTrue(
            path.exists(),
            f"Missing fixture {path.name}. Run: python3 tests/capture_fixtures.py",
        )
        expected = load(name)
        self.assert_payload(name, normalize(actual), expected)

    def assert_payload(self, label: str, actual: dict, expected: dict) -> None:
        self.assertEqual(actual.get("type"), expected.get("type"), f"{label}: type changed")

        if expected.get("type") == "dataframe":
            self.assertEqual(
                actual["columns"], expected["columns"],
                f"{label}: columns changed\n  was:  {expected['columns']}\n  now:  {actual['columns']}",
            )
            self.assertEqual(
                actual["shape"], expected["shape"],
                f"{label}: row/column count changed — was {expected['shape']}, now {actual['shape']}",
            )
            if "rows" in expected:
                # Small frame: compare row by row so failures point at the row.
                for i, (got, want) in enumerate(zip(actual["rows"], expected["rows"])):
                    self.assertEqual(got, want, f"{label}: row {i} changed")
            else:
                self.assertEqual(actual["head"], expected["head"], f"{label}: leading rows changed")
                self.assertEqual(actual["tail"], expected["tail"], f"{label}: trailing rows changed")
            self.assertEqual(
                actual["digest"], expected["digest"],
                f"{label}: contents changed somewhere outside the sampled rows",
            )
            return

        if expected.get("type") == "dict":
            self.assertEqual(
                sorted(actual["value"]), sorted(expected["value"]),
                f"{label}: keys changed",
            )
            for key in expected["value"]:
                self.assert_payload(f"{label}[{key}]", actual["value"][key], expected["value"][key])
            return

        self.assertEqual(actual, expected, f"{label}: changed")


class TestSourceData(FixtureAssertions):
    def test_csv_schema_is_stable(self):
        expected = load("00_source_schema")["value"]
        actual = {
            key: {"shape": list(df.shape), "columns": [str(c) for c in df.columns]}
            for key, df in D.load_all().items()
        }
        self.assertEqual(sorted(actual), sorted(expected), "a CSV was added or removed")
        for key in expected:
            self.assertEqual(
                actual[key]["columns"], expected[key]["columns"],
                f"{key}.csv: columns changed",
            )
            self.assertEqual(
                actual[key]["shape"], expected[key]["shape"],
                f"{key}.csv: row count changed — was {expected[key]['shape'][0]}, "
                f"now {actual[key]['shape'][0]}. Intended? Re-capture fixtures.",
            )


class TestChampionsAndManagers(FixtureAssertions):
    def test_champions(self):
        self.assert_matches("get_champions", D.get_champions())

    def test_manager_stats(self):
        self.assert_matches("get_manager_stats", D.get_manager_stats())

    def test_all_time_manager_stats(self):
        self.assert_matches("get_all_time_manager_stats", D.get_all_time_manager_stats())

    def test_manager_season_history(self):
        expected = load("get_manager_season_history")
        actual = {
            "type": "dict",
            "value": {m: normalize(D.get_manager_season_history(m)) for m in expected["value"]},
        }
        self.assert_payload("get_manager_season_history", actual, expected)

    def test_manager_h2h(self):
        expected = load("get_manager_h2h")
        actual = {
            "type": "dict",
            "value": {m: normalize(D.get_manager_h2h(m)) for m in expected["value"]},
        }
        self.assert_payload("get_manager_h2h", actual, expected)


class TestFranchises(FixtureAssertions):
    def test_steward_periods(self):
        self.assert_matches("get_franchise_steward_periods", D.get_franchise_steward_periods())

    def test_franchise_stats(self):
        self.assert_matches("get_franchise_stats", D.get_franchise_stats())

    def test_franchise_legends(self):
        expected = load("get_franchise_legends")
        actual = {
            "type": "dict",
            "value": {f: normalize(D.get_franchise_legends(f)) for f in expected["value"]},
        }
        self.assert_payload("get_franchise_legends", actual, expected)


class TestDraftAndKeepers(FixtureAssertions):
    def test_draft_picks_with_pos(self):
        self.assert_matches("get_draft_picks_with_pos", D.get_draft_picks_with_pos())

    def test_position_trends(self):
        self.assert_matches("get_position_trends_data", D.get_position_trends_data())

    def test_draft_records(self):
        self.assert_matches("get_draft_records", D.get_draft_records())

    def test_keeper_chains(self):
        self.assert_matches("get_keeper_chains", D.get_keeper_chains())

    def test_keeper_enriched(self):
        self.assert_matches("get_keeper_enriched", D.get_keeper_enriched())

    def test_player_ownership(self):
        self.assert_matches("get_player_ownership", D.get_player_ownership())


class TestHome(FixtureAssertions):
    def test_home_view(self):
        """Covers the logic lifted out of app.py."""
        self.assert_matches("get_home_view", D.get_home_view())

    def test_legends_are_ordered_deterministically(self):
        legends = D.get_home_view()["legends"]
        keys = [(-l["titles"], l["manager"]) for l in legends]
        self.assertEqual(keys, sorted(keys), "legends must sort by titles then name")

    def test_best_season_copy_names_every_tied_manager(self):
        """The old copy hardcoded two names; regenerating must cover them all."""
        best = D.get_home_view()["storylines"]["best_season"]
        for manager in best["managers"]:
            self.assertIn(manager, best["summary"], f"{manager} missing from best-season copy")


class TestLeagueHistory(FixtureAssertions):
    def test_season_scoring(self):
        self.assert_matches("get_season_scoring", D.get_season_scoring())

    def test_league_history_view(self):
        """Covers the logic lifted out of pages/league_history.py."""
        self.assert_matches("get_league_history_view", D.get_league_history_view())

    def test_era_bands_match_the_era_cards(self):
        """The chart used to shade eras from a second hardcoded list that had
        already drifted from LEAGUE_ERAS."""
        view = D.get_league_history_view()
        self.assertEqual(
            [(b["label"], b["start"], b["end"]) for b in view["era_bands"]],
            [(e["short"], e["start"], e["end"]) for e in view["eras"]],
            "era shading must come from the same definition as the era cards",
        )

    def test_title_counts_are_ordered_deterministically(self):
        counts = D.get_league_history_view()["balance"]["title_counts"]
        keys = [(-c["titles"], c["manager"]) for c in counts]
        self.assertEqual(keys, sorted(keys), "title ranking must break ties by name")


class TestSeasons(FixtureAssertions):
    def test_season_list(self):
        seasons = D.get_all_seasons()
        self.assertEqual(seasons, sorted(seasons, reverse=True), "seasons must be newest-first")
        self.assertEqual(len(seasons), len(set(seasons)), "duplicate season")

    def test_season_detail(self):
        """Covers the logic lifted out of pages/season_archive.py, including
        the generated season titles and narrative copy."""
        expected = load("get_season_detail")
        actual = {
            "type": "dict",
            "value": {year: normalize(D.get_season_detail(int(year))) for year in expected["value"]},
        }
        self.assert_payload("get_season_detail", actual, expected)


class TestRivalriesAndTimeline(FixtureAssertions):
    def test_all_rivalries(self):
        self.assert_matches("get_all_rivalries", D.get_all_rivalries())

    def test_franchise_rivalries(self):
        self.assert_matches("get_franchise_rivalries", D.get_franchise_rivalries())

    def test_playoff_eliminations(self):
        self.assert_matches("get_playoff_eliminations", D.get_playoff_eliminations())

    def test_timeline_events(self):
        self.assert_matches("get_timeline_events", D.get_timeline_events())

    def test_era_by_season(self):
        self.assert_matches(
            "get_era_by_season", {str(k): v for k, v in D.get_era_by_season().items()}
        )

    def test_timeline_view(self):
        """Covers the enrichment lifted out of pages/league_timeline.py."""
        self.assert_matches("get_timeline_view", D.get_timeline_view())

    def test_timeline_grouping(self):
        shown = [e for e in D.get_timeline_view()["events"] if e["show_on_league_timeline"]]
        self.assert_matches("group_timeline_by_season", D.group_timeline_by_season(shown))

    def test_h2h_detail(self):
        expected = load("get_h2h_detail")
        actual = {"type": "dict", "value": {}}
        for label in expected["value"]:
            mgr_a, mgr_b = label.split(" vs ")
            actual["value"][label] = normalize(D.get_h2h_detail(mgr_a, mgr_b))
        self.assert_payload("get_h2h_detail", actual, expected)


class TestInvariants(unittest.TestCase):
    """A few facts that should hold regardless of what the fixtures say.

    Golden files catch drift; these catch a change that is wrong on its face.
    """

    def test_one_champion_per_season(self):
        champions = D.get_champions()
        self.assertEqual(
            len(champions), champions["season"].nunique(),
            "more than one champion recorded for some season",
        )

    def test_champion_outscored_runner_up(self):
        champions = D.get_champions()
        losing = champions[champions["champion_score"] < champions["runner_up_score"]]
        self.assertTrue(
            losing.empty,
            f"champion scored less than the runner-up in: {losing['season'].tolist()}",
        )

    def test_manager_games_reconcile(self):
        stats = D.get_manager_stats()
        played = stats["wins"] + stats["losses"] + stats["ties"]
        self.assertTrue((played > 0).all(), "a manager has zero recorded games")

    def test_head_to_head_wins_reconcile(self):
        riv = D.get_all_rivalries()
        mismatched = riv[riv["rs_a_wins"] + riv["rs_b_wins"] > riv["rs_games"]]
        self.assertTrue(
            mismatched.empty,
            "a rivalry records more wins than games played",
        )

    def test_every_drafted_player_has_a_position(self):
        picks = D.get_draft_picks_with_pos()
        missing = picks[picks["position"].isna()]
        self.assertTrue(
            missing.empty,
            f"{len(missing)} draft picks have no position — re-run build_player_positions.py",
        )


if __name__ == "__main__":
    unittest.main()
