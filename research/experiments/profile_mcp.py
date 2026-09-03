"""Generate reproducible feasibility reports for the local MCP snapshot."""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

ROOT = Path("data/raw/mcp")
REPORT_ROOT = Path("research")
POINT_PATH = ROOT / "charting-w-points-to-2009.csv"
MATCH_PATH = ROOT / "charting-w-matches.csv"

POINT_FIELDS = (
    "match_id",
    "Pt",
    "Set1",
    "Set2",
    "Gm1",
    "Gm2",
    "Pts",
    "Gm#",
    "TbSet",
    "Svr",
    "1st",
    "2nd",
    "Notes",
    "PtWinner",
)
DATA_DICTIONARY_FIELDS = {
    "1stSV",
    "2ndSV",
    "1stIn",
    "2ndIn",
    "isAce",
    "isUnret",
    "isRallyWinner",
    "isForced",
    "isUnforced",
    "isDouble",
    "isSvrWinner",
    "rallyCount",
}


def parse_date(value: str) -> datetime | None:
    try:
        return datetime.strptime(value, "%Y%m%d")
    except ValueError:
        return None


def quantiles(values: list[int]) -> tuple[float, float, float, float, float]:
    ordered = sorted(values)
    if not ordered:
        return (math.nan,) * 5
    positions = [0, 0.25, 0.5, 0.75, 1]
    result = []
    for position in positions:
        index = round(position * (len(ordered) - 1))
        result.append(float(ordered[index]))
    return tuple(result)  # type: ignore[return-value]


def distribution_table(counter: Counter[str], limit: int = 10) -> str:
    rows = ["| Value | Count |", "|---|---:|"]
    for value, count in counter.most_common(limit):
        rows.append(f"| `{value or '(blank)'}` | {count:,} |")
    return "\n".join(rows)


def is_valid_value(field: str, value: str) -> bool:
    if not value.strip():
        return False
    if field in {"Pt", "Set1", "Set2", "Gm1", "Gm2"}:
        return value.isdigit()
    if field in {"Svr", "PtWinner"}:
        return value in {"1", "2"}
    if field == "TbSet":
        return value.lower() in {"true", "false", "0", "1"}
    return True


def coverage_table(
    point_rows: list[dict[str, str]],
    match_by_id: dict[str, dict[str, str]],
    field: str,
    dimension: str,
) -> str:
    totals: Counter[str] = Counter()
    present: Counter[str] = Counter()
    for row in point_rows:
        metadata = match_by_id.get(row["match_id"])
        if metadata is None:
            continue
        if dimension == "season":
            date = parse_date(metadata["Date"])
            group = str(date.year) if date else "invalid-date"
            groups = (group,)
        elif dimension == "tournament":
            groups = (metadata["Tournament"],)
        elif dimension == "player":
            groups = (metadata["Player 1"], metadata["Player 2"])
        else:
            raise ValueError(f"unsupported coverage dimension: {dimension}")
        for group in groups:
            totals[group] += 1
            present[group] += int(bool(row.get(field, "").strip()))
    rows = [f"| {dimension.title()} | Rows | Non-empty | Coverage |", "|---|---:|---:|---:|"]
    for group, total in totals.most_common(10):
        rows.append(f"| `{group or '(blank)'}` | {total:,} | {present[group]:,} | {present[group] / total:.1%} |")
    return "\n".join(rows)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def duplicate_profile(
    rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, int]]:
    """Apply the documented duplicate policy and return auditable counts."""

    grouped: defaultdict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    order: list[tuple[str, str]] = []
    for row in rows:
        key = (row.get("match_id", ""), row.get("Pt", ""))
        if key not in grouped:
            order.append(key)
        grouped[key].append(row)

    usable: list[dict[str, str]] = []
    counts = {
        "groups": 0,
        "exact": 0,
        "conflicting": 0,
        "excess_rows": 0,
        "conflicting_rows": 0,
    }
    for key in order:
        records = grouped[key]
        if len(records) == 1:
            usable.append(records[0])
            continue
        counts["groups"] += 1
        counts["excess_rows"] += len(records) - 1
        signatures = {tuple(sorted(record.items())) for record in records}
        if len(signatures) == 1:
            counts["exact"] += 1
            usable.append(records[0])
        else:
            counts["conflicting"] += 1
            counts["conflicting_rows"] += len(records)
    return usable, counts


def profile(
    point_path: Path = POINT_PATH,
    match_path: Path = MATCH_PATH,
) -> dict[str, object]:
    with match_path.open(newline="", encoding="utf-8-sig") as source:
        match_reader = csv.DictReader(source)
        match_fields = tuple(match_reader.fieldnames or ())
        matches = list(match_reader)
    required_match_fields = {
        "match_id", "Date", "Tournament", "Round", "Surface", "Best of", "Player 1", "Player 2"
    }
    if missing := required_match_fields.difference(match_fields):
        raise ValueError(f"missing MCP match columns: {sorted(missing)}")

    metadata_groups: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in matches:
        metadata_groups[row["match_id"]].append(row)
    metadata_duplicate_ids = sum(len(rows) > 1 for rows in metadata_groups.values())
    conflicting_metadata_ids = sum(
        len(rows) > 1
        and len({tuple(sorted(row.items())) for row in rows}) > 1
        for rows in metadata_groups.values()
    )
    match_by_id = {
        match_id: rows[0]
        for match_id, rows in metadata_groups.items()
        if len({tuple(sorted(row.items())) for row in rows}) == 1
    }

    point_rows: list[dict[str, str]] = []
    with point_path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        actual_fields = tuple(reader.fieldnames or ())
        missing = set(POINT_FIELDS).difference(actual_fields)
        if missing:
            raise ValueError(f"missing MCP point columns: {sorted(missing)}")
        for row in reader:
            point_rows.append(row)

    usable_point_rows, duplicate_counts = duplicate_profile(point_rows)
    point_match_ids = {row["match_id"] for row in point_rows}
    orphan_match_ids = point_match_ids.difference(match_by_id)
    orphan_point_rows = sum(row["match_id"] in orphan_match_ids for row in usable_point_rows)
    matched_point_rows = [row for row in usable_point_rows if row["match_id"] in match_by_id]
    player_match_counts: Counter[str] = Counter()
    player_point_counts: Counter[str] = Counter()
    point_fields: dict[str, dict[str, int]] = {}
    for field in actual_fields:
        values = [row.get(field, "") for row in usable_point_rows]
        nonempty = sum(bool(value.strip()) for value in values)
        point_fields[field] = {
            "rows": len(values),
            "nonempty": nonempty,
            "null": len(values) - nonempty,
            "valid": sum(is_valid_value(field, value) for value in values),
        }

    for match_id in point_match_ids:
        metadata = match_by_id.get(match_id)
        if metadata is None:
            continue
        for player_key in ("Player 1", "Player 2"):
            player = metadata[player_key]
            player_match_counts[player] += 1
    for row in matched_point_rows:
        metadata = match_by_id.get(row["match_id"])
        if metadata is None:
            continue
        for player_key in ("Player 1", "Player 2"):
            player_point_counts[metadata[player_key]] += 1

    match_dates = [parse_date(row["Date"]) for row in matches]
    charted_metadata = [match_by_id[match_id] for match_id in point_match_ids if match_id in match_by_id]
    seasons = Counter(str(date.year) for date in match_dates if date)
    charted_seasons = Counter(str(parse_date(row["Date"]).year) for row in charted_metadata if parse_date(row["Date"]))
    surfaces = Counter(row["Surface"] for row in matches)
    charted_surfaces = Counter(row["Surface"] for row in charted_metadata)
    tournaments = Counter(row["Tournament"] for row in matches)
    rounds = Counter(row["Round"] for row in matches)
    players = set()
    for row in matches:
        players.update((row["Player 1"], row["Player 2"]))
    charted_players = set()
    for row in charted_metadata:
        charted_players.update((row["Player 1"], row["Player 2"]))
    valid_surfaces = {"Hard", "Clay", "Grass", "Carpet"}
    metadata_anomalies = Counter()
    for row in matches:
        metadata_anomalies["invalid_surface"] += row["Surface"] not in valid_surfaces
        metadata_anomalies["invalid_date"] += parse_date(row["Date"]) is None
        metadata_anomalies["invalid_best_of"] += row["Best of"] not in {"3", "5"}

    charted_tournaments = Counter(row["Tournament"] for row in charted_metadata)
    charted_rounds = Counter(row["Round"] for row in charted_metadata)
    players_by_tour: defaultdict[str, set[str]] = defaultdict(set)
    for row in charted_metadata:
        parts = row["match_id"].split("-")
        tour = "ATP" if len(parts) > 1 and parts[1] == "M" else "WTA" if len(parts) > 1 and parts[1] == "W" else "Unknown"
        players_by_tour[tour].update((row["Player 1"], row["Player 2"]))

    return {
        "matches": matches,
        "charted_metadata": charted_metadata,
        "point_rows": point_rows,
        "usable_point_rows": usable_point_rows,
        "matched_point_rows": matched_point_rows,
        "actual_fields": actual_fields,
        "point_fields": point_fields,
        "point_match_ids": point_match_ids,
        "player_match_counts": player_match_counts,
        "player_point_counts": player_point_counts,
        "seasons": seasons,
        "charted_seasons": charted_seasons,
        "surfaces": surfaces,
        "charted_surfaces": charted_surfaces,
        "tournaments": tournaments,
        "rounds": rounds,
        "players": players,
        "charted_players": charted_players,
        "metadata_anomalies": metadata_anomalies,
        "valid_surfaces": valid_surfaces,
        "duplicate_counts": duplicate_counts,
        "metadata_duplicate_ids": metadata_duplicate_ids,
        "conflicting_metadata_ids": conflicting_metadata_ids,
        "orphan_match_ids": orphan_match_ids,
        "orphan_point_rows": orphan_point_rows,
        "metadata_without_points": len(set(match_by_id).difference(point_match_ids)),
        "charted_tournaments": charted_tournaments,
        "charted_rounds": charted_rounds,
        "players_by_tour": {tour: len(names) for tour, names in players_by_tour.items()},
        "point_path": point_path,
        "match_path": match_path,
        "point_sha256": file_sha256(point_path),
        "match_sha256": file_sha256(match_path),
    }


def write_reports(data: dict[str, object], report_root: Path = REPORT_ROOT) -> None:
    matches = data["matches"]
    charted_metadata = data["charted_metadata"]
    point_rows = data["point_rows"]
    usable_point_rows = data["usable_point_rows"]
    matched_point_rows = data["matched_point_rows"]
    actual_fields = data["actual_fields"]
    point_fields = data["point_fields"]
    player_match_counts = data["player_match_counts"]
    player_point_counts = data["player_point_counts"]
    seasons = data["seasons"]
    charted_seasons = data["charted_seasons"]
    surfaces = data["surfaces"]
    charted_surfaces = data["charted_surfaces"]
    tournaments = data["tournaments"]
    rounds = data["rounds"]
    players = data["players"]
    charted_players = data["charted_players"]
    metadata_anomalies = data["metadata_anomalies"]
    valid_surfaces = data["valid_surfaces"]
    duplicate_counts = data["duplicate_counts"]
    players_by_tour = data["players_by_tour"]

    match_quantiles = quantiles(list(player_match_counts.values()))
    point_quantiles = quantiles(list(player_point_counts.values()))
    unavailable = sorted(DATA_DICTIONARY_FIELDS.difference(actual_fields))
    completeness_rows = ["| Field | Non-empty | Null | Null rate | Valid | Valid rate |", "|---|---:|---:|---:|---:|---:|"]
    for field in actual_fields:
        stats = point_fields[field]
        null_rate = stats["null"] / stats["rows"]
        completeness_rows.append(
            f"| `{field}` | {stats['nonempty']:,} | {stats['null']:,} | {null_rate:.1%} | {stats['valid']:,} | {stats['valid'] / stats['rows']:.1%} |"
        )

    match_by_id = {
        row["match_id"]: row
        for row in charted_metadata
        if row["match_id"] not in data["orphan_match_ids"]
    }
    coverage_sections = []
    for field in ("1st", "2nd", "Notes"):
        for dimension in ("season", "tournament", "player"):
            coverage_sections.append(
                f"### `{field}` by {dimension}\n\n{coverage_table(matched_point_rows, match_by_id, field, dimension)}"
            )

    profile_report = f"""# MCP dataset profile

**Generated:** {date.today().isoformat()}

**Source scope:** `{data['point_path'].name}` and `{data['match_path'].name}`

**Coverage:** women’s charted matches through 2009 in the current local snapshot

## Source snapshot

| File | Bytes | SHA-256 |
|---|---:|---|
| `{data['point_path'].name}` | {data['point_path'].stat().st_size:,} | `{data['point_sha256']}` |
| `{data['match_path'].name}` | {data['match_path'].stat().st_size:,} | `{data['match_sha256']}` |

## Counts

| Measure | Count |
|---|---:|
| Raw match metadata rows | {len(matches):,} |
| Matches with point rows and safe metadata | {len(charted_metadata):,} |
| Raw point rows | {len(point_rows):,} |
| Point rows after safe duplicate policy | {len(usable_point_rows):,} |
| Usable point rows joined to metadata | {len(matched_point_rows):,} |
| Unique players in match metadata | {len(players):,} |
| Players in charted matches | {len(charted_players):,} |
| Unique ATP players in charted matches | {players_by_tour.get('ATP', 0):,} |
| Unique WTA players in charted matches | {players_by_tour.get('WTA', 0):,} |
| Reliable total shots | Not available |

The safe duplicate policy collapses exact copies and excludes every conflicting `(match_id, Pt)` group. It never chooses between conflicting annotations.

## Data integrity

| Check | Count |
|---|---:|
| Duplicate point-key groups | {duplicate_counts['groups']:,} |
| Exact duplicate point-key groups | {duplicate_counts['exact']:,} |
| Conflicting duplicate point-key groups | {duplicate_counts['conflicting']:,} |
| Excess rows in duplicate point groups | {duplicate_counts['excess_rows']:,} |
| Rows excluded in conflicting groups | {duplicate_counts['conflicting_rows']:,} |
| Point match IDs without safe metadata | {len(data['orphan_match_ids']):,} |
| Usable point rows without safe metadata | {data['orphan_point_rows']:,} |
| Safe metadata IDs without point rows | {data['metadata_without_points']:,} |
| Duplicate metadata IDs | {data['metadata_duplicate_ids']:,} |
| Conflicting metadata IDs | {data['conflicting_metadata_ids']:,} |
| Invalid dates | {metadata_anomalies['invalid_date']:,} |
| Invalid surfaces | {metadata_anomalies['invalid_surface']:,} |
| Invalid best-of values | {metadata_anomalies['invalid_best_of']:,} |

Anomaly flags are counted independently. Unsafe metadata IDs are excluded from joins instead of being resolved by guesswork.

The point file currently exposes {len(actual_fields)} fields. The data dictionary lists additional convenience fields, but they are not present in this downloaded file. The `1st` and `2nd` columns contain chart notation strings; their characters cannot be counted as shots without implementing and validating the MCP notation parser.

## Field completeness after duplicate handling

{chr(10).join(completeness_rows)}

`PtWinner`, `Svr`, score counters, and match identifiers are available in the current file. Shot-level behavior is encoded in `1st`/`2nd` and requires a separate notation parser. Fields absent from this file: {', '.join(f'`{field}`' for field in unavailable)}.

For notation and free-text fields, “valid” currently means non-empty only. It does not establish syntactic or semantic validity.

## Coverage

### Seasons

All match metadata:

{distribution_table(seasons, 20)}

Charted matches:

{distribution_table(charted_seasons, 20)}

### Surfaces

All match metadata:

{distribution_table(surfaces)}

Charted matches:

{distribution_table(charted_surfaces)}

Documented surface values are: {', '.join(sorted(valid_surfaces))}. Invalid values remain visible in the all-metadata table as source anomalies.

### Tournaments in charted matches

{distribution_table(data['charted_tournaments'])}

### Rounds in charted matches

{distribution_table(data['charted_rounds'])}

The full match metadata contains records without rows in this local point snapshot. Its tournament and round distributions are not substituted for charted-point coverage.

## Player exposure

| Distribution | Minimum | 25th percentile | Median | 75th percentile | Maximum |
|---|---:|---:|---:|---:|---:|
| Matches per charted player | {match_quantiles[0]:.0f} | {match_quantiles[1]:.0f} | {match_quantiles[2]:.0f} | {match_quantiles[3]:.0f} | {match_quantiles[4]:.0f} |
| Point rows per charted player | {point_quantiles[0]:.0f} | {point_quantiles[1]:.0f} | {point_quantiles[2]:.0f} | {point_quantiles[3]:.0f} | {point_quantiles[4]:.0f} |

The point count assigns each charted point to both participating players, so it is an exposure count, not a count of points won.

## Field coverage by group

The following tables show the ten largest groups by usable, metadata-matched row count. Player tables count each point for both participants; they describe exposure, not independent observations. Coverage means a raw notation string is present, not that its component shots are validly parsed.

{chr(10).join(coverage_sections)}

## Ranking coverage

ATP/WTA ranking fields are not present in the current MCP match metadata snapshot. Ranking-band coverage is therefore unavailable until a separately sourced rankings table is joined and validated.

## Reproducibility

Run from the repository root:

```powershell
python -m research.experiments.profile_mcp
```
"""

    feasibility_report = f"""# MCP data feasibility

**Status:** Phase 1 feasibility audit. No Tennis DNA feature has been approved.

## What the current snapshot supports

- Match-level identity, date, tournament, round, surface, format, and first server.
- Point-level score state and point winner for {len(matched_point_rows):,} usable rows across {len(charted_metadata):,} charted matches.
- Serve/rally notation strings in `1st` and `2nd`, subject to notation parsing and validation.
- Player exposure counts for the charted sample.

## Data-quality decision

**BLOCKED:** no Tennis DNA behavioral feature is approved from this snapshot yet. The source contains {duplicate_counts['exact']:,} exact duplicate point-key groups and {duplicate_counts['conflicting']:,} conflicting groups. Exact copies are collapsed; conflicting groups are excluded rather than guessed.

## What it does not yet support reliably

- A reliable total-shot count from the current raw columns.
- Direct coverage rates for `serve direction`, `shot direction`, `shot type`, `rally length`, `return depth`, winners, forced errors, unforced errors, or net points, because those convenience fields are absent from the downloaded point CSV.
- Ranking-based coverage, because ranking fields are absent from the current metadata.
- Population-level claims about ATP/WTA professional tennis, because this local snapshot is women’s pre-2010 charted data and is selected.

## Candidate feature status

| Feature family | Current feasibility | Reason |
|---|---|---|
| Score state / point outcome | Supported with exclusions | Raw fields exist; duplicate conflicts and reconstruction failures remain visible |
| Serve outcome rates | Exploratory only | Can be derived only after validating `1st`/`2nd` notation parsing |
| Serve direction | Blocked | Encoded in notation; no validated parser yet |
| Rally length | Blocked | Not available as a convenience field; notation parser required |
| Shot type/direction | Blocked | Not available as a convenience field; notation parser required |
| Errors/winners | Blocked | Derived fields absent; notation semantics must be validated |
| Net usage | Blocked | Derived fields absent; notation semantics must be validated |
| Raw match context | Supported | Date, surface, tournament, round, format, players available |

## Recommendation

This focused single-shard audit is retained as a reconstruction fixture, not as the current data-feasibility decision. Use `python -m research.experiments.profile_mcp_snapshot` and the complete-snapshot reports for the current parser and feature gates. Do not infer Tennis DNA feasibility from this historical subset alone.

This is an engineering/data-feasibility result, not evidence that Tennis DNA will or will not distinguish player styles.
"""

    bias_report = f"""# MCP sampling bias and eligibility risks

**Scope:** current local MCP snapshot with {len(charted_metadata):,} safely joined charted matches and {len(charted_players):,} participating players.

## Known selection mechanisms

- Charting is crowdsourced and not a random sample of professional tennis.
- Famous players, Grand Slam matches, late rounds, and memorable matches may be overrepresented.
- Coverage varies by player, tournament, season, surface, and era.
- The current local point snapshot is women’s pre-2010 data only.
- Point notation quality and completeness may vary by chart and contributor.

## Observed exposure imbalance

| Distribution | Minimum | Median | Maximum |
|---|---:|---:|---:|
| Matches per charted player | {match_quantiles[0]:.0f} | {match_quantiles[2]:.0f} | {match_quantiles[4]:.0f} |
| Point rows per charted player | {point_quantiles[0]:.0f} | {point_quantiles[2]:.0f} | {point_quantiles[4]:.0f} |

These ranges describe the selected charted sample; they do not estimate coverage of the full professional-tour population.

## Consequences

A Tennis DNA profile should be phrased as a description of a player's charted sample, not a universal statement about how that player always plays. Comparisons can be confounded by different opponents, surfaces, rounds, eras, and tournament selection.

The absence of a field is not the same as a zero value. Missing or unparsed notation must remain missing. A player with more charted matches may appear more stable simply because the estimate is less noisy.

## Eligibility policy under investigation

No fixed threshold is selected yet. Candidate eligibility should consider:

- Number of complete charted matches.
- Number of valid point and notation records.
- Surface diversity.
- Tournament and round diversity.
- Opponent diversity.
- Field-specific denominator coverage.
- Split-sample stability.

Eligibility tiers such as HIGH, MEDIUM, and LOW confidence should be calibrated from these distributions and sensitivity analyses, not assigned by an arbitrary match count.

## Ranking coverage

Ranking-band analysis is currently blocked because the downloaded MCP metadata has no ranking field. A future rankings join must be validated before using ranking to describe coverage or adjust comparisons.

## Reproducibility

The profile is generated from a versioned local source manifest. Run:

```powershell
python -m research.experiments.profile_mcp
```
"""

    report_root.mkdir(parents=True, exist_ok=True)
    (report_root / "dataset_profile.md").write_text(profile_report, encoding="utf-8")
    (report_root / "data_feasibility.md").write_text(feasibility_report, encoding="utf-8")
    (report_root / "sampling_bias.md").write_text(bias_report, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--points", type=Path, default=POINT_PATH)
    parser.add_argument("--matches", type=Path, default=MATCH_PATH)
    parser.add_argument("--output", type=Path, default=REPORT_ROOT)
    arguments = parser.parse_args()
    write_reports(profile(arguments.points, arguments.matches), arguments.output)
    for filename in ("dataset_profile.md", "data_feasibility.md", "sampling_bias.md"):
        print(f"Generated {arguments.output / filename}")


if __name__ == "__main__":
    main()
