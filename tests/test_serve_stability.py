import unittest
from collections import Counter

from research.experiments.serve_stability import (
    MatchServeRecord,
    conditional_direction_distance,
    direction_profile,
    mean_absolute_distance,
    outcome_profile,
    split_records,
)


def record(match_id: str, **metrics: int) -> MatchServeRecord:
    return MatchServeRecord("ATP", "Alice", match_id, match_id[:8], Counter(metrics))


class ServeStabilityTests(unittest.TestCase):
    def test_outcome_profile_uses_field_specific_denominators(self) -> None:
        profile = outcome_profile(
            [
                record(
                    "20200101-a",
                    first_in=6,
                    aces=1,
                    dfs=2,
                    resolved_first_serve_status=10,
                    resolved_ace_status=8,
                    resolved_double_fault_status=4,
                )
            ]
        )
        self.assertEqual(profile, (0.6, 0.125, 0.5))

    def test_direction_profile_normalizes_each_side(self) -> None:
        metrics = {
            "direction:1:deuce:wide": 2,
            "direction:1:deuce:middle": 1,
            "direction:1:deuce:t": 1,
            "direction:1:ad:wide": 1,
            "direction:1:ad:middle": 1,
            "direction:1:ad:t": 2,
        }
        self.assertEqual(
            direction_profile([record("20200101-a", **metrics)], "1"),
            (0.5, 0.25, 0.25, 0.25, 0.25, 0.5),
        )

    def test_distances_have_expected_scale(self) -> None:
        self.assertEqual(mean_absolute_distance((0.0, 0.5), (1.0, 0.5)), 0.5)
        self.assertEqual(
            conditional_direction_distance(
                (1.0, 0.0, 0.0, 0.0, 1.0, 0.0),
                (0.0, 1.0, 0.0, 0.0, 1.0, 0.0),
            ),
            0.5,
        )

    def test_split_strategies_are_deterministic_and_disjoint(self) -> None:
        records = [record(f"2020010{day}-m") for day in range(1, 7)]
        chronological = split_records(records, "chronological")
        alternating = split_records(records, "alternating")
        self.assertEqual(
            [row.match_id for row in chronological[0]],
            [row.match_id for row in records[:3]],
        )
        self.assertEqual(
            [row.match_id for row in alternating[0]],
            [row.match_id for row in records[::2]],
        )
        left_ids = {row.match_id for row in chronological[0]}
        right_ids = {row.match_id for row in chronological[1]}
        self.assertFalse(left_ids.intersection(right_ids))


if __name__ == "__main__":
    unittest.main()
