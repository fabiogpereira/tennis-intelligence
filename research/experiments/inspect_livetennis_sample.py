"""Inspect the public LiveTennisAPI sample without third-party dependencies."""

from __future__ import annotations

import csv
import gzip
from collections import defaultdict
from pathlib import Path


ROOT = Path("data/raw/livetennisapi")


def read_gzip_csv(name: str):
    with gzip.open(ROOT / name, mode="rt", newline="", encoding="utf-8") as source:
        yield from csv.DictReader(source)


def main() -> None:
    matches = list(read_gzip_csv("matches.csv.gz"))
    players = list(read_gzip_csv("players.csv.gz"))
    points_by_match: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_gzip_csv("points_sample_2026-06.csv.gz"):
        points_by_match[row["match_id"]].append(row)

    first_match_id = next(iter(points_by_match))
    first_tape = points_by_match[first_match_id]
    missing_servers = sum(
        row["server"] == "" for rows in points_by_match.values() for row in rows
    )
    zero_zero_starts = sum(
        rows[0]["sets_p1"] == "0"
        and rows[0]["sets_p2"] == "0"
        and rows[0]["games_p1"] == "[0]"
        and rows[0]["games_p2"] == "[0]"
        and rows[0]["points_p1"] == "0"
        and rows[0]["points_p2"] == "0"
        for rows in points_by_match.values()
    )

    print(f"match_rows={len(matches)}")
    print(f"player_rows={len(players)}")
    print(f"point_rows={sum(map(len, points_by_match.values()))}")
    print(f"point_matches={len(points_by_match)}")
    print(f"missing_server_states={missing_servers}")
    print(f"zero_zero_starts={zero_zero_starts}")
    print(f"point_columns={list(first_tape[0])}")
    print(f"first_match_id={first_match_id}")
    print(f"first_state={first_tape[0]}")
    print(f"last_state={first_tape[-1]}")


if __name__ == "__main__":
    main()
