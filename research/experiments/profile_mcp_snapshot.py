"""Profile a complete Match Charting Project snapshot and its shot notation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

from pipelines.processing.mcp_notation import PARSER_VERSION, parse_notation
from pipelines.processing.mcp_serve import serve_point_metrics_from_parsed
from research.experiments.mcp_serve_reconciliation import (
    DIRECTION_COLUMNS,
    OVERVIEW_METRICS,
    computed_records,
    read_aggregate_rows,
    reconcile_directions,
    reconcile_overview,
)


DEFAULT_SOURCE = Path("data/raw/mcp_upstream")
DEFAULT_REPORT_ROOT = Path("research")
SNAPSHOT_ID = "mcp-atp-wta-2026-09-03-2c59eef1"
PINNED_SOURCE_COMMIT = "2c59eef194967e688b69e73df344184a06322cd8"
POINT_PATTERN = "charting-[mw]-points-*.csv"
MATCH_PATTERN = "charting-[mw]-matches.csv"
AGGREGATE_NAMES = (
    "Overview",
    "ServeDirection",
    "ShotTypes",
    "Rally",
    "ReturnDepth",
    "NetPoints",
)
REQUIRED_POINT_FIELDS = frozenset(
    {"match_id", "Pt", "Set1", "Set2", "Gm1", "Gm2", "Pts", "Svr", "1st", "2nd", "PtWinner"}
)
REQUIRED_MATCH_FIELDS = frozenset(
    {"match_id", "Player 1", "Player 2", "Date", "Tournament", "Round", "Surface", "Best of"}
)
VALID_SURFACES = frozenset({"Hard", "Clay", "Grass", "Carpet"})
DOCUMENTED_NOTATION_CHARS = frozenset(
    "0123456789fbrsvzopuy lmhijktqnwdxgecVSRPQC+*#@!-=;^".replace(" ", "")
)


class InvalidSnapshot(ValueError):
    """Raised when the snapshot structure cannot be audited safely."""


@dataclass
class FieldCounts:
    rows: int = 0
    nonempty: int = 0
    valid: int = 0

    def observe(self, field: str, value: str, delta: int = 1) -> None:
        self.rows += delta
        if value.strip():
            self.nonempty += delta
        if _valid_value(field, value):
            self.valid += delta


def _valid_value(field: str, value: str) -> bool:
    value = value.strip()
    if not value:
        return False
    if field in {"Pt", "Set1", "Set2", "Gm1", "Gm2"}:
        return value.isdigit()
    if field in {"Svr", "PtWinner"}:
        return value in {"1", "2"}
    if field in {"TbSet", "TB?"}:
        return value.lower() in {"true", "false", "0", "1"}
    return True


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _tour(path_or_id: str) -> str:
    name = Path(path_or_id).name
    if name.startswith("charting-m-") or "-M-" in path_or_id:
        return "ATP"
    if name.startswith("charting-w-") or "-W-" in path_or_id:
        return "WTA"
    return "Unknown"


def _parse_date(value: str) -> datetime | None:
    try:
        return datetime.strptime(value, "%Y%m%d")
    except (TypeError, ValueError):
        return None


def _signature(row: dict[str, str], fields: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(row.get(field, "") for field in fields)


def _discover(source_root: Path, pattern: str, expected: int | None = None) -> list[Path]:
    files = sorted(source_root.glob(pattern))
    if expected is not None and len(files) != expected:
        raise InvalidSnapshot(f"expected {expected} files for {pattern!r}, found {len(files)}")
    if not files:
        raise InvalidSnapshot(f"no files found for {pattern!r} under {source_root}")
    return files


def _source_commit(source_root: Path) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _read_metadata(match_files: Iterable[Path]) -> dict[str, object]:
    records: defaultdict[str, list[tuple[str, ...]]] = defaultdict(list)
    rows_by_id: dict[str, dict[str, str]] = {}
    fields_by_file: dict[str, list[str]] = {}
    rows_by_file: Counter[str] = Counter()
    players_by_tour: defaultdict[str, set[str]] = defaultdict(set)
    anomalies: Counter[str] = Counter()
    anomalous_ids: set[str] = set()

    for path in match_files:
        with path.open(newline="", encoding="utf-8-sig") as source:
            reader = csv.DictReader(source)
            fields = tuple(reader.fieldnames or ())
            if missing := REQUIRED_MATCH_FIELDS.difference(fields):
                raise InvalidSnapshot(f"{path.name} missing match columns: {sorted(missing)}")
            fields_by_file[path.name] = list(fields)
            for row in reader:
                match_id = sys.intern(row["match_id"])
                signature = _signature(row, fields)
                records[match_id].append(signature)
                rows_by_id.setdefault(match_id, row)
                rows_by_file[path.name] += 1
                players_by_tour[_tour(path.name)].update((row["Player 1"], row["Player 2"]))
                row_anomalous = False
                for label, invalid in (
                    ("invalid_date", _parse_date(row["Date"]) is None),
                    ("invalid_surface", row["Surface"] not in VALID_SURFACES),
                    ("invalid_best_of", row["Best of"] not in {"3", "5"}),
                ):
                    anomalies[label] += invalid
                    row_anomalous |= invalid
                if row_anomalous:
                    anomalous_ids.add(match_id)

    duplicate_ids = {match_id for match_id, values in records.items() if len(values) > 1}
    conflicting_ids = {
        match_id for match_id in duplicate_ids if len(set(records[match_id])) > 1
    }
    safe_rows = {
        match_id: row
        for match_id, row in rows_by_id.items()
        if match_id not in conflicting_ids and match_id not in anomalous_ids
    }
    return {
        "rows_by_file": dict(rows_by_file),
        "fields_by_file": fields_by_file,
        "unique_match_ids": len(records),
        "duplicate_match_ids": len(duplicate_ids),
        "conflicting_match_ids": len(conflicting_ids),
        "anomalous_match_ids": len(anomalous_ids),
        "safe_rows": safe_rows,
        "_all_ids": set(records),
        "_conflicting_ids": conflicting_ids,
        "_anomalous_ids": anomalous_ids,
        "players_by_tour": {key: len(value) for key, value in players_by_tour.items()},
        "anomalies": dict(anomalies),
    }


def _observe_fields(
    counters: dict[str, FieldCounts],
    fields: tuple[str, ...],
    values: tuple[str, ...],
    delta: int,
) -> None:
    for field, value in zip(fields, values):
        counters.setdefault(field, FieldCounts()).observe(field, value, delta)


def _observe_notation(
    fields: tuple[str, ...],
    values: tuple[str, ...],
    nonempty: Counter[str],
    characters: Counter[str],
    undocumented_cells: Counter[str],
    special_codes: Counter[str],
    parse_counts: Counter[str],
    parse_issues: Counter[str],
    parse_issue_characters: Counter[str],
    outcomes: Counter[str],
    attribute_counts: Counter[str],
    component_states: Counter[str],
    serve_direction_cells_by_match_server: Counter[tuple[str, str]],
    serve_direction_known_by_match_server: Counter[tuple[str, str]],
    delta: int,
) -> tuple[int, int, Counter[str]]:
    row = dict(zip(fields, values))
    observed_cells = 0
    valid_cells = 0
    parsed_cells = {}
    for field in ("1st", "2nd"):
        value = row.get(field, "")
        if not value:
            continue
        observed_cells += delta
        nonempty[field] += delta
        characters.update({character: delta * count for character, count in Counter(value).items()})
        if any(character not in DOCUMENTED_NOTATION_CHARS for character in value):
            undocumented_cells[field] += delta
        if value in {"S", "R", "P", "Q", "V"}:
            special_codes[value] += delta
        parsed = parse_notation(value, field)  # type: ignore[arg-type]
        parsed_cells[field] = parsed
        for component in (
            "serve_direction",
            "serve_and_volley",
            "rally",
            "outcome",
        ):
            state = getattr(parsed, f"{component}_state")
            component_states[f"{field}:{component}:{state}"] += delta
        parse_counts[f"{field}_cells"] += delta
        parse_counts[f"{field}_{'valid' if parsed.valid else 'invalid'}"] += delta
        valid_cells += delta * parsed.valid
        for issue in parsed.issues:
            parse_issues[f"{field}:{issue.code}"] += delta
            character = value[issue.position] if issue.position < len(value) else "<end>"
            parse_issue_characters[f"{field}:{issue.code}:{character}"] += delta
        if parsed.outcome:
            outcomes[parsed.outcome] += delta
        if parsed.exceptional:
            outcomes[parsed.exceptional] += delta
        if parsed.serve_direction is not None:
            attribute_counts["regular_serve_cells"] += delta
            attribute_counts["known_serve_direction"] += delta * (parsed.serve_direction != "0")
        if parsed.serve_direction_state in {"observed", "unknown"}:
            serve_direction_cells_by_match_server[(row["match_id"], row["Svr"])] += delta
        if parsed.serve_direction_state == "observed":
            serve_direction_known_by_match_server[(row["match_id"], row["Svr"])] += delta
        attribute_counts["serve_and_volley_attempts"] += delta * parsed.serve_and_volley
        attribute_counts["parsed_shots"] += delta * len(parsed.shots)
        attribute_counts["shots_with_known_direction"] += delta * sum(
            shot.direction not in {None, "0"} for shot in parsed.shots
        )
        if parsed.shots:
            attribute_counts["parsed_returns"] += delta
            attribute_counts["returns_with_known_direction"] += delta * (
                parsed.shots[0].direction not in {None, "0"}
            )
            attribute_counts["returns_with_known_depth"] += delta * (
                parsed.shots[0].return_depth not in {None, "0"}
            )
    serve_metrics = serve_point_metrics_from_parsed(
        row,
        parsed_cells.get("1st") or parse_notation("", "1st"),
        parsed_cells.get("2nd"),
    )
    return observed_cells, valid_cells, serve_metrics


def _read_points(point_files: Iterable[Path]) -> dict[str, object]:
    seen: dict[tuple[str, str], tuple[tuple[str, ...], str]] = {}
    duplicate_keys: set[tuple[str, str]] = set()
    conflicting_keys: set[tuple[str, str]] = set()
    duplicate_occurrences: Counter[tuple[str, str]] = Counter()
    fields_reference: tuple[str, ...] | None = None
    fields_by_file: dict[str, list[str]] = {}
    raw_rows_by_file: Counter[str] = Counter()
    usable_rows_by_file: Counter[str] = Counter()
    usable_points_by_match: Counter[str] = Counter()
    field_counts: dict[str, FieldCounts] = {}
    point_match_ids: set[str] = set()
    notation_nonempty: Counter[str] = Counter()
    notation_characters: Counter[str] = Counter()
    undocumented_notation_cells: Counter[str] = Counter()
    special_notation_codes: Counter[str] = Counter()
    notation_parse_counts: Counter[str] = Counter()
    notation_parse_issues: Counter[str] = Counter()
    notation_parse_issue_characters: Counter[str] = Counter()
    notation_outcomes: Counter[str] = Counter()
    notation_attribute_counts: Counter[str] = Counter()
    notation_component_states: Counter[str] = Counter()
    notation_cells_by_match_server: Counter[tuple[str, str]] = Counter()
    notation_valid_by_match_server: Counter[tuple[str, str]] = Counter()
    serve_direction_cells_by_match_server: Counter[tuple[str, str]] = Counter()
    serve_direction_known_by_match_server: Counter[tuple[str, str]] = Counter()
    serve_metrics_by_match_server: defaultdict[tuple[str, str], Counter[str]] = defaultdict(Counter)

    for path in point_files:
        with path.open(newline="", encoding="utf-8-sig") as source:
            reader = csv.DictReader(source)
            fields = tuple(reader.fieldnames or ())
            if missing := REQUIRED_POINT_FIELDS.difference(fields):
                raise InvalidSnapshot(f"{path.name} missing point columns: {sorted(missing)}")
            if fields_reference is None:
                fields_reference = fields
            elif fields != fields_reference:
                raise InvalidSnapshot(f"point schema drift in {path.name}")
            fields_by_file[path.name] = list(fields)
            for row in reader:
                raw_rows_by_file[path.name] += 1
                match_id = sys.intern(row["match_id"])
                point_match_ids.add(match_id)
                key = (match_id, row["Pt"])
                signature = _signature(row, fields)
                previous = seen.get(key)
                if previous is None:
                    seen[key] = (signature, path.name)
                    usable_rows_by_file[path.name] += 1
                    usable_points_by_match[match_id] += 1
                    _observe_fields(field_counts, fields, signature, 1)
                    observed_cells, valid_cells, serve_metrics = _observe_notation(
                        fields,
                        signature,
                        notation_nonempty,
                        notation_characters,
                        undocumented_notation_cells,
                        special_notation_codes,
                        notation_parse_counts,
                        notation_parse_issues,
                        notation_parse_issue_characters,
                        notation_outcomes,
                        notation_attribute_counts,
                        notation_component_states,
                        serve_direction_cells_by_match_server,
                        serve_direction_known_by_match_server,
                        1,
                    )
                    server_key = (match_id, row["Svr"])
                    notation_cells_by_match_server[server_key] += observed_cells
                    notation_valid_by_match_server[server_key] += valid_cells
                    serve_metrics_by_match_server[server_key].update(serve_metrics)
                    continue

                duplicate_keys.add(key)
                duplicate_occurrences[key] += 1
                previous_signature, previous_file = previous
                if signature != previous_signature and key not in conflicting_keys:
                    conflicting_keys.add(key)
                    usable_rows_by_file[previous_file] -= 1
                    usable_points_by_match[match_id] -= 1
                    _observe_fields(field_counts, fields, previous_signature, -1)
                    observed_cells, valid_cells, serve_metrics = _observe_notation(
                        fields,
                        previous_signature,
                        notation_nonempty,
                        notation_characters,
                        undocumented_notation_cells,
                        special_notation_codes,
                        notation_parse_counts,
                        notation_parse_issues,
                        notation_parse_issue_characters,
                        notation_outcomes,
                        notation_attribute_counts,
                        notation_component_states,
                        serve_direction_cells_by_match_server,
                        serve_direction_known_by_match_server,
                        -1,
                    )
                    previous_row = dict(zip(fields, previous_signature))
                    server_key = (match_id, previous_row["Svr"])
                    notation_cells_by_match_server[server_key] += observed_cells
                    notation_valid_by_match_server[server_key] += valid_cells
                    serve_metrics_by_match_server[server_key].subtract(serve_metrics)

    unique_keys = len(seen)
    raw_rows = sum(raw_rows_by_file.values())
    return {
        "fields_by_file": fields_by_file,
        "raw_rows_by_file": dict(raw_rows_by_file),
        "usable_rows_by_file": dict(usable_rows_by_file),
        "raw_rows": raw_rows,
        "unique_point_keys": unique_keys,
        "usable_point_rows": unique_keys - len(conflicting_keys),
        "duplicate_groups": len(duplicate_keys),
        "exact_duplicate_groups": len(duplicate_keys.difference(conflicting_keys)),
        "conflicting_duplicate_groups": len(conflicting_keys),
        "duplicate_excess_rows": raw_rows - unique_keys,
        "conflicting_raw_rows": sum(duplicate_occurrences[key] + 1 for key in conflicting_keys),
        "point_match_ids": point_match_ids,
        "usable_points_by_match": usable_points_by_match,
        "field_counts": {field: asdict(counts) for field, counts in field_counts.items()},
        "notation_nonempty": dict(notation_nonempty),
        "notation_characters": _counter_records(notation_characters, "character"),
        "undocumented_notation_characters": _counter_records(
            {
                character: count
                for character, count in notation_characters.items()
                if character not in DOCUMENTED_NOTATION_CHARS
            },
            "character",
        ),
        "undocumented_notation_cells": dict(undocumented_notation_cells),
        "special_notation_codes": dict(special_notation_codes),
        "notation_parse_counts": dict(notation_parse_counts),
        "notation_parse_issues": dict(notation_parse_issues),
        "notation_parse_issue_characters": _counter_records(
            notation_parse_issue_characters, "issue_character"
        ),
        "notation_outcomes": dict(notation_outcomes),
        "notation_attribute_counts": dict(notation_attribute_counts),
        "notation_component_states": dict(notation_component_states),
        "_notation_cells_by_match_server": notation_cells_by_match_server,
        "_notation_valid_by_match_server": notation_valid_by_match_server,
        "_serve_direction_cells_by_match_server": serve_direction_cells_by_match_server,
        "_serve_direction_known_by_match_server": serve_direction_known_by_match_server,
        "_serve_metrics_by_match_server": serve_metrics_by_match_server,
    }


def _aggregate_key_fields(fields: tuple[str, ...]) -> tuple[str, ...]:
    candidates = ("match_id", "player", "server", "returner", "set", "row")
    return tuple(field for field in candidates if field in fields)


def _read_aggregates(
    paths: Iterable[Path],
    safe_match_ids: set[str],
    charted_match_ids: set[str] | None = None,
) -> list[dict[str, object]]:
    profiles: list[dict[str, object]] = []
    for path in paths:
        rows = 0
        matches: set[str] = set()
        players: set[str] = set()
        categories: Counter[str] = Counter()
        seen_keys: dict[tuple[str, ...], tuple[str, ...]] = {}
        duplicate_keys: set[tuple[str, ...]] = set()
        conflicting_keys: set[tuple[str, ...]] = set()
        duplicate_grain_rows = 0
        nonempty_numeric_values = 0
        invalid_numeric_values = 0
        negative_numeric_values = 0
        field_counts: dict[str, FieldCounts] = {}
        with path.open(newline="", encoding="utf-8-sig") as source:
            reader = csv.DictReader(source)
            fields = tuple(reader.fieldnames or ())
            if "match_id" not in fields:
                raise InvalidSnapshot(f"{path.name} has no match_id")
            key_fields = _aggregate_key_fields(fields)
            numeric_fields = tuple(field for field in fields if field not in key_fields)
            for row in reader:
                rows += 1
                match_id = row["match_id"]
                matches.add(match_id)
                for player_field in ("player", "server", "returner"):
                    if row.get(player_field):
                        players.add(row[player_field])
                if "row" in row:
                    categories[row["row"]] += 1
                key = tuple(row.get(field, "") for field in key_fields)
                signature = _signature(row, fields)
                if key in seen_keys:
                    duplicate_grain_rows += 1
                    duplicate_keys.add(key)
                    if signature != seen_keys[key]:
                        conflicting_keys.add(key)
                else:
                    seen_keys[key] = signature
                _observe_fields(field_counts, fields, signature, 1)
                for field in numeric_fields:
                    value = row.get(field, "").strip()
                    if not value:
                        continue
                    nonempty_numeric_values += 1
                    try:
                        number = int(value)
                    except ValueError:
                        invalid_numeric_values += 1
                    else:
                        negative_numeric_values += number < 0
        profiles.append(
            {
                "file": path.name,
                "tour": _tour(path.name),
                "rows": rows,
                "matches": len(matches),
                "players": len(players),
                "orphan_match_ids": len(matches.difference(safe_match_ids)),
                "charted_matches_covered": len(
                    matches.intersection(charted_match_ids or safe_match_ids)
                ),
                "duplicate_grain_rows": duplicate_grain_rows,
                "duplicate_grain_groups": len(duplicate_keys),
                "exact_duplicate_grain_groups": len(duplicate_keys.difference(conflicting_keys)),
                "conflicting_grain_groups": len(conflicting_keys),
                "conflicting_grain_match_ids": len({key[0] for key in conflicting_keys}),
                "conflicting_grain_examples": [
                    dict(zip(key_fields, key)) for key in sorted(conflicting_keys)[:5]
                ],
                "key_fields": list(key_fields),
                "numeric_fields": list(numeric_fields),
                "nonempty_numeric_values": nonempty_numeric_values,
                "invalid_numeric_values": invalid_numeric_values,
                "negative_numeric_values": negative_numeric_values,
                "categories": dict(categories),
                "field_counts": {field: asdict(counts) for field, counts in field_counts.items()},
            }
        )
    return profiles


def _counter_from_matches(
    match_ids: set[str], metadata: dict[str, dict[str, str]], field: str
) -> Counter[str]:
    values: list[str] = []
    for match_id in match_ids:
        if match_id not in metadata:
            continue
        value = metadata[match_id][field]
        if field == "Date":
            parsed = _parse_date(value)
            value = str(parsed.year) if parsed else "invalid-date"
        values.append(value)
    return Counter(values)


def _five_number(values: Iterable[int]) -> dict[str, int]:
    ordered = sorted(values)
    if not ordered:
        return {"minimum": 0, "p25": 0, "median": 0, "p75": 0, "maximum": 0}
    positions = {"minimum": 0, "p25": 0.25, "median": 0.5, "p75": 0.75, "maximum": 1}
    return {
        label: ordered[round(position * (len(ordered) - 1))]
        for label, position in positions.items()
    }


def profile_snapshot(source_root: Path = DEFAULT_SOURCE) -> dict[str, object]:
    source_commit = _source_commit(source_root)
    if source_commit != PINNED_SOURCE_COMMIT:
        raise InvalidSnapshot(
            f"expected MCP commit {PINNED_SOURCE_COMMIT}, found {source_commit or 'no Git metadata'}"
        )
    point_files = _discover(source_root, POINT_PATTERN, expected=6)
    match_files = _discover(source_root, MATCH_PATTERN, expected=2)
    aggregate_files = sorted(
        path
        for name in AGGREGATE_NAMES
        for path in source_root.glob(f"charting-[mw]-stats-{name}.csv")
    )
    if len(aggregate_files) != len(AGGREGATE_NAMES) * 2:
        raise InvalidSnapshot("one or more required aggregate files are missing")
    support_files = [
        source_root / "README.md",
        source_root / "data_dictionary.txt",
        source_root / "MatchChart 0.3.2.xlsm",
    ]
    missing_support = [path.name for path in support_files if not path.is_file()]
    if missing_support:
        raise InvalidSnapshot(f"missing source documentation: {missing_support}")

    metadata = _read_metadata(match_files)
    points = _read_points(point_files)
    safe_metadata = metadata["safe_rows"]
    point_match_ids = points["point_match_ids"]
    charted_ids = point_match_ids.intersection(safe_metadata)
    usable_points_by_match = points["usable_points_by_match"]
    computed_serves = computed_records(points["_serve_metrics_by_match_server"], safe_metadata)
    overview_rows, overview_source_profile = read_aggregate_rows(
        source_root.glob("charting-[mw]-stats-Overview.csv"),
        "set",
        {"Total"},
        OVERVIEW_METRICS,
    )
    direction_rows, direction_source_profile = read_aggregate_rows(
        source_root.glob("charting-[mw]-stats-ServeDirection.csv"),
        "row",
        {"1", "2", "Total"},
        DIRECTION_COLUMNS,
    )

    player_match_counts: Counter[str] = Counter()
    player_point_counts: Counter[str] = Counter()
    opponents: defaultdict[str, set[str]] = defaultdict(set)
    charted_players_by_tour: defaultdict[str, set[str]] = defaultdict(set)
    charted_matches_by_tour: Counter[str] = Counter()
    surfaces_by_player: defaultdict[str, set[str]] = defaultdict(set)
    tournaments_by_player: defaultdict[str, set[str]] = defaultdict(set)
    for match_id in charted_ids:
        row = safe_metadata[match_id]
        player_1, player_2 = row["Player 1"], row["Player 2"]
        tour = _tour(match_id)
        charted_matches_by_tour[tour] += 1
        charted_players_by_tour[tour].update((player_1, player_2))
        player_match_counts.update((player_1, player_2))
        player_point_counts[player_1] += usable_points_by_match[match_id]
        player_point_counts[player_2] += usable_points_by_match[match_id]
        opponents[player_1].add(player_2)
        opponents[player_2].add(player_1)
        surfaces_by_player[player_1].add(row["Surface"])
        surfaces_by_player[player_2].add(row["Surface"])
        tournaments_by_player[player_1].add(row["Tournament"])
        tournaments_by_player[player_2].add(row["Tournament"])

    parser_by_tour: defaultdict[str, Counter[str]] = defaultdict(Counter)
    parser_by_season: defaultdict[str, Counter[str]] = defaultdict(Counter)
    parser_by_player: defaultdict[str, Counter[str]] = defaultdict(Counter)
    parser_by_chart_author: defaultdict[str, Counter[str]] = defaultdict(Counter)
    serve_direction_by_tour: defaultdict[str, Counter[str]] = defaultdict(Counter)
    serve_direction_by_season: defaultdict[str, Counter[str]] = defaultdict(Counter)
    serve_direction_by_player: defaultdict[str, Counter[str]] = defaultdict(Counter)
    serve_direction_by_chart_author: defaultdict[str, Counter[str]] = defaultdict(Counter)
    for match_id in charted_ids:
        row = safe_metadata[match_id]
        parsed_date = _parse_date(row["Date"])
        season = str(parsed_date.year) if parsed_date else "invalid-date"
        tour = _tour(match_id)
        chart_author = row.get("Charted by", "").strip() or "(blank)"
        for server_number, player in (("1", row["Player 1"]), ("2", row["Player 2"])):
            key = (match_id, server_number)
            cells = points["_notation_cells_by_match_server"][key]
            valid = points["_notation_valid_by_match_server"][key]
            direction_cells = points["_serve_direction_cells_by_match_server"][key]
            direction_known = points["_serve_direction_known_by_match_server"][key]
            for counter in (
                parser_by_tour[tour],
                parser_by_season[season],
                parser_by_chart_author[chart_author],
            ):
                counter["cells"] += cells
                counter["valid"] += valid
            parser_by_player[player]["cells"] += cells
            parser_by_player[player]["valid"] += valid
            for counter in (
                serve_direction_by_tour[tour],
                serve_direction_by_season[season],
                serve_direction_by_player[player],
                serve_direction_by_chart_author[chart_author],
            ):
                counter["eligible"] += direction_cells
                counter["known"] += direction_known

    files = []
    for path in sorted(point_files + match_files + aggregate_files + support_files):
        files.append({"file": path.name, "bytes": path.stat().st_size, "sha256": _sha256(path)})

    return {
        "generated_on": date.today().isoformat(),
        "snapshot_id": SNAPSHOT_ID,
        "parser_version": PARSER_VERSION,
        "source_root": str(source_root),
        "source_commit": source_commit,
        "files": files,
        "metadata": {
            key: value
            for key, value in metadata.items()
            if key not in {"safe_rows", "_all_ids", "_conflicting_ids", "_anomalous_ids"}
        },
        "points": {
            key: value
            for key, value in points.items()
            if key
            not in {
                "point_match_ids",
                "usable_points_by_match",
                "_notation_cells_by_match_server",
                "_notation_valid_by_match_server",
                "_serve_direction_cells_by_match_server",
                "_serve_direction_known_by_match_server",
                "_serve_metrics_by_match_server",
            }
        },
        "joins": {
            "charted_match_ids": len(charted_ids),
            "point_match_ids_without_safe_metadata": len(point_match_ids.difference(safe_metadata)),
            "point_match_ids_absent_from_metadata": len(point_match_ids.difference(metadata["_all_ids"])),
            "point_match_ids_with_conflicting_metadata": len(point_match_ids.intersection(metadata["_conflicting_ids"])),
            "point_match_ids_with_anomalous_metadata": len(point_match_ids.intersection(metadata["_anomalous_ids"])),
            "safe_metadata_ids_without_points": len(set(safe_metadata).difference(point_match_ids)),
        },
        "coverage": {
            "players_in_charted_matches": len(player_match_counts),
            "charted_matches_by_tour": dict(charted_matches_by_tour),
            "charted_players_by_tour": {
                tour: len(players) for tour, players in charted_players_by_tour.items()
            },
            "seasons": dict(_counter_from_matches(charted_ids, safe_metadata, "Date")),
            "surfaces": dict(_counter_from_matches(charted_ids, safe_metadata, "Surface")),
            "tournaments": dict(_counter_from_matches(charted_ids, safe_metadata, "Tournament")),
            "rounds": dict(_counter_from_matches(charted_ids, safe_metadata, "Round")),
            "top_players_by_matches": player_match_counts.most_common(20),
            "top_players_by_points": player_point_counts.most_common(20),
            "opponents_per_player": dict(Counter({player: len(values) for player, values in opponents.items()})),
            "exposure_five_number": {
                "matches_per_player": _five_number(player_match_counts.values()),
                "points_per_player": _five_number(player_point_counts.values()),
                "opponents_per_player": _five_number(len(values) for values in opponents.values()),
                "surfaces_per_player": _five_number(len(values) for values in surfaces_by_player.values()),
                "tournaments_per_player": _five_number(len(values) for values in tournaments_by_player.values()),
            },
            "parser_coverage_by_tour": {
                key: dict(value) for key, value in parser_by_tour.items()
            },
            "parser_coverage_by_season": {
                key: dict(value) for key, value in parser_by_season.items()
            },
            "parser_coverage_for_most_charted_players": [
                {
                    "player": player,
                    "matches": matches,
                    "cells": parser_by_player[player]["cells"],
                    "valid": parser_by_player[player]["valid"],
                }
                for player, matches in player_match_counts.most_common(20)
            ],
            "parser_coverage_by_chart_author": [
                {"chart_author": key, **dict(value)}
                for key, value in sorted(parser_by_chart_author.items())
            ],
            "serve_direction_coverage_by_tour": {
                key: dict(value) for key, value in serve_direction_by_tour.items()
            },
            "serve_direction_coverage_by_season": {
                key: dict(value) for key, value in serve_direction_by_season.items()
            },
            "serve_direction_coverage_for_most_charted_players": [
                {
                    "player": player,
                    "matches": matches,
                    "eligible": serve_direction_by_player[player]["eligible"],
                    "known": serve_direction_by_player[player]["known"],
                }
                for player, matches in player_match_counts.most_common(20)
            ],
            "serve_direction_coverage_by_chart_author": [
                {"chart_author": key, **dict(value)}
                for key, value in sorted(serve_direction_by_chart_author.items())
            ],
        },
        "aggregates": _read_aggregates(
            aggregate_files, set(safe_metadata), set(charted_ids)
        ),
        "serve_reconciliation": {
            "computed_match_player_records": len(computed_serves),
            "overview_source": overview_source_profile,
            "overview": reconcile_overview(computed_serves, overview_rows, safe_metadata),
            "serve_direction_source": direction_source_profile,
            "serve_direction": reconcile_directions(
                computed_serves, direction_rows, safe_metadata
            ),
        },
    }


def _table(counter: dict[str, int], limit: int = 15) -> str:
    rows = ["| Value | Count |", "|---|---:|"]
    ordered = sorted(counter.items(), key=lambda item: (-item[1], item[0]))[:limit]
    rows.extend(f"| `{value or '(blank)'}` | {count:,} |" for value, count in ordered)
    return "\n".join(rows)


def _counter_records(
    counter: dict[str, int] | Counter[str], label: str = "value"
) -> list[dict[str, str | int]]:
    """Return case-preserving JSON records that PowerShell can deserialize safely."""
    return [
        {label: value, "count": count}
        for value, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]


def _record_table(
    records: list[dict[str, str | int]], label: str, limit: int = 15
) -> str:
    rows = ["| Value | Count |", "|---|---:|"]
    rows.extend(
        f"| `{item[label] or '(blank)'}` | {item['count']:,} |"
        for item in records[:limit]
    )
    return "\n".join(rows)


def render_dataset_profile(result: dict[str, object]) -> str:
    metadata = result["metadata"]
    points = result["points"]
    joins = result["joins"]
    coverage = result["coverage"]
    parse_counts = points["notation_parse_counts"]
    attributes = points["notation_attribute_counts"]
    raw_by_tour = Counter()
    usable_by_tour = Counter()
    for filename, count in points["raw_rows_by_file"].items():
        raw_by_tour[_tour(filename)] += count
    for filename, count in points["usable_rows_by_file"].items():
        usable_by_tour[_tour(filename)] += count

    file_rows = ["| File | Bytes | SHA-256 |", "|---|---:|---|"]
    file_rows.extend(
        f"| `{item['file']}` | {item['bytes']:,} | `{item['sha256']}` |"
        for item in result["files"]
    )
    field_rows = [
        "| Point field | Rows | Non-empty | Completeness | Valid | Valid rate |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for field, counts in points["field_counts"].items():
        field_rows.append(
            f"| `{field}` | {counts['rows']:,} | {counts['nonempty']:,} | "
            f"{counts['nonempty'] / counts['rows']:.1%} | {counts['valid']:,} | "
            f"{counts['valid'] / counts['rows']:.1%} |"
        )
    aggregate_rows = [
        "| Aggregate | Tour | Rows | Charted matches covered | Coverage | Players | Orphan IDs | Conflicting grain groups | Invalid numeric values |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    aggregate_rows.extend(
        f"| `{item['file']}` | {item['tour']} | {item['rows']:,} | {item['charted_matches_covered']:,} | "
        f"{item['charted_matches_covered'] / coverage['charted_matches_by_tour'][item['tour']]:.1%} | "
        f"{item['players']:,} | {item['orphan_match_ids']:,} | "
        f"{item['conflicting_grain_groups']:,} | {item['invalid_numeric_values']:,} |"
        for item in result["aggregates"]
    )
    player_rows = ["| Player | Matches |", "|---|---:|"]
    player_rows.extend(f"| `{player}` | {count:,} |" for player, count in coverage["top_players_by_matches"])
    exposure_rows = [
        "| Exposure per player | Minimum | P25 | Median | P75 | Maximum |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for label, values in coverage["exposure_five_number"].items():
        exposure_rows.append(
            f"| {label.replace('_', ' ').title()} | {values['minimum']:,} | {values['p25']:,} | "
            f"{values['median']:,} | {values['p75']:,} | {values['maximum']:,} |"
        )
    parser_tour_rows = ["| Tour | Cells | Parsed | Success |", "|---|---:|---:|---:|"]
    for tour, values in sorted(coverage["parser_coverage_by_tour"].items()):
        parser_tour_rows.append(
            f"| {tour} | {values['cells']:,} | {values['valid']:,} | "
            f"{values['valid'] / max(values['cells'], 1):.1%} |"
        )
    parser_season_rows = ["| Season | Cells | Parsed | Success |", "|---|---:|---:|---:|"]
    for season, values in sorted(coverage["parser_coverage_by_season"].items()):
        parser_season_rows.append(
            f"| {season} | {values['cells']:,} | {values['valid']:,} | "
            f"{values['valid'] / max(values['cells'], 1):.1%} |"
        )
    parser_player_rows = [
        "| Player | Matches | Cells | Parsed | Success |",
        "|---|---:|---:|---:|---:|",
    ]
    for values in coverage["parser_coverage_for_most_charted_players"]:
        parser_player_rows.append(
            f"| `{values['player']}` | {values['matches']:,} | {values['cells']:,} | "
            f"{values['valid']:,} | {values['valid'] / max(values['cells'], 1):.1%} |"
        )

    return f"""# Complete MCP snapshot profile

**Generated:** {result['generated_on']}

**Snapshot ID:** `{result['snapshot_id']}`

**Official source commit:** `{result['source_commit'] or 'unavailable'}`

**Parser version:** `{result['parser_version']}`

**Scope:** six point shards, two match metadata files, and twelve behavior-relevant aggregate files

## Counts

| Measure | ATP | WTA | Total |
|---|---:|---:|---:|
| Raw point rows | {raw_by_tour['ATP']:,} | {raw_by_tour['WTA']:,} | {points['raw_rows']:,} |
| Usable logical point rows | {usable_by_tour['ATP']:,} | {usable_by_tour['WTA']:,} | {points['usable_point_rows']:,} |
| Players in match metadata | {metadata['players_by_tour'].get('ATP', 0):,} | {metadata['players_by_tour'].get('WTA', 0):,} | {sum(metadata['players_by_tour'].values()):,} |
| Safely joined charted matches | {coverage['charted_matches_by_tour'].get('ATP', 0):,} | {coverage['charted_matches_by_tour'].get('WTA', 0):,} | {joins['charted_match_ids']:,} |
| Players in safely joined matches | {coverage['charted_players_by_tour'].get('ATP', 0):,} | {coverage['charted_players_by_tour'].get('WTA', 0):,} | {coverage['players_in_charted_matches']:,} |

| Integrity check | Count |
|---|---:|
| Unique point keys | {points['unique_point_keys']:,} |
| Duplicate point-key groups | {points['duplicate_groups']:,} |
| Exact duplicate groups | {points['exact_duplicate_groups']:,} |
| Conflicting duplicate groups | {points['conflicting_duplicate_groups']:,} |
| Raw rows in conflicting groups | {points['conflicting_raw_rows']:,} |
| Unique metadata match IDs | {metadata['unique_match_ids']:,} |
| Conflicting metadata IDs | {metadata['conflicting_match_ids']:,} |
| Structurally anomalous metadata IDs | {metadata['anomalous_match_ids']:,} |
| Safely joined charted matches | {joins['charted_match_ids']:,} |
| Point match IDs without safe metadata | {joins['point_match_ids_without_safe_metadata']:,} |
| Point match IDs absent from metadata | {joins['point_match_ids_absent_from_metadata']:,} |
| Point match IDs with conflicting metadata | {joins['point_match_ids_with_conflicting_metadata']:,} |
| Point match IDs with structurally anomalous metadata | {joins['point_match_ids_with_anomalous_metadata']:,} |
| Safe metadata IDs without points | {joins['safe_metadata_ids_without_points']:,} |

The usable-point policy collapses exact duplicate keys and excludes conflicting keys. It does
not repair or select among conflicting annotations.

## Point-field coverage after duplicate handling

{chr(10).join(field_rows)}

For `1st`, `2nd`, and `Notes`, “valid” means non-empty only. Shot-notation validity remains an
open parser question. A blank `2nd` value usually means no second serve and is not automatically
a data-quality failure; feature denominators must reflect tennis semantics.

## Notation preflight

| Check | Count |
|---|---:|
| Non-empty first-serve cells | {points['notation_nonempty'].get('1st', 0):,} |
| Non-empty second-serve cells | {points['notation_nonempty'].get('2nd', 0):,} |
| First-serve cells containing undocumented characters | {points['undocumented_notation_cells'].get('1st', 0):,} |
| Second-serve cells containing undocumented characters | {points['undocumented_notation_cells'].get('2nd', 0):,} |

### Undocumented characters

{_record_table(points['undocumented_notation_characters'], 'character', 30)}

### Whole-point and exceptional codes

{_table(points['special_notation_codes'], 10)}

### Parser foundation result

| Cell | Parsed | Rejected | Parse success |
|---|---:|---:|---:|
| First serve | {parse_counts.get('1st_valid', 0):,} | {parse_counts.get('1st_invalid', 0):,} | {parse_counts.get('1st_valid', 0) / parse_counts.get('1st_cells', 1):.1%} |
| Second serve | {parse_counts.get('2nd_valid', 0):,} | {parse_counts.get('2nd_invalid', 0):,} | {parse_counts.get('2nd_valid', 0) / parse_counts.get('2nd_cells', 1):.1%} |

| Parsed attribute | Observed | Eligible parsed denominator | Coverage |
|---|---:|---:|---:|
| Known serve direction | {attributes.get('known_serve_direction', 0):,} | {attributes.get('regular_serve_cells', 0):,} | {attributes.get('known_serve_direction', 0) / max(attributes.get('regular_serve_cells', 0), 1):.1%} |
| Known shot direction | {attributes.get('shots_with_known_direction', 0):,} | {attributes.get('parsed_shots', 0):,} | {attributes.get('shots_with_known_direction', 0) / max(attributes.get('parsed_shots', 0), 1):.1%} |
| Known return direction | {attributes.get('returns_with_known_direction', 0):,} | {attributes.get('parsed_returns', 0):,} | {attributes.get('returns_with_known_direction', 0) / max(attributes.get('parsed_returns', 0), 1):.1%} |
| Known return depth | {attributes.get('returns_with_known_depth', 0):,} | {attributes.get('parsed_returns', 0):,} | {attributes.get('returns_with_known_depth', 0) / max(attributes.get('parsed_returns', 0), 1):.1%} |

Most common parser rejection classes:

{_table(points['notation_parse_issues'], 15)}

Most common rejection classes with the character found at the failing position:

{_record_table(points['notation_parse_issue_characters'], 'issue_character', 20)}

### Parser coverage by tour

{chr(10).join(parser_tour_rows)}

### Parser coverage by season

{chr(10).join(parser_season_rows)}

### Parser coverage for the most-charted players

{chr(10).join(parser_player_rows)}

The parser result is a conservative foundation, not a final validity claim. Rejection classes must
be manually reviewed against the workbook before any normalization rule is added. Field-aware
attribute rates include only safely decoded prefixes and can change as parser coverage improves.

## Charted-match coverage

### Surface

{_table(coverage['surfaces'])}

### Tournament

{_table(coverage['tournaments'])}

### Round

{_table(coverage['rounds'])}

### Most-charted players

{chr(10).join(player_rows)}

These are exposure counts within a crowdsourced sample, not population rankings.

### Exposure distribution

{chr(10).join(exposure_rows)}

## Published aggregate-file coverage

{chr(10).join(aggregate_rows)}

Aggregate rows are generated from MCP notation. Their presence is useful for feasibility and
cross-checking, but it does not replace parser validation or prove that every denominator is
complete. The reported grain uses the available match/player-or-server/row-or-set keys. Conflicts
are excluded from feature consideration until they can be reconciled with raw point annotations.

## Snapshot files

{chr(10).join(file_rows)}

The machine-readable companion is `research/mcp_snapshot_profile.json`.
"""


def render_feasibility(result: dict[str, object]) -> str:
    points = result["points"]
    joins = result["joins"]
    aggregates = result["aggregates"]
    parse_counts = points["notation_parse_counts"]
    aggregate_matches = max(item["charted_matches_covered"] for item in aggregates)
    return f"""# MCP data feasibility

**Status:** Phase 2 data foundation; serve candidates show provisional aggregate persistence but
are not approved for publication.

## Established for this snapshot

- Six ATP/WTA point shards were profiled at official commit `{result['source_commit']}`.
- {points['raw_rows']:,} raw point rows produce {points['usable_point_rows']:,} usable logical points under the conservative duplicate policy.
- {joins['charted_match_ids']:,} point-bearing matches join to unambiguous MCP metadata.
- Behavior-relevant aggregate files cover as many as {aggregate_matches:,} matches, depending on the aggregate and its row semantics.
- Draft parser success is {parse_counts.get('1st_valid', 0) / max(parse_counts.get('1st_cells', 0), 1):.1%} for non-empty first-serve cells and {parse_counts.get('2nd_valid', 0) / max(parse_counts.get('2nd_cells', 0), 1):.1%} for non-empty second-serve cells.
- Field-aware serve prefixes and outcomes are independently reconciled in `research/mcp_serve_reconciliation.md`.

## Data-quality decision

**PROCEED TO CONTEXT-CONTROLLED FALSIFICATION:** versioned serve outcome and direction candidates
have software-consistency evidence and provisional aggregate split-sample persistence. This does
not approve a player profile or Tennis DNA vector.

**EXPLORATORY ONLY:** return, rally, ending, and net families still require parser and denominator
work before feature nomination.

**BLOCKED:** population-level claims, player rankings, similarity scores, clusters, and confidence
tiers remain blocked by selected charting coverage, unresolved aggregate grains, parser validity,
and untested context-controlled profile stability.

## Candidate families for the next audit

| Family | Evidence now available | Next gate |
|---|---|---|
| Serve outcomes and direction | Field-aware parsing, strong reconciliation, and aggregate split persistence | Context sensitivity, shrinkage, and player-level uncertainty |
| Return behavior and depth | Raw notation plus ReturnDepth aggregates | Missingness semantics and player-side validation |
| Shot selection and direction | Raw notation plus ShotTypes aggregates | Shot-code parser and redundancy review |
| Rally behavior | Raw notation plus Rally aggregates | Row-category and rally-denominator validation |
| Winners and errors | Overview/ShotTypes/Rally aggregates | Cross-file agreement and point-ending semantics |
| Net usage | NetPoints aggregates and notation | Approach definition and sparse-denominator audit |

No family should enter Tennis DNA merely because an aggregate CSV exists. Serve nomination is
documented in `research/serve_feature_candidates.md` and remains subject to falsification.

## Reproduce

```powershell
python -m research.experiments.profile_mcp_snapshot
```
"""


def render_sampling_bias(result: dict[str, object]) -> str:
    coverage = result["coverage"]
    exposure = coverage["exposure_five_number"]
    return f"""# MCP sampling bias and eligibility risks

## Established limitation

The Match Charting Project is crowdsourced. Its {result['joins']['charted_match_ids']:,} safely
joined point-bearing matches are not a random sample of professional tennis. Dataset size does not
remove famous-player, event, round, era, surface, or contributor selection effects.

## Observed dimensions

- Players represented in point-bearing matches: {coverage['players_in_charted_matches']:,}.
- Median matches per represented player: {exposure['matches_per_player']['median']:,}; maximum: {exposure['matches_per_player']['maximum']:,}.
- Median usable point exposure per represented player: {exposure['points_per_player']['median']:,}; maximum: {exposure['points_per_player']['maximum']:,}.
- Median distinct opponents per represented player: {exposure['opponents_per_player']['median']:,}; maximum: {exposure['opponents_per_player']['maximum']:,}.
- Median represented surfaces per player: {exposure['surfaces_per_player']['median']:,} of at most four source labels.
- Surface, tournament, round, player, and opponent exposure are recorded in the machine-readable profile.
- Ranking-band coverage is unavailable until the MCP-to-ATP/WTA match join is implemented and validated.

## Eligibility remains an open question

No minimum-match threshold or HIGH/MEDIUM/LOW confidence label is approved. A future eligibility
analysis must jointly evaluate usable matches, field-specific point/shot denominators, opponent and
surface diversity, temporal coverage, and split-sample stability. Threshold sensitivity must be
reported rather than selecting a convenient cutoff.

## Claim boundary

Use “in the charted MCP sample” for player descriptions. Do not infer that a profile represents all
matches played by that player, an entire tour, or causal playing-style traits.
"""


def render_parser_baseline(result: dict[str, object]) -> str:
    points = result["points"]
    coverage = result["coverage"]
    counts = points["notation_parse_counts"]
    attributes = points["notation_attribute_counts"]
    first_cells = counts.get("1st_cells", 0)
    second_cells = counts.get("2nd_cells", 0)
    issue_rows = ["| Rejection | Cells |", "|---|---:|"]
    issue_rows.extend(
        f"| `{label}` | {count:,} |"
        for label, count in sorted(
            points["notation_parse_issues"].items(), key=lambda item: (-item[1], item[0])
        )[:20]
    )
    component_rows = [
        "| Cell | Component | Observed | Unknown | Absent | Partial | Invalid | N/A |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    states = points["notation_component_states"]
    for field in ("1st", "2nd"):
        for component in ("serve_direction", "serve_and_volley", "rally", "outcome"):
            component_rows.append(
                f"| {field} | {component.replace('_', ' ')} | "
                f"{states.get(f'{field}:{component}:observed', 0):,} | "
                f"{states.get(f'{field}:{component}:unknown', 0):,} | "
                f"{states.get(f'{field}:{component}:absent', 0):,} | "
                f"{states.get(f'{field}:{component}:partial', 0):,} | "
                f"{states.get(f'{field}:{component}:invalid', 0):,} | "
                f"{states.get(f'{field}:{component}:not_applicable', 0):,} |"
            )
    era_ranges = (
        ("through 2009", 0, 2009),
        ("2010-2018", 2010, 2018),
        ("2019", 2019, 2019),
        ("2020-2023", 2020, 2023),
        ("2024-2026", 2024, 2026),
    )
    era_rows = ["| Match era | Cells | Parsed | Success |", "|---|---:|---:|---:|"]
    direction_era_rows = [
        "| Match era | All notation cells | Extractable direction | Known direction | Known / extractable |",
        "|---|---:|---:|---:|---:|",
    ]
    for label, first_year, last_year in era_ranges:
        cells = sum(
            values["cells"]
            for season, values in coverage["parser_coverage_by_season"].items()
            if first_year <= int(season) <= last_year
        )
        valid = sum(
            values["valid"]
            for season, values in coverage["parser_coverage_by_season"].items()
            if first_year <= int(season) <= last_year
        )
        era_rows.append(
            f"| {label} | {cells:,} | {valid:,} | {valid / max(cells, 1):.1%} |"
        )
        direction_eligible = sum(
            values["eligible"]
            for season, values in coverage["serve_direction_coverage_by_season"].items()
            if first_year <= int(season) <= last_year
        )
        direction_known = sum(
            values["known"]
            for season, values in coverage["serve_direction_coverage_by_season"].items()
            if first_year <= int(season) <= last_year
        )
        direction_era_rows.append(
            f"| {label} | {cells:,} | {direction_eligible:,} | {direction_known:,} | "
            f"{direction_known / max(direction_eligible, 1):.1%} |"
        )
    player_rates = [
        (
            values["player"],
            values["matches"],
            values["valid"] / max(values["cells"], 1),
        )
        for values in coverage["parser_coverage_for_most_charted_players"]
    ]
    lowest_player = min(player_rates, key=lambda item: item[2])
    highest_player = max(player_rates, key=lambda item: item[2])
    direction_player_rates = [
        (
            values["player"],
            values["matches"],
            values["known"] / max(values["eligible"], 1),
        )
        for values in coverage["serve_direction_coverage_for_most_charted_players"]
    ]
    lowest_direction_player = min(direction_player_rates, key=lambda item: item[2])
    highest_direction_player = max(direction_player_rates, key=lambda item: item[2])
    author_rows = [
        "| Chart author | Cells | Whole-cell success | Extractable serve directions | Known / extractable |",
        "|---|---:|---:|---:|---:|",
    ]
    direction_by_author = {
        values["chart_author"]: values
        for values in coverage["serve_direction_coverage_by_chart_author"]
    }
    for author_parser in sorted(
        coverage["parser_coverage_by_chart_author"],
        key=lambda item: (-item["cells"], item["chart_author"]),
    )[:20]:
        author = author_parser["chart_author"]
        author_direction = direction_by_author[author]
        author_rows.append(
            f"| `{author}` | {author_parser['cells']:,} | "
            f"{author_parser['valid'] / max(author_parser['cells'], 1):.1%} | "
            f"{author_direction['eligible']:,} | "
            f"{author_direction['known'] / max(author_direction['eligible'], 1):.1%} |"
        )
    return f"""# MCP notation parser baseline

**Snapshot:** `{result['snapshot_id']}`

**Parser:** `{result['parser_version']}`

**Status:** draft engineering result; no behavioral feature is approved

## Parse result

| Cell | Non-empty cells | Parsed | Rejected | Success |
|---|---:|---:|---:|---:|
| First serve | {first_cells:,} | {counts.get('1st_valid', 0):,} | {counts.get('1st_invalid', 0):,} | {counts.get('1st_valid', 0) / max(first_cells, 1):.1%} |
| Second serve | {second_cells:,} | {counts.get('2nd_valid', 0):,} | {counts.get('2nd_invalid', 0):,} | {counts.get('2nd_valid', 0) / max(second_cells, 1):.1%} |

## Rejection classes

{chr(10).join(issue_rows)}

The largest class is a valid serve/shot prefix followed by a token that the simplified official
grammar does not permit at that position. Depth-like codes on non-return shots account for much of
this class. These forms remain rejected until their semantics are documented and tested.

## Field-aware component states

{chr(10).join(component_rows)}

A cell with any issue remains rejected as a whole. The v0.2 component states retain only fields
decoded before the issue; they do not reinterpret or normalize the unsupported suffix.

## Attribute coverage among currently parsed cells

| Attribute | Observed | Parsed denominator | Coverage |
|---|---:|---:|---:|
| Known serve direction | {attributes.get('known_serve_direction', 0):,} | {attributes.get('regular_serve_cells', 0):,} | {attributes.get('known_serve_direction', 0) / max(attributes.get('regular_serve_cells', 0), 1):.1%} |
| Known shot direction | {attributes.get('shots_with_known_direction', 0):,} | {attributes.get('parsed_shots', 0):,} | {attributes.get('shots_with_known_direction', 0) / max(attributes.get('parsed_shots', 0), 1):.1%} |
| Known return direction | {attributes.get('returns_with_known_direction', 0):,} | {attributes.get('parsed_returns', 0):,} | {attributes.get('returns_with_known_direction', 0) / max(attributes.get('parsed_returns', 0), 1):.1%} |
| Known return depth | {attributes.get('returns_with_known_depth', 0):,} | {attributes.get('parsed_returns', 0):,} | {attributes.get('returns_with_known_depth', 0) / max(attributes.get('parsed_returns', 0), 1):.1%} |

These are field-level diagnostic rates over safely decoded prefixes. Each feature still needs its
own eligibility and denominator audit.

## Coverage shift by match era

{chr(10).join(era_rows)}

**ESTABLISHED FOR THIS PARSER AND SNAPSHOT:** acceptance varies materially by match era. It is not
missing completely at random. Among the twenty most-charted players, acceptance ranges from
{lowest_player[2]:.1%} for {lowest_player[0]} ({lowest_player[1]:,} matches) to
{highest_player[2]:.1%} for {highest_player[0]} ({highest_player[1]:,} matches). Consequently,
parser-derived player or era comparisons would currently mix tennis behavior with notation-version
and charting-practice effects.

## Serve-direction extraction despite whole-cell rejection

{chr(10).join(direction_era_rows)}

**ESTABLISHED FOR THIS PARSER AND SNAPSHOT:** safely extracting the serve prefix removes most of the
era variation affecting whole-cell parsing. Among the twenty most-charted players, known direction
coverage within extractable serve prefixes ranges from {lowest_direction_player[2]:.1%} for
{lowest_direction_player[0]} ({lowest_direction_player[1]:,} matches) to
{highest_direction_player[2]:.1%} for {highest_direction_player[0]}
({highest_direction_player[1]:,} matches). This is necessary but not sufficient for feature
approval; court-side, serve-number, and aggregate agreement remain separate gates.

## Coverage by chart author

{chr(10).join(author_rows)}

The table shows the twenty authors with the most notation cells; all authors remain in the
machine-readable profile. Author differences describe data-production patterns and must not be
interpreted as player behavior.

## Gate decision

**PROCEED WITH A SERVE-ONLY STABILITY PILOT:** field-aware serve prefixes have strong aggregate
agreement and explicit missingness. No player feature is approved for publication. Continue parser
revision for return/rally/net families and investigate serve exceptions, context dependence, and
split-sample persistence before constructing Tennis DNA profiles.
"""


def render_serve_reconciliation(result: dict[str, object]) -> str:
    reconciliation = result["serve_reconciliation"]
    overview_rows = [
        "| Metric | Comparable match-player records | Exact | Exact rate | Mean absolute difference |",
        "|---|---:|---:|---:|---:|",
    ]
    for metric in OVERVIEW_METRICS:
        values = reconciliation["overview"][metric]
        exact_rate = values["exact_rate"]
        mean_difference = values["mean_absolute_difference"]
        overview_rows.append(
            f"| `{metric}` | {values['comparable_records']:,} | {values['exact_records']:,} | "
            f"{exact_rate:.1%} | {mean_difference:.3f} |"
        )
    direction_rows = [
        "| Aggregate row | Comparable | Exact wide/body/T | Marginal exact rate | Exact deuce/ad vector | Side-aware exact rate |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row_name in ("1", "2", "Total"):
        values = reconciliation["serve_direction"][row_name]
        direction_rows.append(
            f"| `{row_name}` | {values['comparable_records']:,} | "
            f"{values['marginal_exact_records']:,} | {values['marginal_exact_rate']:.1%} | "
            f"{values['exact_records']:,} | {values['exact_rate']:.1%} |"
        )
    context_rows = [
        "| Comparison | Mismatches | ATP rate | WTA rate | Largest surface count (rate) | Largest author count (rate) | Largest season count (rate) |",
        "|---|---:|---:|---:|---|---|---|",
    ]
    context_sources = [
        (f"Overview `{metric}`", reconciliation["overview"][metric])
        for metric in OVERVIEW_METRICS
    ] + [
        (f"ServeDirection `{row_name}`", reconciliation["serve_direction"][row_name])
        for row_name in ("1", "2", "Total")
    ]
    for label, values in context_sources:
        mismatch_count = values["comparable_records"] - values["exact_records"]
        tours = {row["tour"]: row for row in values["mismatch_context"]["tour"]}
        top_surface = values["mismatch_context"]["surface"][0]
        top_author = values["mismatch_context"]["chart_author"][0]
        top_season = values["mismatch_context"]["season"][0]
        context_rows.append(
            f"| {label} | {mismatch_count:,} | "
            f"{tours['ATP']['mismatch_rate']:.2%} | {tours['WTA']['mismatch_rate']:.2%} | "
            f"`{top_surface['surface']}`: {top_surface['mismatch_records']:,} "
            f"({top_surface['mismatch_rate']:.2%}) | "
            f"`{top_author['chart_author']}`: {top_author['mismatch_records']:,} "
            f"({top_author['mismatch_rate']:.2%}) | "
            f"`{top_season['season']}`: {top_season['mismatch_records']:,} "
            f"({top_season['mismatch_rate']:.2%}) |"
        )
    overview_source = reconciliation["overview_source"]
    direction_source = reconciliation["serve_direction_source"]
    return f"""# MCP serve reconciliation

**Snapshot:** `{result['snapshot_id']}`

**Parser:** `{result['parser_version']}`

**Status:** raw-notation validation evidence; no player feature is approved by this report alone

## Question

Do independently parsed raw serve records reproduce the match-player totals published in MCP
`Overview` and `ServeDirection` aggregates?

## Source-grain integrity

| Source | Raw grain groups | Safe groups | Duplicate groups | Conflicting groups | Invalid rows |
|---|---:|---:|---:|---:|---:|
| Overview `Total` | {overview_source['raw_grain_groups']:,} | {overview_source['safe_grain_groups']:,} | {overview_source['duplicate_grain_groups']:,} | {overview_source['conflicting_grain_groups']:,} | {overview_source['invalid_rows']:,} |
| ServeDirection `1`/`2`/`Total` | {direction_source['raw_grain_groups']:,} | {direction_source['safe_grain_groups']:,} | {direction_source['duplicate_grain_groups']:,} | {direction_source['conflicting_grain_groups']:,} | {direction_source['invalid_rows']:,} |

Exact duplicate aggregate rows are collapsed. Conflicting grain groups are excluded rather than
selected. Raw notation uses the same point-key policy as the complete snapshot profile.

## Overview agreement

{chr(10).join(overview_rows)}

The source column `second_in` is retained by name for reconciliation. In inspected MCP aggregates it
behaves as a second-serve-attempt count, including double faults; this empirical interpretation is
not silently renamed into a product feature.

## ServeDirection agreement

{chr(10).join(direction_rows)}

A direction record is comparable only when every contributing raw serve has a known court side,
serve number, and direction. Marginal agreement compares wide/body/T after summing over court side;
side-aware agreement requires all six deuce/ad by wide/body/T cells to agree. This separation tests
whether discrepancies arise in notation direction or in court-side reconstruction.

## Mismatch context

{chr(10).join(context_rows)}

Counts identify where mismatches accumulate; parenthetical values are stratum-specific rates using
only comparable records as denominators. The full surface, case-preserving author, and season
breakdown is stored as record lists in the machine-readable profile. Concentration is a
data-production warning, not evidence that a contributor caused the discrepancy.

## Interpretation boundary

Agreement shows software consistency with MCP's convenience aggregates; it does not independently
validate the source charting, remove sample-selection bias, or prove temporal player-style stability.
Mismatch examples, context denominators, and metric-specific missingness remain available in the
machine-readable profile.

## Reproduce

```powershell
python -m research.experiments.profile_mcp_snapshot
```
"""


def write_outputs(result: dict[str, object], report_root: Path = DEFAULT_REPORT_ROOT) -> None:
    report_root.mkdir(parents=True, exist_ok=True)
    (report_root / "mcp_snapshot_profile.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    (report_root / "dataset_profile.md").write_text(
        render_dataset_profile(result), encoding="utf-8"
    )
    (report_root / "data_feasibility.md").write_text(
        render_feasibility(result), encoding="utf-8"
    )
    (report_root / "sampling_bias.md").write_text(
        render_sampling_bias(result), encoding="utf-8"
    )
    (report_root / "mcp_notation_parser_baseline.md").write_text(
        render_parser_baseline(result), encoding="utf-8"
    )
    (report_root / "mcp_serve_reconciliation.md").write_text(
        render_serve_reconciliation(result), encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT_ROOT)
    arguments = parser.parse_args()
    result = profile_snapshot(arguments.source)
    write_outputs(result, arguments.output)
    print(f"Profiled MCP commit {result['source_commit'] or 'unknown'}")
    print(f"Wrote {arguments.output / 'mcp_snapshot_profile.json'}")
    print(f"Wrote {arguments.output / 'dataset_profile.md'}")
    print(f"Wrote {arguments.output / 'data_feasibility.md'}")
    print(f"Wrote {arguments.output / 'sampling_bias.md'}")
    print(f"Wrote {arguments.output / 'mcp_notation_parser_baseline.md'}")
    print(f"Wrote {arguments.output / 'mcp_serve_reconciliation.md'}")


if __name__ == "__main__":
    main()
