---
name: relax
description: Prepare VASP geometry-relaxation input tasks from a user-provided structure and essential DFT settings. Use when the user needs ionic or cell-coupled relaxation and requires explicit ISIF-driven relaxation intent mapping, INCAR generation, and POTCAR mapping instructions.
compatibility: Requires a user-provided structure and valid VASP pseudopotential resources/license in the target environment.
catalog-hidden: true
license: GPL-3.0-only
metadata:
  author: qqgu
  version: 0.2.0
  repository: https://vasp.at/
---

# VASP Relaxation (Subskill)

## Scope

This skill prepares relaxation tasks only. It generates `POSCAR`, `INCAR`,
optional `KPOINTS`, and POTCAR mapping instructions. It does not submit or
execute jobs — hand off to `dpdisp-submit`.

## Relaxation intent is mandatory

Before assigning `ISIF`, classify user intent. The canonical
[VASP wiki ISIF table](https://www.vasp.at/wiki/index.php/ISIF):

| `ISIF` | Positions | Cell shape | Cell volume | Typical use |
|:------:|:---------:|:----------:|:-----------:|-------------|
| **2** | yes | no  | no  | Ion-only relax at fixed cell (defects, surfaces with frozen vectors) |
| **3** | yes | yes | yes | **Full** cell+ion relax — bulk equilibrium |
| **4** | yes | yes | no  | Cell-shape+ion relax at fixed volume (non-cubic phase search) |
| **5** | yes | yes | no  | Like 4 but no stress check |
| **6** | no  | yes | yes | Cell shape + volume, atoms frozen in direct coordinates |
| **7** | no  | no  | yes | Volume-only (isotropic scan, rarely used directly) |

If intent is ambiguous, ask the user for clarification.

## Must provide

- structure input (POSCAR)
- `ENCUT` (see "ENCUT for relaxation" below)
- `ISMEAR` / `SIGMA` (use the static/SCF table from `dft-vasp/static`)
- relaxation controls: `IBRION`, `NSW`, `EDIFFG`, `ISIF`
- k-point policy (`KSPACING` or explicit `KPOINTS`)
- POTCAR mapping per element

## Usually should be explicit

- `EDIFF` (1E-6 for NEP labeling seed structures, 1E-5 otherwise)
- `NELM` (60 default; raise to 100 if SCF struggles)
- `PREC = Accurate` (required when any cell-DOF is relaxed)
- `POTIM` (see "Algorithm selection")
- `LREAL = .FALSE.` (small cells) or `Auto` (> 30 atoms)
- `ISPIN` / `MAGMOM` when magnetic
- `IVDW` when vdW is physically relevant

## ENCUT for relaxation

- **Cell-DOF relaxations (`ISIF ∈ {3,4,5,6,7,8}`) must use `ENCUT = 1.3 × max(ENMAX)`**
  to suppress Pulay stress. This is a physical requirement, not a convention:
  Pulay stress biases the cell toward smaller volumes when the plane-wave
  basis set adapts to a changing cell. 30% headroom is the community
  standard that makes this bias smaller than typical `EDIFFG`.
- Ion-only relaxations (`ISIF = 2`) can use `ENCUT = max(ENMAX)`.

## Algorithm selection (`IBRION` / `POTIM`)

Based on [VASP wiki IBRION](https://www.vasp.at/wiki/index.php/IBRION):

| `IBRION` | Algorithm | When to pick | `POTIM` |
|:--------:|-----------|--------------|:-------:|
| **2** | Conjugate gradient | Robust default. Pick first. | 0.5 |
| **1** | RMM-DIIS quasi-Newton | > 20 DOF and already near the minimum | 0.5 |
| **3** | Damped MD | Large systems far from the minimum | 0.1 |

Rule of thumb: start with `IBRION=2`, only switch to 1 if CG stalls after
~10 NSW steps, and only use 3 when a structure came from a non-VASP source
(force field, cif with bad geometry).

## `EDIFFG` convention

- Negative value → force criterion in eV/Å (recommended). `-1E-2` for
  quick screening, `-1E-3` for production, `-5E-4` for phonon seeds.
- Positive value → total energy change in eV. Weaker physical meaning,
  discouraged unless the system has phonon-soft modes.

## Concrete example — fcc Si full cell+ion relax

Anchored on [VASP wiki Fcc Si](https://www.vasp.at/wiki/index.php/Fcc_Si).
The 1-atom primitive cell has no internal ion DOF, so `ISIF=3` only relaxes
the lattice constant — this is the minimal useful relaxation test.

Task directory:

```text
Si_fcc_relax/
├── POSCAR
├── INCAR
├── KPOINTS
└── POTCAR            # cat <POTPAW>/Si/POTCAR
```

`POSCAR` (start `a = 3.9 Å` — the VASP wiki EOS scan starting point):

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

`INCAR`:

```text
SYSTEM = fcc Si relax
ISTART = 0
ICHARG = 2
ENCUT  = 320          # 1.3 × ENMAX(Si) = 1.3 × 245 ≈ 320 (Pulay headroom)
PREC   = Accurate
LREAL  = .FALSE.
EDIFF  = 1E-6
EDIFFG = -1E-3        # force threshold 1 meV/Å
NELM   = 60
ISMEAR = 0
SIGMA  = 0.05
IBRION = 2            # CG
ISIF   = 3            # cell + ion (ion is symmetry-locked for Si primitive)
NSW    = 40
POTIM  = 0.5
LWAVE  = .FALSE.
LCHARG = .FALSE.
```

`KPOINTS`: same 11×11×11 Γ-centered mesh as the static SCF example.

## Physical sanity checks after the run

1. `grep 'reached required accuracy' OUTCAR` — one line means converged.
2. `grep '  volume of cell' OUTCAR | tail -1` — for this **fcc 1-atom-primitive**
   Si test (the VASP wiki EOS toy model, **not** real diamond Si), PBE
   equilibrium volume is ≈ 14.5 Å³/atom, corresponding to `a ≈ 3.87 Å` in
   the fcc-primitive convention. Deviation > 0.3 Å³ signals ENCUT too low
   or k-mesh too coarse. *(Real diamond Si with 2 atoms/primitive has PBE
   volume ≈ 20.4 Å³/atom and `a_conv ≈ 5.47 Å` — a different POSCAR.)*
3. `grep 'external pressure' OUTCAR | tail -1` — residual |pressure| < 1 kBar.
4. `grep 'TOTEN' OUTCAR | tail -1` — final energy lower than the starting
   SCF energy by ~3–10 meV/atom (the Pulay contraction).
5. **Pulay check**: rerun the final geometry as a static SCF at the same
   ENCUT. If the static TOTEN differs from the relax TOTEN by > 1 meV/atom,
   the relax ENCUT was still too low — raise it and repeat.

## Slab / low-dimensional policy

- For slabs, **never use `ISIF=3`**: the vacuum axis collapses.
- Use `ISIF=2` with selective dynamics in POSCAR to freeze bottom layers,
  or `ISIF=4` if you want to allow in-plane lattice rebuild while keeping
  the vacuum thickness.
- For 2D heterobilayers (e.g. the Bi/MoS₂ case used by the GPUMD skill
  family), `LDIPOL=.TRUE.` + `IDIPOL=3` is recommended to remove spurious
  dipole interaction across the vacuum.

## Known build traps

- Non-collinear/SOC (`LSORBIT=.TRUE.`) requires a non-`NGXhalf` build.
  The standard `vasp_std` will crash — see `dft-vasp/static` for details.
- `IBRION=5/6/7/8` (DFPT phonons) require additional settings — they are
  out of scope for this relaxation skill.

## Expected output

1. task directory with generated input files
2. explicit `ISIF` selection rationale (quote the table row)
3. ENCUT + Pulay rationale
4. physical sanity check checklist
5. unresolved choices (functional, vdW, spin)
6. handoff note to `dpdisp-submit`
