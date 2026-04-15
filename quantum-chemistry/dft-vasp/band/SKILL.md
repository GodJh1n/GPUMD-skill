---
name: band
description: Prepare VASP band-structure workflow inputs from existing SCF context and user-specified band-path settings. Use when the user requests electronic band-structure calculations and needs explicit prerequisite checks, line-mode KPOINTS path setup, and stage-specific INCAR preparation.
compatibility: Requires prerequisite SCF context and valid VASP pseudopotential resources/license in the target environment.
catalog-hidden: true
license: GPL-3.0-only
metadata:
  author: qqgu
  version: 0.2.0
  repository: https://vasp.at/
---

# VASP Band Preparation (Subskill)

## Scope

This skill prepares band-structure-stage input tasks only. It verifies
prerequisite SCF context, generates line-mode `KPOINTS`, and prepares a
stage-appropriate `INCAR`. It does not submit or execute jobs.

## Two-step workflow (canonical)

Per [VASP wiki Fcc_Si_bandstructure](https://www.vasp.at/wiki/index.php/Fcc_Si_bandstructure):

1. **Step 1 — SCF** with `LCHARG = .TRUE.` on a regular Monkhorst–Pack
   / Γ-centered mesh (done by `dft-vasp/static`).
2. **Step 2 — Band** (this skill): fix the charge density (`ICHARG = 11`),
   sample along a high-symmetry path using line-mode `KPOINTS`, and use
   Gaussian smearing (`ISMEAR = 0`) — **not tetrahedron**, because line-mode
   meshes are not suitable for tetrahedron integration.

> VASP wiki: *"This calculation needs a converged charge density as input
> (ICHARG=11)."*

## Prerequisites (hard)

- `CHGCAR` (non-empty) from a prior SCF/DOS run
- same `POSCAR`, `POTCAR`, `ENCUT`, `PREC`, `GGA` as the prerequisite SCF
- the prior SCF ran with `LCHARG = .TRUE.`

If any of these is missing, stop and ask.

## Must provide

- source SCF context path (verify the four items above)
- crystal symmetry / Bravais lattice (to pick the canonical k-path)
- number of points per line segment (typical: 20–40)
- band intent (plain band, projected band, fat-band)

## Usually should be explicit

| Tag | Role | Recommended |
|-----|------|-------------|
| `ICHARG` | charge handling | `11` |
| `ISMEAR` | k-sampling method | `0` (Gaussian, `SIGMA = 0.05`) |
| `LORBIT` | projection mode | `11` for fat/projected bands, omit for plain |
| `NBANDS` | extra bands | ≥ 1.3 × occupied to resolve conduction manifold |
| `LWAVE`, `LCHARG` | do not overwrite | `.FALSE.`, `.FALSE.` |

## K-path selection

- Face-centered cubic (Si, Ge, C, GaAs, NaCl, ...): `L – Γ – X – U | K – Γ`.
- Body-centered cubic (Fe, Na): `Γ – H – N – Γ – P`.
- Hexagonal (MoS₂, graphene): `Γ – M – K – Γ`.
- Generic: use `sumo-kgen` or `seekpath` (or `pymatgen-structure`'s
  high-symmetry helper) — never guess coordinates.

## Concrete example — fcc Si band structure

Line-mode `KPOINTS` exactly as in [VASP wiki Fcc_Si_bandstructure](https://www.vasp.at/wiki/index.php/Fcc_Si_bandstructure)
(L – Γ – X – U, then K – Γ, 20 points per segment):

```text
k-points for bandstructure L-G-X-U K-G
 20
line
reciprocal
  0.50000  0.50000  0.50000    1    ! L
  0.00000  0.00000  0.00000    1    ! Gamma

  0.00000  0.00000  0.00000    1    ! Gamma
  0.00000  0.50000  0.50000    1    ! X

  0.00000  0.50000  0.50000    1    ! X
  0.25000  0.62500  0.62500    1    ! U

  0.37500  0.75000  0.37500    1    ! K
  0.00000  0.00000  0.00000    1    ! Gamma
```

`INCAR`:

```text
SYSTEM = fcc Si band
ISTART = 1
ICHARG = 11
ENCUT  = 320
PREC   = Accurate
LREAL  = .FALSE.
EDIFF  = 1E-6
NELM   = 60
ISMEAR = 0
SIGMA  = 0.05
LORBIT = 11
LWAVE  = .FALSE.
LCHARG = .FALSE.
```

## Physical sanity checks after the run

1. `grep -c 'BZINTS' OUTCAR` — should be 0 (line-mode k-points must not
   trigger Brillouin-zone integration warnings).
2. `ls EIGENVAL` — file must exist and be larger than `POSCAR`.
3. `head -6 EIGENVAL` — line 6 reports `NELECT NKPTS NBANDS` (for the
   fcc Si 4-segment × 20-point example: `4 80 8`, i.e. 4 valence
   electrons, 80 k-points along the path, 8 bands auto-picked by VASP).
4. Plot `EIGENVAL` (or `vaspkit 211`, `sumo-bandplot`): verify connectivity
   — the bands must follow the path without gaps in the k-axis.
5. For fcc 1-atom Si (metallic by construction), the Fermi level lies
   *inside* a band — there is **no** gap. If you want the textbook
   diamond-Si indirect gap (Γ → 0.85 X, ~0.7 eV in PBE), use a
   **2-atom diamond** POSCAR, not the 1-atom fcc cell.

## Known build traps

- `ICHARG = 11` with `ISYM ≠ 0` on a low-symmetry path sometimes
  symmetry-reduces k-points you wanted to sample. Set `ISYM = 0` if the
  resulting `NKPTS` is smaller than the number of requested line points.
- Hybrid functional band structures (`LHFCALC = .TRUE.`) cannot use
  `ICHARG = 11` line-mode directly — use the zero-weight-KPOINTS trick
  or `LOPTICS`/`wannier90` path.

## Expected output

1. band-stage task directory with generated `INCAR`, line-mode `KPOINTS`,
   staged `CHGCAR` from the prerequisite SCF
2. generated k-path summary (list segments, labels, total NKPTS)
3. prerequisite check summary (SCF path, CHGCAR size, k-path convention)
4. settings summary (ISMEAR rationale: Gaussian not tetrahedron)
5. physical sanity check checklist
6. handoff note to `dpdisp-submit`
