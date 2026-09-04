"""Aggregate coverage and clustered-uncertainty audit for serve targets."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from statistics import median
from typing import Iterable, Sequence

from models.shrinkage import beta_posterior, dirichlet_posterior
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
from research.experiments.serve_shrinkage import (
    DIRECTIONS,
    HISTORY_SEASONS,
    TARGETS,
    TargetSpec,
    _observations,
)


EXPERIMENT_ID = "research-serve-publication-readiness-v0.1"
SPECIFICATION = "research/serve_publication_readiness_spec.md"
MATCH_GRID = (2, 5, 10, 20)
SEASON_GRID = (1, 2, 3)
OPPONENT_GRID = (2, 3, 5)
TOURNAMENT_GRID = (1, 2, 3)
AUTHOR_GRID = (1, 2)
MAX_MATCH_SHARE_GRID = (0.75, 0.50, 0.33)
EFFECTIVE_MATCH_GRID = (2, 5, 10, 20)
Counts = tuple[int, ...]
PlayerSurface = tuple[str, str, str]


@dataclass
class HistoryAccumulator:
    tour: str
    player_key: str
    surface: str
    as_of_year: int
    matches: dict[str, tuple[Counts, ...]] = field(default_factory=dict)
    seasons: set[int] = field(default_factory=set)
    opponents: set[str] = field(default_factory=set)
    tournaments: set[str] = field(default_factory=set)
    chart_authors: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class HistoryDiagnostic:
    tour: str
    player_key: str
    surface: str
    as_of_year: int
    matches: int
    seasons: int
    opponents: int
    tournaments: int
    chart_authors: int
    eligible_events: int
    largest_match_share: float
    effective_matches: float
    cluster_standard_error: float | None
    conditional_standard_deviation: float | None
    cluster_to_conditional_sd_ratio: float | None

    @property
    def cluster_half_width_95(self) -> float | None:
        if self.cluster_standard_error is None:
            return None
        return 1.96 * self.cluster_standard_error

def _player_surface(record: ContextualServeRecord) -> PlayerSurface:
    return (
        record.tour,
        normalize_identity(record.player),
        normalize_identity(record.surface) or "(blank)",
    )


def _add_known(values: set[str], raw_value: str) -> None:
    normalized = normalize_identity(raw_value)
    if normalized:
        values.add(normalized)


def histories_for_window(
    records: Iterable[ContextualServeRecord],
    target: TargetSpec,
    as_of_year: int,
) -> list[HistoryAccumulator]:
    """Build target-valid five-season histories without using the as-of season."""

    histories: dict[PlayerSurface, HistoryAccumulator] = {}
    first_year = as_of_year - HISTORY_SEASONS
    for record in records:
        record_year = int(record.date[:4])
        if not first_year <= record_year < as_of_year:
            continue
        observations = _observations(record, target)
        if not observations:
            continue
        key = _player_surface(record)
        history = histories.setdefault(
            key,
            HistoryAccumulator(key[0], key[1], key[2], as_of_year),
        )
        history.matches[record.match_id] = tuple(
            counts for _, counts in observations
        )
        history.seasons.add(record_year)
        _add_known(history.opponents, record.opponent)
        _add_known(history.tournaments, record.tournament)
        _add_known(history.chart_authors, record.chart_author)
    return list(histories.values())


def _ratio_cluster_standard_error(
    match_counts: Sequence[Counts], category: int
) -> float | None:
    clusters = len(match_counts)
    if clusters < 2:
        return None
    total_trials = sum(sum(counts) for counts in match_counts)
    if total_trials == 0:
        return None
    rate = sum(counts[category] for counts in match_counts) / total_trials
    squared_influence = sum(
        (counts[category] - rate * sum(counts)) ** 2 for counts in match_counts
    )
    variance = clusters / (clusters - 1) * squared_influence / total_trials**2
    return math.sqrt(variance)


def _conditional_standard_deviation(
    match_counts: Sequence[Counts], category: int
) -> float:
    totals = tuple(
        sum(counts[index] for counts in match_counts)
        for index in range(len(match_counts[0]))
    )
    if len(totals) == 2:
        _, deviation = beta_posterior(totals[0], sum(totals), 0.5, 0)
        return deviation
    _, deviations = dirichlet_posterior(totals, (1 / len(totals),) * len(totals), 0)
    return deviations[category]


def diagnose_history(history: HistoryAccumulator) -> HistoryDiagnostic:
    match_blocks = list(history.matches.values())
    match_events = [
        sum(sum(counts) for counts in blocks) for blocks in match_blocks
    ]
    total_events = sum(match_events)
    effective_matches = total_events**2 / sum(value**2 for value in match_events)
    clustered = []
    conditional = []
    clustered_to_conditional = []
    block_count = len(match_blocks[0])
    categories = len(match_blocks[0][0])
    for block_index in range(block_count):
        counts = [blocks[block_index] for blocks in match_blocks]
        component_indexes = (0,) if categories == 2 else range(categories)
        for category in component_indexes:
            cluster_deviation = _ratio_cluster_standard_error(counts, category)
            conditional_deviation = _conditional_standard_deviation(counts, category)
            if cluster_deviation is not None:
                clustered.append(cluster_deviation)
                if conditional_deviation > 0:
                    clustered_to_conditional.append(
                        cluster_deviation / conditional_deviation
                    )
            conditional.append(conditional_deviation)
    return HistoryDiagnostic(
        tour=history.tour,
        player_key=history.player_key,
        surface=history.surface,
        as_of_year=history.as_of_year,
        matches=len(match_blocks),
        seasons=len(history.seasons),
        opponents=len(history.opponents),
        tournaments=len(history.tournaments),
        chart_authors=len(history.chart_authors),
        eligible_events=total_events,
        largest_match_share=max(match_events) / total_events,
        effective_matches=effective_matches,
        cluster_standard_error=max(clustered) if clustered else None,
        conditional_standard_deviation=max(conditional) if conditional else None,
        cluster_to_conditional_sd_ratio=(
            max(clustered_to_conditional) if clustered_to_conditional else None
        ),
    )


def _quantiles(values: Iterable[float]) -> dict[str, float] | None:
    ordered = sorted(values)
    if not ordered:
        return None

    def value_at(fraction: float) -> float:
        return ordered[round(fraction * (len(ordered) - 1))]

    return {
        "minimum": ordered[0],
        "p25": value_at(0.25),
        "median": median(ordered),
        "p75": value_at(0.75),
        "maximum": ordered[-1],
    }


def _threshold_counts(
    diagnostics: Sequence[HistoryDiagnostic],
    attribute: str,
    thresholds: Sequence[float],
    maximum: bool = False,
) -> dict[str, int]:
    return {
        str(threshold): sum(
            getattr(item, attribute) <= threshold
            if maximum
            else getattr(item, attribute) >= threshold
            for item in diagnostics
        )
        for threshold in thresholds
    }


def _uncertainty_summary(
    diagnostics: Sequence[HistoryDiagnostic],
) -> dict[str, object]:
    uncertain = [
        item for item in diagnostics if item.cluster_standard_error is not None
    ]
    return {
        "history_instances": len(uncertain),
        "cluster_half_width_95": _quantiles(
            item.cluster_half_width_95
            for item in uncertain
            if item.cluster_half_width_95 is not None
        ),
        "cluster_to_conditional_sd_ratio": _quantiles(
            item.cluster_to_conditional_sd_ratio
            for item in uncertain
            if item.cluster_to_conditional_sd_ratio is not None
        ),
    }


def summarize(diagnostics: Sequence[HistoryDiagnostic]) -> dict[str, object]:
    total = len(diagnostics)
    intersection = sum(
        item.matches >= 5
        and item.seasons >= 2
        and item.opponents >= 3
        and item.tournaments >= 2
        and item.largest_match_share <= 0.50
        and item.effective_matches >= 3
        for item in diagnostics
    )
    return {
        "history_instances": total,
        "distinct_players": len(
            {(item.tour, item.player_key) for item in diagnostics}
        ),
        "exposure_quantiles": {
            "matches": _quantiles(item.matches for item in diagnostics),
            "eligible_events": _quantiles(
                item.eligible_events for item in diagnostics
            ),
            "effective_matches": _quantiles(
                item.effective_matches for item in diagnostics
            ),
            "largest_match_share": _quantiles(
                item.largest_match_share for item in diagnostics
            ),
        },
        "sensitivity_counts": {
            "minimum_matches": _threshold_counts(
                diagnostics, "matches", MATCH_GRID
            ),
            "minimum_seasons": _threshold_counts(
                diagnostics, "seasons", SEASON_GRID
            ),
            "minimum_opponents": _threshold_counts(
                diagnostics, "opponents", OPPONENT_GRID
            ),
            "minimum_tournaments": _threshold_counts(
                diagnostics, "tournaments", TOURNAMENT_GRID
            ),
            "minimum_chart_authors": _threshold_counts(
                diagnostics, "chart_authors", AUTHOR_GRID
            ),
            "maximum_largest_match_share": _threshold_counts(
                diagnostics,
                "largest_match_share",
                MAX_MATCH_SHARE_GRID,
                maximum=True,
            ),
            "minimum_effective_matches": _threshold_counts(
                diagnostics, "effective_matches", EFFECTIVE_MATCH_GRID
            ),
        },
        "diagnostic_intersection": {
            "history_instances": intersection,
            "share": intersection / total if total else None,
        },
        "uncertainty": _uncertainty_summary(diagnostics),
        "uncertainty_by_minimum_matches": {
            str(threshold): _uncertainty_summary(
                [item for item in diagnostics if item.matches >= threshold]
            )
            for threshold in MATCH_GRID
        },
    }


def run_audit(
    records: Sequence[ContextualServeRecord], source_profile: dict[str, object]
) -> dict[str, object]:
    years = sorted({int(record.date[:4]) for record in records})
    as_of_years = list(range(min(years) + HISTORY_SEASONS, max(years) + 1))
    target_results = []
    for target in TARGETS:
        diagnostics = []
        for as_of_year in as_of_years:
            diagnostics.extend(
                diagnose_history(history)
                for history in histories_for_window(records, target, as_of_year)
            )
        by_tour = {
            tour: summarize([item for item in diagnostics if item.tour == tour])
            for tour in sorted({item.tour for item in diagnostics})
        }
        by_surface = {
            f"{tour}|{surface}": summarize(
                [
                    item
                    for item in diagnostics
                    if item.tour == tour and item.surface == surface
                ]
            )
            for tour, surface in sorted(
                {(item.tour, item.surface) for item in diagnostics}
            )
        }
        by_as_of_year = {
            str(as_of_year): summarize(
                [item for item in diagnostics if item.as_of_year == as_of_year]
            )
            for as_of_year in as_of_years
        }
        target_results.append(
            {
                "target": target.name,
                "overall": summarize(diagnostics),
                "by_tour": by_tour,
                "by_surface": by_surface,
                "by_as_of_year": by_as_of_year,
            }
        )
    return {
        "generated_on": date.today().isoformat(),
        "experiment_id": EXPERIMENT_ID,
        "specification": SPECIFICATION,
        "mcp_snapshot_id": SNAPSHOT_ID,
        "context_snapshot_id": CONTEXT_SNAPSHOT_ID,
        "context_mirror_commit": CONTEXT_COMMIT,
        "history_seasons": HISTORY_SEASONS,
        "as_of_years": as_of_years,
        "source_profile": source_profile,
        "results": target_results,
    }


def _number(value: float | None, digits: int = 3) -> str:
    return "NA" if value is None else f"{value:.{digits}f}"


def render_report(result: dict[str, object]) -> str:
    rows = [
        "| Target | Tour | Histories | Players | Median matches | Median effective matches | "
        "Stress-test share | Median clustered half-width | Median cluster/conditional SD |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for target in result["results"]:
        for label, summary in (("All", target["overall"]), *target["by_tour"].items()):
            exposure = summary["exposure_quantiles"]
            uncertainty = summary["uncertainty"]
            rows.append(
                f"| `{target['target']}` | {label} | "
                f"{summary['history_instances']:,} | {summary['distinct_players']:,} | "
                f"{_number(exposure['matches']['median'], 1)} | "
                f"{_number(exposure['effective_matches']['median'], 1)} | "
                f"{_number(summary['diagnostic_intersection']['share'])} | "
                f"{_number(uncertainty['cluster_half_width_95']['median'])} | "
                f"{_number(uncertainty['cluster_to_conditional_sd_ratio']['median'])} |"
            )
    threshold_rows = [
        "| Target | Minimum matches | Histories | Median clustered half-width | "
        "Median cluster/conditional SD |",
        "|---|---:|---:|---:|---:|",
    ]
    for target in result["results"]:
        for threshold, uncertainty in target["overall"][
            "uncertainty_by_minimum_matches"
        ].items():
            threshold_rows.append(
                f"| `{target['target']}` | {threshold} | "
                f"{uncertainty['history_instances']:,} | "
                f"{_number(uncertainty['cluster_half_width_95']['median'])} | "
                f"{_number(uncertainty['cluster_to_conditional_sd_ratio']['median'])} |"
            )
    profile = result["source_profile"]
    return f"""# Serve publication-readiness audit

**Experiment:** `{result['experiment_id']}`

**Status:** aggregate coverage and uncertainty audit; no player output

## Design boundary

The audit uses {profile['eligible_contextual_match_player_records']:,} collision-safe match-player
records from {profile['eligible_matches']:,} matches. It creates trailing five-season histories for
as-of years {result['as_of_years'][0]}-{result['as_of_years'][-1]} without requiring future player
participation. A history is one player-surface-as-of-year instance, so the same player may
contribute in multiple windows.

The final as-of year uses data only through the preceding season. The partial latest season in the
snapshot is excluded from the final history rather than treated as complete.

The stress-test intersection requires at least five matches, two seasons, three opponents, two
tournaments, no match above 50% of eligible events, and effective match count of at least three.
It is not a publication threshold.

## Aggregate results

{chr(10).join(rows)}

The clustered half-width is `1.96` times a match-clustered ratio standard error. The comparison
standard deviation is the zero-strength conditional count-model diagnostic. Neither quantity
captures charted-match selection, parser error, or all forms of temporal and contextual change.

## Uncertainty by exposure

{chr(10).join(threshold_rows)}

These cohorts are nested rather than independent. The two-match cluster estimator is itself noisy;
the higher thresholds show whether the direction of the discrepancy persists with more clusters.

## Adversarial interpretation

The median history contains only two distinct matches and about 1.9 effective matches. The
diagnostic diversity/concentration intersection retains roughly one quarter of history instances,
so broad player availability and defensible coverage cannot both be assumed.

Direction is the clearest warning against point-count uncertainty. Its clustered uncertainty
remains materially larger than the conditional count-model diagnostic even at twenty matches.
Outcome rates show smaller discrepancies, but this does not address selected charting or incomplete
context adjustment. Grass coverage is especially sparse relative to hard-court coverage.

**DATA-QUALITY DECISION:** no public eligibility or confidence policy is supported yet. Continue
internal feature specification, but require match-clustered uncertainty and surface-specific
coverage in any future proposal. Conditional posterior precision must not be displayed as total
confidence.

## Interpretation boundary

**OPEN QUESTION:** surface and as-of-year results remain in the machine-readable artifact and must
be checked for reversals before any policy is proposed. Coverage, statistical precision, and
representativeness are different properties; a narrow conditional interval cannot repair a
selected sample.

No player estimate or identity is serialized. No sensitivity-grid value or stress-test rule is
approved by this audit.

## Reproduce

```powershell
python -m research.experiments.serve_publication_readiness
```
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp-source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--context-source", type=Path, default=DEFAULT_CONTEXT_SOURCE)
    parser.add_argument(
        "--json", type=Path, default=Path("research/serve_publication_readiness.json")
    )
    parser.add_argument(
        "--report", type=Path, default=Path("research/serve_publication_readiness.md")
    )
    parser.add_argument("--render-existing", action="store_true")
    arguments = parser.parse_args()
    if arguments.render_existing:
        result = json.loads(arguments.json.read_text(encoding="utf-8"))
    else:
        records, source_profile = load_experiment_records(
            arguments.mcp_source, arguments.context_source
        )
        result = run_audit(records, source_profile)
        arguments.json.write_text(
            json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
        )
    arguments.report.write_text(render_report(result), encoding="utf-8")
    if not arguments.render_existing:
        print(f"Wrote {arguments.json}")
    print(f"Wrote {arguments.report}")


if __name__ == "__main__":
    main()
