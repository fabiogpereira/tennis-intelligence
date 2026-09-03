"""Field-level serve observations derived from raw MCP notation."""

from __future__ import annotations

from collections import Counter
from typing import Mapping

from pipelines.processing.mcp_notation import ParsedNotation, parse_notation


DIRECTION_NAMES = {"4": "wide", "5": "middle", "6": "t"}
NORMAL_SCORE_VALUES = {"0": 0, "15": 1, "30": 2, "40": 3, "AD": 4}


def court_side(point_score: str) -> str | None:
    """Return the serving court from a pre-point score, or ``None`` if unsafe."""

    parts = point_score.upper().split("-")
    if len(parts) != 2:
        return None
    if all(part in NORMAL_SCORE_VALUES for part in parts):
        points_played = sum(NORMAL_SCORE_VALUES[part] for part in parts)
    elif all(part.isdigit() for part in parts):
        points_played = sum(int(part) for part in parts)
    else:
        return None
    return "deuce" if points_played % 2 == 0 else "ad"


def _serve_in(parsed: ParsedNotation) -> bool | None:
    if parsed.serve_fault is not None:
        return False
    if parsed.outcome in {"ace", "unreturnable"} or parsed.shots:
        return True
    return None


def _terminal_serve(parsed: ParsedNotation) -> bool:
    """Whether the notation safely proves the serve was not an ace or fault."""

    return bool(parsed.shots) or parsed.outcome in {
        "ace",
        "unreturnable",
        "serve_fault",
    }


def serve_point_metrics(row: Mapping[str, str]) -> Counter[str]:
    """Return additive raw-notation metrics and explicit unresolved counters."""

    first = parse_notation(row.get("1st", ""), "1st")
    second_raw = row.get("2nd", "")
    second = parse_notation(second_raw, "2nd") if second_raw else None
    return serve_point_metrics_from_parsed(row, first, second)


def serve_point_metrics_from_parsed(
    row: Mapping[str, str],
    first: ParsedNotation,
    second: ParsedNotation | None,
) -> Counter[str]:
    """Build serve metrics from parser results already produced for the row."""

    metrics: Counter[str] = Counter()
    time_violation_second_serve = (
        first.exceptional == "first_serve_lost_time_violation" and second is not None
    )
    if first.exceptional is not None and not time_violation_second_serve:
        metrics["_excluded_exceptional_point"] += 1
        return metrics
    metrics["serve_pts"] += 1
    side = court_side(row.get("Pts", ""))
    first_in = False if time_violation_second_serve else _serve_in(first)

    if first_in is None:
        metrics["_unresolved_first_in"] += 1
    elif first_in:
        metrics["first_in"] += 1
        if first.serve_direction in DIRECTION_NAMES and side:
            metrics[f"direction:1:{side}:{DIRECTION_NAMES[first.serve_direction]}"] += 1
        else:
            metrics["_unresolved_direction"] += 1
            metrics["_unresolved_direction_1"] += 1
    elif second is None:
        metrics["_unresolved_second_in"] += 1
        metrics["_unresolved_ace"] += 1
        metrics["_unresolved_df"] += 1
        metrics["_unresolved_direction"] += 1
        metrics["_unresolved_direction_2"] += 1
        return metrics
    else:
        # The MCP Overview column named second_in empirically counts second-serve
        # attempts, including double faults. Keep the source name for comparison.
        metrics["second_in"] += 1
        if second.serve_direction in DIRECTION_NAMES and side:
            metrics[f"direction:2:{side}:{DIRECTION_NAMES[second.serve_direction]}"] += 1
        else:
            metrics["_unresolved_direction"] += 1
            metrics["_unresolved_direction_2"] += 1

    terminal = second if first_in is False and second is not None else first
    if terminal.outcome == "ace":
        metrics["aces"] += 1
    elif not _terminal_serve(terminal):
        metrics["_unresolved_ace"] += 1

    if first_in is False and second is not None:
        if second.serve_fault is not None:
            metrics["dfs"] += 1
        elif not _terminal_serve(second):
            metrics["_unresolved_df"] += 1
    elif first_in is None:
        metrics["_unresolved_df"] += 1

    return metrics
