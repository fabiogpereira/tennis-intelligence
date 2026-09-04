# Tennis DNA feature gate

**Review date:** 2026-09-03

**Snapshot:** `mcp-atp-wta-2026-09-03-2c59eef1`

**Parser:** `mcp-parser-v0.2-draft`

**Decision:** retain serve candidates after an aggregate stability pilot; do not publish player features

## Proposed estimand

**PROJECT HYPOTHESIS:** Tennis DNA may describe reproducible differences in player behavior within
the charted Match Charting Project sample. The intended unit is a player-period profile composed of
directly interpretable rates. It is not a measure of talent, a causal effect, or evidence of a fixed
psychological trait.

No feature vector, weighting rule, similarity metric, or minimum-sample threshold is approved by
this review.

## Evidence entering the gate

**ESTABLISHED FOR THIS SNAPSHOT:** 1,849,994 usable logical points join safely to 11,590 matches and
1,732 players after duplicate and metadata exclusions. Exposure is highly unequal: the median
represented player has two matches, while the maximum is 722.

**ESTABLISHED FOR THIS PARSER:** the documented-core parser accepts 90.9% of non-empty first-serve
cells and 85.8% of non-empty second-serve cells. Acceptance is 91.1% for ATP cells and 86.1% for WTA
cells. It is near 99% in many historical seasons but falls to 74.2%-88.5% in 2020-2026. The largest
rejection class contains depth-like codes in positions not covered by the extracted official
instructions.

Field-aware parsing safely extracts known serve direction from 2,522,149 of 2,524,448 extractable
serve prefixes (99.9%). Raw serve outcomes reconcile with MCP Overview at 99.9%-100.0% exact
agreement across comparable match-player records. Side-aware ServeDirection vectors reconcile at
98.6% for first serves, 96.8% for second serves, and 95.7% overall.

The `research-serve-stability-v0.1` pilot compares chronological and alternating match splits over
2/5/10/20 matches per half. Median within-player distance is lower than the within-tour
between-player control in every aggregate scenario. At five matches per half, chronological ratios
are 0.510 for outcomes, 0.542 for first-serve direction, and 0.606 for second-serve direction.
Alternating-match ratios are lower, leaving temporal drift and changing context unresolved.

The automated context audit safely links 11,336 of 11,590 MCP matches (97.8%) to a pinned ATP/WTA
archive, with ranking populated for 99.5% of linked player-match sides. The subsequent human review
confirmed all 25 sampled safe links as the same match. One different-match candidate was found
among already excluded canonical collisions, and 15 exceptions remain unreviewed and excluded. The
safe links may support internal contextual falsification, not published ranking-band or adjusted
player claims.

## Ranked validity threats

1. **Parser selection bias — critical for rally features, reduced but not removed for serve.**
   Rejected cells are concentrated by era and player. Field-aware prefixes prevent downstream rally
   failures from automatically deleting serve direction, but feature-specific missingness remains.
2. **Charted-match selection — critical.** MCP is a contributed sample, not a probability sample of
   professional tennis. Popular players and prominent matches are overrepresented.
3. **Context confounding — high.** Opponent, surface, era, event, round, handedness, and score state
   can produce apparent player differences without a stable player characteristic.
4. **Unequal and dependent exposure — high.** Most players have very few matches; points within a
   match are not independent. Raw point counts exaggerate effective sample size.
5. **Denominator drift — high.** Serve, return, rally, error, and net rates have different eligible
   events. Published aggregate tables cannot be assumed to share the parser's grain or denominator.
6. **Researcher degrees of freedom — medium.** Choosing features, thresholds, and weights after
   inspecting recognizable player profiles can manufacture persuasive-looking separation.

## Candidate families and current gate

| Family | Candidate unit and denominator | Current decision | Blocking evidence |
|---|---|---|---|
| Serve direction | Eligible serves with known direction, split by serve number and court side | **RETAIN; CONTEXT GATE OPEN** | Aggregate persistence observed; temporal drift, context, author effects, eligibility, and shrinkage remain |
| Serve outcome | Resolvable service points and second-serve attempts | **RETAIN; CONTEXT GATE OPEN** | Aggregate persistence observed; context, eligibility, and shrinkage remain |
| Return behavior | Parsed returns with known type, direction, or depth | **STOP** | Accepted-cell denominator is selective; depth grammar is unresolved |
| Rally shape | Points with a fully parsed rally; length and shot-type composition | **STOP** | Recent-season rejection is too large for player comparison |
| Ending type | Fully parsed points ending in winner, forced error, or unforced error | **DEFER** | Ending attribution and aggregate reconciliation are incomplete |
| Net behavior | Eligible approach or serve-and-volley opportunities | **STOP** | Opportunity denominator and aggregate grain are not validated |

These statuses are data-quality decisions, not claims that the behaviors are unimportant.

## Required falsification tests

Before any family advances, the experiment must:

1. reconcile match-level parser counts against the corresponding MCP aggregate with explicit
   tolerances and an exception report;
2. report missingness and parser acceptance by tour, season, player, chart author, and feature;
3. repeat player estimates on temporal halves and disjoint match subsets, with uncertainty at the
   match level rather than treating points as independent;
4. compare raw player rates with surface-, opponent-, era-, and tournament-stratified results;
5. use a temporal holdout for any learned adjustment or similarity model;
6. disclose every tested feature and retain null, unstable, and contradictory results; and
7. show sensitivity to eligibility thresholds instead of selecting a single convenient cutoff.

## Falsification criteria

The stable-style hypothesis is weakened or rejected for a feature when player differences disappear
after simple context stratification, reverse across temporal halves, are smaller than match-level
uncertainty, or track parser/chart-author coverage more strongly than the player. Failure to
reconcile raw and aggregate denominators also blocks the feature, even when its face validity is
appealing.

## Recommendation

**PROCEED WITH INTERNAL CONTROLLED FALSIFICATION; HOLD PUBLIC PLAYER CLAIMS.** The definitions and boundaries are recorded
in [serve_feature_candidates.md](serve_feature_candidates.md), and the aggregate pilot is reported
in [serve_stability.md](serve_stability.md). Continue parser work for other families. Do not publish
rankings, player fingerprints, similarity maps, or "elite versus the rest" comparisons. Approval
remains per feature family, not a blanket approval of a Tennis DNA vector.
