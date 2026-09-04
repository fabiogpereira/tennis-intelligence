import json
import unittest
from collections import Counter
from dataclasses import replace

from research.experiments.context_serve_stability import ContextualServeRecord
from research.experiments.serve_publication_readiness import (
    diagnose_history,
    histories_for_window,
    run_audit,
    summarize,
)
from research.experiments.serve_shrinkage import DIRECTIONS, TARGETS


def record(
    player: str,
    year: int,
    match_number: int,
    first_in: int = 5,
    trials: int = 10,
) -> ContextualServeRecord:
    metrics = Counter(
        first_in=first_in,
        aces=1,
        dfs=1,
        resolved_first_serve_status=trials,
        resolved_ace_status=trials,
        resolved_double_fault_status=5,
    )
    for serve_number in ("1", "2"):
        for side in ("deuce", "ad"):
            for direction, count in zip(DIRECTIONS, (3, 2, 1)):
                metrics[f"direction:{serve_number}:{side}:{direction}"] = count
    return ContextualServeRecord(
        tour="ATP",
        player=player,
        match_id=f"{year}-{match_number}-{player}",
        date=f"{year}0101",
        metrics=metrics,
        opponent=f"Opponent {match_number}",
        surface="Hard",
        tournament=f"Tournament {match_number}",
        round_name="R1",
        chart_author="Ann",
        player_rank=10,
        opponent_rank=20,
        context_player_id=f"atp:{player}",
        context_match_id=f"context-{year}-{match_number}-{player}",
    )


class ServePublicationReadinessTests(unittest.TestCase):
    def test_window_uses_only_five_years_before_as_of_year(self) -> None:
        records = [
            record("Alice", 2014, 1),
            record("Alice", 2015, 2),
            record("Alice", 2019, 3),
            record("Alice", 2020, 4),
        ]
        histories = histories_for_window(records, TARGETS[0], 2020)
        self.assertEqual(set(histories[0].matches), {"2015-2-Alice", "2019-3-Alice"})

    def test_equal_match_exposure_has_full_effective_match_count(self) -> None:
        records = [record("Alice", 2018, 1), record("Alice", 2019, 2)]
        history = histories_for_window(records, TARGETS[0], 2020)[0]
        diagnostic = diagnose_history(history)
        self.assertEqual(diagnostic.matches, 2)
        self.assertAlmostEqual(diagnostic.effective_matches, 2)
        self.assertAlmostEqual(diagnostic.largest_match_share, 0.5)

    def test_cluster_uncertainty_detects_between_match_variation(self) -> None:
        records = [
            record("Alice", 2018, 1, first_in=10),
            record("Alice", 2019, 2, first_in=0),
        ]
        history = histories_for_window(records, TARGETS[0], 2020)[0]
        diagnostic = diagnose_history(history)
        self.assertGreater(diagnostic.cluster_standard_error, 0)
        self.assertGreater(diagnostic.cluster_to_conditional_sd_ratio, 1)

    def test_blank_diversity_values_are_not_counted(self) -> None:
        source = replace(
            record("Alice", 2019, 1),
            opponent="",
            tournament="",
            chart_author="",
        )
        diagnostic = diagnose_history(
            histories_for_window([source], TARGETS[0], 2020)[0]
        )
        self.assertEqual(diagnostic.opponents, 0)
        self.assertEqual(diagnostic.tournaments, 0)
        self.assertEqual(diagnostic.chart_authors, 0)

    def test_summary_and_json_do_not_expose_player_identity(self) -> None:
        records = [record("Alice", 2018, 1), record("Alice", 2019, 2)]
        history = histories_for_window(records, TARGETS[0], 2020)[0]
        output = summarize([diagnose_history(history)])
        serialized = json.dumps(output)
        self.assertNotIn("Alice", serialized)
        self.assertNotIn("alice", serialized)
        self.assertEqual(output["distinct_players"], 1)
        self.assertEqual(
            output["uncertainty_by_minimum_matches"]["2"]["history_instances"],
            1,
        )
        self.assertEqual(
            output["uncertainty_by_minimum_matches"]["5"]["history_instances"],
            0,
        )

    def test_audit_does_not_treat_latest_observed_season_as_complete(self) -> None:
        records = [record("Alice", year, year) for year in range(2014, 2021)]
        result = run_audit(records, {"fixture": True})
        self.assertEqual(result["as_of_years"], [2019, 2020])


if __name__ == "__main__":
    unittest.main()
