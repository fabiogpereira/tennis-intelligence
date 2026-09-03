"""Deterministic tennis scoring state transitions."""

from __future__ import annotations

from dataclasses import dataclass


class InvalidPoint(ValueError):
    """Raised when a point cannot be applied to the current match state."""


@dataclass(frozen=True)
class MatchConfig:
    """Rules needed to score a standard singles match."""

    best_of: int = 3
    tiebreak_at_six_all: bool = True

    def __post_init__(self) -> None:
        if self.best_of not in (3, 5):
            raise ValueError("best_of must be 3 or 5")

    @property
    def sets_to_win(self) -> int:
        return self.best_of // 2 + 1


@dataclass(frozen=True)
class MatchState:
    """State immediately before the next point."""

    sets_won: tuple[int, int] = (0, 0)
    games_won: tuple[int, int] = (0, 0)
    points_won: tuple[int, int] = (0, 0)
    server: int = 0
    in_tiebreak: bool = False
    tiebreak_points: tuple[int, int] = (0, 0)
    tiebreak_first_server: int | None = None
    completed: bool = False

    def __post_init__(self) -> None:
        if self.server not in (0, 1):
            raise ValueError("server must be 0 or 1")
        if any(value < 0 for values in (self.sets_won, self.games_won, self.points_won, self.tiebreak_points) for value in values):
            raise ValueError("scores cannot be negative")
        if self.in_tiebreak and self.games_won != (6, 6):
            raise ValueError("a tiebreak must begin at 6-6")
        if self.in_tiebreak and self.tiebreak_first_server not in (0, 1):
            raise ValueError("a tiebreak must record its first server")
        if not self.in_tiebreak and self.tiebreak_first_server is not None:
            raise ValueError("tiebreak first server must be empty outside a tiebreak")
        if not self.in_tiebreak and self.tiebreak_points != (0, 0):
            raise ValueError("tiebreak points must be zero outside a tiebreak")


def _winner_index(winner: int) -> int:
    if winner not in (0, 1):
        raise InvalidPoint("winner must be player 0 or player 1")
    return winner


def _increment_pair(values: tuple[int, int], winner: int) -> tuple[int, int]:
    updated = list(values)
    updated[winner] += 1
    return tuple(updated)  # type: ignore[return-value]


def _has_set_won(games: tuple[int, int], winner: int) -> bool:
    other = 1 - winner
    return games[winner] >= 6 and games[winner] - games[other] >= 2


def advance_point(state: MatchState, winner: int, config: MatchConfig = MatchConfig()) -> MatchState:
    """Apply one point and return the state before the following point."""

    winner = _winner_index(winner)
    if state.completed:
        raise InvalidPoint("cannot apply a point after match completion")

    if state.in_tiebreak:
        tiebreak_points = _increment_pair(state.tiebreak_points, winner)
        leader = tiebreak_points[winner]
        margin = leader - tiebreak_points[1 - winner]
        total_points = sum(tiebreak_points)
        next_server = state.server
        if total_points == 1 or (total_points >= 3 and total_points % 2 == 1):
            next_server = 1 - state.server
        if leader < 7 or margin < 2:
            return MatchState(
                sets_won=state.sets_won,
                games_won=state.games_won,
                server=next_server,
                in_tiebreak=True,
                tiebreak_points=tiebreak_points,
                tiebreak_first_server=state.tiebreak_first_server,
            )

        return _finish_set(
            state,
            winner,
            config,
            next_server=1 - state.tiebreak_first_server,
        )

    points_won = _increment_pair(state.points_won, winner)
    winner_points = points_won[winner]
    other_points = points_won[1 - winner]
    if winner_points < 4 or winner_points - other_points < 2:
        return MatchState(
            sets_won=state.sets_won,
            games_won=state.games_won,
            points_won=points_won,
            server=state.server,
        )

    games_won = _increment_pair(state.games_won, winner)
    next_server = 1 - state.server
    if config.tiebreak_at_six_all and games_won == (6, 6):
        return MatchState(
            sets_won=state.sets_won,
            games_won=games_won,
            server=next_server,
            in_tiebreak=True,
            tiebreak_first_server=next_server,
        )
    if not _has_set_won(games_won, winner):
        return MatchState(
            sets_won=state.sets_won,
            games_won=games_won,
            server=next_server,
        )

    return _finish_set(state, winner, config, games_won=games_won, next_server=next_server)


def _finish_set(
    state: MatchState,
    winner: int,
    config: MatchConfig,
    *,
    games_won: tuple[int, int] | None = None,
    next_server: int,
) -> MatchState:
    sets_won = _increment_pair(state.sets_won, winner)
    completed = sets_won[winner] >= config.sets_to_win
    final_games = games_won
    if final_games is None and state.in_tiebreak:
        final_games = _increment_pair(state.games_won, winner)
    if final_games is None:
        final_games = state.games_won
    return MatchState(
        sets_won=sets_won,
        games_won=(0, 0) if not completed else final_games,
        server=next_server,
        completed=completed,
    )


def conventional_point_score(state: MatchState) -> str:
    """Return the familiar point score for a non-tiebreak game."""

    points = state.tiebreak_points if state.in_tiebreak else state.points_won
    return _format_point_score(points, state.in_tiebreak)


def server_point_score(state: MatchState) -> str:
    """Return the MCP-style score with the server listed first."""

    points = state.tiebreak_points if state.in_tiebreak else state.points_won
    ordered_points = (points[state.server], points[1 - state.server])
    return _format_point_score(ordered_points, state.in_tiebreak)

def _format_point_score(points: tuple[int, int], tiebreak: bool = False) -> str:
    """Format points in the supplied player order."""

    if tiebreak:
        return f"{points[0]}-{points[1]}"
    labels = ("0", "15", "30", "40")
    first, second = points
    if first >= 3 and second >= 3:
        if first == second:
            return "40-40"
        if first > second:
            return "AD-40"
        return "40-AD"
    return f"{labels[min(first, 3)]}-{labels[min(second, 3)]}"
