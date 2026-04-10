#!/usr/bin/env python3
"""Fit a diffusion coefficient from a GPUMD msd.out file.

msd.out is a whitespace-separated table. The exact column layout depends on
the GPUMD version, but for the default `compute_msd` output the file
typically contains:

    time  MSD_x  MSD_y  MSD_z  [MSD_total]

where `time` is in ps and the MSD columns are in Å^2.

This helper:
  * reads numeric rows
  * picks a time column and an MSD column (default: last column as total MSD)
  * fits a straight line over a user-chosen fraction of the trajectory
  * reports the diffusion coefficient D = slope / (2 * dim)

Usage:
    python fit_msd_diffusion.py msd.out
    python fit_msd_diffusion.py msd.out --time-col 0 --msd-col 4 --dim 3
    python fit_msd_diffusion.py msd.out --start-frac 0.3 --end-frac 0.9

Units:
    time  in ps
    MSD   in Å^2
    D     reported in Å^2 / ps  and also converted to m^2 / s.
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


def linear_fit(xs: list[float], ys: list[float]) -> tuple[float, float]:
    if len(xs) != len(ys) or len(xs) < 2:
        raise SystemExit("not enough points to fit")
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den = sum((x - mean_x) ** 2 for x in xs)
    if den == 0.0:
        raise SystemExit("x values do not vary; cannot fit a line")
    slope = num / den
    intercept = mean_y - slope * mean_x
    return slope, intercept


def main() -> int:
    parser = argparse.ArgumentParser(description="Fit D from GPUMD msd.out.")
    parser.add_argument("path", type=Path, help="path to msd.out")
    parser.add_argument("--time-col", type=int, default=0, help="time column index (0-based)")
    parser.add_argument(
        "--msd-col",
        type=int,
        default=-1,
        help="MSD column index (0-based). -1 = last column.",
    )
    parser.add_argument("--dim", type=int, default=3, help="spatial dimensionality (3 bulk, 2 in-plane, 1 confined)")
    parser.add_argument("--start-frac", type=float, default=0.3, help="fit start as a fraction of the file")
    parser.add_argument("--end-frac", type=float, default=0.9, help="fit end as a fraction of the file")
    args = parser.parse_args()

    rows = read_rows(args.path)
    if not rows:
        print("no numeric rows found", file=sys.stderr)
        return 1
    ncol = len(rows[0])
    if args.time_col < 0 or args.time_col >= ncol:
        raise SystemExit(f"time-col {args.time_col} out of range (ncol={ncol})")
    msd_col = args.msd_col if args.msd_col >= 0 else ncol - 1
    if msd_col < 0 or msd_col >= ncol:
        raise SystemExit(f"msd-col {msd_col} out of range (ncol={ncol})")

    n = len(rows)
    start = max(1, int(args.start_frac * n))
    end = min(n, int(args.end_frac * n))
    if end <= start + 1:
        raise SystemExit("fit window is empty; adjust --start-frac/--end-frac")

    xs = [rows[i][args.time_col] for i in range(start, end)]
    ys = [rows[i][msd_col] for i in range(start, end)]
    slope, intercept = linear_fit(xs, ys)

    d_angstrom2_per_ps = slope / (2.0 * args.dim)
    # 1 Å^2 / ps = 1e-20 m^2 / 1e-12 s = 1e-8 m^2 / s
    d_m2_per_s = d_angstrom2_per_ps * 1e-8

    print(f"rows_total: {n}")
    print(f"fit_window_rows: {end - start}")
    print(f"time_col: {args.time_col}")
    print(f"msd_col: {msd_col}")
    print(f"dim: {args.dim}")
    print(f"slope_Angstrom2_per_ps: {slope:.6g}")
    print(f"intercept_Angstrom2: {intercept:.6g}")
    print(f"D_Angstrom2_per_ps: {d_angstrom2_per_ps:.6g}")
    print(f"D_m2_per_s: {d_m2_per_s:.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
