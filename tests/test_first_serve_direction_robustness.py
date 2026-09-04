import json
import unittest
from collections import Counter

from research.experiments.context_serve_stability import ContextualServeRecord
from research.experiments.first_serve_direction_robustness import (
    audit_court_side_records,
    build_histories,
    component_estimates,
    score_histories,
    summarize,
)


def record(
    player: str,
    year: int,
    match_number: int,
    deuce: tuple[int, int, int] = (3, 2, 1),
    ad: tuple[int, int, int] = (1, 2, 3),
) -> ContextualServeRecord:
    metrics = Counter()
    for side, counts in (("deuce", deuce), ("ad", ad)):
        for direction, count in zip(("wide", "middle", "t"), counts):
            metrics[f"direction:1:{side}:{direction}"] = count
    return ContextualServeRecord(
        tour="ATP",
        player=player,
        match_id=f"{year}-{match_number}-{player}",
        date=f"{year}0101",
        metrics=metrics,
        opponent=f"Opponent {match_number}",
        surface="Hard",
        tournament="Test",
        round_name="R1",
        chart_author="Ann",
        player_rank=10,
        opponent_rank=20,
        context_player_id=f"atp:{player}",
        context_match_id=f"context-{year}-{match_number}-{player}",
    )


class FirstServeDirectionRobustnessTests(unittest.TestCase):
    def test_court_side_audit_keeps_one_side_visible(self) -> None:
        records = [
            record("Alice", 2019, 1),
            record("Bob", 2019, 2, ad=(0, 0, 0)),
            record("Carol", 2019, 3, deuce=(0, 0, 0), ad=(0, 0, 0)),
        ]
        result = audit_court_side_records(records)["overall"]
        self.assertEqual(result["both_sides"], 1)
        self.assertEqual(result["one_side"], 1)
        self.assertEqual(result["no_direction"], 1)
        self.assertEqual(result["both_given_any_rate"], 0.5)

    def test_period_history_excludes_boundaries_and_one_side_records(self) -> None:
        records = [
            record("Alice", 2017, 1),
            record("Alice", 2018, 2),
            record("Alice", 2019, 3, ad=(0, 0, 0)),
            record("Alice", 2020, 4),
        ]
        history = next(iter(build_histories(records, 2018, 2020).values()))
        self.assertEqual(set(history.matches), {"2018-2-Alice"})

    def test_component_estimates_require_two_matches(self) -> None:
        history = next(
            iter(build_histories([record("Alice", 2019, 1)], 2019, 2020).values())
        )
        with self.assertRaises(ValueError):
            component_estimates(history)

    def test_identical_history_and_test_are_covered(self) -> None:
        history_records = [record("Alice", 2018, 1), record("Alice", 2019, 2)]
        test_records = [record("Alice", 2020, 3), record("Alice", 2020, 4)]
        history = next(iter(build_histories(history_records, 2018, 2020).values()))
        test = next(iter(build_histories(test_records, 2020, 2021).values()))
        row = score_histories(history, test, 2020)
        self.assertEqual(row.errors, (0.0,) * 6)
        self.assertTrue(all(row.conditional_covered))
        self.assertTrue(all(row.clustered_covered))
        self.assertAlmostEqual(row.smaller_side_share, 0.5)

    def test_aggregate_summary_does_not_expose_identity(self) -> None:
        history_records = [record("Alice", 2018, 1), record("Alice", 2019, 2)]
        test_records = [record("Alice", 2020, 3), record("Alice", 2020, 4)]
        history = next(iter(build_histories(history_records, 2018, 2020).values()))
        test = next(iter(build_histories(test_records, 2020, 2021).values()))
        serialized = json.dumps(summarize([score_histories(history, test, 2020)]))
        self.assertNotIn("Alice", serialized)
        self.assertNotIn("alice", serialized)


if __name__ == "__main__":
    unittest.main()
