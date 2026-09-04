"""Small dependency-free partial-pooling estimators for serve-rate experiments."""

from __future__ import annotations

import math
from typing import Sequence


def beta_posterior(
    successes: int,
    trials: int,
    prior_mean: float,
    prior_strength: float,
) -> tuple[float, float]:
    """Return stabilized posterior mean and standard deviation for a binary rate."""

    if trials < 0 or successes < 0 or successes > trials:
        raise ValueError("binary counts must satisfy 0 <= successes <= trials")
    if not 0 <= prior_mean <= 1 or prior_strength < 0:
        raise ValueError("prior mean and strength are outside their valid ranges")
    alpha = successes + prior_strength * prior_mean + 0.5
    beta = trials - successes + prior_strength * (1 - prior_mean) + 0.5
    total = alpha + beta
    mean = alpha / total
    variance = alpha * beta / (total**2 * (total + 1))
    return mean, math.sqrt(variance)


def dirichlet_posterior(
    counts: Sequence[int],
    prior_mean: Sequence[float],
    prior_strength: float,
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Return stabilized posterior component means and standard deviations."""

    if len(counts) < 2 or len(counts) != len(prior_mean):
        raise ValueError("counts and prior mean require the same multi-category shape")
    if any(count < 0 for count in counts):
        raise ValueError("categorical counts cannot be negative")
    if prior_strength < 0 or any(value < 0 for value in prior_mean):
        raise ValueError("prior values and strength cannot be negative")
    if not math.isclose(sum(prior_mean), 1.0, abs_tol=1e-9):
        raise ValueError("categorical prior mean must sum to one")
    parameters = tuple(
        count + prior_strength * prior + 0.5
        for count, prior in zip(counts, prior_mean)
    )
    total = sum(parameters)
    means = tuple(value / total for value in parameters)
    deviations = tuple(
        math.sqrt(value * (total - value) / (total**2 * (total + 1)))
        for value in parameters
    )
    return means, deviations
