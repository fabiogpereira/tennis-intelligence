import csv
import tempfile
import unittest
from pathlib import Path

from research.experiments.profile_mcp_snapshot import (
    InvalidSnapshot,
    _counter_records,
    _five_number,
    _read_aggregates,
    _read_metadata,
    _read_points,
    profile_snapshot,
)


POINT_FIELDS = [
    "match_id",
    "Pt",
    "Set1",
    "Set2",
    "Gm1",
    "Gm2",
    "Pts",
    "Svr",
    "1st",
    "2nd",
    "PtWinner",
]
MATCH_FIELDS = [
    "match_id",
    "Player 1",
    "Player 2",
    "Date",
    "Tournament",
    "Round",
    "Surface",
    "Best of",
]


class McpSnapshotProfileTests(unittest.TestCase):
    def test_complete_profile_rejects_unversioned_source_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(InvalidSnapshot, "expected MCP commit"):
                profile_snapshot(Path(directory))

    def test_counter_records_preserve_case_distinct_characters(self) -> None:
        self.assertEqual(
            _counter_records({"A": 1, "a": 2}, "character"),
            [
                {"character": "a", "count": 2},
                {"character": "A", "count": 1},
            ],
        )

    def test_five_number_summary_is_deterministic(self) -> None:
        self.assertEqual(
            _five_number([1, 2, 3, 4, 100]),
            {"minimum": 1, "p25": 2, "median": 3, "p75": 4, "maximum": 100},
        )

    def write_csv(self, path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
        with path.open("w", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(output, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def point(self, match_id: str, number: str, notation: str) -> dict[str, str]:
        return {
            "match_id": match_id,
            "Pt": number,
            "Set1": "0",
            "Set2": "0",
            "Gm1": "0",
            "Gm2": "0",
            "Pts": "0-0",
            "Svr": "1",
            "1st": notation,
            "2nd": "",
            "PtWinner": "1",
        }

    def match(self, match_id: str, **updates: str) -> dict[str, str]:
        row = {
            "match_id": match_id,
            "Player 1": "Alice",
            "Player 2": "Bob",
            "Date": "20200101",
            "Tournament": "Test",
            "Round": "F",
            "Surface": "Hard",
            "Best of": "3",
        }
        row.update(updates)
        return row

    def test_point_profile_collapses_exact_and_excludes_conflicting_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "charting-w-points-2020s.csv"
            first = self.point("20200101-W-Test-F-Alice-Bob", "1", "4*")
            conflict_a = self.point("20200101-W-Test-F-Alice-Bob", "2", "5f2*")
            conflict_b = dict(conflict_a, **{"1st": "6b3@"})
            self.write_csv(path, POINT_FIELDS, [first, dict(first), conflict_a, conflict_b])
            result = _read_points([path])

        self.assertEqual(result["raw_rows"], 4)
        self.assertEqual(result["unique_point_keys"], 2)
        self.assertEqual(result["usable_point_rows"], 1)
        self.assertEqual(result["exact_duplicate_groups"], 1)
        self.assertEqual(result["conflicting_duplicate_groups"], 1)
        self.assertEqual(result["conflicting_raw_rows"], 2)
        self.assertEqual(result["field_counts"]["1st"]["rows"], 1)
        self.assertEqual(result["notation_nonempty"]["1st"], 1)
        self.assertEqual(result["undocumented_notation_characters"], [])

    def test_metadata_profile_excludes_conflicts_and_structural_anomalies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "charting-w-matches.csv"
            safe = self.match("20200101-W-Test-F-Alice-Bob")
            conflict = self.match("20200102-W-Test-F-Cal-Dan")
            conflicting_copy = dict(conflict, Tournament="Other")
            anomalous = self.match("20200103-W-Test-F-Eve-Fay", Surface="Unknown")
            self.write_csv(path, MATCH_FIELDS, [safe, conflict, conflicting_copy, anomalous])
            result = _read_metadata([path])

        self.assertEqual(result["unique_match_ids"], 3)
        self.assertEqual(result["conflicting_match_ids"], 1)
        self.assertEqual(result["anomalous_match_ids"], 1)
        self.assertEqual(set(result["safe_rows"]), {safe["match_id"]})

    def test_aggregate_profile_flags_conflicting_grain_and_invalid_numbers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "charting-m-stats-Overview.csv"
            fields = ["match_id", "player", "set", "serve_pts"]
            match_id = "20200101-M-Test-F-Alice-Bob"
            rows = [
                {"match_id": match_id, "player": "Alice", "set": "Total", "serve_pts": "50"},
                {"match_id": match_id, "player": "Alice", "set": "Total", "serve_pts": "51"},
                {"match_id": match_id, "player": "Bob", "set": "Total", "serve_pts": "unknown"},
            ]
            self.write_csv(path, fields, rows)
            result = _read_aggregates([path], {match_id}, {match_id})[0]

        self.assertEqual(result["duplicate_grain_rows"], 1)
        self.assertEqual(result["conflicting_grain_groups"], 1)
        self.assertEqual(result["invalid_numeric_values"], 1)
        self.assertEqual(result["charted_matches_covered"], 1)


if __name__ == "__main__":
    unittest.main()
