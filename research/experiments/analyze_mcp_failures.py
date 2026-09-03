"""Profile first strict-reconstruction failures in the local MCP snapshot."""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

from pipelines.processing.mcp import (
    InvalidMcpRow,
    McpPoint,
    normalize_mcp_rows,
    parse_mcp_row,
    reconstruct_match,
)

SOURCE = Path("data/raw/mcp/charting-w-points-to-2009.csv")


def category(message: str) -> str:
    if "expected point" in message:
        return "point gap"
    if "server disagrees" in message:
        return "server mismatch"
    if "point score disagrees" in message:
        return "point-score mismatch"
    if "score disagrees" in message:
        return "set/game score mismatch"
    return "other"


def main() -> None:
    raw_groups: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    with SOURCE.open(newline="", encoding="utf-8-sig") as source:
        for row in csv.DictReader(source):
            raw_groups[row["match_id"]].append(row)

    examples: dict[str, tuple[str, str, McpPoint | None, McpPoint | None]] = {}
    for match_id, raw_rows in raw_groups.items():
        points = [
            parse_mcp_row(row)
            for row in normalize_mcp_rows(raw_rows, reject_conflicts=False)
        ]
        try:
            reconstruct_match(points)
        except InvalidMcpRow as error:
            failure_category = category(str(error))
            if failure_category not in examples:
                message = str(error)
                point_match = re.search(r"point (\d+)", message)
                point_number = int(point_match.group(1)) if point_match else None
                previous = next(
                    (point for point in points if point.point_number == point_number - 1),
                    None,
                ) if point_number else None
                current = next(
                    (point for point in points if point.point_number == point_number),
                    None,
                ) if point_number else None
                examples[failure_category] = (match_id, message, previous, current)

    for failure_category, (match_id, message, previous, current) in sorted(examples.items()):
        print(f"[{failure_category}] {match_id}")
        print(message)
        print(f"previous={previous}")
        print(f"current={current}")


if __name__ == "__main__":
    main()
