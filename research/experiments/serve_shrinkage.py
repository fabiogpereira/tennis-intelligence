"""Temporal out-of-sample shrinkage pilot for retained serve candidates."""

from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from statistics import mean, median
from typing import Iterable, Mapping, Sequence

from models.shrinkage import beta_posterior, dirichlet_posterior
from pipelines.processing.entity_resolution import normalize_identity
from research.experiments.context_serve_stability import (
    CONTEXT_COMMIT,
    CONTEXT_SNAPSHOT_ID,
    DEFAULT_CONTEXT_SOURCE,
    DEFAULT_SOURCE,
    ContextualServeRecord,
    load_experiment_records,
    rank_band,
)
from research.experiments.profile_mcp_snapshot import SNAPSHOT_ID


EXPERIMENT_ID = "research-serve-shrinkage-v0.1"
SPECIFICATION = "research/serve_shrinkage_uncertainty_spec.md"
ELIGIBILITY_GRID = (2, 5, 10, 20)
PRIOR_STRENGTHS = (0, 25, 100, 400)
HISTORY_SEASONS = 5
BOOTSTRAP_REPLICATES = 200
BOOTSTRAP_SEED = 20260904
SIDES = ("deuce", "ad")
DIRECTIONS = ("wide", "middle", "t")
MODELS = ("tour", "context", "raw_player", "shrunk_player")
Counts = tuple[int, ...]
Key = tuple[str, ...]


@dataclass(frozen=True)
class TargetSpec:
    name: str
    kind: str
    numerator: str = ""
    denominator: str = ""
    serve_number: str = ""


TARGETS = (
    TargetSpec(
        "first_serve_in_rate",
        "binary",
        numerator="first_in",
        denominator="resolved_first_serve_status",
    ),
    TargetSpec(
        "ace_per_service_point",
        "binary",
        numerator="aces",
        denominator="resolved_ace_status",
    ),
    TargetSpec(
        "double_fault_per_second_serve_attempt",
        "binary",
        numerator="dfs",
        denominator="resolved_double_fault_status",
    ),
    TargetSpec("first_serve_direction", "direction", serve_number="1"),
    TargetSpec("second_serve_direction", "direction", serve_number="2"),
)


@dataclass
class HistoryModel:
    categories: int
    player: dict[Key, Counts]
    exact: dict[Key, Counts]
    surface: dict[Key, Counts]
    tour: dict[Key, Counts]
    exact_player: dict[Key, Counts]
    surface_player: dict[Key, Counts]
    tour_player: dict[Key, Counts]


@dataclass(frozen=True)
class ScoreRow:
    match_id: str
    tour: str
    player_key: str
    test_year: int
    losses: Mapping[str, float]
    briers: Mapping[str, float]
    predictions: Mapping[str, tuple[float, ...]]
    observed: tuple[float, ...]
    posterior_sd: float


def _add_counts(target: dict[Key, Counts], key: Key, counts: Counts) -> None:
    previous = target.get(key, (0,) * len(counts))
    target[key] = tuple(left + right for left, right in zip(previous, counts))


def _subtract_counts(total: Counts, contribution: Counts | None) -> Counts:
    if contribution is None:
        return total
    return tuple(left - right for left, right in zip(total, contribution))


def _player_surface(record: ContextualServeRecord) -> Key:
    return (
        record.tour,
        normalize_identity(record.player),
        normalize_identity(record.surface) or "(blank)",
    )


def _observations(record: ContextualServeRecord, target: TargetSpec) -> list[tuple[str, Counts]]:
    if target.kind == "binary":
        trials = record.metrics[target.denominator]
        successes = record.metrics[target.numerator]
        if trials <= 0 or successes < 0 or successes > trials:
            return []
        return [("", (successes, trials - successes))]
    observations = []
    for side in SIDES:
        counts = tuple(
            record.metrics[f"direction:{target.serve_number}:{side}:{direction}"]
            for direction in DIRECTIONS
        )
        if sum(counts) == 0:
            return []
        observations.append((side, counts))
    return observations


def build_history(
    records: Iterable[ContextualServeRecord], target: TargetSpec
) -> HistoryModel:
    stores: list[defaultdict[Key, Counts]] = [defaultdict(tuple) for _ in range(7)]
    player, exact, surface, tour, exact_player, surface_player, tour_player = stores
    for record in records:
        player_surface = _player_surface(record)
        player_name = player_surface[1]
        surface_name = player_surface[2]
        opponent_band = rank_band(record.opponent_rank)
        for side, counts in _observations(record, target):
            player_key = (*player_surface, side)
            exact_key = (record.tour, surface_name, opponent_band, side)
            surface_key = (record.tour, surface_name, side)
            tour_key = (record.tour, side)
            for store, key in (
                (player, player_key),
                (exact, exact_key),
                (surface, surface_key),
                (tour, tour_key),
                (exact_player, (*exact_key, player_name)),
                (surface_player, (*surface_key, player_name)),
                (tour_player, (*tour_key, player_name)),
            ):
                _add_counts(store, key, counts)
    categories = 2 if target.kind == "binary" else len(DIRECTIONS)
    return HistoryModel(categories, *(dict(store) for store in stores))


def _stabilized_proportions(counts: Counts) -> tuple[float, ...]:
    total = sum(counts) + 0.5 * len(counts)
    return tuple((count + 0.5) / total for count in counts)


def _leave_player_prior(
    record: ContextualServeRecord,
    side: str,
    history: HistoryModel,
    level: str,
) -> tuple[float, ...]:
    player = normalize_identity(record.player)
    surface = normalize_identity(record.surface) or "(blank)"
    opponent_band = rank_band(record.opponent_rank)
    levels = {
        "exact": (
            history.exact,
            history.exact_player,
            (record.tour, surface, opponent_band, side),
        ),
        "surface": (
            history.surface,
            history.surface_player,
            (record.tour, surface, side),
        ),
        "tour": (history.tour, history.tour_player, (record.tour, side)),
    }
    order = ("exact", "surface", "tour") if level == "exact" else ("tour",)
    for current in order:
        totals, contributions, key = levels[current]
        counts = totals.get(key)
        if counts is None:
            continue
        remaining = _subtract_counts(counts, contributions.get((*key, player)))
        if sum(remaining) > 0:
            return _stabilized_proportions(remaining)
    return (1 / history.categories,) * history.categories


def _posterior_prediction(
    counts: Counts,
    prior: tuple[float, ...],
    strength: int,
) -> tuple[tuple[float, ...], float]:
    if len(counts) == 2:
        probability, deviation = beta_posterior(
            counts[0], sum(counts), prior[0], strength
        )
        return (probability, 1 - probability), deviation
    probabilities, deviations = dirichlet_posterior(counts, prior, strength)
    return probabilities, mean(deviations)


def _cross_entropy(observed: Counts, predicted: Sequence[float]) -> float:
    trials = sum(observed)
    return -sum(
        count / trials * math.log(min(max(probability, 1e-12), 1 - 1e-12))
        for count, probability in zip(observed, predicted)
    )


def _brier(observed: Counts, predicted: Sequence[float]) -> float:
    trials = sum(observed)
    rates = tuple(count / trials for count in observed)
    if len(observed) == 2:
        return (rates[0] - predicted[0]) ** 2
    return sum((actual - forecast) ** 2 for actual, forecast in zip(rates, predicted))


def score_records(
    records: Iterable[ContextualServeRecord],
    target: TargetSpec,
    history: HistoryModel,
    eligible: set[Key],
    strength: int,
    test_year: int,
) -> list[ScoreRow]:
    rows = []
    for record in records:
        player_surface = _player_surface(record)
        if player_surface not in eligible:
            continue
        player_name = player_surface[1]
        for side, observed_counts in _observations(record, target):
            player_counts = history.player.get((*player_surface, side))
            if player_counts is None or sum(player_counts) == 0:
                continue
            context_prior = _leave_player_prior(record, side, history, "exact")
            tour_prior = _leave_player_prior(record, side, history, "tour")
            raw_prediction, _ = _posterior_prediction(player_counts, context_prior, 0)
            shrunk_prediction, posterior_sd = _posterior_prediction(
                player_counts, context_prior, strength
            )
            predictions = {
                "tour": tour_prior,
                "context": context_prior,
                "raw_player": raw_prediction,
                "shrunk_player": shrunk_prediction,
            }
            trials = sum(observed_counts)
            observed = tuple(count / trials for count in observed_counts)
            rows.append(
                ScoreRow(
                    match_id=record.match_id,
                    tour=record.tour,
                    player_key=player_name,
                    test_year=test_year,
                    losses={
                        model: _cross_entropy(observed_counts, prediction)
                        for model, prediction in predictions.items()
                    },
                    briers={
                        model: _brier(observed_counts, prediction)
                        for model, prediction in predictions.items()
                    },
                    predictions=predictions,
                    observed=observed,
                    posterior_sd=posterior_sd,
                )
            )
    return rows


def _match_average(rows: Sequence[ScoreRow], field: str, model: str) -> float | None:
    by_match: defaultdict[str, list[float]] = defaultdict(list)
    for row in rows:
        values = row.losses if field == "log_loss" else row.briers
        by_match[row.match_id].append(values[model])
    return mean(mean(values) for values in by_match.values()) if by_match else None


def _calibration_error(rows: Sequence[ScoreRow], model: str) -> float | None:
    if not rows or len(rows[0].observed) != 2:
        return None
    bins: defaultdict[int, list[tuple[float, float]]] = defaultdict(list)
    for row in rows:
        prediction = row.predictions[model][0]
        bins[min(int(prediction * 10), 9)].append((prediction, row.observed[0]))
    total = sum(len(values) for values in bins.values())
    if not total:
        return None
    return sum(
        len(values) / total
        * abs(mean(value[0] for value in values) - mean(value[1] for value in values))
        for values in bins.values()
    )


def _paired_bootstrap(
    rows: Sequence[ScoreRow], left: str, right: str, seed: int
) -> list[float] | None:
    by_match: defaultdict[str, list[float]] = defaultdict(list)
    for row in rows:
        by_match[row.match_id].append(row.losses[left] - row.losses[right])
    differences = [mean(values) for _, values in sorted(by_match.items())]
    if not differences:
        return None
    rng = random.Random(seed)
    estimates = [
        mean(rng.choice(differences) for _ in differences)
        for _ in range(BOOTSTRAP_REPLICATES)
    ]
    estimates.sort()
    return [
        estimates[round(0.025 * (len(estimates) - 1))],
        estimates[round(0.975 * (len(estimates) - 1))],
    ]


def _valid_player_match_counts(
    records: Iterable[ContextualServeRecord], target: TargetSpec
) -> Counter[Key]:
    matches: defaultdict[Key, set[str]] = defaultdict(set)
    for record in records:
        if _observations(record, target):
            matches[_player_surface(record)].add(record.match_id)
    return Counter({key: len(values) for key, values in matches.items()})


def _keys_with_observations(
    records: Iterable[ContextualServeRecord], target: TargetSpec
) -> set[Key]:
    return {
        _player_surface(record)
        for record in records
        if _observations(record, target)
    }


def fold_partitions(
    records: Sequence[ContextualServeRecord], test_year: int
) -> tuple[
    list[ContextualServeRecord],
    list[ContextualServeRecord],
    list[ContextualServeRecord],
    list[ContextualServeRecord],
]:
    """Return selection history, validation, test, and refit history for a fold."""

    by_year = [(record, int(record.date[:4])) for record in records]
    training = [
        record
        for record, year in by_year
        if test_year - HISTORY_SEASONS - 1 <= year <= test_year - 2
    ]
    validation = [record for record, year in by_year if year == test_year - 1]
    test = [record for record, year in by_year if year == test_year]
    refit_history = [
        record
        for record, year in by_year
        if test_year - HISTORY_SEASONS <= year < test_year
    ]
    return training, validation, test, refit_history


def _score_summary(rows: Sequence[ScoreRow]) -> dict[str, object]:
    return {
        model: {
            "match_average_log_loss": _match_average(rows, "log_loss", model),
            "match_average_brier": _match_average(rows, "brier", model),
            "binary_expected_calibration_error": _calibration_error(rows, model),
        }
        for model in MODELS
    }


def _evaluate_target_threshold(
    records: Sequence[ContextualServeRecord],
    target: TargetSpec,
    threshold: int,
    seed: int,
) -> dict[str, object]:
    years = [int(record.date[:4]) for record in records]
    fold_records = []
    all_test_rows: list[ScoreRow] = []
    empty_years = []
    for test_year in range(min(years) + HISTORY_SEASONS + 1, max(years) + 1):
        validation_year = test_year - 1
        training, validation, test, refit_history = fold_partitions(
            records, test_year
        )
        counts = _valid_player_match_counts(training, target)
        eligible = {
            key
            for key, matches in counts.items()
            if matches >= threshold
        }
        eligible &= _keys_with_observations(validation, target)
        eligible &= _keys_with_observations(test, target)
        if not eligible:
            empty_years.append(test_year)
            continue
        validation_history = build_history(training, target)
        validation_scores = []
        for strength in PRIOR_STRENGTHS:
            rows = score_records(
                validation,
                target,
                validation_history,
                eligible,
                strength,
                validation_year,
            )
            score = _match_average(rows, "log_loss", "shrunk_player")
            if score is not None:
                validation_scores.append((score, strength))
        if not validation_scores:
            empty_years.append(test_year)
            continue
        selected_strength = min(validation_scores)[1]
        test_history = build_history(refit_history, target)
        test_rows = score_records(
            test, target, test_history, eligible, selected_strength, test_year
        )
        if not test_rows:
            empty_years.append(test_year)
            continue
        all_test_rows.extend(test_rows)
        fold_records.append(
            {
                "test_year": test_year,
                "eligible_player_surfaces": len(eligible),
                "test_matches": len({row.match_id for row in test_rows}),
                "selected_prior_strength": selected_strength,
                "scores": _score_summary(test_rows),
                "shrunk_minus_context_log_loss": (
                    _match_average(test_rows, "log_loss", "shrunk_player")
                    - _match_average(test_rows, "log_loss", "context")
                ),
                "shrunk_minus_raw_log_loss": (
                    _match_average(test_rows, "log_loss", "shrunk_player")
                    - _match_average(test_rows, "log_loss", "raw_player")
                ),
            }
        )
    by_tour = {}
    for tour in sorted({row.tour for row in all_test_rows}):
        tour_rows = [row for row in all_test_rows if row.tour == tour]
        by_tour[tour] = {
            "test_matches": len({row.match_id for row in tour_rows}),
            "scores": _score_summary(tour_rows),
            "shrunk_minus_context_log_loss_bootstrap_95_range": _paired_bootstrap(
                tour_rows, "shrunk_player", "context", seed + (0 if tour == "ATP" else 1)
            ),
            "shrunk_minus_raw_log_loss_bootstrap_95_range": _paired_bootstrap(
                tour_rows, "shrunk_player", "raw_player", seed + (2 if tour == "ATP" else 3)
            ),
        }
    return {
        "target": target.name,
        "minimum_training_matches": threshold,
        "folds_attempted": max(years) - min(years) - HISTORY_SEASONS,
        "folds_evaluated": len(fold_records),
        "empty_test_years": empty_years,
        "test_matches": len({row.match_id for row in all_test_rows}),
        "distinct_players": len(
            {(row.tour, row.player_key) for row in all_test_rows}
        ),
        "selected_prior_strength_counts": dict(
            Counter(row["selected_prior_strength"] for row in fold_records)
        ),
        "scores": _score_summary(all_test_rows),
        "shrunk_minus_context_log_loss_bootstrap_95_range": _paired_bootstrap(
            all_test_rows, "shrunk_player", "context", seed
        ),
        "shrunk_minus_raw_log_loss_bootstrap_95_range": _paired_bootstrap(
            all_test_rows, "shrunk_player", "raw_player", seed + 2
        ),
        "median_shrunk_posterior_standard_deviation": (
            median(row.posterior_sd for row in all_test_rows)
            if all_test_rows
            else None
        ),
        "by_tour": by_tour,
        "folds": fold_records,
    }


def run_experiment(
    records: Sequence[ContextualServeRecord], source_profile: dict[str, object]
) -> dict[str, object]:
    results = []
    seed = BOOTSTRAP_SEED
    for target in TARGETS:
        for threshold in ELIGIBILITY_GRID:
            results.append(
                _evaluate_target_threshold(records, target, threshold, seed)
            )
            seed += 10
    return {
        "generated_on": date.today().isoformat(),
        "experiment_id": EXPERIMENT_ID,
        "specification": SPECIFICATION,
        "mcp_snapshot_id": SNAPSHOT_ID,
        "context_snapshot_id": CONTEXT_SNAPSHOT_ID,
        "context_mirror_commit": CONTEXT_COMMIT,
        "history_seasons": HISTORY_SEASONS,
        "eligibility_grid_training_matches": list(ELIGIBILITY_GRID),
        "prior_strength_grid_eligible_events": list(PRIOR_STRENGTHS),
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "source_profile": source_profile,
        "results": results,
    }


def _format(value: float | None, digits: int = 4) -> str:
    return "NA" if value is None else f"{value:.{digits}f}"


def _range(values: Sequence[float] | None) -> str:
    return "NA" if values is None else f"{_format(values[0])} to {_format(values[1])}"


def _comparison_status(values: Sequence[float] | None) -> str:
    if values is None:
        return "no estimate"
    if values[1] < 0:
        return "favors shrinkage"
    if values[0] > 0:
        return "favors comparator"
    return "inconclusive"


def render_report(result: dict[str, object]) -> str:
    rows = [
        "| Target | Training matches | Folds | Players | Test matches | Context loss | Raw loss | "
        "Shrunk loss | Shrunk-context bootstrap | Shrunk-raw bootstrap | Posterior SD |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for evaluation in result["results"]:
        scores = evaluation["scores"]
        rows.append(
            f"| `{evaluation['target']}` | {evaluation['minimum_training_matches']} | "
            f"{evaluation['folds_evaluated']} | {evaluation['distinct_players']:,} | "
            f"{evaluation['test_matches']:,} | "
            f"{_format(scores['context']['match_average_log_loss'])} | "
            f"{_format(scores['raw_player']['match_average_log_loss'])} | "
            f"{_format(scores['shrunk_player']['match_average_log_loss'])} | "
            f"{_range(evaluation['shrunk_minus_context_log_loss_bootstrap_95_range'])} | "
            f"{_range(evaluation['shrunk_minus_raw_log_loss_bootstrap_95_range'])} | "
            f"{_format(evaluation['median_shrunk_posterior_standard_deviation'])} |"
        )
    endpoint_rows = [
        "| Target | Matches | Overall vs raw | ATP vs raw | WTA vs raw | "
        "Folds favoring context | Folds favoring raw | Selected strengths |",
        "|---|---:|---|---|---|---:|---:|---|",
    ]
    for evaluation in result["results"]:
        if evaluation["minimum_training_matches"] not in (2, 20):
            continue
        folds = evaluation["folds"]
        context_wins = sum(
            fold["shrunk_minus_context_log_loss"] < 0 for fold in folds
        )
        raw_wins = sum(fold["shrunk_minus_raw_log_loss"] < 0 for fold in folds)
        strengths = ", ".join(
            f"{strength}:{count}"
            for strength, count in sorted(
                evaluation["selected_prior_strength_counts"].items(),
                key=lambda item: int(item[0]),
            )
        )
        overall_raw = evaluation["shrunk_minus_raw_log_loss_bootstrap_95_range"]
        atp_raw = evaluation["by_tour"]["ATP"][
            "shrunk_minus_raw_log_loss_bootstrap_95_range"
        ]
        wta_raw = evaluation["by_tour"]["WTA"][
            "shrunk_minus_raw_log_loss_bootstrap_95_range"
        ]
        endpoint_rows.append(
            f"| `{evaluation['target']}` | {evaluation['minimum_training_matches']} | "
            f"{_comparison_status(overall_raw)} | "
            f"{_comparison_status(atp_raw)} | "
            f"{_comparison_status(wta_raw)} | "
            f"{context_wins}/{evaluation['folds_evaluated']} | "
            f"{raw_wins}/{evaluation['folds_evaluated']} | {strengths} |"
        )
    profile = result["source_profile"]
    return f"""# Serve shrinkage and temporal uncertainty pilot

**Experiment:** `{result['experiment_id']}`

**Status:** temporal predictive falsification; no player ranking or profile is produced

## Design boundary

The experiment uses {profile['eligible_contextual_match_player_records']:,} collision-safe
match-player records from {profile['eligible_matches']:,} matches. Five historical seasons train
each fold, the following season selects one of the fixed prior strengths
`{result['prior_strength_grid_eligible_events']}`, and the next season is untouched test data.
Eligibility uses only pre-validation match counts on the 2/5/10/20 grid.

Context baselines use tour, surface, and opponent-rank band with documented backoff. The target
player is removed from every context baseline. Binary targets use stabilized Beta-style means;
direction targets use stabilized Dirichlet-style means by court side. Scores average within match
before averaging across matches.

## Results

{chr(10).join(rows)}

Negative bootstrap ranges favor shrinkage. Ranges crossing zero are inconclusive. Posterior
standard deviation is a model-based diagnostic, not a confidence interval; it does not capture MCP
selection, charting error, or all within-match dependence.

## Adversarial review

Every target beats the context-only comparator overall and within ATP and WTA at all four exposure
thresholds. That is evidence that historical player-surface behavior contains some later-season
predictive information beyond these coarse context fields. It is not evidence that the current
context model is complete or that the effect is causal.

The comparison with the raw player estimate is less uniform. The table below shows the least and
most restrictive exposure endpoints; the machine-readable artifact retains all thresholds and
folds.

{chr(10).join(endpoint_rows)}

At two training matches, shrinkage beats raw estimates for all targets overall and in both tours.
At twenty matches, the advantage remains clear for first-serve-in rate, remains clear overall and
for ATP aces, and is inconclusive for the remaining tour/target comparisons. This is compatible
with shrinkage helping sparse histories and converging toward raw estimates as exposure grows.
It also means the experiment does not justify one universal shrinkage strength.

Validation selected both zero and the maximum strength. Maximum-strength selections are frequent
for the binary outcomes, especially first-serve-in rate, so the upper grid boundary remains a model
adequacy question. Fold-level wins are less uniform than aggregate wins, especially against the
raw player comparator. Binary calibration scores are descriptive because no acceptance cutoff was
pre-specified.

**DATA-QUALITY DECISION:** retain all five serve targets for a bounded feature-definition review;
do not approve a composite vector or player output. Preserve raw and shrunk estimates as competing
candidates until the estimand, reporting period, exposure policy, and uncertainty display are
chosen explicitly.

## Interpretation boundary

This experiment tests prediction in later charted seasons, not causality or universal player
identity. Validation chooses shrinkage strength separately for each target, exposure threshold, and
fold. Test data never select a strength. No player estimate is serialized.

**OPEN QUESTION:** feature-by-feature decisions require reviewing aggregate, ATP/WTA, exposure,
calibration, strength-boundary, and period consistency together. A favorable overall score cannot
override a tour reversal or sparse low-exposure result.

## Reproduce

```powershell
python -m research.experiments.serve_shrinkage
```
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp-source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--context-source", type=Path, default=DEFAULT_CONTEXT_SOURCE)
    parser.add_argument(
        "--json", type=Path, default=Path("research/serve_shrinkage.json")
    )
    parser.add_argument(
        "--report", type=Path, default=Path("research/serve_shrinkage.md")
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
