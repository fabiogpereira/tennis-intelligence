# Phase 2 progress: parser v0.2 and serve validation

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

## Gate result

**PROCEED TO A SERVE-ONLY STABILITY PILOT:** use the versioned definitions in
[serve_feature_candidates.md](../research/serve_feature_candidates.md). Do not create rankings,
similarity maps, clusters, confidence labels, or public player fingerprints yet.

Return, rally, ending, and net families remain exploratory or blocked. Aggregate agreement is a
software consistency check against a derived representation of the same source, not independent
validation of chart accuracy.

## Next work

1. characterize serve reconciliation exceptions by era, tour, match, and chart author;
2. define canonical player/match identifiers and join broader ATP/WTA context;
3. implement a serve-only stability experiment using independent match splits and match-level
   uncertainty;
4. test surface, opponent, era, and tournament sensitivity; and
5. approve, revise, or reject each serve candidate separately.
