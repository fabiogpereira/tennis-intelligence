import unittest
from datetime import date

from pipelines.processing.entity_resolution import (
    ContextMatchIdentity,
    McpMatchIdentity,
    canonical_context_match_id,
    canonical_context_player_id,
    canonical_pair,
    index_context_matches,
    normalize_identity,
    resolve_mcp_match,
)


def context_match(
    tournament_date: date,
    tournament: str = "Roland Garros",
    round_name: str = "R128",
    match_number: str = "1",
) -> ContextMatchIdentity:
    return ContextMatchIdentity(
        canonical_match_id=f"sackmann:atp:2026-1:{match_number}",
        tour="ATP",
        tournament_date=tournament_date,
        tournament=tournament,
        round_name=round_name,
        surface="Clay",
        best_of="5",
        winner_name="Joao Fonseca",
        winner_id="123",
        winner_rank="50",
        loser_name="Novak Djokovic",
        loser_id="456",
        loser_rank="2",
        source_family="tour",
        source_file="atp_matches_2026.csv",
    )


def mcp_match() -> McpMatchIdentity:
    return McpMatchIdentity(
        match_id="m1",
        tour="ATP",
        match_date=date(2026, 5, 25),
        tournament="Roland_Garros",
        round_name="R128",
        surface="Clay",
        best_of="5",
        player_1="Joao Fonseca",
        player_2="Novak Djokovic",
    )


class EntityResolutionTests(unittest.TestCase):
    def test_normalization_is_exact_but_case_diacritic_and_separator_insensitive(self) -> None:
        self.assertEqual(normalize_identity(" João_Fonseca "), "joao fonseca")
        self.assertEqual(canonical_pair("B", "A"), ("a", "b"))

    def test_canonical_ids_preserve_source_namespace(self) -> None:
        self.assertEqual(
            canonical_context_match_id("ATP", "tour", "2026-520", "300"),
            "sackmann:atp:tour:2026-520:300",
        )
        self.assertEqual(canonical_context_player_id("WTA", "123"), "sackmann:wta:123")

    def test_unique_pair_in_date_window_matches(self) -> None:
        candidate = context_match(date(2026, 5, 24))
        result = resolve_mcp_match(mcp_match(), index_context_matches([candidate]))
        self.assertEqual(result.status, "matched")
        self.assertEqual(result.method, "exact_pair_date_unique")
        self.assertEqual(result.context_match, candidate)

    def test_candidate_outside_date_window_is_not_guessed(self) -> None:
        candidate = context_match(date(2026, 4, 1))
        result = resolve_mcp_match(mcp_match(), index_context_matches([candidate]))
        self.assertEqual(result.status, "unresolved_date_window")
        self.assertEqual(
            result.candidate_match_ids, (candidate.canonical_match_id,)
        )

    def test_unique_pair_without_supporting_context_is_rejected(self) -> None:
        candidate = context_match(
            date(2026, 5, 24),
            tournament="Other Event",
            round_name="Q1",
        )
        result = resolve_mcp_match(mcp_match(), index_context_matches([candidate]))
        self.assertEqual(result.status, "conflicting_context")

    def test_missing_exact_pair_has_distinct_status(self) -> None:
        result = resolve_mcp_match(mcp_match(), index_context_matches([]))
        self.assertEqual(result.status, "unresolved_pair")

    def test_tournament_and_round_can_disambiguate_two_nearby_candidates(self) -> None:
        candidates = [
            context_match(date(2026, 5, 24), match_number="1"),
            context_match(
                date(2026, 5, 20),
                tournament="Other Event",
                round_name="Q1",
                match_number="2",
            ),
        ]
        result = resolve_mcp_match(mcp_match(), index_context_matches(candidates))
        self.assertEqual(result.status, "matched")
        self.assertEqual(result.method, "exact_pair_date_tournament_round_unique")

    def test_multiple_candidates_remain_ambiguous(self) -> None:
        candidates = [
            context_match(date(2026, 5, 24), match_number="1"),
            context_match(date(2026, 5, 20), match_number="2"),
        ]
        result = resolve_mcp_match(mcp_match(), index_context_matches(candidates))
        self.assertEqual(result.status, "ambiguous")
        self.assertEqual(result.candidate_count, 2)
        self.assertEqual(
            result.candidate_match_ids,
            tuple(candidate.canonical_match_id for candidate in candidates),
        )


if __name__ == "__main__":
    unittest.main()
