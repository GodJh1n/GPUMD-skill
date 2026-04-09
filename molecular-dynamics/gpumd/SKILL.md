---
name: gpumd
description: Route GPUMD requests to task-specific subskills based on user intent. Use when the user asks for GPUMD molecular dynamics, `model.xyz`, `run.in`, phonon dispersion via `compute_phonon`, thermal transport via EMD/HNEMD/NEMD, or GPUMD output interpretation.
compatibility: Requires a runnable GPUMD environment, or a user-provided executable/module/container path for `gpumd`.
license: LGPL-3.0-or-later
metadata:
  author: Codex
  version: 0.1.0
  repository: https://github.com/brucefan1983/GPUMD
---

# GPUMD Task Router

Use this skill as the top-level routing layer for GPUMD work.

## Purpose

This router chooses one GPUMD subskill path:

- `gpumd/md`
- `gpumd/phonon`
- `gpumd/transport`

## Scope

This router should:

- classify the request into one GPUMD workflow
- collect only the shared physical context needed before dispatch
- point the agent to the right bundled references, templates, and scripts
- keep method selection scientifically consistent

This router should not:

- collapse all GPUMD logic into one response
- mix phonon and transport guardrails into a generic MD answer
- skip convergence and validity checks when a property calculation is requested

## Routing rules

1. If the user wants a GPUMD MD input, ensemble setup, `model.xyz`, `run.in`, restart logic, or trajectory output, route to `gpumd/md`.
1. If the user wants harmonic phonons, `compute_phonon`, `kpoints.in`, `omega2.out`, or phonon dispersion, route to `gpumd/phonon`.
1. If the user wants thermal conductivity, heat-current autocorrelation, HNEMD, NEMD, SHC, or transport post-processing, route to `gpumd/transport`.
1. If the request spans more than one area, start from the dominant goal and load only the extra reference files that are needed.

## Shared policy for all GPUMD subskills

- Do not invent missing physical parameters.
- Validate `model.xyz` and extxyz headers before trusting downstream runs.
- Keep the timestep, ensemble, and target observable physically consistent.
- Treat transport results as provisional until size, sampling, and method-specific convergence are discussed.
- For low-dimensional materials, require an explicit thickness convention before reporting conductivity in bulk units.

## Resource map

- Core files and ensemble rules: `references/core-files-and-ensembles.md`
- Phonon workflow notes: `references/phonon-workflow.md`
- Thermal-transport workflow notes: `references/thermal-transport-workflow.md`
- Local tutorial index: `references/tutorial-map.md`
- Small reusable templates: `assets/examples/`
- Deterministic helpers: `scripts/average_hnemd_kappa.py`, `scripts/validate_extxyz_headers.py`

