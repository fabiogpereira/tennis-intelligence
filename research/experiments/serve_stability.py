"""Falsification-first split-sample stability pilot for MCP serve candidates."""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Callable, Iterable, Sequence

from research.experiments.profile_mcp_snapshot import (
    DEFAULT_SOURCE,
    MATCH_PATTERN,
    PINNED_SOURCE_COMMIT,
    POINT_PATTERN,
    SNAPSHOT_ID,
    InvalidSnapshot,
    _discover,
    _read_metadata,
    _read_points,
    _source_commit,
    _tour,
)


EXPERIMENT_ID = "research-serve-stability-v0.1"
ELIGIBILITY_GRID = (2, 5, 10, 20)
BOOTSTRAP_REPLICATES = 100
BOOTSTRAP_SEED = 20260903
DIRECTIONS = ("wide", "middle", "t")
SIDES = ("deuce", "ad")


@dataclass(frozen=True)
class MatchServeRecord:
    tour: str
    player: str
    match_id: str
    date: str
    metrics: Counter[str]
    opponent: str = ""
    surface: str = ""
    tournament: str = ""
    round_name: str = ""
    chart_author: str = ""


Profile = tuple[float, ...]
ProfileBuilder = Callable[[Iterable[MatchServeRecord]], Profile | None]
Distance = Callable[[Profile, Profile], float]


def load_match_records(source_root: Path = DEFAULT_SOURCE) -> list[MatchServeRecord]:
    """Load one additive serve record per safely joined match and server."""

    source_commit = _source_commit(source_root)
    if source_commit != PINNED_SOURCE_COMMIT:
        raise InvalidSnapshot(
            f"expected MCP commit {PINNED_SOURCE_COMMIT}, "
            f"found {source_commit or 'no Git metadata'}"
        )
    metadata = _read_metadata(_discover(source_root, MATCH_PATTERN, expected=2))["safe_rows"]
    points = _read_points(_discover(source_root, POINT_PATTERN, expected=6))
    records = []
    for (match_id, server_number), metrics in points[
        "_serve_metrics_by_match_server"
    ].items():
        row = metadata.get(match_id)
        if row is None or server_number not in {"1", "2"}:
            continue
        records.append(
            MatchServeRecord(
                tour=_tour(match_id),
                player=row[f"Player {server_number}"],
                match_id=match_id,
                date=row["Date"],
                metrics=metrics,
                opponent=row[f"Player {'2' if server_number == '1' else '1'}"],
                surface=row["Surface"],
                tournament=row["Tournament"],
                round_name=row["Round"],
                chart_author=row.get("Charted by", "").strip(),
            )
        )
    return sorted(records, key=lambda row: (row.tour, row.player, row.date, row.match_id))


def _sum_metrics(records: Iterable[MatchServeRecord]) -> Counter[str]:
    total: Counter[str] = Counter()
    for record in records:
        total.update(record.metrics)
    return total


def outcome_profile(records: Iterable[MatchServeRecord]) -> Profile | None:
    """Return three outcome rates only when every audited denominator is non-zero."""

    metrics = _sum_metrics(records)
    denominators = (
        metrics["resolved_first_serve_status"],
        metrics["resolved_ace_status"],
        metrics["resolved_double_fault_status"],
    )
    if any(value == 0 for value in denominators):
        return None
    return (
        metrics["first_in"] / denominators[0],
        metrics["aces"] / denominators[1],
        metrics["dfs"] / denominators[2],
    )


def direction_profile(
    records: Iterable[MatchServeRecord], serve_number: str
) -> Profile | None:
    """Return wide/body/T shares normalized separately within each court side."""

    metrics = _sum_metrics(records)
    values: list[float] = []
    for side in SIDES:
        counts = [
            metrics[f"direction:{serve_number}:{side}:{direction}"]
            for direction in DIRECTIONS
        ]
        denominator = sum(counts)
        if denominator == 0:
            return None
        values.extend(count / denominator for count in counts)
    return tuple(values)


def mean_absolute_distance(left: Profile, right: Profile) -> float:
    return sum(abs(a - b) for a, b in zip(left, right)) / len(left)


def conditional_direction_distance(left: Profile, right: Profile) -> float:
    """Mean total-variation distance across the deuce and ad distributions."""

    side_distances = []
    for offset in (0, 3):
        side_distances.append(
            0.5 * sum(abs(left[offset + index] - right[offset + index]) for index in range(3))
        )
    return sum(side_distances) / len(side_distances)


def split_records(
    records: Sequence[MatchServeRecord], strategy: str
) -> tuple[list[MatchServeRecord], list[MatchServeRecord]]:
    ordered = sorted(records, key=lambda row: (row.date, row.match_id))
    if strategy == "chronological":
        midpoint = len(ordered) // 2
        return ordered[:midpoint], ordered[midpoint:]
    if strategy == "alternating":
        return ordered[::2], ordered[1::2]
    raise ValueError(f"unknown split strategy: {strategy}")


def _percentile(values: Sequence[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("percentile requires at least one value")
    return ordered[round(probability * (len(ordered) - 1))]


def bootstrap_median_within(
    eligible: Sequence[tuple[list[MatchServeRecord], list[MatchServeRecord]]],
    profile_builder: ProfileBuilder,
    distance: Distance,
    seed: int,
    replicates: int = BOOTSTRAP_REPLICATES,
) -> tuple[float, float] | None:
    rng = random.Random(seed)
    estimates = []
    for _ in range(replicates):
        distances = []
        for left, right in eligible:
            sampled_left = [rng.choice(left) for _ in left]
            sampled_right = [rng.choice(right) for _ in right]
            left_profile = profile_builder(sampled_left)
            right_profile = profile_builder(sampled_right)
            if left_profile is not None and right_profile is not None:
                distances.append(distance(left_profile, right_profile))
        if distances:
            estimates.append(median(distances))
    if not estimates:
        return None
    return _percentile(estimates, 0.025), _percentile(estimates, 0.975)


def evaluate_family(
    grouped: dict[tuple[str, str], list[MatchServeRecord]],
    profile_builder: ProfileBuilder,
    distance: Distance,
    split_strategy: str,
    minimum_matches_per_split: int,
    seed: int,
) -> dict[str, object]:
    """Compare same-player split distance with cross-player negative controls."""

    EvaluationRow = tuple[
        str, list[MatchServeRecord], list[MatchServeRecord], Profile, Profile
    ]
    by_tour: dict[str, list[EvaluationRow]] = defaultdict(list)
    for (tour, player), records in sorted(grouped.items()):
        left, right = split_records(records, split_strategy)
        if min(len(left), len(right)) < minimum_matches_per_split:
            continue
        left_profile = profile_builder(left)
        right_profile = profile_builder(right)
        if left_profile is not None and right_profile is not None:
            by_tour[tour].append((player, left, right, left_profile, right_profile))

    tour_results = []
    all_within = []
    all_between = []
    all_bootstrap_pairs = []
    for tour, rows in sorted(by_tour.items()):
        within = [distance(row[3], row[4]) for row in rows]
        between = [
            distance(left[3], right[4])
            for left in rows
            for right in rows
            if left[0] != right[0]
        ]
        all_within.extend(within)
        all_between.extend(between)
        all_bootstrap_pairs.extend((row[1], row[2]) for row in rows)
        tour_results.append(
            {
                "tour": tour,
                "eligible_players": len(rows),
                "median_within_player_distance": median(within) if within else None,
                "median_between_player_distance": median(between) if between else None,
                "within_to_between_ratio": (
                    median(within) / median(between) if between and median(between) else None
                ),
            }
        )
    interval = bootstrap_median_within(
        all_bootstrap_pairs, profile_builder, distance, seed
    )
    return {
        "split_strategy": split_strategy,
        "minimum_matches_per_split": minimum_matches_per_split,
        "eligible_players": len(all_within),
        "median_within_player_distance": median(all_within) if all_within else None,
        "match_bootstrap_resampled_95_range": list(interval) if interval else None,
        "median_between_player_distance": median(all_between) if all_between else None,
        "within_to_between_ratio": (
            median(all_within) / median(all_between)
            if all_within and all_between and median(all_between)
            else None
        ),
        "by_tour": tour_results,
    }


def candidate_families() -> tuple[tuple[str, ProfileBuilder, Distance], ...]:
    """Return the versioned candidate families shared by stability experiments."""

    return (
        ("serve_outcomes", outcome_profile, mean_absolute_distance),
        (
            "first_serve_direction",
            lambda rows: direction_profile(rows, "1"),
            conditional_direction_distance,
        ),
        (
            "second_serve_direction",
            lambda rows: direction_profile(rows, "2"),
            conditional_direction_distance,
        ),
    )


def run_experiment(records: Sequence[MatchServeRecord]) -> dict[str, object]:
    grouped: defaultdict[tuple[str, str], list[MatchServeRecord]] = defaultdict(list)
    for record in records:
        grouped[(record.tour, record.player)].append(record)
    results = {}
    seed = BOOTSTRAP_SEED
    for family, profile_builder, distance in candidate_families():
        results[family] = []
        for strategy in ("chronological", "alternating"):
            for threshold in ELIGIBILITY_GRID:
                results[family].append(
                    evaluate_family(
                        grouped,
                        profile_builder,
                        distance,
                        strategy,
                        threshold,
                        seed,
                    )
                )
                seed += 1
    return {
        "experiment_id": EXPERIMENT_ID,
        "snapshot_id": SNAPSHOT_ID,
        "match_player_records": len(records),
        "player_tour_groups": len(grouped),
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "eligibility_grid_matches_per_split": list(ELIGIBILITY_GRID),
        "families": results,
    }


def _format(value: float | None, digits: int = 3) -> str:
    return "NA" if value is None else f"{value:.{digits}f}"


def render_report(result: dict[str, object]) -> str:
    rows = [
        "| Family | Split | Matches / half | Players | Within median | "
        "Bootstrap resampled 95% range | Between median | Ratio |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for family, evaluations in result["families"].items():
        for evaluation in evaluations:
            interval = evaluation["match_bootstrap_resampled_95_range"]
            interval_text = (
                f"{_format(interval[0])}-{_format(interval[1])}" if interval else "NA"
            )
            rows.append(
                f"| `{family}` | {evaluation['split_strategy']} | "
                f"{evaluation['minimum_matches_per_split']} | {evaluation['eligible_players']:,} | "
                f"{_format(evaluation['median_within_player_distance'])} | {interval_text} | "
                f"{_format(evaluation['median_between_player_distance'])} | "
                f"{_format(evaluation['within_to_between_ratio'])} |"
            )
    return f"""# Serve split-sample stability pilot

**Experiment:** `{result['experiment_id']}`

**Snapshot:** `{result['snapshot_id']}`

**Status:** aggregate falsification evidence; no player ranking or profile is produced

## Question

Are candidate serve descriptions more similar across independent match samples from the same
player than across different players in the same tour?

## Design

- The unit resampled for uncertainty is the match, not the point.
- Chronological halves test temporal persistence; alternating matches test sensitivity to the split.
- The 2/5/10/20 matches-per-half grid is a sensitivity analysis, not an approved eligibility rule.
- Outcome distance is the mean absolute difference across first-serve-in, ace, and double-fault
  rates, each using its field-specific resolved denominator.
- Direction distance is mean total-variation distance for wide/body/T distributions normalized
  separately on deuce and ad courts.
- Between-player negative controls compare the first split of one player with the second split of
  every other player in the same tour.
- The resampled range is the central 95% of a deterministic {result['bootstrap_replicates']}-replicate
  match-level bootstrap distribution of the median within-player distance. Because distances are
  non-negative, this range is not presented as a confidence interval and can be upward-biased. Its
  low replicate count is suitable for this feasibility pilot, not final inference.

## Results

{chr(10).join(rows)}

Lower within-player distance than between-player distance is necessary, not sufficient, evidence
of persistence. A ratio below one favors player-specific repeatability; overlapping context,
selection, opponent, era, surface, and chart-author effects remain plausible explanations.

## Interpretation boundary

**OPEN QUESTION:** whether any family remains stable after surface, opponent strength, era, and
tournament controls. This snapshot does not yet contain validated canonical joins for those tests.

**ENGINEERING DECISION:** do not combine families, assign weights, rank players, cluster styles, or
publish Tennis DNA profiles from this pilot. Eligibility and shrinkage rules remain unresolved.

## Reproduce

```powershell
python -m research.experiments.serve_stability
```
"""


def write_outputs(result: dict[str, object], report_root: Path = Path("research")) -> None:
    (report_root / "serve_stability.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    (report_root / "serve_stability.md").write_text(render_report(result), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=Path("research"))
    arguments = parser.parse_args()
    result = run_experiment(load_match_records(arguments.source))
    write_outputs(result, arguments.output)
    print(f"Wrote {arguments.output / 'serve_stability.json'}")
    print(f"Wrote {arguments.output / 'serve_stability.md'}")


if __name__ == "__main__":
    main()
