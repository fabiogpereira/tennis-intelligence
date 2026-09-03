"""Deterministic parser for Match Charting Project point notation.

The parser preserves missing optional attributes and rejects undocumented or
structurally ambiguous sequences. It does not calculate player features.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


CellColumn = Literal["1st", "2nd"]
PARSER_VERSION = "mcp-parser-v0.1-draft"
Outcome = Literal[
    "ace",
    "unreturnable",
    "winner",
    "forced_error",
    "unforced_error",
    "incorrect_challenge",
    "serve_fault",
    "incomplete",
]

SHOT_TYPES = frozenset("fbrsvzopuy lmhijktq".replace(" ", ""))
SHOT_MODIFIERS = frozenset("+-=;^")
SHOT_DIRECTIONS = frozenset("0123")
RETURN_DEPTHS = frozenset("0789")
SERVE_DIRECTIONS = frozenset("0456")
SERVE_FAULTS = frozenset("nwdxge!")
ERROR_DETAILS = frozenset("nwdxe!")
EXCEPTIONAL_POINTS = {
    "S": "server_awarded_unobserved",
    "R": "returner_awarded_unobserved",
    "P": "penalty_against_server",
    "Q": "penalty_against_returner",
    "V": "first_serve_lost_time_violation",
}


@dataclass(frozen=True)
class ParseIssue:
    code: str
    position: int
    message: str


@dataclass(frozen=True)
class McpShot:
    shot_type: str
    direction: str | None
    return_depth: str | None
    modifiers: tuple[str, ...]
    error_detail: str | None
    ending: str | None


@dataclass(frozen=True)
class ParsedNotation:
    raw: str
    column: CellColumn
    let_count: int
    serve_direction: str | None
    serve_and_volley: bool
    serve_fault: str | None
    shots: tuple[McpShot, ...]
    outcome: Outcome | None
    exceptional: str | None
    issues: tuple[ParseIssue, ...]

    @property
    def valid(self) -> bool:
        return not self.issues


def _invalid(raw: str, column: CellColumn, position: int, code: str, message: str) -> ParsedNotation:
    return ParsedNotation(
        raw=raw,
        column=column,
        let_count=0,
        serve_direction=None,
        serve_and_volley=False,
        serve_fault=None,
        shots=(),
        outcome=None,
        exceptional=None,
        issues=(ParseIssue(code, position, message),),
    )


def parse_notation(raw: str, column: CellColumn) -> ParsedNotation:
    """Parse one non-empty MCP first- or second-serve cell.

    Optional direction/depth remains ``None``. The function never strips or
    repairs input because whitespace and undocumented characters are source
    quality findings.
    """

    if not raw:
        return _invalid(raw, column, 0, "empty_cell", "notation cell is empty")
    if raw in EXCEPTIONAL_POINTS:
        return ParsedNotation(
            raw, column, 0, None, False, None, (), None, EXCEPTIONAL_POINTS[raw], ()
        )

    index = 0
    while index < len(raw) and raw[index] == "c":
        index += 1
    let_count = index
    if index >= len(raw) or raw[index] not in SERVE_DIRECTIONS:
        character = raw[index] if index < len(raw) else "end of cell"
        return _invalid(
            raw,
            column,
            index,
            "expected_serve_direction",
            f"expected serve direction 0/4/5/6, found {character!r}",
        )

    serve_direction = raw[index]
    index += 1
    serve_and_volley = index < len(raw) and raw[index] == "+"
    if serve_and_volley:
        index += 1

    if index < len(raw) and raw[index] in SERVE_FAULTS:
        fault = raw[index]
        index += 1
        if index != len(raw):
            return _invalid(
                raw,
                column,
                index,
                "trailing_after_serve_fault",
                "serve fault must end the cell",
            )
        return ParsedNotation(
            raw, column, let_count, serve_direction, serve_and_volley, fault, (), "serve_fault", None, ()
        )

    if index < len(raw) and raw[index] in "*#":
        marker = raw[index]
        index += 1
        if index != len(raw):
            return _invalid(raw, column, index, "trailing_after_serve_outcome", "serve outcome must end the cell")
        outcome: Outcome = "ace" if marker == "*" else "unreturnable"
        return ParsedNotation(
            raw, column, let_count, serve_direction, serve_and_volley, None, (), outcome, None, ()
        )

    shots: list[McpShot] = []
    outcome: Outcome | None = None
    while index < len(raw):
        shot_start = index
        if raw[index] not in SHOT_TYPES:
            return _invalid(
                raw,
                column,
                index,
                "expected_shot_type",
                f"expected rally shot type, found {raw[index]!r}",
            )
        shot_type = raw[index]
        index += 1

        modifiers: list[str] = []
        while index < len(raw) and raw[index] in SHOT_MODIFIERS:
            modifier = raw[index]
            if modifier in modifiers:
                return _invalid(raw, column, index, "duplicate_modifier", f"duplicate modifier {modifier!r}")
            modifiers.append(modifier)
            index += 1

        direction: str | None = None
        if index < len(raw) and raw[index] in SHOT_DIRECTIONS:
            direction = raw[index]
            index += 1

        return_depth: str | None = None
        if not shots and index < len(raw) and raw[index] in RETURN_DEPTHS:
            return_depth = raw[index]
            index += 1

        error_detail: str | None = None
        ending: str | None = None
        if index < len(raw) and raw[index] in ERROR_DETAILS:
            if index + 1 < len(raw) and raw[index + 1] in "@#":
                error_detail = raw[index]
                index += 1
        if index < len(raw) and raw[index] in "*@#C":
            ending = raw[index]
            index += 1
            outcome = {
                "*": "winner",
                "@": "unforced_error",
                "#": "forced_error",
                "C": "incorrect_challenge",
            }[ending]

        shots.append(
            McpShot(
                shot_type=shot_type,
                direction=direction,
                return_depth=return_depth,
                modifiers=tuple(modifiers),
                error_detail=error_detail,
                ending=ending,
            )
        )
        if ending is not None:
            if index != len(raw):
                return _invalid(
                    raw,
                    column,
                    index,
                    "trailing_after_rally_outcome",
                    "point-ending marker must end the cell",
                )
            break
        if index == shot_start:
            return _invalid(raw, column, index, "parser_stalled", "parser made no progress")

    if not shots:
        outcome = "incomplete"
    elif outcome is None:
        return _invalid(
            raw,
            column,
            len(raw),
            "missing_point_ending",
            "rally notation has no terminal outcome",
        )

    return ParsedNotation(
        raw=raw,
        column=column,
        let_count=let_count,
        serve_direction=serve_direction,
        serve_and_volley=serve_and_volley,
        serve_fault=None,
        shots=tuple(shots),
        outcome=outcome,
        exceptional=None,
        issues=(),
    )
