# ADR-012: Serve coverage and clustered uncertainty

**Status:** Accepted for internal measurement; public eligibility remains unapproved

**Date:** 2026-09-04

## Context

Serve estimates contain many point events but often very few charted matches. Treating events as
independent can make an estimate appear precise even when it is dominated by one match, opponent,
tournament, or contributor. A minimum match count alone also hides concentration and unequal
surface coverage.

## Decision

**ENGINEERING DECISION:** future serve-measurement proposals must treat the match as the
uncertainty cluster and report distinct matches alongside effective match count, distinct seasons,
opponents, tournaments, chart authors, and largest-match event share. Surface-specific coverage
must remain visible.

Five-season histories use complete seasons preceding the as-of year. The partial latest observed
season is not treated as complete. Coverage and uncertainty sensitivity grids are audit outputs,
not automatic publication thresholds.

Conditional Beta/Dirichlet posterior deviation may be used as a model diagnostic. It must not be
presented as total confidence or as a substitute for match-clustered uncertainty.

## Evidence

The `research-serve-publication-readiness-v0.1` audit finds a median of two distinct matches and
about 1.9 effective matches per player-surface-period history. Its diagnostic diversity and
concentration intersection retains 22.5% of history instances. Even among histories with at least
twenty matches, median clustered uncertainty is 1.66 times the conditional diagnostic for
first-serve direction and 1.96 times for second-serve direction. Grass coverage is materially
sparser than hard-court coverage.

## Consequences

- No public eligibility threshold, confidence badge, or player profile is approved.
- Point count cannot stand alone as an exposure label.
- Direction features require cluster-aware intervals if they advance.
- Broad availability and strict coverage will trade off; the product must not hide excluded
  players.
- A narrow interval cannot correct MCP charting selection or establish population
  representativeness.

## Alternatives rejected

- Point-independent uncertainty: contradicted by the clustered direction diagnostics.
- One minimum-match rule: does not measure match dominance or context diversity.
- Using the partial latest season as a complete period: creates inconsistent exposure.
- Choosing the stress-test intersection as policy: the audit was designed for sensitivity, not
  automatic approval.
