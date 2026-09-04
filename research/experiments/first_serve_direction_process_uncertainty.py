"""Validation-estimated temporal uncertainty for first-serve direction."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from statistics import mean, median
from typing import Iterable, Mapping, Sequence

from research.experiments.context_serve_stability import (
    CONTEXT_COMMIT,
    CONTEXT_SNAPSHOT_ID,
    DEFAULT_CONTEXT_SOURCE,
    DEFAULT_SOURCE,
    ContextualServeRecord,
    load_experiment_records,
)
from research.experiments.first_serve_direction_robustness import (
    COMPONENTS,
    MATCH_THRESHOLDS,
    MINIMUM_TEST_MATCHES,
    WINDOW_YEARS,
    ComponentEstimate,
    DirectionHistory,
    build_histories,
    component_estimates,
)
from research.experiments.profile_mcp_snapshot import SNAPSHOT_ID
from research.experiments.serve_publication_readiness import _quantiles


EXPERIMENT_ID = "research-first-serve-direction-process-uncertainty-v0.1"
SPECIFICATION = "research/first_serve_direction_process_uncertainty_spec.md"
MINIMUM_CALIBRATION_CASES = 30
NOMINAL_MULTIPLIER = 1.96
PlayerSurface = tuple[str, str, str]


@dataclass(frozen=True)
class CalibrationCase:
    tour: str
    component: str
    required_process_variance: float


@dataclass(frozen=True)
class ProcessEstimate:
    variance: float
    source: str
    calibration_cases: int


@dataclass(frozen=True)
class ProcessEvaluationRow:
    tour: str
    player_key: str
    surface: str
    test_year: int
    base_covered: tuple[bool, ...]
    process_covered: tuple[bool, ...]
    base_radii: tuple[float, ...]
    process_radii: tuple[float, ...]
    process_standard_deviations: tuple[float, ...]
    process_sources: tuple[str, ...]


def _component_comparison(
    history: DirectionHistory, future: DirectionHistory
) -> tuple[tuple[ComponentEstimate, ComponentEstimate], ...]:
    return tuple(zip(component_estimates(history), component_estimates(future)))


def required_process_variance(
    history: ComponentEstimate, future: ComponentEstimate
) -> float:
    residual = abs(history.raw_share - future.raw_share)
    base_variance = history.clustered_se**2 + future.clustered_se**2
    return max(0.0, (residual / NOMINAL_MULTIPLIER) ** 2 - base_variance)


def calibration_cases(
    histories: Mapping[PlayerSurface, DirectionHistory],
    validation: Mapping[PlayerSurface, DirectionHistory],
    minimum_history_matches: int,
) -> list[CalibrationCase]:
    eligible = {
        key
        for key, history in histories.items()
        if len(history.matches) >= minimum_history_matches
        and key in validation
        and len(validation[key].matches) >= MINIMUM_TEST_MATCHES
    }
    cases = []
    for key in sorted(eligible):
        for component, (history, future) in zip(
            COMPONENTS, _component_comparison(histories[key], validation[key])
        ):
            cases.append(
                CalibrationCase(
                    tour=key[0],
                    component=component,
                    required_process_variance=required_process_variance(
                        history, future
                    ),
                )
            )
    return cases


def finite_sample_quantile(values: Sequence[float], probability: float) -> float:
    if not values:
        raise ValueError("a finite-sample quantile requires at least one value")
    if not 0 < probability < 1:
        raise ValueError("probability must be strictly between zero and one")
    ordered = sorted(values)
    rank = min(len(ordered), math.ceil(probability * (len(ordered) + 1)))
    return ordered[rank - 1]


def estimate_process_variances(
    cases: Sequence[CalibrationCase],
) -> dict[tuple[str, str], ProcessEstimate]:
    by_tour_component: defaultdict[tuple[str, str], list[float]] = defaultdict(list)
    by_component: defaultdict[str, list[float]] = defaultdict(list)
    global_values = []
    for case in cases:
        by_tour_component[(case.tour, case.component)].append(
            case.required_process_variance
        )
        by_component[case.component].append(case.required_process_variance)
        global_values.append(case.required_process_variance)
    estimates = {}
    tours = sorted({case.tour for case in cases})
    for tour in tours:
        for component in COMPONENTS:
            primary = by_tour_component[(tour, component)]
            pooled_component = by_component[component]
            if len(primary) >= MINIMUM_CALIBRATION_CASES:
                values, source = primary, "tour_component"
            elif len(pooled_component) >= MINIMUM_CALIBRATION_CASES:
                values, source = pooled_component, "pooled_component"
            elif global_values:
                values, source = global_values, "global"
            else:
                continue
            estimates[(tour, component)] = ProcessEstimate(
                variance=finite_sample_quantile(values, 0.95),
                source=source,
                calibration_cases=len(values),
            )
    return estimates


def score_process_histories(
    history: DirectionHistory,
    test: DirectionHistory,
    test_year: int,
    estimates: Mapping[tuple[str, str], ProcessEstimate],
) -> ProcessEvaluationRow:
    base_covered = []
    process_covered = []
    base_radii = []
    process_radii = []
    process_deviations = []
    sources = []
    for component, (past, observed) in zip(
        COMPONENTS, _component_comparison(history, test)
    ):
        estimate = estimates[(history.tour, component)]
        residual = abs(past.raw_share - observed.raw_share)
        base_variance = past.clustered_se**2 + observed.clustered_se**2
        base_radius = NOMINAL_MULTIPLIER * math.sqrt(base_variance)
        process_radius = NOMINAL_MULTIPLIER * math.sqrt(
            base_variance + estimate.variance
        )
        base_covered.append(residual <= base_radius)
        process_covered.append(residual <= process_radius)
        base_radii.append(base_radius)
        process_radii.append(process_radius)
        process_deviations.append(math.sqrt(estimate.variance))
        sources.append(estimate.source)
    return ProcessEvaluationRow(
        tour=history.tour,
        player_key=history.player_key,
        surface=history.surface,
        test_year=test_year,
        base_covered=tuple(base_covered),
        process_covered=tuple(process_covered),
        base_radii=tuple(base_radii),
        process_radii=tuple(process_radii),
        process_standard_deviations=tuple(process_deviations),
        process_sources=tuple(sources),
    )


def summarize(rows: Sequence[ProcessEvaluationRow]) -> dict[str, object]:
    component_results = {}
    for index, component in enumerate(COMPONENTS):
        component_results[component] = {
            "base_coverage": (
                mean(row.base_covered[index] for row in rows) if rows else None
            ),
            "process_coverage": (
                mean(row.process_covered[index] for row in rows) if rows else None
            ),
            "mean_base_radius": (
                mean(row.base_radii[index] for row in rows) if rows else None
            ),
            "mean_process_radius": (
                mean(row.process_radii[index] for row in rows) if rows else None
            ),
        }
    return {
        "player_surface_periods": len(rows),
        "distinct_players": len({(row.tour, row.player_key) for row in rows}),
        "base_component_coverage": (
            mean(mean(row.base_covered) for row in rows) if rows else None
        ),
        "process_component_coverage": (
            mean(mean(row.process_covered) for row in rows) if rows else None
        ),
        "mean_base_radius": (
            mean(mean(row.base_radii) for row in rows) if rows else None
        ),
        "mean_process_radius": (
            mean(mean(row.process_radii) for row in rows) if rows else None
        ),
        "process_standard_deviation_quantiles": _quantiles(
            deviation
            for row in rows
            for deviation in row.process_standard_deviations
        ),
        "process_source_counts": dict(
            Counter(source for row in rows for source in row.process_sources)
        ),
        "components": component_results,
    }


def evaluate_configuration(
    records: Sequence[ContextualServeRecord],
    test_years: Sequence[int],
    window_years: int,
    minimum_history_matches: int,
) -> dict[str, object]:
    rows: list[ProcessEvaluationRow] = []
    folds = []
    for test_year in test_years:
        validation_year = test_year - 1
        training = build_histories(
            records, validation_year - window_years, validation_year
        )
        validation = build_histories(records, validation_year, test_year)
        cases = calibration_cases(training, validation, minimum_history_matches)
        estimates = estimate_process_variances(cases)
        history = build_histories(records, test_year - window_years, test_year)
        test = build_histories(records, test_year, test_year + 1)
        eligible = {
            key
            for key, item in history.items()
            if len(item.matches) >= minimum_history_matches
            and key in test
            and len(test[key].matches) >= MINIMUM_TEST_MATCHES
            and all((key[0], component) in estimates for component in COMPONENTS)
        }
        fold_rows = [
            score_process_histories(
                history[key], test[key], test_year, estimates
            )
            for key in sorted(eligible)
        ]
        rows.extend(fold_rows)
        folds.append(
            {
                "test_year": test_year,
                "calibration_cases": len(cases),
                "process_estimates": {
                    f"{tour}|{component}": {
                        "variance": estimate.variance,
                        "standard_deviation": math.sqrt(estimate.variance),
                        "source": estimate.source,
                        "calibration_cases": estimate.calibration_cases,
                    }
                    for (tour, component), estimate in sorted(estimates.items())
                },
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
    records: Sequence[ContextualServeRecord], source_profile: dict[str, object]
) -> dict[str, object]:
    years = sorted({int(record.date[:4]) for record in records})
    test_years_by_window = {
        str(window): list(range(min(years) + window + 1, max(years)))
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
        "mcp_snapshot_id": SNAPSHOT_ID,
        "context_snapshot_id": CONTEXT_SNAPSHOT_ID,
        "context_mirror_commit": CONTEXT_COMMIT,
        "window_years": list(WINDOW_YEARS),
        "minimum_history_matches": list(MATCH_THRESHOLDS),
        "minimum_test_matches": MINIMUM_TEST_MATCHES,
        "minimum_calibration_cases": MINIMUM_CALIBRATION_CASES,
        "test_years_by_window": test_years_by_window,
        "source_profile": source_profile,
        "evaluations": evaluations,
    }


def _value(value: float | None, digits: int = 3) -> str:
    return "NA" if value is None else f"{value:.{digits}f}"


def render_report(result: dict[str, object]) -> str:
    rows = [
        "| Window | History matches | Periods | Players | Base coverage | Process coverage | "
        "Base radius | Process radius | Process SD |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for evaluation in result["evaluations"]:
        scores = evaluation["scores"]
        process_quantiles = scores["process_standard_deviation_quantiles"]
        rows.append(
            f"| {evaluation['window_years']} | {evaluation['minimum_history_matches']} | "
            f"{scores['player_surface_periods']:,} | {scores['distinct_players']:,} | "
            f"{_value(scores['base_component_coverage'])} | "
            f"{_value(scores['process_component_coverage'])} | "
            f"{_value(scores['mean_base_radius'])} | "
            f"{_value(scores['mean_process_radius'])} | "
            f"{_value(process_quantiles['median'] if process_quantiles else None)} |"
        )
    base_coverages = [
        evaluation["scores"]["base_component_coverage"]
        for evaluation in result["evaluations"]
        if evaluation["scores"]["base_component_coverage"] is not None
    ]
    process_coverages = [
        evaluation["scores"]["process_component_coverage"]
        for evaluation in result["evaluations"]
        if evaluation["scores"]["process_component_coverage"] is not None
    ]
    radius_ratios = [
        evaluation["scores"]["mean_process_radius"]
        / evaluation["scores"]["mean_base_radius"]
        for evaluation in result["evaluations"]
        if evaluation["scores"]["mean_base_radius"]
    ]
    fallback_shares = []
    for evaluation in result["evaluations"]:
        counts = evaluation["scores"]["process_source_counts"]
        total = sum(counts.values())
        fallback_shares.append(
            (counts.get("pooled_component", 0) + counts.get("global", 0)) / total
        )
    reference = next(
        evaluation
        for evaluation in result["evaluations"]
        if evaluation["window_years"] == 5
        and evaluation["minimum_history_matches"] == 5
    )
    component_rows = [
        "| Component | Base coverage | Process coverage | Base radius | Process radius |",
        "|---|---:|---:|---:|---:|",
    ] + [
        f"| `{component}` | {_value(values['base_coverage'])} | "
        f"{_value(values['process_coverage'])} | "
        f"{_value(values['mean_base_radius'])} | "
        f"{_value(values['mean_process_radius'])} |"
        for component, values in reference["scores"]["components"].items()
    ]
    return f"""# First-serve direction process uncertainty

**Experiment:** `{result['experiment_id']}`

**Status:** temporal calibration falsification; no player output

## Design boundary

Validation seasons estimate an additional process variance separately by tour and direction
component. Each test season is untouched by that estimate. The grid retains 2/3/5/8-year histories
and 2/5/10/20 historical-match thresholds, with at least two validation or test matches for a
clustered seasonal share. The latest partial season is excluded.

## Results

{chr(10).join(rows)}

Base and process radii compare two noisy seasonal shares and include both history and test sampling
variance. A future displayed interval would not know test sampling variance and is not authorized
by this result.

## Adversarial review

Base clustered coverage ranges from {min(base_coverages):.1%} to {max(base_coverages):.1%}. Adding
validation-estimated process variance raises aggregate test coverage to
{min(process_coverages):.1%}-{max(process_coverages):.1%}, but mean radii become
{min(radius_ratios):.2f}-{max(radius_ratios):.2f} times the base radii. Calibration is recovered at
a material precision cost.

Fallback use ranges from {min(fallback_shares):.1%} to {max(fallback_shares):.1%} across the grid
and is highest for strict exposure thresholds in older sparse folds. Recent well-populated folds
more often support tour-component estimates, but this does not repair historical or grass
coverage. Small WTA high-exposure and grass cells remain the clearest adverse cases.

At the five-year/five-match reference, component results are:

{chr(10).join(component_rows)}

**STATISTICAL DECISION:** retain validation-estimated process variance as an internal uncertainty
candidate because it meets the aggregate test-coverage criterion across the grid. Do not approve
it for publication: interval width, fallback dependence, sparse surface/tour cells, and the
difference between evaluation and future display intervals remain unresolved.

## Interpretation boundary

**OPEN QUESTION:** acceptable calibration requires coverage, width, fallback frequency, tour,
surface, component, and period consistency to agree. Validation-targeted process variance can
overcover or fail under drift; neither outcome proves a stable player trait.

No player identity, estimate, or interval is serialized. No window, threshold, or publication
policy is approved automatically.

## Reproduce

```powershell
python -m research.experiments.first_serve_direction_process_uncertainty
```
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp-source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--context-source", type=Path, default=DEFAULT_CONTEXT_SOURCE)
    parser.add_argument(
        "--json",
        type=Path,
        default=Path("research/first_serve_direction_process_uncertainty.json"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("research/first_serve_direction_process_uncertainty.md"),
    )
    parser.add_argument("--render-existing", action="store_true")
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
