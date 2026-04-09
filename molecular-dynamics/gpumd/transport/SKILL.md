---
name: transport
description: Prepare GPUMD thermal-transport workflows for EMD, HNEMD, or NEMD-style studies. Use when the user needs `compute_hac`, `compute_hnemd`, `compute_shc`, conductivity extraction, or transport-specific sampling and convergence guidance.
compatibility: Requires GPUMD and a structure/potential for nonequilibrium or equilibrium transport calculations.
catalog-hidden: true
license: LGPL-3.0-or-later
metadata:
  author: Codex
  version: 0.1.0
---

# GPUMD Transport

## Scope

Use this subskill for thermal-transport calculations in GPUMD.

It should choose and prepare among:

- EMD / Green-Kubo via `compute_hac`
- HNEMD via `compute_hnemd`
- NEMD or spectral workflows when explicitly requested

It should enforce:

- correct ensemble choice for each method
- linear-response checks for HNEMD
- size, seed, and sampling discussions before strong conclusions are made

## Read first

- `references/thermal-transport-workflow.md`

Read when needed:

- `references/core-files-and-ensembles.md`
- `references/tutorial-map.md`

## Bundled templates and helpers

- `assets/examples/transport/emd/run.in`
- `assets/examples/transport/hnemd/run.in`
- `scripts/average_hnemd_kappa.py`

## Expected output

1. a transport-specific GPUMD input template
1. a statement of the method choice and why it fits the target observable
1. explicit convergence and reporting caveats

