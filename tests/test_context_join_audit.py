import csv
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from pipelines.processing.entity_resolution import (
    ContextMatchIdentity,
    MatchResolution,
    McpMatchIdentity,
)
from research.experiments.audit_context_join import (
    CONTEXT_COMMIT,
    REQUIRED_CONTEXT_FIELDS,
    _review_row,
    read_context_matches,
)


class ContextJoinAuditTests(unittest.TestCase):
    def test_review_row_contains_source_evidence_and_blank_human_labels(self) -> None:
        match = McpMatchIdentity(
            match_id="mcp-1",
            tour="ATP",
            match_date=date(2026, 5, 25),
            tournament="Roland_Garros",
            round_name="R128",
            surface="Clay",
            best_of="5",
            player_1="Joao Fonseca",
            player_2="Novak Djokovic",
        )
        context = ContextMatchIdentity(
            canonical_match_id="sackmann:atp:tour:2026-520:1",
            tour="ATP",
            tournament_date=date(2026, 5, 24),
            tournament="Roland Garros",
            round_name="R128",
            surface="Clay",
            best_of="5",
            winner_name="Joao Fonseca",
            winner_id="123",
            winner_rank="50",
            loser_name="Novak Djokovic",
            loser_id="456",
            loser_rank="2",
            source_family="tour",
            source_file="atp/atp_matches_2026.csv",
        )
        resolution = MatchResolution(
            "matched",
            "exact_pair_date_unique",
            1,
            context,
            (context.canonical_match_id,),
        )

        row = _review_row(match, resolution)

        self.assertEqual(row["mcp_date"], "2026-05-25")
        self.assertEqual(row["context_tournament_date"], "2026-05-24")
        self.assertEqual(row["candidate_context_ids"], context.canonical_match_id)
        self.assertEqual(row["context_source_file"], context.source_file)
        self.assertEqual(row["best_of_agrees"], "true")
        self.assertEqual(row["review_status"], "")
        self.assertEqual(row["review_notes"], "")

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
