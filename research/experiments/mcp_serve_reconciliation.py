"""Reconcile raw-notation serve metrics with MCP aggregate CSVs."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping


OVERVIEW_METRICS = ("serve_pts", "aces", "dfs", "first_in", "second_in")
DIRECTION_COLUMNS = (
    "deuce_wide",
    "deuce_middle",
    "deuce_t",
    "ad_wide",
    "ad_middle",
    "ad_t",
)
OVERVIEW_UNRESOLVED = {
    "serve_pts": (),
    "aces": ("_unresolved_ace",),
    "dfs": ("_unresolved_df",),
    "first_in": ("_unresolved_first_in",),
    "second_in": ("_unresolved_first_in", "_unresolved_second_in"),
}


def read_aggregate_rows(
    paths: Iterable[Path],
    row_field: str,
    accepted_rows: set[str],
    value_fields: tuple[str, ...],
) -> tuple[dict[tuple[str, str, str], dict[str, int]], dict[str, int]]:
    """Read aggregate rows, collapsing exact duplicates and excluding conflicts."""

    grouped: defaultdict[tuple[str, str, str], list[tuple[str, ...]]] = defaultdict(list)
    invalid_rows = 0
    for path in paths:
        with path.open(newline="", encoding="utf-8-sig") as source:
            reader = csv.DictReader(source)
            required = {"match_id", "player", row_field, *value_fields}
            if missing := required.difference(reader.fieldnames or ()):
                raise ValueError(f"{path.name} missing aggregate fields: {sorted(missing)}")
            for row in reader:
                row_name = row[row_field]
                if row_name not in accepted_rows:
                    continue
                try:
                    values = tuple(str(int(row[field])) for field in value_fields)
                except (TypeError, ValueError):
                    invalid_rows += 1
                    continue
                grouped[(row["match_id"], row["player"], row_name)].append(values)

    safe: dict[tuple[str, str, str], dict[str, int]] = {}
    duplicate_groups = 0
    conflicting_groups = 0
    for key, records in grouped.items():
        signatures = set(records)
        if len(records) > 1:
            duplicate_groups += 1
        if len(signatures) > 1:
            conflicting_groups += 1
            continue
        safe[key] = dict(zip(value_fields, map(int, records[0])))
    return safe, {
        "raw_grain_groups": len(grouped),
        "safe_grain_groups": len(safe),
        "duplicate_grain_groups": duplicate_groups,
        "conflicting_grain_groups": conflicting_groups,
        "invalid_rows": invalid_rows,
    }


def computed_records(
    metrics_by_match_server: Mapping[tuple[str, str], Counter[str]],
    safe_metadata: Mapping[str, Mapping[str, str]],
) -> dict[tuple[str, str], Counter[str]]:
    records: dict[tuple[str, str], Counter[str]] = {}
    for (match_id, server_number), metrics in metrics_by_match_server.items():
        metadata = safe_metadata.get(match_id)
        if metadata is None or server_number not in {"1", "2"}:
            continue
        records[(match_id, metadata[f"Player {server_number}"])] = metrics
    return records


def _metric_summary(
    computed: Mapping[tuple[str, str], Counter[str]],
    aggregate: Mapping[tuple[str, str, str], Mapping[str, int]],
    metric: str,
    unresolved_fields: tuple[str, ...],
) -> dict[str, object]:
    comparable = 0
    exact = 0
    absolute_difference = 0
    examples: list[dict[str, object]] = []
    for key, raw_values in computed.items():
        aggregate_values = aggregate.get((*key, "Total"))
        if aggregate_values is None or any(raw_values[field] for field in unresolved_fields):
            continue
        comparable += 1
        raw_value = raw_values[metric]
        aggregate_value = aggregate_values[metric]
        difference = raw_value - aggregate_value
        absolute_difference += abs(difference)
        if difference == 0:
            exact += 1
        elif len(examples) < 10:
            examples.append(
                {
                    "match_id": key[0],
                    "player": key[1],
                    "raw": raw_value,
                    "aggregate": aggregate_value,
                    "difference": difference,
                }
            )
    return {
        "comparable_records": comparable,
        "exact_records": exact,
        "exact_rate": exact / comparable if comparable else None,
        "mean_absolute_difference": absolute_difference / comparable if comparable else None,
        "mismatch_examples": examples,
    }


def reconcile_overview(
    computed: Mapping[tuple[str, str], Counter[str]],
    aggregate: Mapping[tuple[str, str, str], Mapping[str, int]],
) -> dict[str, object]:
    return {
        metric: _metric_summary(computed, aggregate, metric, OVERVIEW_UNRESOLVED[metric])
        for metric in OVERVIEW_METRICS
    }


def reconcile_directions(
    computed: Mapping[tuple[str, str], Counter[str]],
    aggregate: Mapping[tuple[str, str, str], Mapping[str, int]],
) -> dict[str, object]:
    summaries: dict[str, object] = {}
    for row_name, serve_numbers, unresolved_field in (
        ("1", ("1",), "_unresolved_direction_1"),
        ("2", ("2",), "_unresolved_direction_2"),
        ("Total", ("1", "2"), "_unresolved_direction"),
    ):
        comparable = 0
        exact = 0
        absolute_difference = 0
        marginal_exact = 0
        marginal_absolute_difference = 0
        examples: list[dict[str, object]] = []
        for key, raw_values in computed.items():
            aggregate_values = aggregate.get((*key, row_name))
            if aggregate_values is None or raw_values[unresolved_field]:
                continue
            raw_directions = {
                column: sum(
                    raw_values[f"direction:{serve_number}:{column.replace('_', ':')}"]
                    for serve_number in serve_numbers
                )
                for column in DIRECTION_COLUMNS
            }
            differences = {
                column: raw_directions[column] - aggregate_values[column]
                for column in DIRECTION_COLUMNS
            }
            raw_marginal = {
                direction: sum(
                    raw_directions[f"{side}_{direction}"] for side in ("deuce", "ad")
                )
                for direction in ("wide", "middle", "t")
            }
            aggregate_marginal = {
                direction: sum(
                    aggregate_values[f"{side}_{direction}"] for side in ("deuce", "ad")
                )
                for direction in ("wide", "middle", "t")
            }
            marginal_differences = {
                direction: raw_marginal[direction] - aggregate_marginal[direction]
                for direction in ("wide", "middle", "t")
            }
            comparable += 1
            absolute_difference += sum(abs(value) for value in differences.values())
            marginal_absolute_difference += sum(
                abs(value) for value in marginal_differences.values()
            )
            if all(value == 0 for value in differences.values()):
                exact += 1
            elif len(examples) < 10:
                examples.append(
                    {
                        "match_id": key[0],
                        "player": key[1],
                        "raw": raw_directions,
                        "aggregate": dict(aggregate_values),
                    }
                )
            if all(value == 0 for value in marginal_differences.values()):
                marginal_exact += 1
        summaries[row_name] = {
            "comparable_records": comparable,
            "exact_records": exact,
            "exact_rate": exact / comparable if comparable else None,
            "mean_absolute_cell_difference": (
                absolute_difference / (comparable * len(DIRECTION_COLUMNS))
                if comparable
                else None
            ),
            "marginal_exact_records": marginal_exact,
            "marginal_exact_rate": marginal_exact / comparable if comparable else None,
            "marginal_mean_absolute_cell_difference": (
                marginal_absolute_difference / (comparable * 3) if comparable else None
            ),
            "mismatch_examples": examples,
        }
    return summaries
