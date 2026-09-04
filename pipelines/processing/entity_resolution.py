"""Conservative canonical identity rules for tennis match sources."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from typing import Iterable, Mapping


DATE_WINDOW_BEFORE_DAYS = 7
DATE_WINDOW_AFTER_DAYS = 20


def normalize_identity(value: str) -> str:
    """Normalize a source label for exact comparison without fuzzy matching."""

    decomposed = unicodedata.normalize("NFKD", value)
    ascii_value = decomposed.encode("ascii", "ignore").decode("ascii")
    return " ".join(re.findall(r"[a-z0-9]+", ascii_value.casefold()))


def canonical_pair(player_1: str, player_2: str) -> tuple[str, str]:
    return tuple(sorted((normalize_identity(player_1), normalize_identity(player_2))))


def canonical_context_match_id(
    tour: str, source_family: str, tournament_id: str, match_number: str
) -> str:
    return (
        f"sackmann:{tour.casefold()}:{source_family}:"
        f"{tournament_id}:{match_number}"
    )


def canonical_context_player_id(tour: str, player_id: str) -> str:
    return f"sackmann:{tour.casefold()}:{player_id}"


@dataclass(frozen=True)
class McpMatchIdentity:
    match_id: str
    tour: str
    match_date: date
    tournament: str
    round_name: str
    surface: str
    best_of: str
    player_1: str
    player_2: str

    @property
    def pair(self) -> tuple[str, str]:
        return canonical_pair(self.player_1, self.player_2)


@dataclass(frozen=True)
class ContextMatchIdentity:
    canonical_match_id: str
    tour: str
    tournament_date: date
    tournament: str
    round_name: str
    surface: str
    best_of: str
    winner_name: str
    winner_id: str
    winner_rank: str
    loser_name: str
    loser_id: str
    loser_rank: str
    source_family: str
    source_file: str

    @property
    def pair(self) -> tuple[str, str]:
        return canonical_pair(self.winner_name, self.loser_name)


@dataclass(frozen=True)
class MatchResolution:
    status: str
    method: str | None
    candidate_count: int
    context_match: ContextMatchIdentity | None
    candidate_match_ids: tuple[str, ...] = ()


def index_context_matches(
    matches: Iterable[ContextMatchIdentity],
) -> dict[tuple[str, tuple[str, str]], list[ContextMatchIdentity]]:
    result: dict[tuple[str, tuple[str, str]], list[ContextMatchIdentity]] = {}
    for match in matches:
        result.setdefault((match.tour, match.pair), []).append(match)
    for values in result.values():
        values.sort(key=lambda row: (row.tournament_date, row.canonical_match_id))
    return result


def _has_supporting_context(
    match: McpMatchIdentity, candidate: ContextMatchIdentity
) -> bool:
    tournament_agrees = normalize_identity(match.tournament) == normalize_identity(
        candidate.tournament
    )
    secondary_fields_agree = (
        normalize_identity(match.round_name) == normalize_identity(candidate.round_name)
        and normalize_identity(match.surface) == normalize_identity(candidate.surface)
        and match.best_of == candidate.best_of
    )
    return tournament_agrees or secondary_fields_agree


def resolve_mcp_match(
    match: McpMatchIdentity,
    context_index: Mapping[
        tuple[str, tuple[str, str]], list[ContextMatchIdentity]
    ],
    days_before: int = DATE_WINDOW_BEFORE_DAYS,
    days_after: int = DATE_WINDOW_AFTER_DAYS,
) -> MatchResolution:
    """Resolve only exact normalized player pairs inside the documented date window."""

    pair_candidates = context_index.get((match.tour, match.pair), [])
    candidates = [
        candidate
        for candidate in pair_candidates
        if -days_before
        <= (match.match_date - candidate.tournament_date).days
        <= days_after
    ]
    if not pair_candidates:
        return MatchResolution("unresolved_pair", None, 0, None)
    if not candidates:
        return MatchResolution(
            "unresolved_date_window",
            None,
            0,
            None,
            tuple(
                sorted(candidate.canonical_match_id for candidate in pair_candidates)
            ),
        )
    if len(candidates) == 1:
        candidate = candidates[0]
        candidate_ids = (candidate.canonical_match_id,)
        if not _has_supporting_context(match, candidate):
            return MatchResolution(
                "conflicting_context",
                "exact_pair_date_unique",
                1,
                candidate,
                candidate_ids,
            )
        return MatchResolution(
            "matched", "exact_pair_date_unique", 1, candidate, candidate_ids
        )

    candidate_ids = tuple(
        sorted(candidate.canonical_match_id for candidate in candidates)
    )
    tournament = normalize_identity(match.tournament)
    tournament_round = [
        candidate
        for candidate in candidates
        if normalize_identity(candidate.tournament) == tournament
        and normalize_identity(candidate.round_name) == normalize_identity(match.round_name)
    ]
    if len(tournament_round) == 1:
        return MatchResolution(
            "matched",
            "exact_pair_date_tournament_round_unique",
            len(candidates),
            tournament_round[0],
            candidate_ids,
        )
    return MatchResolution("ambiguous", None, len(candidates), None, candidate_ids)
