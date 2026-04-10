#!/usr/bin/env python3
"""Compute parity metrics (RMSE, MAE, R²) from NEP parity output files.

After NEP training or prediction, the `nep` binary writes parity files
such as `energy_train.out`, `energy_test.out`, `force_train.out`, etc.
Each row has two columns: DFT_value  NEP_value.

This script reads such a file and reports summary statistics.

Usage:
    python parity_from_nep_outputs.py --prefix energy_test
    python parity_from_nep_outputs.py --file force_test.out
    python parity_from_nep_outputs.py --prefix virial_train
"""
from __future__ import annotations

import argparse
import math
import statistics
import sys
from pathlib import Path


def read_pairs(path: Path) -> list[tuple[float, float]]:
    """Read (reference, predicted) pairs from a two-column file."""
    pairs: list[tuple[float, float]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if len(parts) < 2:
            continue
        try:
            pairs.append((float(parts[0]), float(parts[1])))
        except ValueError:
            continue
    return pairs


def compute_metrics(pairs: list[tuple[float, float]]) -> dict[str, float]:
    if len(pairs) < 2:
        return {"n": len(pairs), "rmse": float("nan"), "mae": float("nan"), "r2": float("nan")}
    refs = [p[0] for p in pairs]
    preds = [p[1] for p in pairs]
    errors = [pred - ref for ref, pred in pairs]
    abs_errors = [abs(e) for e in errors]
    rmse = math.sqrt(statistics.fmean([e**2 for e in errors]))
    mae = statistics.fmean(abs_errors)
    mean_ref = statistics.fmean(refs)
    ss_res = sum(e**2 for e in errors)
    ss_tot = sum((r - mean_ref) ** 2 for r in refs)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0.0 else float("nan")
    return {"n": len(pairs), "rmse": rmse, "mae": mae, "r2": r2}


def main() -> int:
    parser = argparse.ArgumentParser(description="Parity metrics from NEP outputs.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prefix", type=str, help="file prefix (e.g. energy_test)")
    group.add_argument("--file", type=Path, help="explicit path to parity file")
    args = parser.parse_args()

    if args.file:
        path = args.file
    else:
        path = Path(f"{args.prefix}.out")

    if not path.is_file():
        print(f"file not found: {path}", file=sys.stderr)
        return 1

    pairs = read_pairs(path)
    if not pairs:
        print(f"no valid data pairs in {path}", file=sys.stderr)
        return 1

    m = compute_metrics(pairs)
    print(f"file: {path}")
    print(f"n_points: {m['n']}")
    print(f"RMSE: {m['rmse']:.6g}")
    print(f"MAE:  {m['mae']:.6g}")
    print(f"R2:   {m['r2']:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
