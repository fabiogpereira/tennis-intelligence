"""Adapter for the Match Charting Project point CSV format."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import Iterable, Iterator, Mapping

from models.scoring import (
    InvalidPoint,
    MatchConfig,
    MatchState,
    advance_point,
    server_point_score,
)


REQUIRED_COLUMNS = frozenset({"match_id", "Pt", "Set1", "Set2", "Gm1", "Gm2", "Pts", "Svr", "PtWinner"})


class InvalidMcpRow(ValueError):
    """Raised when an MCP row cannot be interpreted safely."""


def normalize_mcp_rows(
    rows: Iterable[Mapping[str, str]],
    *,
    reject_conflicts: bool = True,
) -> Iterator[Mapping[str, str]]:
    """Collapse exact duplicates and handle conflicting annotations explicitly."""

    grouped: dict[tuple[str, str], list[Mapping[str, str]]] = {}
    order: list[tuple[str, str]] = []
    for row in rows:
        key = (row.get("match_id", ""), row.get("Pt", ""))
        if key not in grouped:
            grouped[key] = []
            order.append(key)
        grouped[key].append(row)

    for key in order:
        records = grouped[key]
        signatures = {tuple(sorted(record.items())) for record in records}
        if len(signatures) > 1:
            if reject_conflicts:
                raise InvalidMcpRow(
                    f"conflicting duplicate annotations for {key[0]} point {key[1]}"
                )
            continue
        yield records[0]


@dataclass(frozen=True)
class McpPoint:
    match_id: str
    point_number: int
    sets_won: tuple[int, int]
    games_won: tuple[int, int]
    point_score: str
    server: int
    winner: int


def parse_mcp_row(row: Mapping[str, str]) -> McpPoint:
    missing = REQUIRED_COLUMNS.difference(row)
    if missing:
        raise InvalidMcpRow(f"missing MCP columns: {sorted(missing)}")
    try:
        match_id = row["match_id"]
        point_number = int(row["Pt"])
        sets_won = (int(row["Set1"]), int(row["Set2"]))
        games_won = (int(row["Gm1"]), int(row["Gm2"]))
        server = int(row["Svr"]) - 1
        winner = int(row["PtWinner"]) - 1
    except (TypeError, ValueError) as error:
        raise InvalidMcpRow(f"invalid numeric MCP field: {error}") from error
    if not match_id or point_number < 1 or server not in (0, 1) or winner not in (0, 1):
        raise InvalidMcpRow("MCP row contains an invalid identity, point, server, or winner")
    return McpPoint(match_id, point_number, sets_won, games_won, row["Pts"], server, winner)


def read_mcp_points(
    path: Path,
    *,
    reject_conflicts: bool = True,
) -> Iterator[McpPoint]:
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None:
            raise InvalidMcpRow("MCP file has no header")
        if missing := REQUIRED_COLUMNS.difference(reader.fieldnames):
            raise InvalidMcpRow(f"missing MCP columns: {sorted(missing)}")
        for row in normalize_mcp_rows(reader, reject_conflicts=reject_conflicts):
            yield parse_mcp_row(row)


def reconstruct_match(
    points: Iterable[McpPoint],
    config: MatchConfig = MatchConfig(),
) -> MatchState:
    """Reconstruct one match, rejecting gaps and source-state mismatches."""

    iterator = iter(points)
    try:
        first = next(iterator)
    except StopIteration as error:
        raise InvalidMcpRow("cannot reconstruct an empty match") from error

    state = MatchState(server=first.server)
    expected_point = first.point_number
    match_id = first.match_id
    for point in chain((first,), iterator):
        if point.match_id != match_id:
            raise InvalidMcpRow("multiple match IDs supplied to reconstruct_match")
        if point.point_number != expected_point:
            raise InvalidMcpRow(f"expected point {expected_point}, got {point.point_number}")
        if point.sets_won != state.sets_won or point.games_won != state.games_won:
            raise InvalidMcpRow(f"source score disagrees before point {point.point_number}")
        if point.server != state.server:
            raise InvalidMcpRow(f"source server disagrees before point {point.point_number}")
        if point.point_score != server_point_score(state):
            raise InvalidMcpRow(
                f"source point score disagrees before point {point.point_number}: "
                f"{point.point_score!r} != {server_point_score(state)!r}"
            )
        try:
            state = advance_point(state, point.winner, config)
        except InvalidPoint as error:
            raise InvalidMcpRow(f"invalid point {point.point_number}: {error}") from error
        expected_point += 1
    return state
