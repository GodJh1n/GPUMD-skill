#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml",
# ]
# ///
"""
Generate/update README skills summary from tracked SKILL.md files.

Discovery: ``git ls-files`` (falls back to glob excluding gpumd-tool-sources/).
Grouping:  hardcoded path-prefix mapping.
Output:    managed blocks in README.md delimited by HTML comment markers.
"""

from __future__ import annotations

import re
import subprocess
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

TABLE_START = "<!-- SKILLS_TABLE_START -->"
TABLE_END = "<!-- SKILLS_TABLE_END -->"
BADGE_START = "<!-- SKILLS_BADGE_START -->"
BADGE_END = "<!-- SKILLS_BADGE_END -->"


# ── Skill entry ──────────────────────────────────────────────────────


@dataclass
class Skill:
    name: str
    description: str
    version: str
    compatibility: str
    rel_path: str
    catalog_hidden: bool


# ── Frontmatter parsing ─────────────────────────────────────────────


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---\n"):
        return {}
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    data = yaml.safe_load(m.group(1)) or {}
    return data if isinstance(data, dict) else {}


def to_skill(fm: dict, rel_path: str) -> Skill:
    name = str(fm.get("name") or Path(rel_path).parent.name)
    md = fm.get("metadata")
    version = (
        str(md["version"]).strip()
        if isinstance(md, dict) and md.get("version") is not None
        else "-"
    )
    desc = str(fm.get("description") or "").replace("\n", " ").strip()
    compat = fm.get("compatibility")
    compat = compat.strip() if isinstance(compat, str) and compat.strip() else "-"
    hidden = fm.get("catalog-hidden", False)
    if isinstance(hidden, str):
        hidden = hidden.strip().lower() in {"1", "true", "yes", "on"}
    return Skill(name, desc, version, compat, rel_path, bool(hidden))


# ── Discovery ────────────────────────────────────────────────────────


def discover() -> list[str]:
    """Return sorted repo-relative paths of tracked SKILL.md files."""
    try:
        proc = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        paths = [
            p
            for p in proc.stdout.strip().splitlines()
            if p.endswith("SKILL.md")
        ]
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback: glob excluding gpumd-tool-sources
        paths = sorted(
            str(p.relative_to(ROOT))
            for p in ROOT.glob("**/SKILL.md")
            if "gpumd-tool-sources" not in str(p)
        )
    return sorted(paths)


# ── Group routing ────────────────────────────────────────────────────

TOP_LEVEL = {
    "molecular-dynamics/gpumd/SKILL.md",
    "machine-learning-potentials/nep-gpumd/SKILL.md",
    "tools/gpumd-tools/SKILL.md",
}

# (group_id, prefix, paths_to_exclude)
PREFIX_RULES: list[tuple[str, str, set[str]]] = [
    ("gpumd-sub", "molecular-dynamics/gpumd/", TOP_LEVEL),
    ("nep-sub", "machine-learning-potentials/nep-gpumd/", TOP_LEVEL),
    ("dft", "quantum-chemistry/", set()),
    ("analysis", "analysis/", set()),
    ("data-processing", "data-processing/", set()),
    ("tools", "tools/", TOP_LEVEL),
    ("workflow", "agent-workflow/", set()),
]


def classify(rel_path: str) -> str:
    """Return the group id for a SKILL.md path, or '' if unrecognized."""
    if rel_path in TOP_LEVEL:
        return "top-level"
    for gid, prefix, excl in PREFIX_RULES:
        if rel_path.startswith(prefix) and rel_path not in excl:
            return gid
    return ""


# ── Table builders ───────────────────────────────────────────────────


def _esc(s: str) -> str:
    return s.replace("|", "\\|") or "-"


def _link(s: Skill) -> str:
    return f"[{s.name}]({s.rel_path})"


def table_full(skills: list[Skill]) -> str:
    """4-column: Skill | Description | Version | Compatibility."""
    rows = [
        "| Skill | Description | Version | Compatibility |",
        "| --- | --- | --- | --- |",
    ]
    for s in skills:
        rows.append(
            f"| {_link(s)} | {_esc(s.description)} "
            f"| {_esc(s.version)} | {_esc(s.compatibility)} |"
        )
    return "\n".join(rows)


def table_compact(skills: list[Skill]) -> str:
    """2-column: Skill | Description."""
    rows = [
        "| Skill | Description |",
        "| --- | --- |",
    ]
    for s in skills:
        rows.append(f"| {_link(s)} | {_esc(s.description)} |")
    return "\n".join(rows)


def table_with_subskills(skills: list[Skill]) -> str:
    """3-column: Skill | Description | Subskills (auto-detected)."""
    rows = [
        "| Skill | Description | Subskills |",
        "| --- | --- | --- |",
    ]
    for s in skills:
        parent = (ROOT / s.rel_path).parent
        subs = sorted(
            d.name
            for d in parent.iterdir()
            if d.is_dir() and (d / "SKILL.md").is_file()
        )
        sub_str = ", ".join(subs) if subs else "\u2014"
        rows.append(f"| {_link(s)} | {_esc(s.description)} | {sub_str} |")
    return "\n".join(rows)


# ── Section assembly ─────────────────────────────────────────────────

# (heading, table_style)
SECTIONS: OrderedDict[str, tuple[str, str]] = OrderedDict(
    [
        ("top-level", ("### Top-level skills", "full")),
        ("gpumd-sub", ("### GPUMD subskills", "full")),
        ("nep-sub", ("### NEP subskills", "full")),
        ("dft", ("### DFT skills (quantum-chemistry)", "subskills")),
        ("analysis", ("### Analysis skills", "compact")),
        ("data-processing", ("### Data-processing skills", "compact")),
        ("tools", ("### Additional tools", "compact")),
        ("workflow", ("### Workflow orchestration", "compact")),
    ]
)

TABLE_FN = {
    "full": table_full,
    "compact": table_compact,
    "subskills": table_with_subskills,
}

# Groups where catalog-hidden entries are suppressed.
# GPUMD and NEP subskill sections show all entries regardless of hidden flag.
RESPECT_HIDDEN = {
    "top-level",
    "dft",
    "analysis",
    "data-processing",
    "tools",
    "workflow",
}


def build_section(groups: dict[str, list[Skill]]) -> str:
    parts: list[str] = ["## Skills summary\n"]
    for gid, (heading, style) in SECTIONS.items():
        skills = groups.get(gid, [])
        if not skills:
            continue
        table = TABLE_FN[style](skills)
        parts.append(f"{heading}\n\n{table}\n")
    return "\n".join(parts)


def build_badge(total: int) -> str:
    return (
        "[![Skills]"
        f"(https://img.shields.io/badge/skills-{total}-blue?style=for-the-badge)]"
        "(#skills-summary)"
    )


# ── Marker update ────────────────────────────────────────────────────


def update_block(content: str, start: str, end: str, body: str) -> str:
    wrapped = f"{start}\n{body}\n{end}"
    pat = re.compile(rf"{re.escape(start)}.*?{re.escape(end)}", re.S)
    if pat.search(content):
        return pat.sub(wrapped, content)
    # Markers missing — append (should not happen if README is prepared).
    return content.rstrip("\n") + "\n\n" + wrapped + "\n"


# ── Main ─────────────────────────────────────────────────────────────


def main() -> int:
    paths = discover()

    groups: dict[str, list[Skill]] = {gid: [] for gid in SECTIONS}
    total = 0

    for rel in paths:
        fp = ROOT / rel
        if not fp.is_file():
            continue
        fm = parse_frontmatter(fp.read_text(encoding="utf-8", errors="replace"))
        skill = to_skill(fm, rel)
        total += 1

        gid = classify(rel)
        if not gid:
            continue
        if gid in RESPECT_HIDDEN and skill.catalog_hidden:
            continue
        groups[gid].append(skill)

    badge = build_badge(total)
    section = build_section(groups)

    text = (
        README.read_text(encoding="utf-8", errors="replace")
        if README.exists()
        else "# GPUMD Agent Skills\n"
    )
    text = update_block(text, BADGE_START, BADGE_END, badge)
    text = update_block(text, TABLE_START, TABLE_END, section)
    README.write_text(text, encoding="utf-8")

    visible = sum(len(v) for v in groups.values())
    print(f"Updated {README}: {total} tracked SKILL.md, {visible} visible in table")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
