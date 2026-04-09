#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path


def parse_rows(path: Path) -> list[list[float]]:
    rows: list[list[float]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            rows.append([float(x) for x in stripped.split()])
        except ValueError:
            continue
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize NEP loss.out")
    parser.add_argument("path", type=Path, help="Path to loss.out")
    args = parser.parse_args()

    rows = parse_rows(args.path)
    if not rows:
        print("no numeric rows found in loss.out", file=sys.stderr)
        return 1

    last = rows[-1]
    ncol = len(last)
    candidate_cols = [
        idx
        for idx in range(1, ncol)
        if any((not math.isnan(row[idx])) and abs(row[idx]) > 0.0 for row in rows)
    ]
    primary_col = candidate_cols[0] if candidate_cols else (1 if ncol > 1 else 0)
    best_idx = min(
        range(len(rows)),
        key=lambda i: rows[i][primary_col] if not math.isnan(rows[i][primary_col]) else float("inf"),
    )
    best = rows[best_idx]

    print(f"rows: {len(rows)}")
    print(f"last_step: {int(last[0]) if last else 'n/a'}")
    print("last_row:", " ".join(f"{x:.6g}" for x in last))
    print(f"primary_metric_column: {primary_col + 1}")
    print(f"best_primary_metric_step: {int(best[0])}")
    print("best_primary_metric_row:", " ".join(f"{x:.6g}" for x in best))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
