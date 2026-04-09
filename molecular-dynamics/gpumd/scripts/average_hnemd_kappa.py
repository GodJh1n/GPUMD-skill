#!/usr/bin/env python3
from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path


def read_rows(path: Path) -> list[list[float]]:
    rows: list[list[float]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        rows.append([float(x) for x in stripped.split()])
    return rows


def mean_and_std(values: list[float]) -> tuple[float, float]:
    if len(values) == 1:
        return values[0], 0.0
    return statistics.fmean(values), statistics.stdev(values)


def main() -> int:
    parser = argparse.ArgumentParser(description="Average GPUMD HNEMD conductivity outputs.")
    parser.add_argument("path", type=Path, help="Path to kappa.out")
    parser.add_argument("--discard-rows", type=int, default=0, help="Rows to discard from the start")
    parser.add_argument(
        "--discard-frac", type=float, default=0.0, help="Fraction of initial rows to discard"
    )
    args = parser.parse_args()

    rows = read_rows(args.path)
    if not rows:
        print("no numeric rows found", file=sys.stderr)
        return 1

    discard = max(args.discard_rows, int(len(rows) * args.discard_frac))
    rows = rows[discard:]
    if not rows:
        print("all rows were discarded", file=sys.stderr)
        return 1

    ncol = len(rows[0])
    if ncol == 5:
        labels = ["x_in", "x_out", "y_in", "y_out", "z"]
    elif ncol == 6:
        labels = ["x_in", "x_out", "y_in", "y_out", "z_in", "z_out"]
    else:
        labels = [f"col{i+1}" for i in range(ncol)]

    columns = list(zip(*rows))
    print(f"rows_used: {len(rows)}")
    print(f"discarded_rows: {discard}")
    for label, values in zip(labels, columns):
        mean, std = mean_and_std(list(values))
        print(f"{label}: mean={mean:.6f} std={std:.6f}")

    if ncol >= 5:
        x_total = [(r[0] + r[1]) / 2.0 for r in rows]
        y_total = [(r[2] + r[3]) / 2.0 for r in rows]
        x_mean, x_std = mean_and_std(x_total)
        y_mean, y_std = mean_and_std(y_total)
        print(f"x_total: mean={x_mean:.6f} std={x_std:.6f}")
        print(f"y_total: mean={y_mean:.6f} std={y_std:.6f}")
        if ncol == 6:
            z_total = [(r[4] + r[5]) / 2.0 for r in rows]
            z_mean, z_std = mean_and_std(z_total)
            print(f"z_total: mean={z_mean:.6f} std={z_std:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
