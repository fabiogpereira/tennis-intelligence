"""Adapter for Live Tennis API scoreboard-state data."""

from __future__ import annotations

import csv
import gzip
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Mapping


REQUIRED_COLUMNS = frozenset(
    {
        "match_id",
        "sets_p1",
        "sets_p2",
        "games_p1",
        "games_p2",
        "points_p1",
        "points_p2",
        "server",
        "is_tiebreak",
        "timestamp_utc",
    }
)
VALID_POINT_LABELS = frozenset({"0", "15", "30", "40", "A", "AD"})


class InvalidLiveTennisRow(ValueError):
    """Raised when a LiveTennisAPI state row cannot be interpreted safely."""


@dataclass(frozen=True)
class LiveTennisState:
    match_id: int
    sets_won: tuple[int, int]
    games_won_by_set: tuple[tuple[int, ...], tuple[int, ...]]
    points_won: tuple[str, str]
    server: int | None
    is_tiebreak: bool
    timestamp_utc: str

    @property
    def games_won(self) -> tuple[int, int]:
        """Return the current-set game score."""

        return tuple(
            games[-1] if games else 0 for games in self.games_won_by_set
        )  # type: ignore[return-value]


def _parse_games(value: str) -> tuple[int, ...]:
    try:
        games = json.loads(value)
    except json.JSONDecodeError as error:
        raise InvalidLiveTennisRow(f"invalid games JSON: {error}") from error
    if not isinstance(games, list) or any(not isinstance(game, int) for game in games):
        raise InvalidLiveTennisRow("games must be a JSON array of integers")
    if any(game < 0 for game in games):
        raise InvalidLiveTennisRow("games cannot be negative")
    return tuple(games)


def _parse_point(value: str, *, is_tiebreak: bool) -> str:
    if value == "":
        return ""
    if value in VALID_POINT_LABELS:
        return value
    if value.isdigit():
        return value
    if is_tiebreak:
        raise InvalidLiveTennisRow(f"invalid tiebreak point: {value!r}")
    if value not in VALID_POINT_LABELS:
        raise InvalidLiveTennisRow(f"invalid game point label: {value!r}")
    return value


def parse_live_state(row: Mapping[str, str]) -> LiveTennisState:
    missing = REQUIRED_COLUMNS.difference(row)
    if missing:
        raise InvalidLiveTennisRow(f"missing LiveTennisAPI columns: {sorted(missing)}")
    try:
        match_id = int(row["match_id"])
        sets_won = (int(row["sets_p1"]), int(row["sets_p2"]))
        games = (_parse_games(row["games_p1"]), _parse_games(row["games_p2"]))
        is_tiebreak = row["is_tiebreak"].lower() == "true"
    except (TypeError, ValueError) as error:
        raise InvalidLiveTennisRow(f"invalid LiveTennisAPI field: {error}") from error
    if match_id < 0 or any(score < 0 for score in sets_won):
        raise InvalidLiveTennisRow("match ID and set scores must be non-negative")
    server_value = row["server"]
    if server_value == "":
        server = None
    elif server_value in ("1", "2"):
        server = int(server_value) - 1
    else:
        raise InvalidLiveTennisRow(f"invalid server value: {server_value!r}")
    points_won = (
        _parse_point(row["points_p1"], is_tiebreak=is_tiebreak),
        _parse_point(row["points_p2"], is_tiebreak=is_tiebreak),
    )
    return LiveTennisState(
        match_id=match_id,
        sets_won=sets_won,
        games_won_by_set=games,
        points_won=points_won,
        server=server,
        is_tiebreak=is_tiebreak,
        timestamp_utc=row["timestamp_utc"],
    )


def read_live_states(path: Path) -> Iterator[LiveTennisState]:
    with gzip.open(path, mode="rt", newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None:
            raise InvalidLiveTennisRow("LiveTennisAPI file has no header")
        for row in reader:
            yield parse_live_state(row)
