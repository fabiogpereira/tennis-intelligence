"""Audit a conservative MCP join to the Sackmann ATP/WTA match archive."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

from pipelines.processing.entity_resolution import (
    ContextMatchIdentity,
    McpMatchIdentity,
    canonical_context_match_id,
    canonical_context_player_id,
    index_context_matches,
    normalize_identity,
    resolve_mcp_match,
)
from research.experiments.profile_mcp_snapshot import (
    DEFAULT_SOURCE as DEFAULT_MCP_SOURCE,
    MATCH_PATTERN,
    PINNED_SOURCE_COMMIT as MCP_COMMIT,
    POINT_PATTERN,
    SNAPSHOT_ID as MCP_SNAPSHOT_ID,
    InvalidSnapshot,
    _discover,
    _read_metadata,
    _source_commit,
    _tour,
)


DEFAULT_CONTEXT_SOURCE = Path("data/raw/sackmann_archive")
DEFAULT_OUTPUT_ROOT = Path("research")
CONTEXT_COMMIT = "83733587353df8a41f2fd4f516147d5aa83f5a8d"
CONTEXT_SNAPSHOT_ID = "sackmann-archive-2026-06-25-8373358"
EXPERIMENT_ID = "research-mcp-context-join-v0.1"
RETRIEVED_ON = "2026-09-03"
REQUIRED_CONTEXT_FIELDS = {
    "tourney_id",
    "tourney_name",
    "surface",
    "tourney_date",
    "match_num",
    "winner_id",
    "winner_name",
    "loser_id",
    "loser_name",
    "best_of",
    "round",
    "winner_rank",
    "loser_rank",
}
CONTEXT_FILE_PATTERN = re.compile(
    r"^(?:atp|wta)_matches_(?:\d{4}|qual_chall_\d{4}|futures_\d{4}|qual_itf_\d{4})\.csv$"
)
WINDOW_SENSITIVITY = ((1, 14), (7, 20), (14, 28))


def _git_commit(path: Path) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _parse_date(value: str) -> date | None:
    try:
        return datetime.strptime(value, "%Y%m%d").date()
    except (TypeError, ValueError):
        return None


def _context_paths(source_root: Path) -> list[Path]:
    paths = sorted(
        path
        for folder in (source_root / "atp", source_root / "wta")
        for path in folder.glob("*_matches_*.csv")
        if CONTEXT_FILE_PATTERN.fullmatch(path.name)
    )
    if not paths:
        raise InvalidSnapshot(f"no context match files found under {source_root}")
    return paths


def _read_point_match_ids(paths: Iterable[Path]) -> set[str]:
    match_ids = set()
    for path in paths:
        with path.open(newline="", encoding="utf-8-sig") as source:
            reader = csv.DictReader(source)
            if "match_id" not in (reader.fieldnames or ()):
                raise InvalidSnapshot(f"{path.name} has no match_id field")
            match_ids.update(row["match_id"] for row in reader if row["match_id"])
    return match_ids


def read_mcp_matches(source_root: Path) -> tuple[list[McpMatchIdentity], dict[str, int]]:
    if _source_commit(source_root) != MCP_COMMIT:
        raise InvalidSnapshot("MCP source does not match its pinned commit")
    metadata = _read_metadata(_discover(source_root, MATCH_PATTERN, expected=2))
    point_ids = _read_point_match_ids(_discover(source_root, POINT_PATTERN, expected=6))
    safe_rows = metadata["safe_rows"]
    records = []
    invalid_dates = 0
    for match_id in sorted(point_ids.intersection(safe_rows)):
        row = safe_rows[match_id]
        match_date = _parse_date(row["Date"])
        if match_date is None:
            invalid_dates += 1
            continue
        records.append(
            McpMatchIdentity(
                match_id=match_id,
                tour=_tour(match_id),
                match_date=match_date,
                tournament=row["Tournament"],
                round_name=row["Round"],
                surface=row["Surface"],
                best_of=row["Best of"],
                player_1=row["Player 1"],
                player_2=row["Player 2"],
            )
        )
    return records, {
        "point_match_ids": len(point_ids),
        "safe_point_bearing_metadata": len(point_ids.intersection(safe_rows)),
        "invalid_dates": invalid_dates,
    }


def read_context_matches(
    source_root: Path,
) -> tuple[list[ContextMatchIdentity], dict[str, object]]:
    if _git_commit(source_root) != CONTEXT_COMMIT:
        raise InvalidSnapshot("context source does not match its pinned mirror commit")
    paths = _context_paths(source_root)
    records: dict[str, ContextMatchIdentity | None] = {}
    raw_rows = 0
    invalid_rows = 0
    exact_duplicate_rows = 0
    conflicting_keys: set[str] = set()
    rows_by_tour: Counter[str] = Counter()
    rows_by_family: Counter[str] = Counter()
    files = []
    for path in paths:
        tour = "ATP" if path.parent.name == "atp" else "WTA"
        if "qual_chall" in path.name:
            family = "qual_chall"
        elif "futures" in path.name:
            family = "futures"
        elif "qual_itf" in path.name:
            family = "qual_itf"
        else:
            family = "tour"
        file_rows = 0
        with path.open(newline="", encoding="utf-8-sig") as source:
            reader = csv.DictReader(source)
            missing = REQUIRED_CONTEXT_FIELDS.difference(reader.fieldnames or ())
            if missing:
                raise InvalidSnapshot(f"{path.name} missing fields: {sorted(missing)}")
            for row in reader:
                raw_rows += 1
                file_rows += 1
                rows_by_tour[tour] += 1
                rows_by_family[family] += 1
                tournament_date = _parse_date(row["tourney_date"])
                required_values = (
                    row["tourney_id"],
                    row["match_num"],
                    row["winner_id"],
                    row["winner_name"],
                    row["loser_id"],
                    row["loser_name"],
                )
                if tournament_date is None or any(not value.strip() for value in required_values):
                    invalid_rows += 1
                    continue
                canonical_id = canonical_context_match_id(
                    tour, family, row["tourney_id"], row["match_num"]
                )
                record = ContextMatchIdentity(
                    canonical_match_id=canonical_id,
                    tour=tour,
                    tournament_date=tournament_date,
                    tournament=row["tourney_name"],
                    round_name=row["round"],
                    surface=row["surface"],
                    best_of=row["best_of"],
                    winner_name=row["winner_name"],
                    winner_id=row["winner_id"],
                    winner_rank=row["winner_rank"],
                    loser_name=row["loser_name"],
                    loser_id=row["loser_id"],
                    loser_rank=row["loser_rank"],
                    source_family=family,
                    source_file=f"{path.parent.name}/{path.name}",
                )
                previous = records.get(canonical_id)
                if canonical_id in records and previous == record:
                    exact_duplicate_rows += 1
                elif canonical_id in records:
                    records[canonical_id] = None
                    conflicting_keys.add(canonical_id)
                else:
                    records[canonical_id] = record
        files.append(
            {
                "file": f"{path.parent.name}/{path.name}",
                "rows": file_rows,
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    safe = [record for record in records.values() if record is not None]
    return safe, {
        "files": files,
        "file_count": len(files),
        "raw_rows": raw_rows,
        "safe_canonical_matches": len(safe),
        "invalid_rows": invalid_rows,
        "exact_duplicate_rows": exact_duplicate_rows,
        "conflicting_canonical_keys": len(conflicting_keys),
        "rows_by_tour": dict(rows_by_tour),
        "rows_by_file_family": dict(rows_by_family),
    }


def _dimension_records(
    totals: Counter[tuple[str, str]], matched: Counter[tuple[str, str]]
) -> dict[str, list[dict[str, object]]]:
    result = {}
    for dimension in ("tour", "season"):
        values = sorted(value for current, value in totals if current == dimension)
        result[dimension] = [
            {
                dimension: value,
                "mcp_matches": totals[(dimension, value)],
                "matched": matched[(dimension, value)],
                "match_rate": matched[(dimension, value)] / totals[(dimension, value)],
            }
            for value in values
        ]
    return result


def audit_join(
    mcp_matches: list[McpMatchIdentity], context_matches: list[ContextMatchIdentity]
) -> tuple[dict[str, object], list[dict[str, str]]]:
    context_index = index_context_matches(context_matches)
    sensitivity = []
    for days_before, days_after in WINDOW_SENSITIVITY:
        statuses = Counter(
            resolve_mcp_match(
                match, context_index, days_before=days_before, days_after=days_after
            ).status
            for match in mcp_matches
        )
        sensitivity.append(
            {
                "days_before": days_before,
                "days_after": days_after,
                **dict(statuses),
            }
        )

    resolutions = [(match, resolve_mcp_match(match, context_index)) for match in mcp_matches]
    target_counts = Counter(
        resolution.context_match.canonical_match_id
        for _, resolution in resolutions
        if resolution.status == "matched" and resolution.context_match is not None
    )
    mcp_ids_by_target: defaultdict[str, list[str]] = defaultdict(list)
    for match, resolution in resolutions:
        if resolution.status == "matched" and resolution.context_match is not None:
            mcp_ids_by_target[resolution.context_match.canonical_match_id].append(
                match.match_id
            )
    statuses: Counter[str] = Counter()
    methods: Counter[str] = Counter()
    totals_by_dimension: Counter[tuple[str, str]] = Counter()
    matched_by_dimension: Counter[tuple[str, str]] = Counter()
    agreements: Counter[str] = Counter()
    date_offsets: list[int] = []
    rank_fields = 0
    rank_known = 0
    player_ids_by_name: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
    review_rows = []
    for match, resolution in resolutions:
        season = str(match.match_date.year)
        for dimension, value in (("tour", match.tour), ("season", season)):
            totals_by_dimension[(dimension, value)] += 1
        context = resolution.context_match
        if context is None:
            statuses[resolution.status] += 1
            review_rows.append(
                {
                    "mcp_match_id": match.match_id,
                    "status": resolution.status,
                    "method": "",
                    "candidate_count": str(resolution.candidate_count),
                    "context_match_id": "",
                    "date_offset_days": "",
                    "surface_agrees": "",
                    "round_agrees": "",
                    "tournament_agrees": "",
                    "review_status": "",
                    "review_notes": "",
                }
            )
            continue
        if resolution.status != "matched":
            statuses[resolution.status] += 1
            review_rows.append(
                {
                    "mcp_match_id": match.match_id,
                    "status": resolution.status,
                    "method": resolution.method or "",
                    "candidate_count": str(resolution.candidate_count),
                    "context_match_id": context.canonical_match_id,
                    "date_offset_days": str(
                        (match.match_date - context.tournament_date).days
                    ),
                    "surface_agrees": str(
                        normalize_identity(match.surface)
                        == normalize_identity(context.surface)
                    ).lower(),
                    "round_agrees": str(
                        normalize_identity(match.round_name)
                        == normalize_identity(context.round_name)
                    ).lower(),
                    "tournament_agrees": str(
                        normalize_identity(match.tournament)
                        == normalize_identity(context.tournament)
                    ).lower(),
                    "review_status": "",
                    "review_notes": "",
                }
            )
            continue
        if target_counts[context.canonical_match_id] > 1:
            statuses["canonical_collision"] += 1
            review_rows.append(
                {
                    "mcp_match_id": match.match_id,
                    "status": "canonical_collision",
                    "method": resolution.method or "",
                    "candidate_count": str(resolution.candidate_count),
                    "context_match_id": context.canonical_match_id,
                    "date_offset_days": str(
                        (match.match_date - context.tournament_date).days
                    ),
                    "surface_agrees": "",
                    "round_agrees": "",
                    "tournament_agrees": "",
                    "review_status": "",
                    "review_notes": "",
                }
            )
            continue
        statuses["matched"] += 1
        methods[resolution.method or "unknown"] += 1
        for dimension, value in (("tour", match.tour), ("season", season)):
            matched_by_dimension[(dimension, value)] += 1
        offset = (match.match_date - context.tournament_date).days
        date_offsets.append(offset)
        comparisons = {
            "surface": normalize_identity(match.surface)
            == normalize_identity(context.surface),
            "round": normalize_identity(match.round_name)
            == normalize_identity(context.round_name),
            "tournament": normalize_identity(match.tournament)
            == normalize_identity(context.tournament),
            "best_of": match.best_of == context.best_of,
        }
        for field, agrees in comparisons.items():
            agreements[f"{field}_comparable"] += 1
            agreements[f"{field}_agrees"] += int(agrees)
        context_players = {
            normalize_identity(context.winner_name): (context.winner_id, context.winner_rank),
            normalize_identity(context.loser_name): (context.loser_id, context.loser_rank),
        }
        for player in (match.player_1, match.player_2):
            player_id, rank = context_players[normalize_identity(player)]
            player_ids_by_name[(match.tour, normalize_identity(player))].add(
                canonical_context_player_id(match.tour, player_id)
            )
            rank_fields += 1
            rank_known += int(bool(rank.strip()))
        review_rows.append(
            {
                "mcp_match_id": match.match_id,
                "status": "matched",
                "method": resolution.method or "",
                "candidate_count": str(resolution.candidate_count),
                "context_match_id": context.canonical_match_id,
                "date_offset_days": str(offset),
                "surface_agrees": str(comparisons["surface"]).lower(),
                "round_agrees": str(comparisons["round"]).lower(),
                "tournament_agrees": str(comparisons["tournament"]).lower(),
                "review_status": "",
                "review_notes": "",
            }
        )

    safe_review = sorted(
        (row for row in review_rows if row["status"] == "matched"),
        key=lambda row: hashlib.sha256(row["mcp_match_id"].encode()).hexdigest(),
    )[:25]
    exceptions_by_status: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in review_rows:
        if row["status"] != "matched":
            exceptions_by_status[row["status"]].append(row)
    for rows in exceptions_by_status.values():
        rows.sort(key=lambda row: row["mcp_match_id"])
    exception_review = []
    while len(exception_review) < 25 and any(exceptions_by_status.values()):
        for status in sorted(exceptions_by_status):
            if exceptions_by_status[status] and len(exception_review) < 25:
                exception_review.append(exceptions_by_status[status].pop(0))
    ambiguous_player_names = [
        {"tour": tour, "normalized_name": name, "player_ids": sorted(ids)}
        for (tour, name), ids in sorted(player_ids_by_name.items())
        if len(ids) > 1
    ]
    target_collision_examples = [
        {"context_match_id": target, "mcp_match_ids": sorted(mcp_ids)}
        for target, mcp_ids in sorted(mcp_ids_by_target.items())
        if len(mcp_ids) > 1
    ]
    matched_count = statuses["matched"]
    return {
        "status_counts": dict(statuses),
        "method_counts": dict(methods),
        "safe_match_rate": matched_count / len(mcp_matches) if mcp_matches else None,
        "coverage": _dimension_records(totals_by_dimension, matched_by_dimension),
        "window_sensitivity": sensitivity,
        "agreement": {
            field: {
                "comparable": agreements[f"{field}_comparable"],
                "agrees": agreements[f"{field}_agrees"],
                "rate": agreements[f"{field}_agrees"]
                / agreements[f"{field}_comparable"],
            }
            for field in ("surface", "round", "tournament", "best_of")
        },
        "date_offset_days": {
            "minimum": min(date_offsets),
            "median": sorted(date_offsets)[len(date_offsets) // 2],
            "maximum": max(date_offsets),
        },
        "rank_field_coverage": {
            "eligible_player_match_sides": rank_fields,
            "known": rank_known,
            "rate": rank_known / rank_fields if rank_fields else None,
        },
        "matched_normalized_names_with_multiple_player_ids": ambiguous_player_names,
        "canonical_target_collisions": sum(count > 1 for count in target_counts.values()),
        "canonical_target_collision_examples": target_collision_examples[:10],
        "review_sample": {
            "matched": len(safe_review),
            "exceptions": len(exception_review),
            "human_review_complete": False,
        },
    }, safe_review + exception_review


def profile(
    mcp_source: Path = DEFAULT_MCP_SOURCE,
    context_source: Path = DEFAULT_CONTEXT_SOURCE,
) -> tuple[dict[str, object], list[dict[str, str]]]:
    mcp_matches, mcp_profile = read_mcp_matches(mcp_source)
    context_matches, context_profile = read_context_matches(context_source)
    join_profile, review_rows = audit_join(mcp_matches, context_matches)
    return {
        "generated_on": date.today().isoformat(),
        "experiment_id": EXPERIMENT_ID,
        "mcp_snapshot_id": MCP_SNAPSHOT_ID,
        "mcp_commit": MCP_COMMIT,
        "context_snapshot_id": CONTEXT_SNAPSHOT_ID,
        "context_mirror_commit": CONTEXT_COMMIT,
        "context_retrieved_on": RETRIEVED_ON,
        "context_license": "CC BY-NC-SA 4.0",
        "mcp": mcp_profile,
        "context": context_profile,
        "join": join_profile,
    }, review_rows


def render_report(result: dict[str, object]) -> str:
    context = result["context"]
    join = result["join"]
    statuses = join["status_counts"]
    coverage_rows = ["| Tour | MCP matches | Safely matched | Rate |", "|---|---:|---:|---:|"]
    for row in join["coverage"]["tour"]:
        coverage_rows.append(
            f"| {row['tour']} | {row['mcp_matches']:,} | {row['matched']:,} | "
            f"{row['match_rate']:.1%} |"
        )
    agreement_rows = ["| Field | Comparable | Agrees | Agreement |", "|---|---:|---:|---:|"]
    for field, values in join["agreement"].items():
        agreement_rows.append(
            f"| `{field}` | {values['comparable']:,} | {values['agrees']:,} | "
            f"{values['rate']:.1%} |"
        )
    sensitivity_rows = [
        "| Window before / after tournament date | Matched before collision check | "
        "Ambiguous | Pair absent | Outside window | Context conflict |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in join["window_sensitivity"]:
        sensitivity_rows.append(
            f"| -{row['days_before']} / +{row['days_after']} days | "
            f"{row.get('matched', 0):,} | {row.get('ambiguous', 0):,} | "
            f"{row.get('unresolved_pair', 0):,} | "
            f"{row.get('unresolved_date_window', 0):,} | "
            f"{row.get('conflicting_context', 0):,} |"
        )
    return f"""# MCP to Sackmann context join audit

**Experiment:** `{result['experiment_id']}`

**Behavior snapshot:** `{result['mcp_snapshot_id']}`

**Context snapshot:** `{result['context_snapshot_id']}`

**Status:** automated precision-first join audit; human sample review is still open

## Source decision

The original `JeffSackmann/tennis_atp` and `tennis_wta` repositories returned `Repository not
found` on {result['context_retrieved_on']}. This audit therefore uses the already identified
`Aneeshers/tennis-sackmann-archive` mirror pinned at commit
`{result['context_mirror_commit']}`. The mirror preserves the upstream READMEs and states that its
ATP/WTA snapshots came from June 2026, but does not provide their exact upstream commit hashes.

**ENGINEERING DECISION:** the mirror is acceptable for a feasibility audit, not silently equivalent
to the unavailable upstream. Its provenance gap and CC BY-NC-SA 4.0 license remain product blockers.

## Context source profile

- {context['file_count']:,} ATP/WTA singles files and
  {context['raw_rows']:,} raw match rows were read.
- {context['safe_canonical_matches']:,} canonical match keys were structurally safe.
- {context['invalid_rows']:,} rows lacked a required identity/date value;
  {context['conflicting_canonical_keys']:,} canonical keys conflicted and were excluded.
- Raw context files remain under `data/raw/` and are not committed.

## Resolution contract

`research-mcp-context-join-v0.1` requires the same tour, an exact unordered pair after conservative
case/diacritic/separator normalization, and a tournament-date window of -7/+20 days. A unique
candidate also needs either exact normalized tournament or joint round/surface/best-of agreement.
Multiple candidates are accepted only when exact normalized tournament and round produce one
candidate. Fuzzy names and hand-authored aliases are not used.

Canonical IDs are namespaced as `sackmann:<tour>:<player_id>` and
`sackmann:<tour>:<file-family>:<tourney_id>:<match_num>`. The file-family segment prevents
main-draw, qualifying/challenger, and futures keys from being treated as the same namespace. MCP
source IDs remain preserved separately.

## Join result

| Status | Matches |
|---|---:|
| Safely matched | {statuses.get('matched', 0):,} |
| Exact normalized pair absent | {statuses.get('unresolved_pair', 0):,} |
| Exact pair outside date window | {statuses.get('unresolved_date_window', 0):,} |
| Pair/date found but supporting context conflicts | {statuses.get('conflicting_context', 0):,} |
| Ambiguous candidates | {statuses.get('ambiguous', 0):,} |
| Canonical target collision | {statuses.get('canonical_collision', 0):,} |

Overall safe match rate: **{join['safe_match_rate']:.1%}**.

{chr(10).join(coverage_rows)}

## Independent agreement checks among matched records

{chr(10).join(agreement_rows)}

These fields do not participate in the unique-pair rule, except tournament and round when multiple
candidates remain. Agreement therefore helps detect false joins and source-definition differences;
it is not independent proof of identity.

Ranking is present for {join['rank_field_coverage']['known']:,} of
{join['rank_field_coverage']['eligible_player_match_sides']:,} safely matched player-match sides
({join['rank_field_coverage']['rate']:.1%}).

## Date-window sensitivity

{chr(10).join(sensitivity_rows)}

The selected window follows the upstream documentation that `tourney_date` is usually the Monday at
or near the start of an event, while MCP records the match date. No window is interpreted as a
validated threshold until the deterministic review sample is checked by a human.

## Remaining blockers

- The 50-row review queue has not been human-labelled.
- {len(join['matched_normalized_names_with_multiple_player_ids']):,} matched normalized player names
  map to multiple source player IDs and require identity review before a player crosswalk is approved.
- Context coverage varies by season and unresolved names have not been given fuzzy aliases.
- The mirror provenance gap and non-commercial/share-alike license remain explicit.
- Surface, opponent, era, and ranking-controlled stability has not yet been run.

**DATA-QUALITY DECISION:** use the safe match links for the next internal sensitivity experiment only
after reviewing the sample. Do not publish canonical player profiles or ranking-band claims yet.

## Reproduce

```powershell
powershell -NoProfile -File pipelines/ingestion/fetch_sackmann_context_snapshot.ps1
python -m research.experiments.audit_context_join
```
"""


def write_outputs(
    result: dict[str, object], review_rows: list[dict[str, str]], output_root: Path
) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "mcp_context_join.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    (output_root / "mcp_context_join.md").write_text(
        render_report(result), encoding="utf-8"
    )
    with (output_root / "mcp_context_join_review.csv").open(
        "w", newline="", encoding="utf-8"
    ) as destination:
        writer = csv.DictWriter(destination, fieldnames=list(review_rows[0]))
        writer.writeheader()
        writer.writerows(review_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp-source", type=Path, default=DEFAULT_MCP_SOURCE)
    parser.add_argument("--context-source", type=Path, default=DEFAULT_CONTEXT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_ROOT)
    arguments = parser.parse_args()
    result, review_rows = profile(arguments.mcp_source, arguments.context_source)
    write_outputs(result, review_rows, arguments.output)
    print(f"Wrote {arguments.output / 'mcp_context_join.json'}")
    print(f"Wrote {arguments.output / 'mcp_context_join.md'}")
    print(f"Wrote {arguments.output / 'mcp_context_join_review.csv'}")


if __name__ == "__main__":
    main()
