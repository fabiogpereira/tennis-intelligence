import unittest
from collections import Counter
from dataclasses import replace
from datetime import date

from pipelines.processing.entity_resolution import ContextMatchIdentity
from research.experiments.context_serve_stability import (
    ContextualServeRecord,
    enrich_contextual_records,
    evaluate_context_family,
    parse_rank,
    rank_band,
    stratum_value,
)
from research.experiments.serve_stability import (
    MatchServeRecord,
    mean_absolute_distance,
    outcome_profile,
)


def context(
    match_id: str,
    player_id: str = "10",
    player_rank: str = "12",
) -> ContextMatchIdentity:
    return ContextMatchIdentity(
        canonical_match_id=f"sackmann:atp:tour:2020-1:{match_id[-1]}",
        tour="ATP",
        tournament_date=date(2020, 1, 1),
        tournament="Test",
        round_name="R1",
        surface="Hard",
        best_of="3",
        winner_name="Alice One",
        winner_id=player_id,
        winner_rank=player_rank,
        loser_name="Bea Two",
        loser_id="20",
        loser_rank="42",
        source_family="tour",
        source_file="atp/atp_matches_2020.csv",
    )


def serve_record(match_id: str) -> MatchServeRecord:
    return MatchServeRecord(
        tour="ATP",
        player="Alice One",
        match_id=match_id,
        date=f"2020010{match_id[-1]}",
        metrics=Counter(),
        opponent="Bea Two",
        surface="Hard",
        tournament="Test Event",
        round_name="R1",
        chart_author="Ann",
    )


def contextual_record(
    player: str, match_number: int, first_in: int
) -> ContextualServeRecord:
    metrics = Counter(
        first_in=first_in,
        aces=first_in,
        dfs=first_in,
        resolved_first_serve_status=10,
        resolved_ace_status=10,
        resolved_double_fault_status=10,
    )
    return ContextualServeRecord(
        tour="ATP",
        player=player,
        match_id=f"2020010{match_number}-{player}",
        date=f"2020010{match_number}",
        metrics=metrics,
        opponent="Opponent",
        surface="Hard",
        tournament="Test",
        round_name="R1",
        chart_author="Ann",
        player_rank=10,
        opponent_rank=50,
        context_player_id=f"sackmann:atp:{player}",
        context_match_id=f"context-{match_number}-{player}",
    )


class ContextServeStabilityTests(unittest.TestCase):
    def test_rank_parsing_and_fixed_bands(self) -> None:
        self.assertEqual(parse_rank("10.0"), 10)
        self.assertIsNone(parse_rank("10.5"))
        self.assertIsNone(parse_rank("NR"))
        self.assertEqual(rank_band(None), "missing")
        self.assertEqual(rank_band(10), "1-10")
        self.assertEqual(rank_band(11), "11-25")
        self.assertEqual(rank_band(201), "201+")

    def test_enrichment_maps_match_specific_ranks(self) -> None:
        source = serve_record("m1")
        records, profile = enrich_contextual_records([source], {"m1": context("m1")})
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].player_rank, 12)
        self.assertEqual(records[0].opponent_rank, 42)
        self.assertEqual(records[0].context_player_id, "sackmann:atp:10")
        self.assertEqual(profile["context_identity_mismatches"], 0)

    def test_enrichment_excludes_normalized_player_id_collisions(self) -> None:
        sources = [serve_record("m1"), serve_record("m2")]
        links = {
            "m1": context("m1", player_id="10"),
            "m2": context("m2", player_id="11"),
        }
        records, profile = enrich_contextual_records(sources, links)
        self.assertEqual(records, [])
        self.assertEqual(profile["normalized_player_id_collisions"], 1)
        self.assertEqual(profile["collision_match_player_records_excluded"], 2)

    def test_strata_are_predefined_and_missing_rank_is_explicit(self) -> None:
        record = contextual_record("Alice", 1, 5)
        record = replace(record, opponent_rank=None)
        self.assertEqual(stratum_value(record, "surface"), "hard")
        self.assertEqual(stratum_value(record, "era"), "2020s")
        self.assertEqual(stratum_value(record, "opponent_rank_band"), "missing")
        self.assertEqual(
            stratum_value(record, "joint_basic_context"), "hard|2020s|missing"
        )

    def test_evaluation_compares_players_only_inside_the_same_stratum(self) -> None:
        records = [
            contextual_record("Alice", 1, 0),
            contextual_record("Alice", 2, 0),
            contextual_record("Bea", 1, 10),
            contextual_record("Bea", 2, 10),
        ]
        result = evaluate_context_family(
            records,
            outcome_profile,
            mean_absolute_distance,
            "surface",
            minimum_matches_per_split=1,
            seed=1,
        )
        self.assertEqual(result["eligible_player_strata"], 2)
        self.assertEqual(result["between_player_comparisons"], 2)
        self.assertEqual(result["median_within_player_distance"], 0.0)
        self.assertEqual(result["within_to_between_ratio"], 0.0)


if __name__ == "__main__":
    unittest.main()
