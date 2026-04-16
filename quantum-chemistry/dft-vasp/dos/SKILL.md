---
name: dos
description: Prepare VASP DOS workflow inputs from existing SCF artifacts and user-specified DOS settings. Use when the user requests total/projected DOS setup and needs INCAR/KPOINTS preparation with explicit prerequisite checks against prior SCF runs.
compatibility: Requires prerequisite SCF artifacts and valid VASP pseudopotential resources/license in the target environment.
catalog-hidden: true
license: GPL-3.0-only
metadata:
  author: qqgu
  version: 0.2.0
  repository: https://vasp.at/
---

# VASP DOS Preparation (Subskill)

## Scope

This skill prepares DOS-stage input tasks only. It verifies prerequisite SCF
artifacts, prepares DOS-specific INCAR/KPOINTS, and reports assumptions. It
does not submit or execute jobs.

## Two-step workflow (canonical)

The VASP wiki enforces a two-step SCF → DOS pattern:

1. **Step 1 — SCF** (done by `dft-vasp/static`): converge the charge
   density on a coarse k-mesh, write out `CHGCAR` (`LCHARG = .TRUE.`).
2. **Step 2 — DOS** (this skill): reuse the `CHGCAR`, fix the charge
   density (`ICHARG = 11`), and sample a **denser** k-mesh using the
   tetrahedron method (`ISMEAR = -5`).

Per [VASP wiki Fcc_Si_DOS](https://www.vasp.at/wiki/index.php/Fcc_Si_DOS):
> "You must do this, otherwise VASP cannot read the CHGCAR and will terminate."

## Prerequisites (hard)

Require the user to point at an existing SCF task with:

- `CHGCAR` (non-empty)
- the same `POSCAR` as will be used for DOS
- the same `POTCAR` (species order, pseudo version)
- `LCHARG = .TRUE.` was set in the SCF INCAR

If any of these is missing, stop and ask.

## Must provide

- source SCF context path (and verify the four items above)
- DOS intent (`total DOS` or `projected DOS`)
- target k-mesh for DOS (typically 2× the SCF mesh in each direction)
- energy window (`EMIN`, `EMAX`) — default: auto from `EFERMI ± 15 eV`
- element-resolved projection level (`LORBIT`)

## Usually should be explicit

| Tag | Role | Recommended |
|-----|------|-------------|
| `ICHARG` | charge handling | `11` (fixed from CHGCAR, non-SCF) |
| `ISMEAR` | k-sampling method | `-5` (tetrahedron, Blöchl correction) — **requires ≥ 4 irreducible k-points** |
| `NEDOS` | energy grid points | `3001` (~10 meV resolution over 30 eV window) |
| `LORBIT` | projection mode | `11` (site + l+m projection, needs `RWIGS` or uses default radii) |
| `EMIN`, `EMAX` | plot window | `EFERMI − 15` to `EFERMI + 15` |
| `NBANDS` | extra bands | ≥ 1.3 × occupied for clean conduction tails |

## Tetrahedron trap

`ISMEAR = -5` is wrong for:
- Small cells with < 4 irreducible k-points (VASP silently falls back or
  errors out) — fall back to `ISMEAR = 0, SIGMA = 0.05`.
- Force / relaxation runs — use the static-SCF smearing instead.
- Hybrid functional runs — use `ISMEAR = 0, SIGMA = 0.05`.

## Concrete example — fcc Si projected DOS

Prerequisite: a converged `dft-vasp/static` run on fcc Si at its relaxed
volume with `LCHARG = .TRUE.` (see `dft-vasp/relax` for the equilibrium
structure — V/atom ≈ 14.5 Å³, a ≈ 3.87 Å).

Task directory:

```text
Si_fcc_dos/
├── POSCAR            # same cell as SCF prerequisite
├── INCAR
├── KPOINTS           # denser than SCF
├── POTCAR            # same as SCF prerequisite
└── CHGCAR            # copied from the SCF run
```

`INCAR`:

```text
SYSTEM = fcc Si DOS
ISTART = 1
ICHARG = 11           # fixed charge, non-SCF
ENCUT  = 320
PREC   = Accurate
LREAL  = .FALSE.
EDIFF  = 1E-6
NELM   = 60
ISMEAR = -5           # tetrahedron + Bloechl
LORBIT = 11           # site-projected + orbital-resolved
NEDOS  = 3001
EMIN   = -15
EMAX   =  15
LWAVE  = .FALSE.
LCHARG = .FALSE.
```

`KPOINTS` — refine to 21×21×21 Γ-centered (~8 × more points than the 11³
SCF mesh; still cheap for a 1-atom cell):

```text
DOS mesh
0
Gamma
21 21 21
0  0  0
```

## Physical sanity checks after the run

1. `ls DOSCAR` — file exists and is > 10 kB.
2. `head -6 DOSCAR` — first header line reports the number of ions; line 5
   should give `EMAX EMIN NEDOS EFERMI weight`.
3. `grep 'E-fermi' OUTCAR | tail -1` — Fermi level in eV.
   - **Semiconductor with a clean gap**: the DOS-stage E_F must match the
     SCF E_F to within 20 meV; larger drift means inconsistent CHGCAR.
   - **Metal / gapless system**: Gaussian→tetrahedron can shift E_F by
     100–300 meV because the two methods assign partial occupancies
     differently at the Fermi surface. This is physical, not a bug.
     Verified locally: fcc 1-atom Si E_F = 9.987 eV (SCF, Gaussian σ=0.05)
     → 10.194 eV (DOS, tetrahedron), Δ = 207 meV.
4. **The fcc 1-atom Si cell is metallic by construction** (4 valence
   electrons half-fill the 3p band). It is the VASP wiki's *EOS tutorial
   cell*, not a band-gap demonstration. For a real semiconductor DOS
   demo, use the 2-atom diamond primitive (POSCAR with positions
   `0 0 0` and `0.25 0.25 0.25`, `a_conv ≈ 5.47 Å` at PBE).
5. For projected DOS (`LORBIT = 11`), open `PROCAR` or check the last
   columns of `DOSCAR` — l+m components must sum (per site) to the
   total DOS within 1%.

## Known build traps

- `ISMEAR = -5` with a highly anisotropic cell (e.g., slab) will produce
  noisy DOS — use denser k-mesh in the short reciprocal directions.
- `ICHARG = 11` with a CHGCAR from a **different** functional / ENCUT
  gives physically meaningless DOS. The skill must verify the two INCARs
  share `GGA`, `ENCUT`, `PREC`, and `LASPH` tags.

## Expected output

1. DOS-stage task directory with `INCAR`, `KPOINTS`, staged `CHGCAR` link
2. prerequisite check summary (SCF path, CHGCAR size, POTCAR hash)
3. settings summary (why tetrahedron vs Gaussian)
4. sanity-check checklist
5. handoff note to `dpdisp-submit`
