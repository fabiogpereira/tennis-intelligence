import unittest
from collections import Counter

from research.experiments.context_serve_stability import ContextualServeRecord
from research.experiments.serve_shrinkage import (
    DIRECTIONS,
    TARGETS,
    _leave_player_prior,
    _observations,
    _paired_bootstrap,
    build_history,
    fold_partitions,
    score_records,
)


def record(
    player: str,
    year: int,
    match_number: int,
    first_in: int = 5,
    opponent_rank: int | None = 20,
) -> ContextualServeRecord:
    metrics = Counter(
        first_in=first_in,
        aces=1,
        dfs=1,
        resolved_first_serve_status=10,
        resolved_ace_status=10,
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
        opponent="Opponent",
        surface="Hard",
        tournament="Test",
        round_name="R1",
        chart_author="Ann",
        player_rank=10,
        opponent_rank=opponent_rank,
        context_player_id=f"atp:{player}",
        context_match_id=f"context-{year}-{match_number}-{player}",
    )


class ServeShrinkageExperimentTests(unittest.TestCase):
    def test_direction_requires_both_court_sides(self) -> None:
        source = record("Alice", 2020, 1)
        source.metrics["direction:1:ad:wide"] = 0
        source.metrics["direction:1:ad:middle"] = 0
        source.metrics["direction:1:ad:t"] = 0
        self.assertEqual(_observations(source, TARGETS[3]), [])

    def test_context_prior_removes_target_player_contribution(self) -> None:
        alice = record("Alice", 2020, 1, first_in=10)
        bob = record("Bob", 2020, 2, first_in=0)
        history = build_history([alice, bob], TARGETS[0])
        prior = _leave_player_prior(alice, "", history, "exact")
        self.assertAlmostEqual(prior[0], 0.5 / 11)

    def test_direction_empty_history_fallback_has_three_categories(self) -> None:
        history = build_history([], TARGETS[3])
        prior = _leave_player_prior(
            record("Alice", 2020, 1), "deuce", history, "exact"
        )
        self.assertEqual(prior, (1 / 3,) * 3)

    def test_fold_partitions_exclude_validation_and_test_from_selection_history(self) -> None:
        records = [record("Alice", year, year) for year in range(2014, 2021)]
        training, validation, test, refit = fold_partitions(records, 2020)
        self.assertEqual(
            [item.date[:4] for item in training],
            [str(year) for year in range(2014, 2019)],
        )
        self.assertEqual([item.date[:4] for item in validation], ["2019"])
        self.assertEqual([item.date[:4] for item in test], ["2020"])
        self.assertEqual(
            [item.date[:4] for item in refit],
            [str(year) for year in range(2015, 2020)],
        )

    def test_all_binary_models_have_calibration_predictions(self) -> None:
        history_records = [
            record("Alice", 2018, 1, 8),
            record("Bob", 2018, 2, 4),
        ]
        history = build_history(history_records, TARGETS[0])
        rows = score_records(
            [record("Alice", 2019, 3, 7)],
            TARGETS[0],
            history,
            {("ATP", "alice", "hard")},
            25,
            2019,
        )
        self.assertEqual(
            set(rows[0].predictions),
            {"tour", "context", "raw_player", "shrunk_player"},
        )

    def test_paired_bootstrap_is_deterministic(self) -> None:
        history_records = [
            record("Alice", 2018, 1, 8),
            record("Bob", 2018, 2, 4),
        ]
        history = build_history(history_records, TARGETS[0])
        rows = score_records(
            [record("Alice", 2019, 3, 7)],
            TARGETS[0],
            history,
            {("ATP", "alice", "hard")},
            25,
            2019,
        )
        first = _paired_bootstrap(rows, "shrunk_player", "context", 7)
        second = _paired_bootstrap(rows, "shrunk_player", "context", 7)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
