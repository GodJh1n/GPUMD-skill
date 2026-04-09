---
name: md
description: Prepare and explain GPUMD molecular-dynamics inputs from a structure, potential, and target ensemble. Use when the user needs `model.xyz`, `run.in`, equilibrium MD, melting, diffusion, viscosity, or general GPUMD trajectory generation.
compatibility: Requires GPUMD and a valid potential file such as `nep.txt`, `nep89_*.txt`, or another GPUMD-supported potential.
catalog-hidden: true
license: LGPL-3.0-or-later
metadata:
  author: Codex
  version: 0.1.0
---

# GPUMD MD

## Scope

Use this subskill for ordinary GPUMD molecular dynamics.

It should prepare or explain:

- `model.xyz`
- `run.in`
- ensemble selection
- timestep and dump policy
- expected outputs such as `thermo.out` and `movie.xyz`

It should not own:

- harmonic phonon workflows
- thermal-transport method selection
- NEP training logic

## Read first

- `references/core-files-and-ensembles.md`

Read when needed:

- `references/tutorial-map.md`

## Bundled templates

- `assets/examples/minimal/model.xyz`
- `assets/examples/minimal/run.in`

## Expected output

1. a physically consistent `model.xyz` or conversion plan
1. a GPUMD `run.in` matched to the requested ensemble and observable
1. assumptions about timestep, thermostat/barostat, and production length
1. a note on what outputs will be used for validation

