import unittest

from pipelines.processing.livetennis import (
    InvalidLiveTennisRow,
    parse_live_state,
)


class LiveTennisAdapterTests(unittest.TestCase):
    def row(self, **updates: str) -> dict[str, str]:
        row = {
            "match_id": "8568",
            "sets_p1": "0",
            "sets_p2": "0",
            "games_p1": "[]",
            "games_p2": "[]",
            "points_p1": "0",
            "points_p2": "0",
            "server": "",
            "is_tiebreak": "False",
            "timestamp_utc": "2026-06-25 11:44:12.494452",
        }
        row.update(updates)
        return row

    def test_parses_empty_games_and_missing_server(self) -> None:
        state = parse_live_state(self.row())
        self.assertEqual(state.match_id, 8568)
        self.assertEqual(state.games_won, (0, 0))
        self.assertIsNone(state.server)

    def test_parses_server_and_player_state(self) -> None:
        state = parse_live_state(
            self.row(games_p1="[3, 4]", games_p2="[6, 5]", points_p1="30", points_p2="15", server="2")
        )
        self.assertEqual(state.games_won_by_set, ((3, 4), (6, 5)))
        self.assertEqual(state.points_won, ("30", "15"))
        self.assertEqual(state.server, 1)

    def test_parses_numeric_tiebreak_points(self) -> None:
        state = parse_live_state(
            self.row(games_p1="[6]", games_p2="[6]", points_p1="7", points_p2="5", server="1", is_tiebreak="True")
        )
        self.assertEqual(state.points_won, ("7", "5"))
        self.assertTrue(state.is_tiebreak)

    def test_preserves_advantage_labels_when_source_tiebreak_flag_is_inconsistent(self) -> None:
        state = parse_live_state(
            self.row(games_p1="[2, 3, 7]", games_p2="[6, 6, 6]", points_p1="40", points_p2="A", server="1", is_tiebreak="True")
        )
        self.assertEqual(state.points_won, ("40", "A"))

    def test_preserves_missing_point_labels(self) -> None:
        state = parse_live_state(self.row(points_p1="", points_p2=""))
        self.assertEqual(state.points_won, ("", ""))

    def test_preserves_numeric_labels_when_tiebreak_flag_lags(self) -> None:
        state = parse_live_state(
            self.row(games_p1="[6, 3, 0]", games_p2="[1, 6, 0]", points_p1="1", points_p2="0")
        )
        self.assertEqual(state.points_won, ("1", "0"))

    def test_rejects_invalid_non_tiebreak_point(self) -> None:
        with self.assertRaises(InvalidLiveTennisRow):
            parse_live_state(self.row(points_p1="invalid"))

    def test_rejects_invalid_games_json(self) -> None:
        with self.assertRaises(InvalidLiveTennisRow):
            parse_live_state(self.row(games_p1="not-json"))


if __name__ == "__main__":
    unittest.main()
