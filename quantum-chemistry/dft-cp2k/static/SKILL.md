---
name: static
description: Prepare CP2K single-point (static) task inputs from a user-provided structure and essential DFT settings. Use when the user needs total-energy/electronic SCF evaluation with explicit CP2K basis/potential and SCF controls.
compatibility: Requires a user-provided structure, suitable CP2K basis/potential files, and runnable CP2K environment.
license: GPL-3.0-only
catalog-hidden: true
metadata:
  author: qqgu
  version: 0.2.0
  repository: https://github.com/cp2k/cp2k
---

# CP2K Static (Subskill)

## Scope

This skill prepares single-point `RUN_TYPE ENERGY` tasks only. It generates
the CP2K input file, the basis/potential mapping, and `CP2K_DATA_DIR` guidance.
It does not submit or execute jobs — hand off to `dpdisp-submit`.

## Must provide

- structure input (Cartesian Å coordinates and a `CELL` block)
- XC functional (`PBE`, `BLYP`, `SCAN`, `PADE`/LDA, ...)
- basis + GTH pseudopotential pair per element (must match the functional)
- SCF convergence policy (`EPS_SCF`, `MAX_SCF`, OT vs diagonalization)
- `MGRID/CUTOFF` in Ry (plane-wave auxiliary grid for GPW)
- charge / multiplicity / `LSD` flag for open-shell species

## Usually should be explicit

| Tag | Role | Recommended |
|-----|------|-------------|
| `CUTOFF` | auxiliary grid, Ry | 400 for MOLOPT-SR-GTH, 600 for light atoms + accurate forces |
| `REL_CUTOFF` | ratio cutoff | 60 (default); raise if grid warning appears |
| `NGRIDS` | multigrid levels | 4 (default) |
| `EPS_DEFAULT` | global QS tolerance | 1.0E-10 production, 1.0E-8 screening |
| `EPS_SCF` | inner SCF stop | 1.0E-6 production |
| `SCF_GUESS` | starting density | `ATOMIC` (cold start), `RESTART` (chained runs) |
| `OT` | orbital transformation | Always use for insulators (gapped). DIIS + FULL_SINGLE_INVERSE preconditioner is the robust default. |
| `OUTER_SCF` | outer loop for OT | `MAX_SCF = 10, EPS_SCF = 1E-6` |
| `PRINT_LEVEL` | verbosity | `LOW` (routine), `MEDIUM` (debug) |

OT rules of thumb:
- **Molecules / insulators**: always prefer `OT` — faster, no diagonalization.
- **Metals / small-gap systems**: OT cannot handle fractional occupations.
  Use traditional diagonalization with `&SMEAR` and `ADDED_MOS`.
- **Open-shell**: set `LSD .TRUE.` and give a `MULTIPLICITY` hint.

## Basis / potential matching rule

MOLOPT-SR-GTH basis sets are optimized **per functional**. Pair rules:

| Basis family | Potential family | Functional |
|--------------|------------------|------------|
| `DZVP-MOLOPT-SR-GTH`, `TZV2P-MOLOPT-GTH` | `GTH-PBE-qN` | PBE, PBE0, BLYP, SCAN |
| `DZVP-GTH-PADE`, `DZV-GTH-PADE` | `GTH-PADE-qN` | LDA / Pade only |
| `DZVP-MOLOPT-SR-GTH` | `GTH-BLYP-qN` | BLYP (if strict matching is desired) |

Never mix a PADE pseudopotential with a PBE basis, or vice versa — the
valence electron count still works but forces and energies become
inconsistent with the functional.

Data path: the distribution ships `BASIS_MOLOPT`, `GTH_POTENTIALS`,
`BASIS_SET`, `POTENTIAL` under `$CP2K_DATA_DIR` (typically
`$CP2K_PREFIX/share/cp2k/data`). Either set `CP2K_DATA_DIR` in the
environment or give an absolute `BASIS_SET_FILE_NAME` path in the input.

## Concrete example — H₂O single-point (PBE, DZVP-MOLOPT-SR-GTH)

Anchored on the upstream CP2K regression test
`tests/QS/regtest-gpw-1/H2O-noheader.inp` with the modern MOLOPT basis
and PBE functional (the CP2K howto:static_calculation reference setup).

Task directory:

```text
H2O_scf/
├── h2o.inp
└── (output: H2O-1.restart, H2O-1_0.wfn, h2o.out)
```

`h2o.inp`:

```text
&GLOBAL
  PROJECT H2O
  PRINT_LEVEL LOW
  RUN_TYPE ENERGY
&END GLOBAL

&FORCE_EVAL
  METHOD QS
  &DFT
    BASIS_SET_FILE_NAME BASIS_MOLOPT
    POTENTIAL_FILE_NAME GTH_POTENTIALS
    &MGRID
      CUTOFF 400
      REL_CUTOFF 60
      NGRIDS 4
    &END MGRID
    &QS
      EPS_DEFAULT 1.0E-10
    &END QS
    &SCF
      EPS_SCF 1.0E-6
      MAX_SCF 50
      SCF_GUESS ATOMIC
      &OT
        MINIMIZER DIIS
        PRECONDITIONER FULL_SINGLE_INVERSE
      &END OT
      &OUTER_SCF
        EPS_SCF 1.0E-6
        MAX_SCF 10
      &END OUTER_SCF
    &END SCF
    &XC
      &XC_FUNCTIONAL PBE
      &END XC_FUNCTIONAL
    &END XC
  &END DFT
  &SUBSYS
    &CELL
      ABC 10.0 10.0 10.0
      PERIODIC XYZ
    &END CELL
    &COORD
      O   0.000000    0.000000   -0.065587
      H   0.000000   -0.757136    0.520545
      H   0.000000    0.757136    0.520545
    &END COORD
    &KIND H
      BASIS_SET DZVP-MOLOPT-SR-GTH
      POTENTIAL GTH-PBE-q1
    &END KIND
    &KIND O
      BASIS_SET DZVP-MOLOPT-SR-GTH
      POTENTIAL GTH-PBE-q6
    &END KIND
  &END SUBSYS
&END FORCE_EVAL
```

Run (single-thread SMP binary):

```bash
export CP2K_DATA_DIR=$CONDA_PREFIX/share/cp2k/data   # or path to your build
cp2k.ssmp -i h2o.inp -o h2o.out
```

## Physical sanity checks after the run

1. `grep 'SCF run converged' h2o.out` — must report `SCF run converged in N steps`.
   For the H₂O example above expect **~16 inner steps** (OT + DIIS) and
   a single outer SCF iteration.
2. `grep 'ENERGY| Total' h2o.out` — total `FORCE_EVAL ( QS )` energy.
   For the H₂O example (PBE + DZVP-MOLOPT-SR-GTH, CUTOFF 400, 10 Å cubic
   box) the reference value is **−17.2196 Hartree ≈ −468.43 eV**. A drift
   > 1 mHa usually means CUTOFF is too low or the basis/functional do not
   match.
3. `grep 'Number of electrons' h2o.out` — must equal the GTH valence sum
   (H₂O: 2 × 1 + 6 = **8**). Mismatches indicate a wrong `-qN` potential
   choice.
4. `grep 'REL_CUTOFF' h2o.out` and check the printed grid distribution —
   if the finest grid holds < 50 % of the Gaussians, raise `CUTOFF` (not
   `REL_CUTOFF`).

## Known build traps

- `OT` + metal (small-gap Cu, graphene, ...) fails to converge or converges
  to a wrong density. Switch to `&SCF / DIAGONALIZATION` with `&SMEAR` and
  set `ADDED_MOS` to 2 × occupied.
- Periodic jobs with a **too-small cell** for a molecule (`< 6 Å` vacuum)
  have significant periodic-image interaction — for dipolar solutes use
  `POISSON / PERIODIC NONE / PSOLVER MT` or grow the box.
- `BASIS_SET_FILE_NAME` using a relative name requires `CP2K_DATA_DIR` to
  point at the directory that *contains* the file. A common error is to
  point it at the parent `share/cp2k-<version>` instead of
  `share/cp2k/data`; the error message prints the failed path literally,
  which is the quickest way to diagnose.
- Hybrid functionals (`PBE0`, `HSE06`) need auxiliary fit basis
  (`FIT3`/`FIT4` in `BASIS_ADMM`) and the `&AUXILIARY_DENSITY_MATRIX_METHOD`
  block — out of scope for the plain-GGA static skill.

## Expected output

1. static-task directory with `.inp` file and data-dir guidance
2. basis / potential mapping summary (must justify each pair)
3. settings summary (`CUTOFF` rationale, OT vs DIAG choice)
4. sanity-check checklist (SCF steps, total energy, electron count)
5. handoff note to `dpdisp-submit`
