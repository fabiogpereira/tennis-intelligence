import unittest

from models.scoring import MatchConfig, MatchState, InvalidPoint, advance_point, conventional_point_score


class ScoringTests(unittest.TestCase):
    def test_game_progression_and_server_rotation(self) -> None:
        state = MatchState(server=0)
        for winner in (0, 0, 0):
            state = advance_point(state, winner)
        self.assertEqual(state.games_won, (0, 0))
        self.assertEqual(state.points_won, (3, 0))
        state = advance_point(state, 0)
        self.assertEqual(state.games_won, (1, 0))
        self.assertEqual(state.points_won, (0, 0))
        self.assertEqual(state.server, 1)

    def test_deuce_and_advantage_require_two_point_margin(self) -> None:
        state = MatchState()
        for winner in (0, 0, 0, 1, 1, 1):
            state = advance_point(state, winner)
        self.assertEqual(conventional_point_score(state), "40-40")
        state = advance_point(state, 0)
        self.assertEqual(conventional_point_score(state), "AD-40")
        state = advance_point(state, 1)
        self.assertEqual(conventional_point_score(state), "40-40")
        state = advance_point(state, 1)
        self.assertEqual(conventional_point_score(state), "40-AD")

    def test_set_and_match_completion_best_of_three(self) -> None:
        state = MatchState()
        for _ in range(24):
            state = advance_point(state, 0)
        self.assertEqual(state.sets_won, (1, 0))
        self.assertEqual(state.games_won, (0, 0))
        for _ in range(24):
            state = advance_point(state, 0)
        self.assertEqual(state.sets_won, (2, 0))
        self.assertTrue(state.completed)
        with self.assertRaises(InvalidPoint):
            advance_point(state, 0)

    def test_tiebreak_completes_at_seven_with_two_point_margin(self) -> None:
        state = MatchState(
            games_won=(6, 6), server=0, in_tiebreak=True, tiebreak_first_server=0
        )
        for _ in range(6):
            state = advance_point(state, 0)
        self.assertTrue(state.in_tiebreak)
        self.assertEqual(state.tiebreak_points, (6, 0))
        state = advance_point(state, 0)
        self.assertFalse(state.in_tiebreak)
        self.assertEqual(state.sets_won, (1, 0))
        self.assertEqual(state.games_won, (0, 0))
        self.assertEqual(state.server, 1)

    def test_invalid_winner_and_best_of(self) -> None:
        with self.assertRaises(InvalidPoint):
            advance_point(MatchState(), 2)
        with self.assertRaises(ValueError):
            MatchConfig(best_of=7)


if __name__ == "__main__":
    unittest.main()
