"""Temporal robustness audit for the first-serve direction candidate."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from statistics import mean, median
from typing import Iterable, Mapping, Sequence

from models.shrinkage import dirichlet_posterior
from pipelines.processing.entity_resolution import normalize_identity
from research.experiments.context_serve_stability import (
    CONTEXT_COMMIT,
    CONTEXT_SNAPSHOT_ID,
    DEFAULT_CONTEXT_SOURCE,
    DEFAULT_SOURCE,
    ContextualServeRecord,
    load_experiment_records,
)
from research.experiments.profile_mcp_snapshot import SNAPSHOT_ID
from research.experiments.serve_publication_readiness import (
    _quantiles,
    _ratio_cluster_standard_error,
)
from research.experiments.serve_shrinkage import DIRECTIONS, SIDES


EXPERIMENT_ID = "research-first-serve-direction-robustness-v0.1"
SPECIFICATION = "research/first_serve_direction_robustness_spec.md"
MEASUREMENT_SPECIFICATION = "research/first_serve_direction_measurement_spec.md"
WINDOW_YEARS = (2, 3, 5, 8)
MATCH_THRESHOLDS = (2, 5, 10, 20)
MINIMUM_TEST_MATCHES = 2
SIDE_SHARE_GRID = (0.10, 0.20, 0.30, 0.40)
COMPONENTS = tuple(f"{side}_{direction}" for side in SIDES for direction in DIRECTIONS)
Counts = tuple[int, ...]
PlayerSurface = tuple[str, str, str]


@dataclass
class DirectionHistory:
    tour: str
    player_key: str
    surface: str
    matches: dict[str, tuple[Counts, Counts]] = field(default_factory=dict)


@dataclass(frozen=True)
class ComponentEstimate:
    raw_share: float
    conditional_mean: float
    conditional_sd: float
    clustered_se: float


@dataclass(frozen=True)
class EvaluationRow:
    tour: str
    player_key: str
    surface: str
    test_year: int
    history_matches: int
    test_matches: int
    errors: tuple[float, ...]
    conditional_covered: tuple[bool, ...]
    clustered_covered: tuple[bool, ...]
    smaller_side_share: float


def _direction_blocks(record: ContextualServeRecord) -> tuple[Counts, Counts]:
    return tuple(
        tuple(
            record.metrics[f"direction:1:{side}:{direction}"]
            for direction in DIRECTIONS
        )
        for side in SIDES
    )


def _surface(record: ContextualServeRecord) -> str:
    return normalize_identity(record.surface) or "(blank)"


def audit_court_side_records(
    records: Iterable[ContextualServeRecord],
) -> dict[str, object]:
    counters: Counter[tuple[str, str, str]] = Counter()
    for record in records:
        blocks = _direction_blocks(record)
        side_totals = tuple(sum(block) for block in blocks)
        status = (
            "both_sides"
            if all(side_totals)
            else "one_side"
            if any(side_totals)
            else "no_direction"
        )
        for dimension, value in (
            ("overall", "all"),
            ("tour", record.tour),
            ("surface", f"{record.tour}|{_surface(record)}"),
        ):
            counters[(dimension, value, status)] += 1

    def rows(dimension: str) -> list[dict[str, object]]:
        values = sorted(
            {value for current, value, _ in counters if current == dimension}
        )
        result = []
        for value in values:
            counts = {
                status: counters[(dimension, value, status)]
                for status in ("both_sides", "one_side", "no_direction")
            }
            any_direction = counts["both_sides"] + counts["one_side"]
            result.append(
                {
                    dimension: value,
                    **counts,
                    "any_direction": any_direction,
                    "both_given_any_rate": (
                        counts["both_sides"] / any_direction
                        if any_direction
                        else None
                    ),
                }
            )
        return result

    return {
        "overall": rows("overall")[0],
        "by_tour": rows("tour"),
        "by_surface": rows("surface"),
    }


def build_histories(
    records: Iterable[ContextualServeRecord], start_year: int, end_year: int
) -> dict[PlayerSurface, DirectionHistory]:
    """Build both-side direction histories for start_year <= year < end_year."""

    histories: dict[PlayerSurface, DirectionHistory] = {}
    for record in records:
        record_year = int(record.date[:4])
        if not start_year <= record_year < end_year:
            continue
        blocks = _direction_blocks(record)
        if any(sum(block) == 0 for block in blocks):
            continue
        key = (record.tour, normalize_identity(record.player), _surface(record))
        history = histories.setdefault(
            key, DirectionHistory(key[0], key[1], key[2])
        )
        history.matches[record.match_id] = blocks
    return histories


def component_estimates(
    history: DirectionHistory,
) -> tuple[ComponentEstimate, ...]:
    match_blocks = list(history.matches.values())
    estimates = []
    for side_index in range(len(SIDES)):
        counts = [blocks[side_index] for blocks in match_blocks]
        totals = tuple(
            sum(match[index] for match in counts) for index in range(len(DIRECTIONS))
        )
        conditional_means, conditional_sds = dirichlet_posterior(
            totals, (1 / len(DIRECTIONS),) * len(DIRECTIONS), 0
        )
        total = sum(totals)
        for direction_index in range(len(DIRECTIONS)):
            clustered_se = _ratio_cluster_standard_error(
                counts, direction_index
            )
            if clustered_se is None:
                raise ValueError("component estimates require at least two matches")
            estimates.append(
                ComponentEstimate(
                    raw_share=totals[direction_index] / total,
                    conditional_mean=conditional_means[direction_index],
                    conditional_sd=conditional_sds[direction_index],
                    clustered_se=clustered_se,
                )
            )
    return tuple(estimates)


def _smaller_side_share(history: DirectionHistory) -> float:
    totals = [0, 0]
    for blocks in history.matches.values():
        for index, counts in enumerate(blocks):
            totals[index] += sum(counts)
    return min(totals) / sum(totals)


def score_histories(
    history: DirectionHistory,
    test: DirectionHistory,
    test_year: int,
) -> EvaluationRow:
    historical = component_estimates(history)
    future = component_estimates(test)
    errors = []
    conditional_covered = []
    clustered_covered = []
    for past, observed in zip(historical, future):
        errors.append(abs(past.raw_share - observed.raw_share))
        conditional_radius = 1.96 * math.sqrt(
            past.conditional_sd**2 + observed.conditional_sd**2
        )
        clustered_radius = 1.96 * math.sqrt(
            past.clustered_se**2 + observed.clustered_se**2
        )
        conditional_covered.append(
            abs(past.conditional_mean - observed.raw_share) <= conditional_radius
        )
        clustered_covered.append(
            abs(past.raw_share - observed.raw_share) <= clustered_radius
        )
    return EvaluationRow(
        tour=history.tour,
        player_key=history.player_key,
        surface=history.surface,
        test_year=test_year,
        history_matches=len(history.matches),
        test_matches=len(test.matches),
        errors=tuple(errors),
        conditional_covered=tuple(conditional_covered),
        clustered_covered=tuple(clustered_covered),
        smaller_side_share=_smaller_side_share(history),
    )


def summarize(rows: Sequence[EvaluationRow]) -> dict[str, object]:
    component_results = {}
    for index, component in enumerate(COMPONENTS):
        component_results[component] = {
            "mean_absolute_error": (
                mean(row.errors[index] for row in rows) if rows else None
            ),
            "conditional_coverage": (
                mean(row.conditional_covered[index] for row in rows)
                if rows
                else None
            ),
            "clustered_coverage": (
                mean(row.clustered_covered[index] for row in rows)
                if rows
                else None
            ),
        }
    return {
        "player_surface_periods": len(rows),
        "distinct_players": len({(row.tour, row.player_key) for row in rows}),
        "mean_component_absolute_error": (
            mean(mean(row.errors) for row in rows) if rows else None
        ),
        "median_component_absolute_error": (
            median(mean(row.errors) for row in rows) if rows else None
        ),
        "conditional_component_coverage": (
            mean(mean(row.conditional_covered) for row in rows) if rows else None
        ),
        "clustered_component_coverage": (
            mean(mean(row.clustered_covered) for row in rows) if rows else None
        ),
        "smaller_side_share_quantiles": _quantiles(
            row.smaller_side_share for row in rows
        ),
        "smaller_side_share_sensitivity": {
            str(threshold): sum(
                row.smaller_side_share >= threshold for row in rows
            )
            for threshold in SIDE_SHARE_GRID
        },
        "components": component_results,
    }


def _compact_reconciliation(profile: Mapping[str, object]) -> dict[str, object]:
    if profile["snapshot_id"] != SNAPSHOT_ID:
        raise ValueError("MCP profile snapshot does not match the experiment snapshot")
    direction = profile["serve_reconciliation"]["serve_direction"]["1"]
    return {
        "comparable_records": direction["comparable_records"],
        "exact_records": direction["exact_records"],
        "exact_rate": direction["exact_rate"],
        "mismatch_context": direction["mismatch_context"],
    }


def evaluate_configuration(
    records: Sequence[ContextualServeRecord],
    test_years: Sequence[int],
    window_years: int,
    minimum_history_matches: int,
) -> dict[str, object]:
    rows: list[EvaluationRow] = []
    folds = []
    for test_year in test_years:
        histories = build_histories(
            records, test_year - window_years, test_year
        )
        tests = build_histories(records, test_year, test_year + 1)
        eligible_keys = {
            key
            for key, history in histories.items()
            if len(history.matches) >= minimum_history_matches
            and key in tests
            and len(tests[key].matches) >= MINIMUM_TEST_MATCHES
        }
        fold_rows = [
            score_histories(histories[key], tests[key], test_year)
            for key in sorted(eligible_keys)
        ]
        rows.extend(fold_rows)
        folds.append(
            {
                "test_year": test_year,
                "player_surface_periods": len(fold_rows),
                "scores": summarize(fold_rows),
            }
        )
    tours = sorted({row.tour for row in rows})
    surfaces = sorted({(row.tour, row.surface) for row in rows})
    return {
        "window_years": window_years,
        "minimum_history_matches": minimum_history_matches,
        "minimum_test_matches": MINIMUM_TEST_MATCHES,
        "scores": summarize(rows),
        "by_tour": {
            tour: summarize([row for row in rows if row.tour == tour])
            for tour in tours
        },
        "by_surface": {
            f"{tour}|{surface}": summarize(
                [
                    row
                    for row in rows
                    if row.tour == tour and row.surface == surface
                ]
            )
            for tour, surface in surfaces
        },
        "folds": folds,
    }


def run_experiment(
    records: Sequence[ContextualServeRecord],
    source_profile: dict[str, object],
    mcp_profile: Mapping[str, object],
) -> dict[str, object]:
    years = sorted({int(record.date[:4]) for record in records})
    test_years_by_window = {
        str(window): list(range(min(years) + window, max(years)))
        for window in WINDOW_YEARS
    }
    evaluations = [
        evaluate_configuration(
            records, test_years_by_window[str(window)], window, threshold
        )
        for window in WINDOW_YEARS
        for threshold in MATCH_THRESHOLDS
    ]
    return {
        "generated_on": date.today().isoformat(),
        "experiment_id": EXPERIMENT_ID,
        "specification": SPECIFICATION,
        "measurement_specification": MEASUREMENT_SPECIFICATION,
        "mcp_snapshot_id": SNAPSHOT_ID,
        "context_snapshot_id": CONTEXT_SNAPSHOT_ID,
        "context_mirror_commit": CONTEXT_COMMIT,
        "window_years": list(WINDOW_YEARS),
        "minimum_history_matches": list(MATCH_THRESHOLDS),
        "minimum_test_matches": MINIMUM_TEST_MATCHES,
        "complete_test_years_by_window": test_years_by_window,
        "source_profile": source_profile,
        "court_side_record_audit": audit_court_side_records(records),
        "reconciliation": _compact_reconciliation(mcp_profile),
        "evaluations": evaluations,
    }


def _value(value: float | None, digits: int = 3) -> str:
    return "NA" if value is None else f"{value:.{digits}f}"


def render_report(result: dict[str, object]) -> str:
    rows = [
        "| Window | History matches | Periods | Players | Mean error | Conditional coverage | "
        "Clustered coverage | Median smaller-side share |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for evaluation in result["evaluations"]:
        scores = evaluation["scores"]
        rows.append(
            f"| {evaluation['window_years']} | {evaluation['minimum_history_matches']} | "
            f"{scores['player_surface_periods']:,} | {scores['distinct_players']:,} | "
            f"{_value(scores['mean_component_absolute_error'])} | "
            f"{_value(scores['conditional_component_coverage'])} | "
            f"{_value(scores['clustered_component_coverage'])} | "
            f"{_value(scores['smaller_side_share_quantiles']['median'])} |"
        )
    reconciliation = result["reconciliation"]
    surfaces = reconciliation["mismatch_context"]["surface"]
    surface_rows = [
        "| Surface | Comparable | Mismatches | Mismatch rate |",
        "|---|---:|---:|---:|",
    ] + [
        f"| `{item['surface']}` | {item['comparable_records']:,} | "
        f"{item['mismatch_records']:,} | {item['mismatch_rate']:.2%} |"
        for item in surfaces
    ]
    clustered_coverages = [
        evaluation["scores"]["clustered_component_coverage"]
        for evaluation in result["evaluations"]
        if evaluation["scores"]["clustered_component_coverage"] is not None
    ]
    reference = next(
        evaluation
        for evaluation in result["evaluations"]
        if evaluation["window_years"] == 5
        and evaluation["minimum_history_matches"] == 5
    )
    component_rows = [
        "| Component | Mean error | Conditional coverage | Clustered coverage |",
        "|---|---:|---:|---:|",
    ] + [
        f"| `{component}` | {_value(values['mean_absolute_error'])} | "
        f"{_value(values['conditional_coverage'])} | "
        f"{_value(values['clustered_coverage'])} |"
        for component, values in reference["scores"]["components"].items()
    ]
    atp_reference = reference["by_tour"]["ATP"]
    wta_reference = reference["by_tour"]["WTA"]
    sides = result["court_side_record_audit"]["overall"]
    return f"""# First-serve direction temporal robustness

**Experiment:** `{result['experiment_id']}`

**Status:** aggregate falsification; no player output

## Input checks

The collision-safe input contains
{result['source_profile']['eligible_contextual_match_player_records']:,} match-player records.
Among records with any known successful first-serve direction, {sides['both_sides']:,} contain both
court sides and {sides['one_side']:,} contain only one. The both-side eligibility rate is
{sides['both_given_any_rate']:.2%}.

Canonical side-aware reconciliation is {reconciliation['exact_rate']:.2%} across
{reconciliation['comparable_records']:,} comparable records:

{chr(10).join(surface_rows)}

## Temporal results

Each row aggregates player-surface-period results over complete test seasons. Coverage is the share
of six component comparisons whose later-season raw share falls inside the diagnostic combined
history/test radius.

{chr(10).join(rows)}

## Adversarial review

Clustered component coverage ranges from {min(clustered_coverages):.1%} to
{max(clustered_coverages):.1%} across the pre-specified grid, well below the 95% diagnostic
reference. Coverage generally falls as the history window and minimum match count increase, even
while mean absolute error falls with exposure. Narrower sampling intervals are not absorbing
season-to-season process variation.

At the five-year/five-match reference, ATP mean component error is
{atp_reference['mean_component_absolute_error']:.3f} and WTA error is
{wta_reference['mean_component_absolute_error']:.3f}. The component breakdown is:

{chr(10).join(component_rows)}

No component reaches adequate diagnostic coverage. Match clustering improves coverage over the
conditional count model but does not close the gap. Both court sides are present in essentially
every record with observed direction, and the median smaller-side event share is near 47%, so
court-side availability does not explain the temporal miss.

**STATISTICAL DECISION:** retain first-serve direction as an internal descriptive measurement, but
reject the current conditional or match-cluster-only interval as a player-stability model. Do not
expand the shrinkage grid yet. The next model must estimate temporal/process variation on
validation seasons and demonstrate later-season calibration without player output.

## Interpretation boundary

Conditional and clustered coverage are empirical diagnostics, not calibrated interval guarantees.
They average correlated direction components and repeated player histories. Requiring two test
matches conditions the evaluation cohort on later participation, while the latest partial season
is excluded completely.

**OPEN QUESTION:** window, exposure, tour, surface, component, and period consistency must be
reviewed together. No favorable aggregate row selects a reporting period or eligibility rule.

No player identity or estimate is serialized. Expanded shrinkage-prior analysis remains blocked
until this raw-measurement result is reviewed.

## Reproduce

```powershell
python -m research.experiments.first_serve_direction_robustness
```
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp-source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--context-source", type=Path, default=DEFAULT_CONTEXT_SOURCE)
    parser.add_argument(
        "--profile", type=Path, default=Path("research/mcp_snapshot_profile.json")
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=Path("research/first_serve_direction_robustness.json"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("research/first_serve_direction_robustness.md"),
    )
    parser.add_argument("--render-existing", action="store_true")
    arguments = parser.parse_args()
    if arguments.render_existing:
        result = json.loads(arguments.json.read_text(encoding="utf-8"))
    else:
        records, source_profile = load_experiment_records(
            arguments.mcp_source, arguments.context_source
        )
        profile = json.loads(arguments.profile.read_text(encoding="utf-8"))
        result = run_experiment(records, source_profile, profile)
        arguments.json.write_text(
            json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
        )
    arguments.report.write_text(render_report(result), encoding="utf-8")
    if not arguments.render_existing:
        print(f"Wrote {arguments.json}")
    print(f"Wrote {arguments.report}")


if __name__ == "__main__":
    main()
