---
name: gpumd-tools
description: Tooling layer for GPUMD helper repositories and local example discovery. Use when the user needs GPUMDkit, upstream `GPUMD/tools`, GPUMD-Tutorials lookup, format conversion into GPUMD/NEP extxyz, or bootstrapping the local GPUMD tool-source ecosystem.
compatibility: Optional local checkouts of GPUMD, GPUMD-Tutorials, GPUMDkit, NepTrain, and NepTrainKit. If absent, use the bundled bootstrap script to clone them.
license: LGPL-3.0-or-later
metadata:
  author: Codex
  version: 0.1.0
---

# GPUMD Tooling

Use this skill when the task is primarily about auxiliary tooling rather than GPUMD physics or NEP fitting alone.

## Source priority

When tools disagree or wrappers hide details, follow this order:

1. current official GPUMD documentation
1. the upstream script or README in `GPUMD/tools`
1. GPUMDkit wrapper behavior
1. tutorial notebooks and third-party blog posts

## Read only what is needed

- Tool inventory and when to use each layer: `references/tool-catalog.md`
- DFT-to-extxyz conversion and dataset assembly: `references/format-conversion-and-dataset-assembly.md`
- High-value example map from GPUMD-Tutorials: `references/tutorial-and-workflow-map.md`

## Bundled scripts

- `scripts/bootstrap_gpumd_tool_sources.sh`
- `scripts/index_local_gpumd_sources.py`

## Working rules

- Prefer lightweight upstream scripts when the transformation is simple and deterministic.
- Prefer GPUMDkit when a wrapper already exists and its assumptions match the task.
- Use tutorial examples as seeds, not as unquestioned canonical inputs.
- Do not silently mix datasets converted with incompatible energy or virial conventions.

