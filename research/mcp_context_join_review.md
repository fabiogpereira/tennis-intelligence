# MCP context join human review

**Status:** awaiting project-owner labels

The generated `research/mcp_context_join_review.csv` contains a deterministic 50-row sample: 25
accepted links and five examples from each automated exception class. It is derived from sources
distributed under CC BY-NC-SA 4.0 and retains Jeff Sackmann / Tennis Abstract attribution through
the [snapshot contract](../data/sackmann_context_snapshot.md).

## Review protocol

For every row, inspect the MCP match ID, context match ID, date offset, and available tournament,
round, and surface agreement flags. Set `review_status` to exactly one of:

- `confirmed`: both identifiers refer to the same match, or the automated rejection is correct;
- `rejected`: an accepted link is false, or the exception classification is demonstrably wrong;
- `needs_investigation`: available evidence cannot decide safely.

Record the evidence and reasoning in `review_notes`. Do not repair a name, date, or identifier in
place. Proposed aliases or source corrections require a separate versioned mapping with evidence.

## Acceptance boundary

The join cannot become an approved player crosswalk from aggregate coverage alone. Review outcomes
must be summarized by class, and any observed false-link rate must be reported with the sample
design. Re-running the audit overwrites the CSV, so preserve completed labels before regeneration.
