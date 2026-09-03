import unittest

from pipelines.processing.mcp_serve import court_side, serve_point_metrics


class McpServeTests(unittest.TestCase):
    def row(self, first: str, second: str = "", score: str = "0-0") -> dict[str, str]:
        return {"1st": first, "2nd": second, "Pts": score}

    def test_court_side_supports_regular_and_tiebreak_scores(self) -> None:
        self.assertEqual(court_side("0-0"), "deuce")
        self.assertEqual(court_side("15-0"), "ad")
        self.assertEqual(court_side("40-40"), "deuce")
        self.assertEqual(court_side("AD-40"), "ad")
        self.assertEqual(court_side("40-0"), "ad")
        self.assertEqual(court_side("40-15"), "deuce")
        self.assertEqual(court_side("6-6"), "deuce")
        self.assertEqual(court_side("7-6"), "ad")
        self.assertIsNone(court_side("unknown"))

    def test_first_serve_direction_and_ace_are_additive(self) -> None:
        metrics = serve_point_metrics(self.row("4*", score="0-0"))
        self.assertEqual(metrics["serve_pts"], 1)
        self.assertEqual(metrics["first_in"], 1)
        self.assertEqual(metrics["aces"], 1)
        self.assertEqual(metrics["direction:1:deuce:wide"], 1)

    def test_second_serve_attempt_and_double_fault(self) -> None:
        metrics = serve_point_metrics(self.row("6n", "5w", "15-0"))
        self.assertEqual(metrics["second_in"], 1)
        self.assertEqual(metrics["dfs"], 1)
        self.assertEqual(metrics["direction:2:ad:middle"], 1)

    def test_partial_rally_keeps_first_serve_direction(self) -> None:
        metrics = serve_point_metrics(self.row("6b39f28*", score="30-30"))
        self.assertEqual(metrics["first_in"], 1)
        self.assertEqual(metrics["direction:1:deuce:t"], 1)
        self.assertEqual(metrics["_unresolved_ace"], 0)

    def test_unknown_serve_prefix_is_not_silently_classified(self) -> None:
        metrics = serve_point_metrics(self.row("n", score="bad"))
        self.assertEqual(metrics["serve_pts"], 1)
        self.assertEqual(metrics["_unresolved_first_in"], 1)
        self.assertEqual(metrics["_unresolved_ace"], 1)
        self.assertEqual(metrics["_unresolved_df"], 1)

    def test_exceptional_point_is_not_counted_as_an_observed_serve(self) -> None:
        metrics = serve_point_metrics(self.row("S"))
        self.assertEqual(metrics["serve_pts"], 0)
        self.assertEqual(metrics["_excluded_exceptional_point"], 1)

    def test_time_violation_preserves_observed_second_serve(self) -> None:
        metrics = serve_point_metrics(self.row("V", "4*", "30-30"))
        self.assertEqual(metrics["serve_pts"], 1)
        self.assertEqual(metrics["first_in"], 0)
        self.assertEqual(metrics["second_in"], 1)
        self.assertEqual(metrics["aces"], 1)
        self.assertEqual(metrics["direction:2:deuce:wide"], 1)


if __name__ == "__main__":
    unittest.main()
