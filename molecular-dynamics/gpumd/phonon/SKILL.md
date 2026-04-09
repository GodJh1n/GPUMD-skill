---
name: phonon
description: Prepare GPUMD phonon-dispersion and lattice-dynamics workflows using `compute_phonon`, `kpoints.in`, and supercell replication. Use when the user needs harmonic phonons, `omega2.out`, `D.out`, or a GPUMD-based starting point for lattice-dynamics analysis.
compatibility: Requires GPUMD and a structure/potential suitable for finite-displacement phonon calculations.
catalog-hidden: true
license: LGPL-3.0-or-later
metadata:
  author: Codex
  version: 0.1.0
---

# GPUMD Phonon

## Scope

Use this subskill for GPUMD harmonic phonon workflows and adjacent lattice-dynamics setup.

It should prepare:

- primitive or supercell `model.xyz`
- `kpoints.in`
- `run.in` with `replicate` and `compute_phonon`
- convergence notes for displacement amplitude and supercell size

It should not:

- treat a single unconverged dispersion as publishable
- conflate harmonic dispersion with full lattice thermal conductivity

## Read first

- `references/phonon-workflow.md`

Read when needed:

- `references/core-files-and-ensembles.md`
- `references/tutorial-map.md`

## Bundled templates

- `assets/examples/phonon/model.xyz`
- `assets/examples/phonon/run.in`
- `assets/examples/phonon/kpoints.in`

## Expected output

1. a phonon-ready GPUMD input set
1. a convergence checklist for supercell and displacement size
1. the expected outputs and how they will be checked

