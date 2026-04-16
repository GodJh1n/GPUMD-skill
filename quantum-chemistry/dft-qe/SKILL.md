---
name: dft-qe
description: Generate Quantum ESPRESSO DFT input tasks from a user-provided structure plus user-specified DFT settings. Use when the user wants to prepare QE calculations such as SCF, NSCF, relax, vc-relax, MD, bands, DOS, or phonons starting from a structure file or coordinates together with pseudopotentials, functional choice, cutoffs, k-point settings, smearing, spin/charge, and convergence parameters. This skill prepares the QE task only; use a separate submission skill such as dpdisp-submit to submit the generated task.
compatibility: Requires a user-provided initial structure and enough DFT parameters to build a scientifically meaningful QE input.
license: GPL-3.0-only
metadata:
  author: Yi-FanLi
  version: '2.0'
  repository: https://gitlab.com/QEF/q-e
  qe_docs: https://www.quantum-espresso.org/Doc/user_guide/
---

# DFT with Quantum ESPRESSO (pw.x)

Build a QE `pw.x` task from a user-provided structure and DFT settings.
This skill prepares the input files only — hand off to `dpdisp-submit`
for execution.

## Units convention

QE is **Rydberg-atomic-units native**:
- `celldm(1)` is in **Bohr**, `A` is in **Å** (pick one)
- `ecutwfc`, `ecutrho`, total energy — all in **Rydberg** (`1 Ry ≈ 13.606 eV`)
- SCF convergence `conv_thr` is in Rydberg

## Hard requirement

A user-provided structure (file or explicit cell + coordinates). Stop
and ask if it is missing.

## Must provide

| Tag | Where | Role |
|-----|-------|------|
| `calculation` | `&CONTROL` | `'scf'`, `'nscf'`, `'bands'`, `'relax'`, `'vc-relax'`, `'md'`, `'vc-md'` |
| `pseudo_dir` | `&CONTROL` | directory containing the UPF files |
| `outdir` | `&CONTROL` | scratch — must be writable; prefix-named wavefunctions land here |
| `prefix` | `&CONTROL` | project tag for `*.save` |
| `ibrav` / `celldm` or `CELL_PARAMETERS` | `&SYSTEM` | lattice |
| `nat`, `ntyp` | `&SYSTEM` | counts must match `ATOMIC_POSITIONS` |
| `ecutwfc` | `&SYSTEM` | wavefunction cutoff, Ry |
| `ATOMIC_SPECIES` | card | pseudo per species (must exist in `pseudo_dir`) |

## Usually should be explicit

| Tag | Role | Recommended |
|-----|------|-------------|
| `ecutrho` | density cutoff | `4 × ecutwfc` for NC, **`8–12 × ecutwfc` for ultrasoft/PAW** |
| `input_dft` | override functional | only if pseudo doesn't match requested functional |
| `occupations` + `smearing` + `degauss` | metallic systems | `'smearing'`, `'mv'` or `'mp'`, `0.01–0.02 Ry` |
| `nspin`, `starting_magnetization(i)` | magnetic | always set for open-shell |
| `conv_thr` | SCF threshold, Ry | `1.0d-8` routine, `1.0d-10` phonons/forces |
| `mixing_beta` | density mixer | `0.7` insulator, `0.3–0.5` metal, `0.1` magnetic |
| `K_POINTS automatic` | MP mesh | dense enough: `2π/a × Nk > 20 Bohr⁻¹` rule of thumb |
| `electron_maxstep` | max SCF | `100` default, `200` for hard cases |

## Pseudopotential sources

| Library | URL | Notes |
|---------|-----|-------|
| PSlibrary (PAW/USPP) | <https://pseudopotentials.quantum-espresso.org/> | Official QE PP site; use `psl.1.0.0` family |
| SSSP Efficiency / Precision | <https://www.materialscloud.org/discover/sssp> | Curated per-element recommendations; start here for unfamiliar elements |
| PseudoDojo (ONCVPSP) | <http://www.pseudo-dojo.org> | NC, `upf` format, with per-element `ecut` hints |
| GBRV USPP | <https://www.physics.rutgers.edu/gbrv/> | Hard but fast USPP |

Pseudo rules:
- PAW / USPP pseudos need `ecutrho ≥ 8 × ecutwfc`. If you set
  `ecutrho = 4 × ecutwfc` with PAW, the density is aliased and
  energies are wrong by ~10 meV/atom silently.
- NC (ONCVPSP) pseudos accept `ecutrho = 4 × ecutwfc` as the default.
- Always match `input_dft` to the functional the pseudo was generated
  for (visible in the UPF header `<PP_INFO>` block).

## Concrete example — bulk silicon SCF (QE first-run tutorial)

Anchored on the canonical [QE user guide](https://www.quantum-espresso.org/Doc/pw_user_guide/)
silicon example, modernized with the PSlibrary 1.0.0 PAW pseudo.

Task directory:

```text
Si_qe_scf/
├── si.scf.in
└── Si.pbe-n-kjpaw_psl.1.0.0.UPF     # from pseudopotentials.quantum-espresso.org
```

`si.scf.in`:

```text
&CONTROL
  calculation = 'scf'
  prefix = 'si'
  outdir = './tmp/'
  pseudo_dir = './'
  verbosity = 'low'
/
&SYSTEM
  ibrav = 2              ! FCC
  celldm(1) = 10.2       ! Bohr (a ≈ 5.398 Å)
  nat = 2
  ntyp = 1
  ecutwfc = 30.0         ! Ry
  ecutrho = 240.0        ! Ry — 8×ecutwfc for the PAW pseudo
/
&ELECTRONS
  conv_thr = 1.0d-8
  mixing_beta = 0.7
/
ATOMIC_SPECIES
  Si  28.086  Si.pbe-n-kjpaw_psl.1.0.0.UPF
ATOMIC_POSITIONS alat
  Si  0.00  0.00  0.00
  Si  0.25  0.25  0.25
K_POINTS automatic
  6 6 6 0 0 0
```

Run:

```bash
pw.x -i si.scf.in > si.scf.out
```

## Physical sanity checks after the run

1. `grep 'convergence has been achieved' si.scf.out` — must report a
   finite iteration count. For the tutorial setup above, SCF converges
   in **8 iterations** (runtime-verified with QE 7.5).
2. `grep '!    total energy' si.scf.out | tail -1` — final total energy.
   For this 2-atom Si diamond cell with PAW PBE + `ecutwfc = 30 Ry`,
   `ecutrho = 240 Ry`, `6×6×6` MP mesh, expect **≈ −93.450 Ry**
   (= **−46.725 Ry/atom ≈ −635.7 eV/atom**). Drift > 1 mRy signals
   `ecutrho` too low or missing PAW augmentation.
3. `grep 'number of k points' si.scf.out` — for the `6×6×6` MP mesh with
   FCC symmetry expect **16 irreducible k-points**.
4. `grep 'estimated scf accuracy' si.scf.out | tail -1` — must be below
   `conv_thr` (reported as `6.7E-12 Ry` for the reference run).
5. `grep 'Fermi-Dirac smearing\|highest occupied' si.scf.out` — for an
   insulator like Si, the code reports `highest occupied, lowest
   unoccupied level` instead of a Fermi level; the HOMO-LUMO gap gives
   a sanity check on the Si indirect gap (~0.6 eV in PBE).

## Task-specific additions

For `relax` / `vc-relax`:

```text
&CONTROL
  calculation = 'relax'   ! or 'vc-relax'
  forc_conv_thr = 1.0d-4  ! Ry/Bohr
  etot_conv_thr = 1.0d-5  ! Ry
/
&IONS
  ion_dynamics = 'bfgs'
/
&CELL                      ! only for vc-relax
  cell_dynamics = 'bfgs'
  cell_dofree = 'all'      ! 'ibrav', 'volume', '2Dxy', etc.
/
```

For metals (add to `&SYSTEM`):

```text
  occupations = 'smearing'
  smearing = 'mv'          ! Marzari-Vanderbilt cold smearing
  degauss = 0.01           ! Ry
```

For magnetic systems:

```text
  nspin = 2
  starting_magnetization(1) = 0.5
```

## Known build traps

- PAW / USPP pseudos with `ecutrho = 4 × ecutwfc`: the density grid is
  too coarse; energies look "converged" but are wrong by 5–50 meV/atom.
  Always use `ecutrho = 8 × ecutwfc` unless the pseudo is NC.
- Relaxations without `ecutrho` set explicitly: QE picks
  `4 × ecutwfc`, which triggers the PAW trap above.
- `ibrav = 0` + `CELL_PARAMETERS` is the only way to use an arbitrary
  cell — `celldm` is **ignored** when `ibrav = 0`. A common silent bug
  is to supply both and get the `celldm` interpretation.
- `pseudo_dir` with a trailing component that doesn't exist: `pw.x`
  exits with "upf file not found" — always use an absolute path in
  production workflows.
- Running metals without smearing yields NaN or eternally oscillating
  SCF. `occupations = 'smearing'` is required whenever the system
  crosses the Fermi level.
- Hybrid functionals (`input_dft='hse'`, `'pbe0'`) need an extra
  `nqx1/2/3` block and are ~100× slower — out of scope for this skill.

## Expected output

1. QE task directory with `.in` input file and staged pseudopotentials
2. pseudopotential mapping summary (library, functional, `ecut` hint)
3. settings summary (smearing / k-mesh / ecutwfc/ecutrho ratio rationale)
4. sanity-check checklist (SCF steps, total energy, irreducible k-points)
5. unresolved choices (functional, vdW, spin) for user confirmation
6. handoff note to `dpdisp-submit`

## GPUMD / NEP integration

QE output can be converted to NEP extxyz via `dpdata-cli`:

```bash
uvx dpdata pw_output -i qe/pw/scf -O train.xyz -o extxyz
```

Verify virial sign convention after conversion before merging into a NEP
training dataset.
