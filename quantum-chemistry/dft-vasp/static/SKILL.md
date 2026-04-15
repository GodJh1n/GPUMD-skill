---
name: static
description: Prepare VASP static SCF input tasks from a user-provided structure and essential DFT settings. Use when the user needs single-point electronic structure/total-energy calculations with INCAR generation, KSPACING-based k-point policy (or explicit KPOINTS on request), and POTCAR mapping instructions.
compatibility: Requires a user-provided structure and valid VASP pseudopotential resources/license in the target environment.
catalog-hidden: true
license: GPL-3.0-only
metadata:
  author: qqgu
  version: 0.2.0
  repository: https://vasp.at/
---

# VASP Static SCF (Subskill)

## Scope

This skill prepares static SCF tasks only. It generates `POSCAR`, `INCAR`,
optional `KPOINTS`, and POTCAR mapping/assembly instructions. It does not
submit or execute jobs — hand off to `dpdisp-submit` for execution.

## Must provide

- structure input (POSCAR or ase-compatible source)
- `ENCUT` — always set manually (do not rely on default)
- k-point policy (`KSPACING` default or explicit mesh)
- `ISMEAR` / `SIGMA`
- POTCAR mapping for each element (species order must match POSCAR)

## Usually should be explicit

- `EDIFF` (tighten to 1E-6 for NEP labeling, 1E-5 for routine SCF)
- `NELM`, `PREC`, `LREAL`
- `ISPIN` / `MAGMOM` when magnetic
- `IVDW` when vdW is physically relevant

## K-point policy

- default: `KSPACING` in `INCAR` (e.g. `KSPACING = 0.3` ≈ coarse, `0.2` ≈ production)
- generate `KPOINTS` only when user asks for an explicit mesh
- for small cells of semiconductors prefer Γ-centered odd mesh (see example)

## ENCUT selection rule

- Read `ENMAX` from the POTCAR header of every species.
- Baseline: `ENCUT = ceil(max(ENMAX))`. This matches the VASP wiki default.
- For stress / volume optimization or NEP label generation, raise ENCUT to
  `1.3 × max(ENMAX)` to suppress Pulay stress. State the rule explicitly in
  the summary so the user can override.

## ISMEAR / SIGMA selection rule

| System class       | `ISMEAR` | `SIGMA` (eV) | Notes |
|--------------------|:--------:|:------------:|-------|
| Semiconductor / insulator | 0 | 0.05 | Gaussian smearing; check that `T*S` entropy per atom is < 2 meV. |
| Metal (routine SCF) | 1 | 0.2  | Methfessel–Paxton order 1. Do **not** use for DOS. |
| Metal DOS / tetrahedron | −5 | — | Only when the cell has ≥ 4 irreducible k-points and is not needed for forces. |
| Small bandgap / charge trap | 0 | 0.03 | Prevents fractional occupation artefacts. |

## Concrete example — fcc Si SCF (anchored on [VASP wiki: Fcc Si](https://www.vasp.at/wiki/index.php/Fcc_Si))

Task directory layout:

```text
Si_fcc_scf/
├── POSCAR
├── INCAR
├── KPOINTS
└── POTCAR            # concatenated from <POTPAW>/Si/POTCAR
```

`POSCAR` (1-atom primitive, `a = 3.9 Å`, matches the wiki tutorial):

```text
fcc Si
  3.9
    0.5  0.5  0.0
    0.0  0.5  0.5
    0.5  0.0  0.5
Si
  1
Direct
  0.0  0.0  0.0
```

`INCAR` (minimal converged SCF, `ENMAX(Si POTCAR) ≈ 245 eV`):

```text
SYSTEM = fcc Si
ISTART = 0
ICHARG = 2
ENCUT  = 320         # 1.3 × ENMAX for safer volume/stress
PREC   = Accurate
LREAL  = .FALSE.     # reciprocal-space projection for small cells
EDIFF  = 1E-6
NELM   = 60
ISMEAR = 0
SIGMA  = 0.05
LWAVE  = .FALSE.
LCHARG = .FALSE.
```

`KPOINTS` (11×11×11 Γ-centered, 56 irreducible k-points per the wiki):

```text
Automatic mesh
0
Gamma
11 11 11
0  0  0
```

`POTCAR` mapping: `cat <POTPAW>/Si/POTCAR > POTCAR`.

## Physical sanity checks after the run

1. `grep -c 'reached required accuracy' OSZICAR` — **not** needed for SCF;
   instead confirm the final DAV line reports `d E` < `EDIFF`.
2. `grep 'free  energy   TOTEN' OUTCAR | tail -1` — should match the
   `E0` in `OSZICAR` within a few meV.
3. For fcc Si with the 1-atom primitive at `a = 3.9 Å` above, expect
   `E0 ≈ −4.89 eV/atom` (PBE, ENCUT 320, 11×11×11 Γ-centered). Note that
   `a = 3.9 Å` is the wiki's EOS scan starting point, not the PBE equilibrium
   (~3.87 Å). Deviation from −4.89 eV by > 30 meV signals POTCAR or ENCUT mismatch.
4. `grep 'entropy T\*S' OUTCAR | tail -1` — entropy contribution per atom
   must be < 2 meV; otherwise lower `SIGMA` or refine k-mesh.

## Known build traps

- **Non-collinear / SOC jobs require a build without `-DNGXhalf -DNGZhalf`**.
  A standard `vasp_std` build will crash on `LSORBIT = .TRUE.` with
  `ERROR: non collinear calculations require that VASP is compiled without
  the flag -DNGXhalf and -DNGZhalf`. If the user supplies such settings,
  stop and ask them to either switch to a `vasp_ncl` build or drop SOC.
- `LHFCALC = .TRUE.` (hybrid functional) also requires a special build.
- `LREAL = Auto` changes forces slightly; for NEP labeling keep `LREAL = .FALSE.`.

## Expected output

1. task directory with generated input files
2. settings summary (explicit ENCUT rule, smearing rationale)
3. unresolved choices for user confirmation (functional, vdW, spin)
4. physical-sanity-check checklist (see above)
5. handoff note to `dpdisp-submit` if execution is requested
