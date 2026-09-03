"""Deterministic, field-aware parser for Match Charting Project notation.

The parser preserves safely decoded prefixes when a later token is unsupported.
It never treats a partial parse as a fully valid cell and does not calculate
player features.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


CellColumn = Literal["1st", "2nd"]
PARSER_VERSION = "mcp-parser-v0.2-draft"
ComponentState = Literal[
    "observed",
    "unknown",
    "absent",
    "partial",
    "invalid",
    "not_applicable",
]
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
    serve_direction_state: ComponentState
    serve_and_volley_state: ComponentState
    rally_state: ComponentState
    outcome_state: ComponentState
    issues: tuple[ParseIssue, ...]

    @property
    def valid(self) -> bool:
        return not self.issues


def _direction_state(direction: str | None) -> ComponentState:
    if direction is None:
        return "invalid"
    return "unknown" if direction == "0" else "observed"


def _invalid(
    raw: str,
    column: CellColumn,
    position: int,
    code: str,
    message: str,
    *,
    let_count: int = 0,
    serve_direction: str | None = None,
    serve_and_volley: bool = False,
    serve_fault: str | None = None,
    shots: tuple[McpShot, ...] = (),
    outcome: Outcome | None = None,
    serve_direction_state: ComponentState = "invalid",
    serve_and_volley_state: ComponentState = "invalid",
    rally_state: ComponentState = "invalid",
    outcome_state: ComponentState = "invalid",
) -> ParsedNotation:
    return ParsedNotation(
        raw=raw,
        column=column,
        let_count=let_count,
        serve_direction=serve_direction,
        serve_and_volley=serve_and_volley,
        serve_fault=serve_fault,
        shots=shots,
        outcome=outcome,
        exceptional=None,
        serve_direction_state=serve_direction_state,
        serve_and_volley_state=serve_and_volley_state,
        rally_state=rally_state,
        outcome_state=outcome_state,
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
            raw=raw,
            column=column,
            let_count=0,
            serve_direction=None,
            serve_and_volley=False,
            serve_fault=None,
            shots=(),
            outcome=None,
            exceptional=EXCEPTIONAL_POINTS[raw],
            serve_direction_state="not_applicable",
            serve_and_volley_state="not_applicable",
            rally_state="not_applicable",
            outcome_state="not_applicable",
            issues=(),
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
    serve_direction_state = _direction_state(serve_direction)
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
                let_count=let_count,
                serve_direction=serve_direction,
                serve_and_volley=serve_and_volley,
                serve_fault=fault,
                outcome="serve_fault",
                serve_direction_state=serve_direction_state,
                serve_and_volley_state="observed" if serve_and_volley else "absent",
                rally_state="not_applicable",
                outcome_state="observed",
            )
        return ParsedNotation(
            raw=raw,
            column=column,
            let_count=let_count,
            serve_direction=serve_direction,
            serve_and_volley=serve_and_volley,
            serve_fault=fault,
            shots=(),
            outcome="serve_fault",
            exceptional=None,
            serve_direction_state=serve_direction_state,
            serve_and_volley_state="observed" if serve_and_volley else "absent",
            rally_state="not_applicable",
            outcome_state="observed",
            issues=(),
        )

    if index < len(raw) and raw[index] in "*#":
        marker = raw[index]
        index += 1
        if index != len(raw):
            return _invalid(
                raw,
                column,
                index,
                "trailing_after_serve_outcome",
                "serve outcome must end the cell",
                let_count=let_count,
                serve_direction=serve_direction,
                serve_and_volley=serve_and_volley,
                outcome="ace" if marker == "*" else "unreturnable",
                serve_direction_state=serve_direction_state,
                serve_and_volley_state="observed" if serve_and_volley else "absent",
                rally_state="not_applicable",
                outcome_state="observed",
            )
        outcome: Outcome = "ace" if marker == "*" else "unreturnable"
        return ParsedNotation(
            raw=raw,
            column=column,
            let_count=let_count,
            serve_direction=serve_direction,
            serve_and_volley=serve_and_volley,
            serve_fault=None,
            shots=(),
            outcome=outcome,
            exceptional=None,
            serve_direction_state=serve_direction_state,
            serve_and_volley_state="observed" if serve_and_volley else "absent",
            rally_state="not_applicable",
            outcome_state="observed",
            issues=(),
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
                let_count=let_count,
                serve_direction=serve_direction,
                serve_and_volley=serve_and_volley,
                shots=tuple(shots),
                serve_direction_state=serve_direction_state,
                serve_and_volley_state="observed" if serve_and_volley else "absent",
                rally_state="partial" if shots else "invalid",
            )
        shot_type = raw[index]
        index += 1

        modifiers: list[str] = []
        while index < len(raw) and raw[index] in SHOT_MODIFIERS:
            modifier = raw[index]
            if modifier in modifiers:
                return _invalid(
                    raw,
                    column,
                    index,
                    "duplicate_modifier",
                    f"duplicate modifier {modifier!r}",
                    let_count=let_count,
                    serve_direction=serve_direction,
                    serve_and_volley=serve_and_volley,
                    shots=tuple(shots),
                    serve_direction_state=serve_direction_state,
                    serve_and_volley_state="observed" if serve_and_volley else "absent",
                    rally_state="partial" if shots else "invalid",
                )
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
                    let_count=let_count,
                    serve_direction=serve_direction,
                    serve_and_volley=serve_and_volley,
                    shots=tuple(shots),
                    outcome=outcome,
                    serve_direction_state=serve_direction_state,
                    serve_and_volley_state="observed" if serve_and_volley else "absent",
                    rally_state="observed",
                    outcome_state="observed",
                )
            break
        if index == shot_start:
            return _invalid(
                raw,
                column,
                index,
                "parser_stalled",
                "parser made no progress",
                let_count=let_count,
                serve_direction=serve_direction,
                serve_and_volley=serve_and_volley,
                shots=tuple(shots),
                serve_direction_state=serve_direction_state,
                serve_and_volley_state="observed" if serve_and_volley else "absent",
                rally_state="partial" if shots else "invalid",
            )

    if not shots:
        outcome = "incomplete"
    elif outcome is None:
        return _invalid(
            raw,
            column,
            len(raw),
            "missing_point_ending",
            "rally notation has no terminal outcome",
            let_count=let_count,
            serve_direction=serve_direction,
            serve_and_volley=serve_and_volley,
            shots=tuple(shots),
            serve_direction_state=serve_direction_state,
            serve_and_volley_state="observed" if serve_and_volley else "absent",
            rally_state="observed",
            outcome_state="absent",
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
        serve_direction_state=serve_direction_state,
        serve_and_volley_state="observed" if serve_and_volley else "absent",
        rally_state="observed" if shots else "absent",
        outcome_state="observed" if outcome != "incomplete" else "absent",
        issues=(),
    )
