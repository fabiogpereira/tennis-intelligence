# MCP context join human review

**Status:** template preserved; safe-link precision review completed separately

The generated `research/mcp_context_join_review.csv` contains a deterministic 50-row sample: 25
accepted links and five examples from each automated exception class. It is derived from sources
distributed under CC BY-NC-SA 4.0 and retains Jeff Sackmann / Tennis Abstract attribution through
the [snapshot contract](../data/sackmann_context_snapshot.md).

## Review protocol

For every row, compare the source evidence presented side by side: dates, tournaments, rounds,
surfaces, best-of values, and player names. `candidate_context_ids` retains every exact-pair
candidate considered by the resolver: candidates inside the date window for ambiguous cases, and
all known exact-pair candidates for `unresolved_date_window`. The selected context row, when one
exists, also records its source file. Set `review_status` to exactly one of:

- `confirmed`: both identifiers refer to the same match;
- `rejected`: the identifiers refer to different matches;
- `needs_investigation`: available evidence cannot decide safely.

Record the evidence and reasoning in `review_notes`. Do not repair a name, date, or identifier in
place. Proposed aliases or source corrections require a separate versioned mapping with evidence.
Blank context-detail columns mean that the automated resolver did not select a unique candidate;
they do not mean the contextual source was inspected and found empty.

## Acceptance boundary

The join cannot become an approved player crosswalk from aggregate coverage alone. Review outcomes
must be summarized by class, and any observed false-link rate must be reported with the sample
design. Re-running the audit overwrites the CSV, so preserve completed labels before regeneration.

The project owner's submitted review is preserved as
[`mcp_context_join_review_reviewed_by_human.csv`](mcp_context_join_review_reviewed_by_human.csv).
Its validated interpretation and bounded decision are reported in
[`mcp_context_join_human_review.md`](mcp_context_join_human_review.md). The original generated CSV
remains an unlabelled, reproducible template.
