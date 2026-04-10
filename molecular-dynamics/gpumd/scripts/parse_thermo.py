#!/usr/bin/env python3
"""Parse GPUMD thermo.out and print a compact summary.

thermo.out is a whitespace-separated numeric table written by dump_thermo.
The exact column layout depends on the GPUMD version and on whether the
run is NVT, NPT, or NVE, so this helper is deliberately schema-agnostic:
it reads all numeric rows and reports per-column mean, std, min, max over
either the whole file or the last N rows.

Usage:
    python parse_thermo.py thermo.out
    python parse_thermo.py thermo.out --last 50
    python parse_thermo.py thermo.out --columns 1,2,6
"""
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
        try:
            rows.append([float(x) for x in stripped.split()])
        except ValueError:
            continue
    return rows


def mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return float("nan"), float("nan")
    if len(values) == 1:
        return values[0], 0.0
    return statistics.fmean(values), statistics.stdev(values)


def parse_column_selection(spec: str | None, ncol: int) -> list[int]:
    if spec is None:
        return list(range(ncol))
    out: list[int] = []
    for token in spec.split(","):
        token = token.strip()
        if not token:
            continue
        idx = int(token)
        if idx < 0 or idx >= ncol:
            raise SystemExit(f"column index {idx} out of range (ncol={ncol})")
        out.append(idx)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize a GPUMD thermo.out file.")
    parser.add_argument("path", type=Path, help="path to thermo.out")
    parser.add_argument("--last", type=int, default=0, help="only use the last N rows")
    parser.add_argument(
        "--columns",
        type=str,
        default=None,
        help="comma-separated column indices to include (0-based); default: all",
    )
    args = parser.parse_args()

    rows = read_rows(args.path)
    if not rows:
        print("no numeric rows found", file=sys.stderr)
        return 1

    if args.last > 0:
        rows = rows[-args.last :]

    ncol = len(rows[0])
    cols = parse_column_selection(args.columns, ncol)
    columns = list(zip(*rows))

    print(f"rows_used: {len(rows)}")
    print(f"ncol: {ncol}")
    print("# col  mean  std  min  max")
    for idx in cols:
        values = list(columns[idx])
        mean, std = mean_std(values)
        print(f"{idx:>4}  {mean:.6g}  {std:.6g}  {min(values):.6g}  {max(values):.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
