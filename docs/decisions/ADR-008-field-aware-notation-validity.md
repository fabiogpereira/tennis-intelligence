# ADR-008: Preserve field-aware validity in MCP notation parsing

## Status
Accepted on 2026-09-03.

## Context
The draft v0.1 parser rejected an entire notation cell when any later token was unsupported. This
made whole-cell validity easy to reason about, but it also discarded independently safe prefixes.
Corpus rejection is concentrated by era and player, so using only fully parsed cells would transfer
rally-grammar missingness into otherwise simple serve fields.

## Decision
**ENGINEERING DECISION:** `mcp-parser-v0.2-draft` retains safely decoded prefix fields while keeping
the cell invalid as a whole. Serve direction, serve-and-volley, rally, and outcome expose explicit
component states: `observed`, `unknown`, `absent`, `partial`, `invalid`, or `not_applicable`.

Unsupported suffixes are preserved verbatim and reported with their failure position. They are not
silently normalized. Feature eligibility is evaluated per component and denominator; whole-cell
parse success is no longer used as a universal feature gate.

## Consequences
- A rally failure can leave serve direction usable without making the rally or outcome usable.
- Reports must show whole-cell success and field-level coverage separately.
- Tests must prove that malformed prefixes expose no downstream fields.
- Each feature family requires its own missingness, aggregate-reconciliation, and stability gate.
- Results from parser v0.1 and v0.2 are not interchangeable even when whole-cell success is equal.
