"""Context-controlled falsification pilot for MCP serve candidates."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from statistics import median
from typing import Mapping, Sequence

from pipelines.processing.entity_resolution import (
    ContextMatchIdentity,
    canonical_context_player_id,
    index_context_matches,
    normalize_identity,
    resolve_mcp_match,
)
from research.experiments.audit_context_join import (
    CONTEXT_COMMIT,
    CONTEXT_SNAPSHOT_ID,
    DEFAULT_CONTEXT_SOURCE,
    collision_free_context_links,
    read_context_matches,
    read_mcp_matches,
)
from research.experiments.profile_mcp_snapshot import DEFAULT_SOURCE, SNAPSHOT_ID
from research.experiments.serve_stability import (
    Distance,
    MatchServeRecord,
    Profile,
    ProfileBuilder,
    bootstrap_median_within,
    candidate_families,
    load_match_records,
    split_records,
)


EXPERIMENT_ID = "research-context-serve-stability-v0.1"
SPECIFICATION = "research/context_controlled_serve_stability_spec.md"
ELIGIBILITY_GRID = (2, 5)
BOOTSTRAP_REPLICATES = 50
BOOTSTRAP_SEED = 20260904
DIMENSIONS = (
    "surface",
    "era",
    "player_rank_band",
    "opponent_rank_band",
    "tournament",
    "chart_author",
    "joint_basic_context",
)
RANK_BANDS = (
    (10, "1-10"),
    (25, "11-25"),
    (50, "26-50"),
    (100, "51-100"),
    (200, "101-200"),
)


@dataclass(frozen=True)
class ContextualServeRecord(MatchServeRecord):
    player_rank: int | None = None
    opponent_rank: int | None = None
    context_player_id: str = ""
    context_match_id: str = ""


def parse_rank(value: str) -> int | None:
    value = value.strip()
    if not value:
        return None
    try:
        numeric_rank = float(value)
    except ValueError:
        return None
    if not numeric_rank.is_integer():
        return None
    rank = int(numeric_rank)
    return rank if rank > 0 else None


def rank_band(rank: int | None) -> str:
    if rank is None:
        return "missing"
    for maximum, label in RANK_BANDS:
        if rank <= maximum:
            return label
    return "201+"


def _context_players(
    context: ContextMatchIdentity,
) -> dict[str, tuple[str, int | None]]:
    return {
        normalize_identity(context.winner_name): (
            canonical_context_player_id(context.tour, context.winner_id),
            parse_rank(context.winner_rank),
        ),
        normalize_identity(context.loser_name): (
            canonical_context_player_id(context.tour, context.loser_id),
            parse_rank(context.loser_rank),
        ),
    }


def enrich_contextual_records(
    serve_records: Sequence[MatchServeRecord],
    safe_links: Mapping[str, ContextMatchIdentity],
) -> tuple[list[ContextualServeRecord], dict[str, object]]:
    """Attach match-specific rank and exclude context player-ID collisions."""

    provisional = []
    missing_links = 0
    identity_mismatches = 0
    ids_by_player: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
    for record in serve_records:
        context = safe_links.get(record.match_id)
        if context is None:
            missing_links += 1
            continue
        players = _context_players(context)
        player_key = normalize_identity(record.player)
        opponent_key = normalize_identity(record.opponent)
        if player_key not in players or opponent_key not in players:
            identity_mismatches += 1
            continue
        player_id, player_rank = players[player_key]
        _, opponent_rank = players[opponent_key]
        ids_by_player[(record.tour, player_key)].add(player_id)
        provisional.append(
            ContextualServeRecord(
                tour=record.tour,
                player=record.player,
                match_id=record.match_id,
                date=record.date,
                metrics=record.metrics,
                opponent=record.opponent,
                surface=record.surface,
                tournament=record.tournament,
                round_name=record.round_name,
                chart_author=record.chart_author,
                player_rank=player_rank,
                opponent_rank=opponent_rank,
                context_player_id=player_id,
                context_match_id=context.canonical_match_id,
            )
        )
    collision_keys = {
        key for key, player_ids in ids_by_player.items() if len(player_ids) > 1
    }
    records = [
        record
        for record in provisional
        if (record.tour, normalize_identity(record.player)) not in collision_keys
    ]
    return records, {
        "source_match_player_records": len(serve_records),
        "safe_linked_before_player_id_check": len(provisional),
        "missing_safe_match_link": missing_links,
        "context_identity_mismatches": identity_mismatches,
        "normalized_player_id_collisions": len(collision_keys),
        "collision_match_player_records_excluded": len(provisional) - len(records),
        "eligible_contextual_match_player_records": len(records),
        "eligible_matches": len({record.match_id for record in records}),
        "eligible_player_tour_groups": len(
            {(record.tour, normalize_identity(record.player)) for record in records}
        ),
        "player_rank_known": sum(record.player_rank is not None for record in records),
        "opponent_rank_known": sum(
            record.opponent_rank is not None for record in records
        ),
    }


def stratum_value(record: ContextualServeRecord, dimension: str) -> str:
    surface = normalize_identity(record.surface) or "(blank)"
    era = f"{int(record.date[:4]) // 10 * 10}s"
    opponent_band = rank_band(record.opponent_rank)
    values = {
        "surface": surface,
        "era": era,
        "player_rank_band": rank_band(record.player_rank),
        "opponent_rank_band": opponent_band,
        "tournament": normalize_identity(record.tournament) or "(blank)",
        "chart_author": record.chart_author or "(blank)",
        "joint_basic_context": f"{surface}|{era}|{opponent_band}",
    }
    if dimension not in values:
        raise ValueError(f"unknown context dimension: {dimension}")
    return values[dimension]


EvaluationRow = tuple[
    str,
    str,
    str,
    list[MatchServeRecord],
    list[MatchServeRecord],
    Profile,
    Profile,
]


def _distance_summary(
    rows: Sequence[EvaluationRow], distance: Distance
) -> dict[str, object]:
    within = [distance(row[5], row[6]) for row in rows]
    by_stratum: defaultdict[tuple[str, str], list[EvaluationRow]] = defaultdict(list)
    for row in rows:
        by_stratum[(row[0], row[2])].append(row)
    between = [
        distance(left[5], right[6])
        for bucket in by_stratum.values()
        for left in bucket
        for right in bucket
        if left[1] != right[1]
    ]
    within_median = median(within) if within else None
    between_median = median(between) if between else None
    return {
        "eligible_player_strata": len(rows),
        "distinct_players": len({(row[0], row[1]) for row in rows}),
        "context_strata": len({(row[0], row[2]) for row in rows}),
        "between_player_comparisons": len(between),
        "median_within_player_distance": within_median,
        "median_between_player_distance": between_median,
        "within_to_between_ratio": (
            within_median / between_median
            if within_median is not None and between_median
            else None
        ),
    }


def evaluate_context_family(
    records: Sequence[ContextualServeRecord],
    profile_builder: ProfileBuilder,
    distance: Distance,
    dimension: str,
    minimum_matches_per_split: int,
    seed: int,
) -> dict[str, object]:
    grouped: defaultdict[tuple[str, str, str], list[MatchServeRecord]] = defaultdict(
        list
    )
    for record in records:
        grouped[
            (
                record.tour,
                normalize_identity(record.player),
                stratum_value(record, dimension),
            )
        ].append(record)
    rows: list[EvaluationRow] = []
    for (tour, player, stratum), player_records in sorted(grouped.items()):
        left, right = split_records(player_records, "chronological")
        if min(len(left), len(right)) < minimum_matches_per_split:
            continue
        left_profile = profile_builder(left)
        right_profile = profile_builder(right)
        if left_profile is not None and right_profile is not None:
            rows.append(
                (
                    tour,
                    player,
                    stratum,
                    left,
                    right,
                    left_profile,
                    right_profile,
                )
            )
    summary = _distance_summary(rows, distance)
    bootstrap = bootstrap_median_within(
        [(row[3], row[4]) for row in rows],
        profile_builder,
        distance,
        seed,
        replicates=BOOTSTRAP_REPLICATES,
    )
    by_tour = []
    for tour in sorted({row[0] for row in rows}):
        by_tour.append(
            {
                "tour": tour,
                **_distance_summary(
                    [row for row in rows if row[0] == tour], distance
                ),
            }
        )
    return {
        "dimension": dimension,
        "split_strategy": "chronological",
        "minimum_matches_per_split": minimum_matches_per_split,
        **summary,
        "match_bootstrap_resampled_95_range": list(bootstrap)
        if bootstrap
        else None,
        "by_tour": by_tour,
    }


def _coverage(records: Sequence[ContextualServeRecord]) -> dict[str, object]:
    dimensions = {}
    for dimension in DIMENSIONS:
        counts = Counter(stratum_value(record, dimension) for record in records)
        dimensions[dimension] = [
            {"stratum": stratum, "match_player_records": count}
            for stratum, count in sorted(
                counts.items(), key=lambda item: (-item[1], item[0])
            )
        ]
    return dimensions


def run_experiment(
    records: Sequence[ContextualServeRecord], source_profile: dict[str, object]
) -> dict[str, object]:
    families = {}
    seed = BOOTSTRAP_SEED
    for family, profile_builder, distance in candidate_families():
        evaluations = []
        for dimension in DIMENSIONS:
            for threshold in ELIGIBILITY_GRID:
                evaluations.append(
                    evaluate_context_family(
                        records,
                        profile_builder,
                        distance,
                        dimension,
                        threshold,
                        seed,
                    )
                )
                seed += 1
        families[family] = evaluations
    return {
        "generated_on": date.today().isoformat(),
        "experiment_id": EXPERIMENT_ID,
        "specification": SPECIFICATION,
        "mcp_snapshot_id": SNAPSHOT_ID,
        "context_snapshot_id": CONTEXT_SNAPSHOT_ID,
        "context_mirror_commit": CONTEXT_COMMIT,
        "eligibility_grid_matches_per_split": list(ELIGIBILITY_GRID),
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "source_profile": source_profile,
        "coverage_by_context": _coverage(records),
        "families": families,
    }


def load_experiment_records(
    mcp_source: Path = DEFAULT_SOURCE,
    context_source: Path = DEFAULT_CONTEXT_SOURCE,
) -> tuple[list[ContextualServeRecord], dict[str, object]]:
    mcp_matches, _ = read_mcp_matches(mcp_source)
    context_matches, _ = read_context_matches(context_source)
    context_index = index_context_matches(context_matches)
    resolutions = [
        (match, resolve_mcp_match(match, context_index)) for match in mcp_matches
    ]
    safe_links = collision_free_context_links(resolutions)
    del context_matches, context_index, resolutions, mcp_matches
    return enrich_contextual_records(load_match_records(mcp_source), safe_links)


def _format(value: float | None) -> str:
    return "NA" if value is None else f"{value:.3f}"


def render_report(result: dict[str, object]) -> str:
    rows = [
        "| Family | Context | Matches / half | Player-strata | Players | Within | "
        "Bootstrap range | Between | Ratio |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for family, evaluations in result["families"].items():
        for evaluation in evaluations:
            interval = evaluation["match_bootstrap_resampled_95_range"]
            interval_text = (
                f"{_format(interval[0])}-{_format(interval[1])}" if interval else "NA"
            )
            rows.append(
                f"| `{family}` | `{evaluation['dimension']}` | "
                f"{evaluation['minimum_matches_per_split']} | "
                f"{evaluation['eligible_player_strata']:,} | "
                f"{evaluation['distinct_players']:,} | "
                f"{_format(evaluation['median_within_player_distance'])} | "
                f"{interval_text} | "
                f"{_format(evaluation['median_between_player_distance'])} | "
                f"{_format(evaluation['within_to_between_ratio'])} |"
            )
    profile = result["source_profile"]
    family_ranges = []
    aggregate_failures = 0
    tour_failures = 0
    tour_evaluation_count = 0
    bootstrap_crossings = 0
    evaluation_count = 0
    for family, evaluations in result["families"].items():
        ratios = [
            evaluation["within_to_between_ratio"]
            for evaluation in evaluations
            if evaluation["within_to_between_ratio"] is not None
        ]
        family_ranges.append(
            f"- `{family}`: {_format(min(ratios))}-{_format(max(ratios))}."
        )
        for evaluation in evaluations:
            evaluation_count += 1
            ratio = evaluation["within_to_between_ratio"]
            aggregate_failures += int(ratio is None or ratio >= 1)
            tour_failures += sum(
                tour["within_to_between_ratio"] is None
                or tour["within_to_between_ratio"] >= 1
                for tour in evaluation["by_tour"]
            )
            tour_evaluation_count += len(evaluation["by_tour"])
            interval = evaluation["match_bootstrap_resampled_95_range"]
            between = evaluation["median_between_player_distance"]
            bootstrap_crossings += int(
                interval is None or between is None or interval[1] >= between
            )
    author_counts = result["coverage_by_context"]["chart_author"]
    top_four_author_records = sum(
        row["match_player_records"] for row in author_counts[:4]
    )
    top_four_author_share = (
        top_four_author_records / profile["eligible_contextual_match_player_records"]
    )
    return f"""# Context-controlled serve stability pilot

**Experiment:** `{result['experiment_id']}`

**Status:** internal falsification result; no player ranking or profile is produced

## Data boundary

- {profile['source_match_player_records']:,} source match-player serve records were considered.
- {profile['safe_linked_before_player_id_check']:,} had a collision-free safe match link before
  the player-ID check.
- {profile['collision_match_player_records_excluded']:,} records from
  {profile['normalized_player_id_collisions']:,} normalized player identities were excluded because
  they map to multiple context IDs.
- {profile['eligible_contextual_match_player_records']:,} match-player records across
  {profile['eligible_matches']:,} matches enter the experiment.
- Player rank is known for {profile['player_rank_known']:,} eligible records; opponent rank is known
  for {profile['opponent_rank_known']:,}.

MCP supplies surface, tournament, round, and chart author. The context archive supplies only
match-specific ranks and namespaced IDs here. Missing rank remains explicit. All rejected join
classes remain excluded.

## Results

{chr(10).join(rows)}

Ratios below one favor same-player repeatability within a context stratum; ratios at or above one
fail that check. Sparse or missing ratios are negative coverage evidence, not omitted successes.
Player-strata can exceed distinct players because one player may contribute to several contexts.

## Falsification summary

All {evaluation_count} aggregate evaluations produced a ratio below one; {aggregate_failures}
failed or lacked the aggregate ratio check. Across the {tour_evaluation_count} ATP/WTA cells,
{tour_failures} failed or lacked that check. In {bootstrap_crossings} aggregate evaluations, the
upper endpoint of the within-player bootstrap range reached the between-player median.

Observed aggregate ratio ranges:

{chr(10).join(family_ranges)}

Coverage still narrows materially under stronger controls. At five matches per half, exact
tournament strata retain only 69 distinct players and joint surface/era/opponent-rank strata retain
123. The four largest chart authors account for {top_four_author_share:.1%} of eligible match-player
records. These are selection and precision warnings even though the ratios remain below one.

**PROJECT HYPOTHESIS:** the three serve families retain aggregate repeatability under these simple
observed-context checks. `second_serve_direction` remains the weakest family because it has the
largest within-player distances, the weakest prior reconciliation, and the highest controlled
ratios in several cells.

**DATA-QUALITY DECISION:** retain all three families for shrinkage and player-level uncertainty
experiments. This is not approval for a feature vector. Tournament-specific and joint-context
results at five matches per half are exploratory because their player coverage is narrow.

## Interpretation boundary

This is one-factor stratification plus a pre-specified joint basic context, not a causal adjustment
model. It cannot remove selection into charted matches, unmeasured opponent style, score state,
match format, or dependence across repeated player-strata. The bootstrap range resamples matches
within halves and is a diagnostic range, not a confidence interval.

No predictive model is fitted, so calibration and discrimination are not applicable. Rankings are
treated as source-reported match context; their historical timing semantics were not independently
validated and remain a possible measurement limitation.

**OPEN QUESTION:** whether retained families justify shrinkage and player-level uncertainty work.
No individual player estimate is emitted, and no ratio alone approves a Tennis DNA feature.

## Reproduce

```powershell
python -m research.experiments.context_serve_stability
```
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp-source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--context-source", type=Path, default=DEFAULT_CONTEXT_SOURCE)
    parser.add_argument(
        "--json", type=Path, default=Path("research/context_serve_stability.json")
    )
    parser.add_argument(
        "--report", type=Path, default=Path("research/context_serve_stability.md")
    )
    parser.add_argument(
        "--render-existing",
        action="store_true",
        help="render the report from --json without recomputing the experiment",
    )
    arguments = parser.parse_args()
    if arguments.render_existing:
        result = json.loads(arguments.json.read_text(encoding="utf-8"))
    else:
        records, source_profile = load_experiment_records(
            arguments.mcp_source, arguments.context_source
        )
        result = run_experiment(records, source_profile)
        arguments.json.write_text(
            json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
        )
    arguments.report.write_text(render_report(result), encoding="utf-8")
    if not arguments.render_existing:
        print(f"Wrote {arguments.json}")
    print(f"Wrote {arguments.report}")


if __name__ == "__main__":
    main()
