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

## Gate result

**RETAIN SERVE CANDIDATES; PROCEED TO CONTEXT-CONTROLLED FALSIFICATION:** the
[stability pilot](../research/serve_stability.md) found within-player medians below between-player
controls across every tested aggregate scenario. Chronological splits were consistently less stable
than alternating matches, and second-serve direction remains the weakest family. Do not create
rankings, similarity maps, clusters, confidence labels, or public player fingerprints yet.

Return, rally, ending, and net families remain exploratory or blocked. Aggregate agreement is a
software consistency check against a derived representation of the same source, not independent
validation of chart accuracy.

## Next work

1. test surface, opponent, era, tournament, ranking, and chart-author sensitivity using only the
   collision-free safe context links;
2. define shrinkage and player-level uncertainty without selecting an eligibility cutoff post hoc;
3. investigate chronological drift and reconciliation mismatch classes;
4. optionally investigate the 15 excluded exception rows to characterize recall without relaxing
   the accepted-link rule; and
5. approve, revise, or reject each serve candidate separately.
