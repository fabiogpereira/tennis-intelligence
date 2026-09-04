# Phase 2 progress: parser v0.2, serve validation, and stability pilot

## Milestone decision

**ENGINEERING DECISION:** MCP notation parsing is now field-aware. Unsupported suffixes still reject
the whole cell, but independently safe serve prefixes remain available with explicit component
states. See [ADR-008](decisions/ADR-008-field-aware-notation-validity.md).

**PROJECT HYPOTHESIS:** a small serve-only feature family has enough software-consistency evidence
to enter stability experiments. It is not approved for publication or inclusion in a Tennis DNA
vector.

## What changed

- Upgraded the parser identifier to `mcp-parser-v0.2-draft`.
- Added `observed`, `unknown`, `absent`, `partial`, `invalid`, and `not_applicable` component states.
- Preserved safe serve and shot prefixes without accepting undocumented suffix grammar.
- Corrected player-level parser coverage to count only points served by that player.
- Added coverage by tour, season, player, and chart author.
- Added deterministic raw-notation serve transformations and focused tests.
- Reconciled match-player metrics against safe `Overview` and `ServeDirection` aggregate grains.
- Documented candidate definitions, denominators, exclusions, confounders, and falsification rules.
- Characterized reconciliation mismatches by tour, season, and chart author using comparable-record
  denominators.
- Ran chronological and alternating split-sample stability checks over four exposure levels, with
  match-level bootstrap diagnostics and within-tour negative controls.
- Pinned an ATP/WTA archival context mirror after the original repositories became unavailable.
- Audited a precision-first match join over 1,749,872 context rows and produced a deterministic
  human-review queue.
- Validated the project-owner review and ran a pre-specified context-controlled serve stability
  pilot over the collision-free safe links.
- Ran a pre-specified rolling temporal shrinkage pilot without serializing player estimates.

## Defects found by reconciliation

The first full comparison found two implementation errors before any player feature was produced:

1. `S/R/P/Q/V` had initially been counted uniformly as service points. `S/R/P/Q` contain no
   observed serve, while `V` can represent a lost first serve followed by a real second serve.
2. numeric-looking normal scores such as `40-0` were evaluated as tiebreak scores before normal
   tennis labels, assigning the wrong deuce/ad court. Regression fixtures now cover both cases.

These defects changed reconciliation results but no published player result, because feature
generation remained gated.

## Current evidence

- Known direction exists in 2,522,149 of 2,524,448 extractable serve prefixes (99.9%).
- Whole-cell parsing still varies sharply by chart author, while serve-prefix direction coverage is
  approximately 99.6%-100.0% among the largest contributors.
- `Overview` agreement is 99.9%-100.0% across the five audited serve fields.
- Side-aware `ServeDirection` vector agreement is 98.6% for first serves, 96.8% for second serves,
  and 95.7% overall across comparable match-player records.
- Aggregate conflicts remain explicit: 11 conflicting `Overview Total` grains and 31 conflicting
  `ServeDirection` grains are excluded.

The generated [parser baseline](../research/mcp_notation_parser_baseline.md),
[serve reconciliation](../research/mcp_serve_reconciliation.md), and
[machine-readable profile](../research/mcp_snapshot_profile.json) are authoritative for current
counts.

The [context join audit](../research/mcp_context_join.md) safely links 11,336 of 11,590 MCP matches
(97.8%). Rank is present for 99.5% of linked player-match sides. These are automated audit results;
the [review sample](../research/mcp_context_join_review.md) required human validation. The subsequent
[human review result](../research/mcp_context_join_human_review.md) confirmed all 25 sampled safe
links and found one different-match candidate already excluded as a canonical collision. Fifteen
exception rows remain unreviewed and excluded. This clears the safe links for internal
context-controlled falsification, not publication or production identity use.

The [context-controlled serve pilot](../research/context_serve_stability.md) includes 22,661
match-player records across all 11,336 safe matches after excluding 11 records from the two
player-ID collision identities. All 42 aggregate family/context/exposure combinations retained a
within/between ratio below one, as did their ATP/WTA breakdowns. Ratios ranged from 0.495-0.704 for
serve outcomes, 0.530-0.726 for first-serve direction, and 0.605-0.740 for second-serve direction.
Tournament and joint-context coverage at five matches per half narrowed to 69 and 123 distinct
players, respectively.

The [temporal shrinkage pilot](../research/serve_shrinkage.md) evaluates five targets over rolling
training, validation, and test seasons. Across 2/5/10/20-match exposure thresholds, every shrunk
target beats the coarse context-only comparator overall and separately for ATP and WTA. At two
training matches, shrinkage also beats raw player estimates for all targets overall and in both
tours. At twenty matches, only first-serve-in remains consistently favorable across both tours;
several other shrunk-versus-raw ranges cross zero. Prior selection reaches both zero and the
maximum grid value, so neither one universal pooling strength nor a publication rule is approved.

The [publication-readiness audit](../research/serve_publication_readiness.md) evaluates trailing
five-complete-season player-surface histories without requiring future participation or exposing
identities. The median history has two distinct matches and about 1.9 effective matches. Only 22.5%
of history instances pass the diagnostic diversity/concentration intersection. At twenty matches,
median match-clustered uncertainty remains 1.66 times the conditional count-model deviation for
first-serve direction and 1.96 times for second-serve direction. Grass coverage is materially
sparser than hard-court coverage.

The first-serve direction [temporal robustness audit](../research/first_serve_direction_robustness.md)
then finds only 77%-82% later-season component coverage from match-clustered sampling uncertainty.
Validation-estimated [process uncertainty](../research/first_serve_direction_process_uncertainty.md)
raises aggregate coverage to approximately 95%-96%, but mean radii expand roughly 1.5-1.8 times
and sparse historical folds require pooled/global fallback. This is an internal modeling advance,
not publication approval.

## Gate result

**RETAIN SERVE CANDIDATES; PROCEED TO FEATURE-DEFINITION REVIEW:** the
[stability pilot](../research/serve_stability.md) found within-player medians below between-player
controls across every tested aggregate scenario. Chronological splits were consistently less stable
than alternating matches. The context-controlled pilot did not reverse that aggregate result, but
stricter context strata materially reduce coverage. The temporal pilot finds the largest sparse-
history gain for second-serve direction despite that family's weaker reconciliation and controlled
stability evidence; this tension must remain visible in any feature decision.
Do not create rankings, similarity maps, clusters, confidence labels, or public player fingerprints
yet.

Return, rally, ending, and net families remain exploratory or blocked. Aggregate agreement is a
software consistency check against a derived representation of the same source, not independent
validation of chart accuracy.

## Next work

1. jointly falsify raw/shrunk first-serve direction centers with validation-estimated process
   uncertainty, preserving width and fallback diagnostics;
2. investigate chronological drift and reconciliation mismatch classes for the remaining targets;
3. optionally investigate the 15 excluded exception rows to characterize recall without relaxing
   the accepted-link rule; and
4. approve, revise, or reject each serve target without constructing a composite vector.
