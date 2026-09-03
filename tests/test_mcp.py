import csv
import tempfile
import unittest
from pathlib import Path

from models.scoring import MatchState
from pipelines.processing.mcp import (
    InvalidMcpRow,
    normalize_mcp_rows,
    parse_mcp_row,
    read_mcp_points,
    reconstruct_match,
)


class McpAdapterTests(unittest.TestCase):
    def test_parse_converts_source_player_numbers_to_zero_based(self) -> None:
        point = parse_mcp_row(
            {
                "match_id": "fixture",
                "Pt": "1",
                "Set1": "0",
                "Set2": "0",
                "Gm1": "0",
                "Gm2": "0",
                "Pts": "0-0",
                "Svr": "1",
                "PtWinner": "2",
            }
        )
        self.assertEqual(point.server, 0)
        self.assertEqual(point.winner, 1)

    def test_reconstructs_a_match_from_fixture_csv(self) -> None:
        rows = []
        point_number = 1
        sets_won = (0, 0)
        games_won = (0, 0)
        points = (0, 0)
        point_scores = ("0-0", "15-0", "30-0", "40-0")
        for _ in range(4):
            rows.append(["fixture", point_number, *sets_won, *games_won, point_scores[point_number - 1], 1, 1])
            point_number += 1
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "points.csv"
            with path.open("w", newline="") as output:
                writer = csv.writer(output)
                writer.writerow(["match_id", "Pt", "Set1", "Set2", "Gm1", "Gm2", "Pts", "Svr", "PtWinner"])
                writer.writerows(rows)
            state = reconstruct_match(list(read_mcp_points(path)))
        self.assertEqual(state, MatchState(games_won=(1, 0), server=1))

    def test_rejects_a_gap_in_point_numbers(self) -> None:
        rows = [
            {"match_id": "fixture", "Pt": "1", "Set1": "0", "Set2": "0", "Gm1": "0", "Gm2": "0", "Pts": "0-0", "Svr": "1", "PtWinner": "1"},
            {"match_id": "fixture", "Pt": "3", "Set1": "0", "Set2": "0", "Gm1": "0", "Gm2": "0", "Pts": "15-0", "Svr": "1", "PtWinner": "1"},
        ]
        with self.assertRaises(InvalidMcpRow):
            reconstruct_match(parse_mcp_row(row) for row in rows)

    def test_collapses_exact_duplicate_rows(self) -> None:
        row = {"match_id": "fixture", "Pt": "1", "PtWinner": "1"}
        self.assertEqual(list(normalize_mcp_rows([row, dict(row)])), [row])

    def test_rejects_conflicting_duplicate_annotations(self) -> None:
        first = {"match_id": "fixture", "Pt": "1", "1st": "ace"}
        second = {"match_id": "fixture", "Pt": "1", "1st": "error"}
        with self.assertRaises(InvalidMcpRow):
            list(normalize_mcp_rows([first, second]))

    def test_can_exclude_conflicting_duplicate_annotations(self) -> None:
        first = {"match_id": "fixture", "Pt": "1", "1st": "ace"}
        second = {"match_id": "fixture", "Pt": "1", "1st": "error"}
        self.assertEqual(list(normalize_mcp_rows([first, second], reject_conflicts=False)), [])

    def test_reader_rejects_conflicts_by_default(self) -> None:
        rows = [
            {"match_id": "fixture", "Pt": "1", "Set1": "0", "Set2": "0", "Gm1": "0", "Gm2": "0", "Pts": "0-0", "Svr": "1", "PtWinner": "1", "1st": "ace"},
            {"match_id": "fixture", "Pt": "1", "Set1": "0", "Set2": "0", "Gm1": "0", "Gm2": "0", "Pts": "0-0", "Svr": "1", "PtWinner": "1", "1st": "error"},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "points.csv"
            with path.open("w", newline="") as output:
                writer = csv.DictWriter(output, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaises(InvalidMcpRow):
                list(read_mcp_points(path))


if __name__ == "__main__":
    unittest.main()
