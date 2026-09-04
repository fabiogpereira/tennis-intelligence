# MCP context join human-review result

**Review date:** 2026-09-03

**Status:** safe-link precision review complete; exception recall review partial

## Label interpretation

The project owner reviewed the sample after receiving the explicit instruction that `confirmed`
means the two records represent the **same match**, `rejected` means **different matches**, and a
blank cell is **not reviewed**. This interpretation replaces the earlier ambiguous wording that
used `confirmed` differently for exception rows. The submitted CSV is preserved unchanged.

## Result

| Automated status | Same match | Different match | Uncertain | Not reviewed |
|---|---:|---:|---:|---:|
| `ambiguous` | 0 | 0 | 0 | 5 |
| `canonical_collision` | 4 | 1 | 0 | 0 |
| `conflicting_context` | 5 | 0 | 0 | 0 |
| `matched` | 25 | 0 | 0 | 0 |
| `unresolved_date_window` | 0 | 0 | 0 | 5 |
| `unresolved_pair` | 0 | 0 | 0 | 5 |

All 25 automated `matched` links were reviewed as the same match; none was
reviewed as a different match. The observed precision in this small deterministic sample is
100.0%. A descriptive 95% Wilson interval is
86.7%-100.0%; this interval is not a design-based confidence interval because
the sample was selected deterministically rather than by recorded random sampling.

One `canonical_collision` row -- the 2003 Filderstadt record for Kim Clijsters and Justine
Henin -- was reviewed as a different match from the selected US Open context row. It was already
excluded from the safe matched set. The remaining reviewed collision and conflict rows referred to
the same underlying matches despite inconsistent metadata.

## Project-owner observations

- Davis Cup records account for several tournament-name disagreements; competition ownership and
  historical source conventions may differ from regular ATP event records.
- Smaller ITF events may use different tournament labels across sources without representing
  different matches.
- Tour Finals / Masters naming varies, and historical indoor surface labels often disagree between
  hard and carpet.
- Same players, year, round, and surface are insufficient for identity: Clijsters and Henin played
  two hard-court finals in 2003, producing the one reviewed wrong-tournament candidate.

These are human observations from this sample, not general rules and not authority to overwrite
source fields.

## Data-quality decision

**ENGINEERING DECISION:** the 11,336 collision-free automated links may be used for the next
internal context-controlled falsification experiment. The review found no false link among the 25
sampled safe links, and the known different-match candidate was already excluded.

**OPEN QUESTION:** five ambiguous, five outside-window, and five absent-pair exceptions were not
reviewed. They affect recall and source coverage, not the measured precision of the accepted set.
They remain excluded; no alias or relaxed join rule is introduced.

**DATA-QUALITY DECISION:** this does not approve a production player crosswalk, published player
profiles, or broad claims of 100% precision. The small deterministic sample, two source player-ID
collisions, mirror provenance gap, and license constraints remain explicit limitations.

## Reproduce

```powershell
python -m research.experiments.summarize_context_join_review
```
