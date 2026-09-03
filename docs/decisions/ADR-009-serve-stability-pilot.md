# ADR-009: Serve stability pilot design

**Status:** Accepted for the Phase 2 feasibility pilot

**Date:** 2026-09-03

## Context

Parser v0.2 and aggregate reconciliation nominated three serve families for stability testing. A
single player profile, distance, or minimum-match threshold would introduce researcher discretion
before context and eligibility rules are validated. Points within a match are also dependent, so
point-level uncertainty would overstate effective sample size.

## Decision

The versioned `research-serve-stability-v0.1` pilot:

- evaluates serve outcomes, first-serve direction, and second-serve direction separately;
- uses chronological halves and alternating disjoint matches;
- reports a 2/5/10/20 matches-per-half sensitivity grid without approving any cutoff;
- compares players only within ATP or WTA;
- uses mean absolute rate distance for outcomes and mean side-conditional total-variation distance
  for direction;
- resamples matches, not points, for a deterministic bootstrap diagnostic; and
- emits aggregate results without player names, rankings, clusters, or a composite Tennis DNA
  vector.

## Result and interpretation

**PROJECT HYPOTHESIS SUPPORTED PROVISIONALLY:** across the tested aggregate scenarios, median
within-player distance is lower than the within-tour between-player negative control. At five
matches per half, chronological ratios are 0.510 for outcomes, 0.542 for first-serve direction, and
0.606 for second-serve direction.

**OPEN QUESTION:** chronological distances are consistently larger than alternating-match
distances. This is compatible with temporal drift, changing context, or selection and prevents a
fixed-style interpretation. The bootstrap range is descriptive rather than a formal confidence
interval because a non-negative distance can be upward-biased under resampling.

## Consequences

- The serve families remain candidates; they are not approved public player features.
- The next validity work is canonical context joining and surface/opponent/era sensitivity.
- Second-serve direction remains the weakest family because it has the highest reconciliation
  mismatch rate and the largest chronological stability ratio.
- Eligibility, shrinkage, weighting, similarity, clustering, and product work remain blocked.

## Evidence

- [Serve stability report](../../research/serve_stability.md)
- [Serve reconciliation report](../../research/mcp_serve_reconciliation.md)
- [Serve feature candidates](../../research/serve_feature_candidates.md)
