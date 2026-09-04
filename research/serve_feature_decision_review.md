# Serve feature-by-feature decision review

**Review date:** 2026-09-04

**Snapshot:** `mcp-atp-wta-2026-09-03-2c59eef1`

**Decision scope:** measurement candidates only; no Tennis DNA vector or player publication

## Decision question

**PROJECT HYPOTHESIS:** selected serve behaviors may support bounded descriptions of a player's
charted five-season, surface-specific sample. The evidence does not support a timeless player
identity, causal effect, talent score, or representative career claim.

This review separates behavioral distributions from outcome rates. They must not be normalized,
weighted, or combined merely because they passed related experiments.

## Evidence standard

Each target is reviewed against five distinct questions:

1. Does the parser provide a defensible numerator and denominator?
2. Does the target reconcile with the MCP aggregate representation?
3. Is within-player variation smaller than a within-tour between-player control?
4. Does the signal survive coarse context stratification?
5. Does player history predict later seasons beyond context and raw-rate comparators?

Passing software reconciliation does not establish statistical validity. Passing prediction does
not remove charted-match selection or make the estimator publishable.

## Decisions

| Target | Intended role | Evidence retained | Contradictory or limiting evidence | Decision |
|---|---|---|---|---|
| `first_serve_in_rate` | Context-sensitive serve outcome | Exact denominator; aggregate reconciliation; context and temporal signal; shrinkage beats raw at every exposure endpoint | Strength 400 is selected in 27/46 low-exposure and 26/37 high-exposure folds; first-serve-in can reflect conditions and tactics | **RETAIN; PRIOR-BOUNDARY REVIEW** |
| `ace_per_service_point` | Context-sensitive serve outcome | Exact denominator; strong reconciliation; context and temporal signal; aggregate shrinkage gain at low and high exposure | WTA high-exposure gain over raw is inconclusive; opponent return and conditions remain coarse | **RETAIN; CONTEXT-SENSITIVE** |
| `double_fault_per_second_serve_attempt` | Context-sensitive risk outcome | Feature-specific second-attempt denominator; strong reconciliation; context signal; sparse-history shrinkage gain | High-exposure shrinkage-versus-raw is inconclusive overall and by tour; within-match dependence is material | **RETAIN; UNCERTAINTY REVIEW** |
| `first_serve_direction` | Behavioral distribution, conditional on first serve landing in | 98.6% side-aware reconciliation; strongest measurement chain; all context checks and temporal comparator pass | Conditional-on-in estimand is not intended direction; empirical clustered coverage is only 77%-82% across window/exposure tests | **RETAIN DESCRIPTIVELY; REVISE TEMPORAL UNCERTAINTY** |
| `second_serve_direction` | Behavioral distribution over recorded second attempts | Strongest sparse-history predictive shrinkage gain; all context comparisons pass | 96.8% reconciliation and the weakest prior controlled-stability family; high-exposure gain over raw is inconclusive | **RETAIN; RECONCILIATION AND UNCERTAINTY REVIEW** |

The shrinkage comparison is expected to narrow with exposure because raw and partially pooled
estimates converge. An inconclusive high-exposure difference is therefore not, by itself, evidence
that the underlying player signal disappears. It does reject a claim that shrinkage is universally
better.

## Exposure consequence

At the two-match threshold, 448 distinct players appear in later-season evaluation. At twenty
matches, 111 remain, or 24.8% of that count. Selecting twenty matches solely because posterior
standard deviations are smaller would discard most represented players and privilege heavily
charted careers. Selecting two solely because shrinkage helps would risk profiles dominated by one
match or tournament.

**DATA-QUALITY DECISION:** do not choose a single minimum-match threshold yet. Audit distinct
seasons, opponents, tournaments, chart authors, event concentration, and match-clustered
uncertainty together. Player availability and confidence are separate product concepts.

## Model consequence

No global shrinkage strength is approved. Validation selects zero in some folds and the maximum
grid value in others. The former is evidence that pooling can add no value in a period; the latter
is an unresolved boundary, not permission to extrapolate. Raw and shrunk estimates remain
competing internal estimators until the boundary and cluster dependence are reviewed.

## Gate

**PROCEED:** run the pre-specified aggregate publication-readiness audit in
[`serve_publication_readiness_spec.md`](serve_publication_readiness_spec.md).

**HOLD:** do not serialize player estimates, set a public eligibility badge, choose feature
weights, construct a vector, calculate similarity, or build the final application.

The subsequent temporal robustness audit falsifies the current interval model for first-serve
direction. Match clustering improves later-season coverage but remains far below the diagnostic
reference. Validation-estimated process variance subsequently restores aggregate coverage near the
diagnostic target, but at materially wider radii and with substantial fallback in sparse folds.
The uncertainty model remains internal and unapproved for publication.

## Evidence artifacts

- [Serve candidate definitions](serve_feature_candidates.md)
- [Serve reconciliation](mcp_serve_reconciliation.md)
- [Aggregate stability pilot](serve_stability.md)
- [Context-controlled pilot](context_serve_stability.md)
- [Temporal shrinkage pilot](serve_shrinkage.md)
- [Feature gate](tennis_dna_feature_gate.md)
