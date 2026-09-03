"""Profile duplicate match-point keys in the local MCP snapshot."""

from __future__ import annotations

import csv
import hashlib
from collections import defaultdict
from pathlib import Path


SOURCE = Path("data/raw/mcp/charting-w-points-to-2009.csv")


def main() -> None:
    counts: defaultdict[tuple[str, str], int] = defaultdict(int)
    signatures: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
    rows_by_key: defaultdict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    with SOURCE.open(newline="", encoding="utf-8-sig") as source:
        for row in csv.DictReader(source):
            key = (row["match_id"], row["Pt"])
            counts[key] += 1
            payload = "\0".join(row.values()).encode("utf-8")
            signatures[key].add(hashlib.sha256(payload).hexdigest())
            rows_by_key[key].append(row)

    repeated = [key for key, count in counts.items() if count > 1]
    identical = [key for key in repeated if len(signatures[key]) == 1]
    conflicting = [key for key in repeated if len(signatures[key]) > 1]
    print(f"duplicate_groups={len(repeated)}")
    print(f"identical_duplicate_groups={len(identical)}")
    print(f"conflicting_duplicate_groups={len(conflicting)}")
    for match_id, point_number in conflicting:
        print(f"conflict={match_id}|{point_number}")
        first, second = rows_by_key[(match_id, point_number)][:2]
        differing = [name for name in first if first[name] != second[name]]
        print(f"differing_fields={','.join(differing)}")


if __name__ == "__main__":
    main()
