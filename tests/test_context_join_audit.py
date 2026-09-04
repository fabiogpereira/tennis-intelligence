import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research.experiments.audit_context_join import (
    CONTEXT_COMMIT,
    REQUIRED_CONTEXT_FIELDS,
    read_context_matches,
)


class ContextJoinAuditTests(unittest.TestCase):
    def test_context_reader_collapses_duplicates_and_excludes_conflicts(self) -> None:
        base = {
            "tourney_id": "2020-1",
            "tourney_name": "Test",
            "surface": "Hard",
            "tourney_date": "20200101",
            "match_num": "1",
            "winner_id": "10",
            "winner_name": "Alice One",
            "loser_id": "20",
            "loser_name": "Bea Two",
            "best_of": "3",
            "round": "F",
            "winner_rank": "1",
            "loser_rank": "2",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "atp").mkdir()
            (root / "wta").mkdir()
            path = root / "atp" / "atp_matches_2020.csv"
            fields = sorted(REQUIRED_CONTEXT_FIELDS)
            conflicting = dict(base, loser_id="21")
            safe = dict(base, match_num="2")
            with path.open("w", newline="", encoding="utf-8") as destination:
                writer = csv.DictWriter(destination, fieldnames=fields)
                writer.writeheader()
                writer.writerows((base, base, conflicting, safe))
            with patch(
                "research.experiments.audit_context_join._git_commit",
                return_value=CONTEXT_COMMIT,
            ):
                records, profile = read_context_matches(root)

        self.assertEqual(profile["raw_rows"], 4)
        self.assertEqual(profile["exact_duplicate_rows"], 1)
        self.assertEqual(profile["conflicting_canonical_keys"], 1)
        self.assertEqual(profile["safe_canonical_matches"], 1)
        self.assertEqual(records[0].canonical_match_id, "sackmann:atp:tour:2020-1:2")


if __name__ == "__main__":
    unittest.main()
