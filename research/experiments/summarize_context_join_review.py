"""Validate and summarize the project owner's MCP context-join review."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path


DEFAULT_AUTOMATED_REVIEW = Path("research/mcp_context_join_review.csv")
DEFAULT_HUMAN_REVIEW = Path(
    "research/mcp_context_join_review_reviewed_by_human.csv"
)
DEFAULT_JSON = Path("research/mcp_context_join_human_review.json")
DEFAULT_REPORT = Path("research/mcp_context_join_human_review.md")
REVIEWED_ON = "2026-09-03"
ALLOWED_REVIEW_STATUSES = {"", "confirmed", "rejected", "needs_investigation"}
DECISION_NAMES = {
    "": "not_reviewed",
    "confirmed": "same_match",
    "rejected": "different_match",
    "needs_investigation": "uncertain",
}
DATE_FIELDS = {"mcp_date", "context_tournament_date"}
BOOLEAN_FIELDS = {
    "surface_agrees",
    "round_agrees",
    "tournament_agrees",
    "best_of_agrees",
}
REVIEW_FIELDS = {"review_status", "review_notes"}


class InvalidHumanReview(ValueError):
    """Raised when the reviewed artifact does not preserve the generated sample."""


def _read_rows(path: Path) -> list[dict[str, str]]:
    sample = path.read_text(encoding="utf-8-sig")
    dialect = csv.Sniffer().sniff(sample[:4096], delimiters=",;")
    return list(csv.DictReader(sample.splitlines(), dialect=dialect))


def _normalize_date(value: str) -> str:
    if not value:
        return ""
    for pattern in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, pattern).date().isoformat()
        except ValueError:
            pass
    raise InvalidHumanReview(f"unsupported date representation: {value!r}")


def _normalize_boolean(value: str) -> str:
    normalized = value.strip().casefold()
    translations = {
        "": "",
        "true": "true",
        "false": "false",
        "verdadeiro": "true",
        "falso": "false",
    }
    if normalized not in translations:
        raise InvalidHumanReview(f"unsupported boolean representation: {value!r}")
    return translations[normalized]


def _normalize_evidence(field: str, value: str) -> str:
    value = value.strip()
    if field in DATE_FIELDS:
        return _normalize_date(value)
    if field in BOOLEAN_FIELDS:
        return _normalize_boolean(value)
    return value


def _wilson_interval(successes: int, trials: int) -> tuple[float, float] | None:
    """Return a descriptive 95% Wilson interval for a binomial proportion."""

    if not trials:
        return None
    z = 1.959963984540054
    estimate = successes / trials
    denominator = 1 + z**2 / trials
    center = (estimate + z**2 / (2 * trials)) / denominator
    margin = (
        z
        * math.sqrt(estimate * (1 - estimate) / trials + z**2 / (4 * trials**2))
        / denominator
    )
    return center - margin, center + margin


def summarize_review(
    automated_path: Path, human_path: Path
) -> dict[str, object]:
    automated_rows = _read_rows(automated_path)
    human_rows = _read_rows(human_path)
    automated_by_id = {row["mcp_match_id"]: row for row in automated_rows}
    human_by_id = {row["mcp_match_id"]: row for row in human_rows}
    if len(automated_by_id) != len(automated_rows):
        raise InvalidHumanReview("automated sample contains duplicate MCP match IDs")
    if len(human_by_id) != len(human_rows):
        raise InvalidHumanReview("human review contains duplicate MCP match IDs")
    if automated_by_id.keys() != human_by_id.keys():
        raise InvalidHumanReview("human review does not contain the generated sample IDs")

    evidence_fields = set(automated_rows[0]).difference(REVIEW_FIELDS)
    decisions = Counter()
    by_automation_status: dict[str, Counter[str]] = {}
    reviewed_rows = []
    for match_id, automated in automated_by_id.items():
        human = human_by_id[match_id]
        for field in evidence_fields:
            expected = _normalize_evidence(field, automated.get(field, ""))
            observed = _normalize_evidence(field, human.get(field, ""))
            if observed != expected:
                raise InvalidHumanReview(
                    f"evidence changed for {match_id}: {field} "
                    f"expected {expected!r}, found {observed!r}"
                )
        label = human.get("review_status", "").strip().casefold()
        if label not in ALLOWED_REVIEW_STATUSES:
            raise InvalidHumanReview(
                f"unsupported review_status for {match_id}: {label!r}"
            )
        decision = DECISION_NAMES[label]
        decisions[decision] += 1
        status_counts = by_automation_status.setdefault(
            automated["status"], Counter()
        )
        status_counts[decision] += 1
        reviewed_rows.append(
            {
                "mcp_match_id": match_id,
                "automation_status": automated["status"],
                "identity_decision": decision,
                "review_notes": human.get("review_notes", "").strip(),
            }
        )

    matched = [
        row for row in reviewed_rows if row["automation_status"] == "matched"
    ]
    matched_same = sum(row["identity_decision"] == "same_match" for row in matched)
    precision_interval = _wilson_interval(matched_same, len(matched))
    return {
        "reviewed_on": REVIEWED_ON,
        "automated_sample": str(automated_path).replace("\\", "/"),
        "human_review": str(human_path).replace("\\", "/"),
        "label_interpretation": DECISION_NAMES,
        "sample_rows": len(reviewed_rows),
        "decision_counts": dict(decisions),
        "by_automation_status": {
            status: dict(counts)
            for status, counts in sorted(by_automation_status.items())
        },
        "safe_match_precision_review": {
            "reviewed": len(matched),
            "same_match": matched_same,
            "different_match": sum(
                row["identity_decision"] == "different_match" for row in matched
            ),
            "uncertain_or_not_reviewed": sum(
                row["identity_decision"] in {"uncertain", "not_reviewed"}
                for row in matched
            ),
            "observed_precision": matched_same / len(matched) if matched else None,
            "descriptive_wilson_95_interval": list(precision_interval)
            if precision_interval
            else None,
        },
        "reviewed_rows": reviewed_rows,
    }


def render_report(result: dict[str, object]) -> str:
    precision = result["safe_match_precision_review"]
    interval = precision["descriptive_wilson_95_interval"]
    status_rows = [
        "| Automated status | Same match | Different match | Uncertain | Not reviewed |",
        "|---|---:|---:|---:|---:|",
    ]
    for status, counts in result["by_automation_status"].items():
        status_rows.append(
            f"| `{status}` | {counts.get('same_match', 0)} | "
            f"{counts.get('different_match', 0)} | {counts.get('uncertain', 0)} | "
            f"{counts.get('not_reviewed', 0)} |"
        )
    return f"""# MCP context join human-review result

**Review date:** {result['reviewed_on']}

**Status:** safe-link precision review complete; exception recall review partial

## Label interpretation

The project owner reviewed the sample after receiving the explicit instruction that `confirmed`
means the two records represent the **same match**, `rejected` means **different matches**, and a
blank cell is **not reviewed**. This interpretation replaces the earlier ambiguous wording that
used `confirmed` differently for exception rows. The submitted CSV is preserved unchanged.

## Result

{chr(10).join(status_rows)}

All {precision['reviewed']} automated `matched` links were reviewed as the same match; none was
reviewed as a different match. The observed precision in this small deterministic sample is
{precision['observed_precision']:.1%}. A descriptive 95% Wilson interval is
{interval[0]:.1%}-{interval[1]:.1%}; this interval is not a design-based confidence interval because
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
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--automated", type=Path, default=DEFAULT_AUTOMATED_REVIEW)
    parser.add_argument("--human", type=Path, default=DEFAULT_HUMAN_REVIEW)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    arguments = parser.parse_args()
    result = summarize_review(arguments.automated, arguments.human)
    arguments.json.write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    arguments.report.write_text(render_report(result), encoding="utf-8")
    print(f"Wrote {arguments.json}")
    print(f"Wrote {arguments.report}")


if __name__ == "__main__":
    main()
