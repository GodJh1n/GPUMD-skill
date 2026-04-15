---
name: static
description: Prepare ABINIT single-point (static) task inputs from a user-provided structure and essential DFT settings. Use when the user needs total-energy/electronic SCF evaluation with explicit ABINIT cutoff, k-point, and SCF controls.
compatibility: Requires a user-provided structure, suitable pseudopotentials, and runnable ABINIT environment.
license: GPL-3.0-only
catalog-hidden: true
metadata:
  author: qqgu
  version: 0.2.0
  repository: https://github.com/abinit/abinit
---

# ABINIT Static (Subskill)

## Scope

This skill prepares single-point total-energy tasks only. It generates a
single ABINIT `.abi` input file, pseudopotential mapping, and
`pp_dirpath` guidance. It does not submit or execute jobs.

## Units convention (important)

ABINIT is **atomic-units native**:
- `acell` is in **Bohr** (convert Å → Bohr with `× 1.88973`)
- `ecut` is in **Hartree** (`1 Ha ≈ 27.2114 eV ≈ 2 Ry`)
- `etotal` printed in Hartree

If the user specifies values in eV or Å, convert explicitly before
writing the input and note the original units in the summary.

## Must provide

- structure (`acell`, `rprim`, `natom`, `typat`, `xred`/`xcart`, `znucl`)
- pseudopotential file per `znucl` species (`pseudos` + `pp_dirpath`)
- `ecut` — plane-wave cutoff (Ha). Depends on pseudo family.
- k-point policy (`kptopt`, `ngkpt`, `shiftk`)
- `ixc` or pseudo-implicit functional choice

## Usually should be explicit

| Tag | Role | Recommended |
|-----|------|-------------|
| `ecut` | plane-wave cutoff, Ha | NC TM: 8–12; ONCVPSP: 20–40; PAW: same as ecut + `pawecutdg = 2 × ecut` |
| `pawecutdg` | PAW fine-grid cutoff | only for `*.xml` PAW pseudos |
| `kptopt` | k-point generation mode | `1` (time-reversal + symmetry), `3` for no symmetry |
| `ngkpt` / `shiftk` | k-mesh + shift | use the Monkhorst–Pack shifted mesh from the tutorial for FCC |
| `nstep` | max SCF iterations | `20` routine, `50` for metals |
| `toldfe` | energy SCF stop, Ha | `1.0d-6` routine, `1.0d-8` for forces / phonons |
| `tolvrs` | density SCF stop | alternative to `toldfe`, use for structural work |
| `diemac` | model dielectric constant | `12.0` for Si/Ge; `2.0` for molecules; `1000000.0` for metals |
| `ecutsm` | smoothing on `ecut` | `0.5` when `optcell ≠ 0` (relaxation), else 0 |
| `occopt` / `tsmear` | smearing for metals | `occopt 4, tsmear 0.01` Ha Marzari cold-smearing |

## Pseudopotential families

| Family | File ext | `ixc` | `ecut` typical | Notes |
|--------|----------|-------|----------------|-------|
| Troullier–Martins (Teter) | `.pspnc`, `.psp1` | LDA (–1012) | 8–12 Ha | Tutorial default; fast |
| FHI | `.fhi` | LDA/GGA | 20 Ha | Older, still used |
| ONCVPSP (SG15 / pseudo-dojo NC) | `.psp8`, `.upf` | `-116133` (PBE) | 20–40 Ha | **Modern default**; check "hint" stanza in the file |
| PAW (JTH / GBRV) | `.xml`, `.GGA_PBE.xml` | set by pseudo | `ecut ≈ 15, pawecutdg ≥ 2×ecut` | Needed for magnetic / transition metals |

Download locations:
- Troullier–Martins test pseudos ship with the ABINIT source tree under
  `tests/Psps_for_tests/PseudosTM_pwteter/`.
- ONCVPSP PBE: <https://www.pseudo-dojo.org> (standard accuracy,
  scalar-relativistic, `psp8` format).
- JTH PAW: <https://www.abinit.org/psp-tables>.

## Concrete example — crystalline silicon total energy (ABINIT tutorial base3)

Anchored on [ABINIT tutorial "base3"](https://docs.abinit.org/tutorial/base3/)
— the first canonical crystalline-solid single-point. The 2-atom FCC
primitive is the textbook diamond-Si cell. Uses the TM-Teter pseudo
`14si.pspnc` that ships with the ABINIT source tree.

Task directory:

```text
Si_tbase3/
├── tbase3_1.abi
└── 14si.pspnc     # ABINIT tests/Psps_for_tests/PseudosTM_pwteter/14si.pspnc
```

`tbase3_1.abi`:

```text
# Crystalline silicon — total energy (ABINIT tutorial base3)

# Unit cell (Bohr)
acell 3*10.18
rprim  0.0  0.5  0.5
       0.5  0.0  0.5
       0.5  0.5  0.0

# Atom species + positions
ntypat 1
znucl  14
natom  2
typat  1 1
xred
   0.0   0.0   0.0
   0.25  0.25  0.25

# Plane-wave basis
ecut 8.0              # Ha — minimal for TM pseudo

# Brillouin zone sampling (Monkhorst–Pack 4×4×4, 4-shift for FCC)
kptopt 1
ngkpt  4 4 4
nshiftk 4
shiftk 0.5 0.5 0.5
       0.5 0.0 0.0
       0.0 0.5 0.0
       0.0 0.0 0.5

# SCF control
nstep 20
toldfe 1.0d-6
diemac 12.0           # static dielectric of Si

# Pseudopotential
pp_dirpath "."
pseudos "14si.pspnc"
```

Run:

```bash
abinit tbase3_1.abi > tbase3_1.log 2>&1
```

## Physical sanity checks after the run

1. `grep 'etot is converged' tbase3_1.abo` — must be present.
   For the tbase3 tutorial setup above, SCF converges in **~5 steps**
   (runtime-verified with abinit 10.0.3).
2. `grep 'etotal' tbase3_1.abo` — final total energy for the 2-atom cell.
   Expect **≈ −8.8725 Ha** (= **−4.4362 Ha / atom ≈ −120.7 eV/atom**).
   Drift > 1 mHa usually means `ecut` is too low or `ngkpt` too coarse.
3. `grep 'Cartesian forces' tbase3_1.abo` — forces must be zero to
   numerical noise (< 1.0d-6 Ha/Bohr) by Si crystal symmetry.
4. `grep 'etotal' tbase3_1.abo` at `ecut = 12` vs `ecut = 8` — difference
   must be < 1 mHa for this TM pseudo. If not, raise `ecut`.
5. `grep 'Ha per atom' tbase3_1.abo` — sanity-check per-atom pressure.

## Known build traps

- `diemac` default (`1.0d6`) assumes a metal. For an insulator this
  makes the density mixer oscillate; set `diemac 12.0` for Si-like
  semiconductors and `diemac 2.0` for molecules.
- `ecutsm` must be > 0 whenever any cell-DOF is being relaxed
  (`optcell ≠ 0`), otherwise the stress tensor has a step-function at
  the plane-wave cutoff.
- The pseudopotential line in the old ABINIT `.in` style used a
  separate `files file`. ABINIT ≥ 9 inlines this via `pp_dirpath` +
  `pseudos` directly in the `.abi` — mixing the two styles silently
  breaks the run.
- ONCVPSP / PAW pseudos have built-in hint cards for `ecut` — **do not
  override below the hint** or the total energy is off by tens of meV
  per atom.

## Expected output

1. static-task directory with `.abi` input and pseudo staged
2. pseudopotential mapping summary (family, `ecut` hint, functional)
3. unit-conversion notes (Bohr/Ha/Ry/eV) when the user supplied SI or eV
4. sanity-check checklist (SCF steps, total energy, force symmetry)
5. handoff note to `dpdisp-submit`
