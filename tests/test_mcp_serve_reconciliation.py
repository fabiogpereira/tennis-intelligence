import csv
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from research.experiments.mcp_serve_reconciliation import (
    DIRECTION_COLUMNS,
    read_aggregate_rows,
    reconcile_directions,
    reconcile_overview,
)


class McpServeReconciliationTests(unittest.TestCase):
    def test_aggregate_reader_collapses_exact_and_excludes_conflicts(self) -> None:
        fields = ["match_id", "player", "set", "serve_pts", "aces", "dfs", "first_in", "second_in"]
        rows = [
            ["m1", "Alice", "Total", 4, 1, 0, 3, 1],
            ["m1", "Alice", "Total", 4, 1, 0, 3, 1],
            ["m2", "Bob", "Total", 5, 0, 1, 2, 3],
            ["m2", "Bob", "Total", 6, 0, 1, 2, 4],
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "overview.csv"
            with path.open("w", newline="") as output:
                writer = csv.writer(output)
                writer.writerow(fields)
                writer.writerows(rows)
            safe, profile = read_aggregate_rows(
                [path], "set", {"Total"}, ("serve_pts", "aces", "dfs", "first_in", "second_in")
            )
        self.assertIn(("m1", "Alice", "Total"), safe)
        self.assertNotIn(("m2", "Bob", "Total"), safe)
        self.assertEqual(profile["duplicate_grain_groups"], 2)
        self.assertEqual(profile["conflicting_grain_groups"], 1)

    def test_overview_comparison_respects_metric_missingness(self) -> None:
        computed = {("m1", "Alice"): Counter(serve_pts=4, aces=1, first_in=3, second_in=1)}
        aggregate = {
            ("m1", "Alice", "Total"): {
                "serve_pts": 4,
                "aces": 1,
                "dfs": 0,
                "first_in": 3,
                "second_in": 1,
            }
        }
        result = reconcile_overview(computed, aggregate)
        self.assertEqual(result["serve_pts"]["exact_rate"], 1.0)
        self.assertEqual(result["aces"]["exact_rate"], 1.0)

        computed[("m1", "Alice")]["_unresolved_ace"] = 1
        result = reconcile_overview(computed, aggregate)
        self.assertEqual(result["aces"]["comparable_records"], 0)
        self.assertEqual(result["serve_pts"]["comparable_records"], 1)

    def test_direction_comparison_keeps_serve_numbers_separate(self) -> None:
        raw = Counter({"direction:1:deuce:wide": 2, "direction:2:ad:t": 1})
        zeroes = {column: 0 for column in DIRECTION_COLUMNS}
        aggregate = {
            ("m1", "Alice", "1"): dict(zeroes, deuce_wide=2),
            ("m1", "Alice", "2"): dict(zeroes, ad_t=1),
            ("m1", "Alice", "Total"): dict(zeroes, deuce_wide=2, ad_t=1),
        }
        result = reconcile_directions({("m1", "Alice"): raw}, aggregate)
        self.assertEqual(result["1"]["exact_rate"], 1.0)
        self.assertEqual(result["1"]["marginal_exact_rate"], 1.0)
        self.assertEqual(result["2"]["exact_rate"], 1.0)
        self.assertEqual(result["Total"]["exact_rate"], 1.0)

    def test_mismatch_context_uses_comparable_denominators(self) -> None:
        computed = {
            ("20200101-M-Test-R1-A-B", "Alice"): Counter(serve_pts=4),
            ("20210101-W-Test-R1-C-D", "Carol"): Counter(serve_pts=5),
        }
        zeroes = {"aces": 0, "dfs": 0, "first_in": 0, "second_in": 0}
        aggregate = {
            ("20200101-M-Test-R1-A-B", "Alice", "Total"): dict(zeroes, serve_pts=3),
            ("20210101-W-Test-R1-C-D", "Carol", "Total"): dict(zeroes, serve_pts=5),
        }
        metadata = {
            "20200101-M-Test-R1-A-B": {
                "Date": "20200101",
                "Surface": "Hard",
                "Charted by": "Ann",
            },
            "20210101-W-Test-R1-C-D": {
                "Date": "20210101",
                "Surface": "Clay",
                "Charted by": "Bea",
            },
        }
        result = reconcile_overview(computed, aggregate, metadata)["serve_pts"]
        by_tour = {row["tour"]: row for row in result["mismatch_context"]["tour"]}
        self.assertEqual(by_tour["ATP"]["mismatch_rate"], 1.0)
        self.assertEqual(by_tour["WTA"]["mismatch_rate"], 0.0)
        by_surface = {
            row["surface"]: row for row in result["mismatch_context"]["surface"]
        }
        self.assertEqual(by_surface["hard"]["mismatch_rate"], 1.0)
        self.assertEqual(by_surface["clay"]["mismatch_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
