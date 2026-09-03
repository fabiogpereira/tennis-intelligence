# ADR-005: Model calibration strategy

## Context
The proposed leverage quantity depends on match-win probabilities, so forecast calibration is part of metric validity.

## Options considered
Report accuracy only, use a single calibration method without diagnostics, or evaluate and calibrate with temporal holdouts.

## Decision
Use chronological holdouts, proper scoring rules, calibration diagnostics, and calibration methods only when they improve held-out behavior without leakage. Publish calibration alongside discrimination.

## Why
A probability that ranks outcomes well but is systematically overconfident can distort leverage.

## Trade-offs
This adds evaluation work and can reduce apparent dramatic differences. That is a feature for a public research product.

## Consequences
No pressure ranking is publishable without a calibration report and uncertainty boundaries.
