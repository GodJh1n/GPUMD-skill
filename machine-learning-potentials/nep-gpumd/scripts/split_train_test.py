#!/usr/bin/env python3
"""Split an extxyz file into train.xyz and test.xyz.

Reads a concatenated extxyz file and randomly splits it into training
and test sets at a user-specified ratio. The split is frame-level (not
atom-level): each frame goes entirely into train or test.

Usage:
    python split_train_test.py all.xyz
    python split_train_test.py all.xyz --ratio 0.9
    python split_train_test.py all.xyz --seed 42 --out-dir ./split
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path


def read_frames(path: Path) -> list[str]:
    """Return a list of raw frame strings from a concatenated extxyz file."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    frames: list[str] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        try:
            atom_count = int(stripped)
        except ValueError:
            print(f"warning: expected atom count at line {i + 1}, skipping", file=sys.stderr)
            i += 1
            continue
        end = i + atom_count + 2
        if end > len(lines):
            print(f"warning: truncated frame at line {i + 1}", file=sys.stderr)
            break
        frames.append("".join(lines[i:end]))
        i = end
    return frames


def main() -> int:
    parser = argparse.ArgumentParser(description="Split extxyz into train/test.")
    parser.add_argument("path", type=Path, help="input extxyz file")
    parser.add_argument(
        "--ratio",
        type=float,
        default=0.9,
        help="fraction of frames for training (default: 0.9)",
    )
    parser.add_argument("--seed", type=int, default=42, help="random seed")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="output directory (default: same as input file)",
    )
    args = parser.parse_args()

    if not args.path.is_file():
        print(f"file not found: {args.path}", file=sys.stderr)
        return 1

    frames = read_frames(args.path)
    if not frames:
        print("no frames found", file=sys.stderr)
        return 1

    rng = random.Random(args.seed)
    indices = list(range(len(frames)))
    rng.shuffle(indices)

    split_point = max(1, int(len(frames) * args.ratio))
    train_indices = sorted(indices[:split_point])
    test_indices = sorted(indices[split_point:])

    out_dir = args.out_dir or args.path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    train_path = out_dir / "train.xyz"
    test_path = out_dir / "test.xyz"

    train_path.write_text("".join(frames[i] for i in train_indices), encoding="utf-8")
    test_path.write_text("".join(frames[i] for i in test_indices), encoding="utf-8")

    print(f"total_frames: {len(frames)}")
    print(f"train_frames: {len(train_indices)} -> {train_path}")
    print(f"test_frames:  {len(test_indices)} -> {test_path}")
    print(f"seed: {args.seed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
