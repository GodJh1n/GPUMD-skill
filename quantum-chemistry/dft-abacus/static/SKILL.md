---
name: static
description: Prepare ABACUS single-point (static SCF) task inputs from a user-provided structure and essential DFT settings. Use when the user needs total-energy/electronic SCF evaluation with explicit ABACUS INPUT/STRU/KPT generation, pseudopotential + orbital mapping, and basis-type selection (PW or LCAO).
compatibility: Requires a user-provided structure, compatible pseudopotentials, optional numerical orbital files (LCAO mode), and runnable ABACUS environment.
license: GPL-3.0-only
catalog-hidden: true
metadata:
  author: qqgu
  version: 0.2.0
  repository: https://github.com/deepmodeling/abacus-develop
---

# ABACUS Static SCF (Subskill)

## Scope

This skill prepares single-point SCF tasks only. It generates the
three ABACUS input files (`INPUT`, `STRU`, `KPT`), stages pseudopotential
and orbital files, and reports settings. It does not submit or execute
jobs — hand off to `dpdisp-submit`.

## Three-file input convention

ABACUS always requires **three** input files in the working directory:

| File | Role |
|------|------|
| `INPUT` | Global parameters (basis type, cutoff, SCF controls, functional) |
| `STRU` | Structure (species, pseudos, orbitals, cell, coordinates) |
| `KPT` | k-point mesh or path |

## Must provide

- structure (`STRU` file: lattice, species, coordinates)
- pseudopotential per species (UPF format, `.upf` / `.UPF`)
- `basis_type` choice: `lcao` (default, uses numerical atomic orbitals)
  or `pw` (plane-wave, no orbital files needed)
- for `lcao`: numerical orbital file per species (`.orb` or named like
  `Si_lda_8.0au_50Ry_2s2p1d`)
- `ecutwfc` — wavefunction / integration cutoff (Ry)
- k-point mesh (`KPT` file)

## Usually should be explicit

| Tag | Where | Role | Recommended |
|-----|-------|------|-------------|
| `basis_type` | `INPUT` | PW or LCAO | `lcao` for efficiency; `pw` for benchmarks |
| `ecutwfc` | `INPUT` | cutoff, Ry | 60–100 Ry for LCAO; 50–80 Ry for PW (depends on pseudo) |
| `scf_thr` | `INPUT` | charge density convergence | `1e-6` routine, `1e-8` for forces/phonons |
| `scf_nmax` | `INPUT` | max SCF iters | `100` default |
| `dft_functional` | `INPUT` | XC functional | `lda` / `pbe` / `scan` — must match pseudo |
| `mixing_type` | `INPUT` | density mixer | `broyden` (default, good); `pulay` alternative |
| `mixing_beta` | `INPUT` | mixing weight | `0.4` default; reduce to `0.1` for metals |
| `smearing_method` | `INPUT` | smearing | `fixed` for insulators; `gauss` or `mp` for metals |
| `smearing_sigma` | `INPUT` | smearing width, Ry | `0.01` for metals |
| `nspin` | `INPUT` | spin | `1` non-magnetic, `2` collinear, `4` SOC |
| `out_level` | `INPUT` | output detail | `ie` for energy+force; `m` for minimal |

## Basis type rules

| `basis_type` | Needs orbital file? | Speed | Accuracy | Typical use |
|:------------:|:-------------------:|:-----:|:--------:|-------------|
| `lcao` | **Yes** | Fast for large systems | Depends on orbital quality (DZP/TZDP) | Default; NEP labeling |
| `pw` | No | Slower, systematic convergence | Exact at high `ecutwfc` | Benchmarks, comparison with QE |

## Pseudopotential + orbital sources

| Resource | URL | Notes |
|----------|-----|-------|
| ABACUS test pseudos | `tests/PP_ORB/` in the [ABACUS repo](https://github.com/deepmodeling/abacus-develop) | LDA Si.pz-vbc.UPF + orbital files included |
| SG15 ONCVPSP | <http://www.quantum-simulation.org/potentials/sg15_oncv/> | NC PBE pseudos, well-tested with ABACUS |
| PseudoDojo | <http://www.pseudo-dojo.org> | NC PBE `.upf`, with `ecut` hints |
| ABACUS orbital library | <https://abacus.ustc.edu.cn/pseudo/list.htm> | Official numerical orbital files per element + pseudo pair |

Matching rule: the pseudo, orbital file, and `dft_functional` in INPUT
must all correspond. Using a PBE orbital with an LDA pseudo gives wrong
forces silently.

## Concrete example — Si diamond LCAO SCF (ABACUS examples/02_scf/02_lcao_Si2)

Anchored on the upstream [ABACUS example 02_scf/02_lcao_Si2](https://github.com/deepmodeling/abacus-develop/tree/develop/examples/02_scf/02_lcao_Si2).

Task directory:

```text
Si_abacus_scf/
├── INPUT
├── STRU
├── KPT
├── Si.pz-vbc.UPF               # pseudo from tests/PP_ORB/
└── Si_lda_8.0au_50Ry_2s2p1d    # orbital from tests/PP_ORB/
```

`INPUT`:

```text
INPUT_PARAMETERS
pseudo_dir           ./
orbital_dir          ./
ecutwfc              60
scf_nmax             100
scf_thr              1e-6
basis_type           lcao
```

`STRU`:

```text
ATOMIC_SPECIES
Si 28.085 Si.pz-vbc.UPF

NUMERICAL_ORBITAL
Si_lda_8.0au_50Ry_2s2p1d

LATTICE_CONSTANT
10.2                    # Bohr

LATTICE_VECTORS
0.0 0.5 0.5
0.5 0.0 0.5
0.5 0.5 0.0

ATOMIC_POSITIONS
Cartesian               # unit is LATTICE_CONSTANT
Si
0.0
2
0.00 0.00 0.00 0 0 0
0.25 0.25 0.25 1 1 1
```

`KPT`:

```text
K_POINTS
0
Gamma
4 4 4 0 0 0
```

Run:

```bash
OMP_NUM_THREADS=4 abacus
```

Output lands in `OUT.ABACUS/running_scf.log`.

## Physical sanity checks after the run

1. `grep 'convergence is achieved' OUT.ABACUS/running_scf.log` — must
   be present. For the Si2 LCAO example, SCF converges in **7 electronic
   steps** (runtime-verified on ABACUS v3.10.1).
2. `grep 'FINAL_ETOT_IS' OUT.ABACUS/running_scf.log` — final total
   energy in eV. Expect **≈ −213.665 eV** for the 2-atom Si cell
   (= −106.83 eV/atom, LDA with DZP-quality orbital). Drift > 10 meV
   signals `ecutwfc` too low or orbital/pseudo mismatch.
3. `grep 'E_KS(sigma->0)' OUT.ABACUS/running_scf.log` — shows the
   Kohn-Sham energy in Ry: expect **≈ −15.704 Ry** for the same run.
4. `ls OUT.ABACUS/CHARGE-DENSITY.dat` — must exist for chained DOS/band
   runs that need the converged charge density.
5. For `basis_type lcao`, check `OUT.ABACUS/running_scf.log` for
   "ORBITAL" lines confirming the orbital file was loaded for each
   species — a missing orbital file produces a crash, not a warning.

## Known build traps

- **Missing orbital file for LCAO**: ABACUS aborts immediately with an
  opaque file-I/O error. Verify all files listed in `NUMERICAL_ORBITAL`
  exist in `orbital_dir`.
- **STRU species order** must match the order in `ATOMIC_SPECIES` and
  `NUMERICAL_ORBITAL`. Swapping the order silently maps wrong pseudos
  to wrong elements.
- `ecutwfc` meaning differs between PW and LCAO modes: in LCAO mode it
  controls the **real-space integration grid**, not the basis-set size
  (that's set by the orbital file). A lower `ecutwfc` in LCAO still gives
  a reasonable calculation; in PW mode it directly controls basis quality.
- ABACUS uses `LATTICE_CONSTANT` in **Bohr** by default in STRU.
  If you specify `latname` in INPUT, you must also match `LATTICE_CONSTANT`.
  Accidentally using Angstrom gives a cell ~1.89× too large.
- For metals: `smearing_method fixed` (the default) with a metallic
  system causes SCF to never converge. Set `smearing_method gauss` +
  `smearing_sigma 0.01`.

## STRU file format reference

```text
ATOMIC_SPECIES
<Element> <Mass> <PseudopotentialFile>

NUMERICAL_ORBITAL          # only for basis_type lcao
<OrbitalFile>

LATTICE_CONSTANT
<a0_in_Bohr>

LATTICE_VECTORS
<v1x> <v1y> <v1z>
<v2x> <v2y> <v2z>
<v3x> <v3y> <v3z>

ATOMIC_POSITIONS
<Cartesian|Direct>
<Element>
<MagneticMoment>
<NumberOfAtoms>
<x> <y> <z> <move_x> <move_y> <move_z>
...
```

## Expected output

1. task directory with `INPUT`, `STRU`, `KPT` + staged pseudo/orbital
2. basis-type rationale (LCAO vs PW) and orbital quality summary
3. settings summary (ecutwfc, smearing, functional matching)
4. sanity-check checklist (SCF steps, total energy, charge-density file)
5. handoff note to `dpdisp-submit`
