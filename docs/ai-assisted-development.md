# AI-assisted development

Tennis Intelligence uses AI as a transparent development collaborator. AI-generated output is treated as a draft or proposal until reviewed and validated by the project owner.

## Ownership

| Area | AI-assisted | Human-owned |
|---|---|---|
| Research discovery | Search expansion, source summaries, competing-method prompts | Research question, source acceptance, interpretation |
| Implementation | Boilerplate, focused modules, test drafts, refactoring suggestions | Architecture, API contracts, methodology approval, final code review |
| Statistics | Candidate formulations, adversarial questions, sensitivity-test proposals | Estimand, assumptions, statistical judgment, conclusions |
| Product | Copy variants, UI iteration, accessibility checklist, screenshot review prompts | Product direction, information hierarchy, visual standard, final decisions |
| Documentation | Drafts, structure, consistency checks | Claims, trade-offs, limitations, public accountability |

## Workflow record

| Task | Skill used | AI contribution | Human review | Validation |
|---|---|---|---|---|
| Establish literature baseline | `research-reviewer` | Proposed source map and claim labels | Verify exact source and scope | DOI/official URL review; unresolved claims retained |
| Challenge PPI | `statistical-skeptic` | Confounders, leakage threats, candidate comparisons | Decide estimand and stopping criteria | Temporal persistence and calibration plan |
| Define repository foundation | `engineering-quality-gate` | Structure and standards draft | Remove speculative infrastructure | Path and Markdown checks |
| Audit MCP feasibility | `data-quality-auditor` | Exposed duplicate conflicts, coverage boundaries, and blocked features | Approve exclusions and future source scope | Reproducible profile, hashes, and fixture tests |
| Audit complete MCP snapshot | `research-reviewer`, `data-quality-auditor`, `engineering-quality-gate` | Corrected stale source claims; pinned and profiled all ATP/WTA shards and selected aggregates | Confirm snapshot policy and parser scope | Commit/hash provenance, streaming audit, focused tests, reproducibility run |
| Build parser v0.2 and reconcile serves | `data-quality-auditor`, `statistical-skeptic`, `engineering-quality-gate` | Proposed field-aware validity, implemented raw-to-aggregate comparisons, and found denominator/court-side defects | Review serve candidate definitions and stability boundary | Prefix regressions, full-corpus reconciliation, missingness report, aggregate conflict exclusions |
| Run serve stability pilot | `data-quality-auditor`, `statistical-skeptic`, `engineering-quality-gate` | Added contextual mismatch denominators, independent match splits, within-tour controls, and match bootstrap diagnostics | Review whether provisional persistence justifies contextual falsification | Threshold/split sensitivity, deterministic seed, regression tests, complete-snapshot reruns |
| Audit MCP-to-context identity | `data-quality-auditor`, `engineering-quality-gate` | Pinned a documented mirror, separated join failure classes, and rejected pair/date links without supporting context | Label the deterministic 50-row sample and decide whether the mirror provenance is acceptable | Source hashes, schema checks, window sensitivity, collision checks, field agreement, focused tests |
| Shape future product story | `portfolio-storyteller` | Narrative structure and reader questions | Keep personal motivation and uncertainty | README review against portfolio checklist |

## Current review status
- Research reviewer: baseline completed with a source-quality caveat. The bibliography is intentionally small and requires exact metadata/access-date verification before publication.
- Statistical skeptic: aggregate serve persistence is provisional; chronological drift and missing context block player profiles, composite distances, and rankings.
- Data-quality auditor: the precision-first context join reaches 97.8% automated match coverage,
  but human sample review and two player-ID collisions block crosswalk approval.
- Complete-snapshot audit: 11,590 safely joined matches and 1.85M usable logical points support Phase 2 work. Serve aggregates are now reconciliation targets with explicit grain conflicts and exceptions.
- Engineering quality gate: foundation, parser, serve validation, and stability milestones passed;
  the context join passes as an audit artifact but not as a production crosswalk.
- Portfolio storyteller: completed as a self-review; README leads with the question and status, while installation is deferred.

These are review artifacts, not automatic approvals. The project owner retains responsibility for methodology, interpretation, and final conclusions.

## Guardrails
AI must not invent citations, silently change methodology, hide negative results, or claim to have run tools or analyses it did not run. Prompts, important disagreements, and consequential decisions should be recorded in the relevant ADR or experiment report.
