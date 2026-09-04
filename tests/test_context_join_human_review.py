import csv
import tempfile
import unittest
from pathlib import Path

from research.experiments.summarize_context_join_review import (
    InvalidHumanReview,
    _wilson_interval,
    summarize_review,
)


FIELDS = [
    "mcp_match_id",
    "mcp_date",
    "status",
    "surface_agrees",
    "review_status",
    "review_notes",
]


def write_rows(path: Path, delimiter: str, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=FIELDS, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)


class ContextJoinHumanReviewTests(unittest.TestCase):
    def test_accepts_excel_localized_evidence_without_changing_meaning(self) -> None:
        automated = {
            "mcp_match_id": "m1",
            "mcp_date": "2026-09-03",
            "status": "matched",
            "surface_agrees": "true",
            "review_status": "",
            "review_notes": "",
        }
        human = dict(
            automated,
            mcp_date="03/09/2026",
            surface_agrees="VERDADEIRO",
            review_status="confirmed",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            automated_path = root / "automated.csv"
            human_path = root / "human.csv"
            write_rows(automated_path, ",", [automated])
            write_rows(human_path, ";", [human])
            result = summarize_review(automated_path, human_path)

        self.assertEqual(result["decision_counts"], {"same_match": 1})
        self.assertEqual(
            result["safe_match_precision_review"]["observed_precision"], 1.0
        )

    def test_rejects_changed_evidence(self) -> None:
        automated = {
            "mcp_match_id": "m1",
            "mcp_date": "2026-09-03",
            "status": "matched",
            "surface_agrees": "true",
            "review_status": "",
            "review_notes": "",
        }
        human = dict(automated, status="ambiguous", review_status="confirmed")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            automated_path = root / "automated.csv"
            human_path = root / "human.csv"
            write_rows(automated_path, ",", [automated])
            write_rows(human_path, ";", [human])
            with self.assertRaises(InvalidHumanReview):
                summarize_review(automated_path, human_path)

    def test_wilson_interval_does_not_treat_25_of_25_as_certainty(self) -> None:
        lower, upper = _wilson_interval(25, 25)
        self.assertLess(lower, 0.9)
        self.assertAlmostEqual(upper, 1.0)


if __name__ == "__main__":
    unittest.main()
