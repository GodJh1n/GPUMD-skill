#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path


def discover_roots(cwd: Path) -> dict[str, list[Path]]:
    candidates = {
        "tutorial": [
            cwd / "gpumd-tool-sources" / "GPUMD-Tutorials",
            cwd.parent / "GPUMD-Tutorials-main",
        ],
        "gpumd": [
            cwd / "gpumd-tool-sources" / "GPUMD",
        ],
        "tool": [
            cwd / "gpumd-tool-sources" / "GPUMD" / "tools",
        ],
    }
    existing: dict[str, list[Path]] = {}
    for key, paths in candidates.items():
        existing[key] = [path for path in paths if path.exists()]
    return existing


def iter_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file()]


def score_path(path: Path, query_terms: list[str]) -> int:
    haystack = str(path).lower()
    return sum(term in haystack for term in query_terms)


def main() -> int:
    parser = argparse.ArgumentParser(description="Search local GPUMD, tutorial, and tool-source trees.")
    parser.add_argument("query", nargs="+", help="Search terms")
    parser.add_argument(
        "--category",
        choices=("all", "tutorial", "gpumd", "tool"),
        default="all",
        help="Restrict search to one source category",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=30,
        help="Maximum number of matches to print",
    )
    args = parser.parse_args()

    cwd = Path.cwd()
    roots = discover_roots(cwd)
    categories = roots.keys() if args.category == "all" else [args.category]
    query_terms = [term.lower() for term in args.query]

    matches: list[tuple[str, int, Path]] = []
    for category in categories:
        for root in roots.get(category, []):
            for path in iter_files(root):
                score = score_path(path, query_terms)
                if score:
                    matches.append((category, score, path))

    if not matches:
        print("no local matches found")
        return 1

    matches.sort(key=lambda item: (-item[1], str(item[2])))
    for category, score, path in matches[: args.limit]:
        print(f"[{category}] score={score} {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

