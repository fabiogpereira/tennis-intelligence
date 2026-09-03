import csv
import tempfile
import unittest
from pathlib import Path

from research.experiments.profile_mcp import profile, write_reports


MATCH_FIELDS = [
    "match_id",
    "Date",
    "Tournament",
    "Round",
    "Surface",
    "Best of",
    "Player 1",
    "Player 2",
]
POINT_FIELDS = [
    "match_id",
    "Pt",
    "Set1",
    "Set2",
    "Gm1",
    "Gm2",
    "Pts",
    "Gm#",
    "TbSet",
    "Svr",
    "1st",
    "2nd",
    "Notes",
    "PtWinner",
]


class McpProfileTests(unittest.TestCase):
    def write_csv(self, path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
        with path.open("w", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(output, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def make_profile(self, directory: str) -> dict[str, object]:
        root = Path(directory)
        matches = root / "matches.csv"
        points = root / "points.csv"
        self.write_csv(
            matches,
            MATCH_FIELDS,
            [
                {
                    "match_id": "20200101-W-Test-R32-Alice-Bob",
                    "Date": "20200101",
                    "Tournament": "Test",
                    "Round": "R32",
                    "Surface": "Hard",
                    "Best of": "3",
                    "Player 1": "Alice",
                    "Player 2": "Bob",
                }
            ],
        )
        first = {
            "match_id": "20200101-W-Test-R32-Alice-Bob",
            "Pt": "1",
            "Set1": "0",
            "Set2": "0",
            "Gm1": "0",
            "Gm2": "0",
            "Pts": "0-0",
            "Gm#": "1 (1)",
            "TbSet": "1",
            "Svr": "1",
            "1st": "4*",
            "2nd": "",
            "Notes": "",
            "PtWinner": "1",
        }
        conflict_a = dict(first, Pt="2", Pts="15-0", **{"1st": "5f2*"})
        conflict_b = dict(conflict_a, **{"1st": "6b3@"})
        orphan = dict(first, match_id="20200102-M-Other-R32-Cal-Dan")
        self.write_csv(points, POINT_FIELDS, [first, dict(first), conflict_a, conflict_b, orphan])
        return profile(points, matches)

    def test_profiles_duplicate_policy_and_orphan_rows(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.make_profile(directory)
        self.assertEqual(len(result["point_rows"]), 5)
        self.assertEqual(result["duplicate_counts"]["groups"], 2)
        self.assertEqual(result["duplicate_counts"]["exact"], 1)
        self.assertEqual(result["duplicate_counts"]["conflicting"], 1)
        self.assertEqual(result["duplicate_counts"]["conflicting_rows"], 2)
        self.assertEqual(len(result["usable_point_rows"]), 2)
        self.assertEqual(len(result["matched_point_rows"]), 1)
        self.assertEqual(result["orphan_point_rows"], 1)
        self.assertEqual(result["players_by_tour"]["WTA"], 2)

    def test_generated_reports_use_fixture_counts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.make_profile(directory)
            output = Path(directory) / "reports"
            write_reports(result, output)
            dataset_report = (output / "dataset_profile.md").read_text(encoding="utf-8")
            feasibility_report = (output / "data_feasibility.md").read_text(encoding="utf-8")
        self.assertIn("| Raw point rows | 5 |", dataset_report)
        self.assertIn("1 usable rows across 1 charted matches", feasibility_report)
        self.assertNotIn("57,913", feasibility_report)

    def test_rejects_missing_required_point_headers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            matches = root / "matches.csv"
            points = root / "points.csv"
            self.write_csv(matches, MATCH_FIELDS, [])
            self.write_csv(points, ["match_id"], [])
            with self.assertRaisesRegex(ValueError, "missing MCP point columns"):
                profile(points, matches)

    def test_rejects_missing_required_match_headers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            matches = root / "matches.csv"
            points = root / "points.csv"
            self.write_csv(matches, ["match_id"], [])
            self.write_csv(points, POINT_FIELDS, [])
            with self.assertRaisesRegex(ValueError, "missing MCP match columns"):
                profile(points, matches)


if __name__ == "__main__":
    unittest.main()
