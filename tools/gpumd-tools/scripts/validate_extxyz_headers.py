#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


HEADER_RE = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)=(?:"([^"]*)"|(\S+))')


def parse_header(header: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, quoted, bare in HEADER_RE.findall(header):
        result[key] = quoted if quoted else bare
    return result


def count_property_columns(properties: str) -> int:
    parts = properties.split(":")
    if len(parts) % 3 != 0:
        raise ValueError(f"invalid Properties field: {properties}")
    total = 0
    for i in range(0, len(parts), 3):
        count = int(parts[i + 2])
        total += count
    return total


def validate_frame(
    atom_count: int, header_map: dict[str, str], atom_lines: list[str], mode: str, frame_id: int
) -> list[str]:
    errors: list[str] = []
    normalized = {key.lower(): value for key, value in header_map.items()}

    if "lattice" not in normalized:
        errors.append(f"frame {frame_id}: missing Lattice")
    else:
        lattice_values = normalized["lattice"].split()
        if len(lattice_values) != 9:
            errors.append(f"frame {frame_id}: Lattice must contain 9 numbers")
    if "properties" not in normalized:
        errors.append(f"frame {frame_id}: missing Properties")
        return errors

    try:
        expected_cols = count_property_columns(normalized["properties"])
    except Exception as exc:
        errors.append(f"frame {frame_id}: {exc}")
        return errors

    if mode == "train" and "energy" not in normalized:
        errors.append(f"frame {frame_id}: training frame missing energy")

    properties = normalized["properties"].lower()
    if mode == "train" and "force:r:3" not in properties and "forces:r:3" not in properties:
        errors.append(f"frame {frame_id}: training frame missing force column declaration")

    if len(atom_lines) != atom_count:
        errors.append(f"frame {frame_id}: expected {atom_count} atom rows, found {len(atom_lines)}")
        return errors

    for idx, line in enumerate(atom_lines, start=1):
        cols = line.split()
        if len(cols) != expected_cols:
            errors.append(
                f"frame {frame_id}: atom row {idx} has {len(cols)} columns, expected {expected_cols}"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate GPUMD/NEP extxyz-like headers.")
    parser.add_argument("path", type=Path, help="Path to model.xyz, train.xyz, or test.xyz")
    parser.add_argument("--mode", choices=("model", "train"), required=True)
    args = parser.parse_args()

    lines = args.path.read_text(encoding="utf-8").splitlines()
    i = 0
    frame_id = 0
    errors: list[str] = []
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        frame_id += 1
        try:
            atom_count = int(lines[i].strip())
        except ValueError:
            errors.append(f"line {i + 1}: expected atom count")
            break
        if i + 1 >= len(lines):
            errors.append(f"frame {frame_id}: missing header line")
            break
        header = lines[i + 1].strip()
        header_map = parse_header(header)
        atom_lines = lines[i + 2 : i + 2 + atom_count]
        errors.extend(validate_frame(atom_count, header_map, atom_lines, args.mode, frame_id))
        i += atom_count + 2

    if errors:
        print("validation failed", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1

    print(f"{args.path}: {frame_id} frame(s) validated successfully in {args.mode} mode")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
