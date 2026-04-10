---
name: phonon
description: >
  Prepare GPUMD harmonic phonon-dispersion calculations using `compute_phonon`,
  `kpoints.in`, and supercell replication. Use when the user needs harmonic
  phonons, `omega2.out`, `D.out`, phonon DOS, or a GPUMD-based starting point
  for lattice-dynamics analysis.
compatibility: >
  Requires GPUMD and a potential stable for the target crystalline structure.
  For DOS workflows, also supports `compute_dos` from NVE trajectories.
catalog-hidden: true
license: LGPL-3.0-or-later
metadata:
  author: Codex
  version: 0.2.0
---

# GPUMD Phonon

Use this subskill for GPUMD harmonic phonon-dispersion, phonon-DOS, and
adjacent lattice-dynamics setup.

## Quick start

```bash
gpumd < run.in | tee gpumd.log
python -c "import numpy as np; print(np.loadtxt('omega2.out').shape)"
```

## Agent responsibilities

1. Confirm the user really wants harmonic phonons and not thermal transport.
   If the user asks about `kappa`, route to `gpumd/transport` instead.
2. Confirm the input structure is **relaxed under the chosen potential**.
   Unrelaxed structures produce misleading imaginary modes.
3. Ask for supercell size and displacement amplitude, or pick conservative
   defaults and state them.
4. Write `model.xyz`, `run.in`, and (if needed) `kpoints.in` yourself.
5. Explain convergence expectations before the user takes the result as final.

## Workflow

### Step 1. Start from a relaxed structure

If the user has not yet relaxed the geometry under the same potential, do that
first in the `gpumd/md` subskill using a small NPT segment followed by
structure extraction, or call an external relaxation tool.

### Step 2. Write `run.in`

Annotated minimal example for silicon (see
[assets/examples/phonon/run.in](../assets/examples/phonon/run.in)):

```text
potential       Si_Fan_2019.txt
replicate       8 8 8
compute_phonon  5 0.005
```

- `potential Si_Fan_2019.txt`
  - Loads the stable potential. Use the exact filename shipped with the user's
    tutorial or NEP fit.
- `replicate 8 8 8`
  - Builds the supercell from the primitive cell stored in `model.xyz`. The
    supercell must be large enough to contain the physically relevant range of
    the interatomic force constants. Increase until the dispersion stops
    changing.
- `compute_phonon 5 0.005`
  - `5` = cutoff in Å used when collecting pairwise force-constant
    contributions.
  - `0.005` = finite-displacement amplitude in Å. `0.005-0.01 Å` is the
    conservative starting range.

If a band-structure path is requested, also supply `kpoints.in` (see below).

### Step 3. Write `kpoints.in`

Each non-blank line contains three fractional coordinates and one label:

```text
0.000 0.000 0.000 G
0.500 0.000 0.500 X
0.375 0.375 0.750 K
0.000 0.000 0.000 G
0.500 0.500 0.500 L
```

Use blank lines between path segments that should not be joined.

### Step 4. Run and inspect

```bash
gpumd < run.in | tee gpumd.log
```

Primary outputs:

- `D.out` — dynamical matrix
- `omega2.out` — squared frequencies along `kpoints.in`

Interpretation:

- negative `omega^2` corresponds to imaginary frequencies
- persistent imaginary branches can indicate a true structural instability OR
  poor relaxation / convergence — never report without cross-checking

### Step 5. Converge

Do at least one convergence pass on:

- supercell size (`replicate`)
- displacement amplitude (`compute_phonon` second argument)
- force cutoff (`compute_phonon` first argument)

## Phonon DOS via NVE trajectory

For a vibrational density of states from direct velocity autocorrelation (no
finite displacements), use `compute_dos` during an NVE run:

```text
potential   nep.txt
velocity    300
time_step   1
ensemble    npt_ber 300 300 100 0 0 0 100 100 100 1000
run         20000

ensemble    nve
compute_dos 5 200 400.0
dump_thermo 100
run         40000
```

The `compute_dos` arguments are the VAC sampling interval, the number of time
correlation points, and the maximum frequency in THz. See the GPUMD docs for
the exact current meaning.

## Convergence checklist

- [ ] structure was relaxed under the same potential
- [ ] at least one larger supercell tested for the same dispersion
- [ ] displacement amplitude tested in the `0.005-0.01 Å` range
- [ ] Γ-point acoustic modes approach zero (not a large imaginary value)
- [ ] potential stability confirmed in a short NVE sanity run

## What this subskill does NOT own

- lattice thermal conductivity → `gpumd/transport`
- fitted IFC (`fc2`, `fc3`) and anharmonic transport → outside bare
  `compute_phonon`; point the user to
  [references/phonon-workflow.md](../references/phonon-workflow.md) and the
  external `25_lattice_dynamics_kappa` tutorial.

## Read first

- [references/phonon-workflow.md](../references/phonon-workflow.md)

Read when needed:

- [references/core-files-and-ensembles.md](../references/core-files-and-ensembles.md)
- [references/gpumd-keyword-cheatsheet.md](../references/gpumd-keyword-cheatsheet.md)
- [references/tutorial-map.md](../references/tutorial-map.md)

## Bundled templates

- [assets/examples/phonon/model.xyz](../assets/examples/phonon/model.xyz)
- [assets/examples/phonon/run.in](../assets/examples/phonon/run.in)
- [assets/examples/phonon/kpoints.in](../assets/examples/phonon/kpoints.in)

## Expected output

1. a phonon-ready GPUMD input set
2. a convergence checklist for supercell size and displacement amplitude
3. the expected output files and how they will be checked

## References

- `compute_phonon`: <https://gpumd.org/gpumd/input_parameters/compute_phonon.html>
- `compute_dos`: <https://gpumd.org/gpumd/input_parameters/compute_dos.html>
- GPUMD-Tutorials example `06_Silicon_phonon_dispersion`
- GPUMD-Tutorials example `02_Carbon_density_of_states`
