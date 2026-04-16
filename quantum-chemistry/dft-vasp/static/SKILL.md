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

## vaspkit workflow for KPOINTS and POTCAR

For production work, **always use vaspkit** to generate KPOINTS and assemble
POTCAR instead of writing them by hand. vaspkit reads `~/.vaspkit` for the
POTCAR library path and automatically selects recommended pseudopotentials.

### Generate KPOINTS + POTCAR in one step

```bash
echo -e "102\n1\n0.04" | vaspkit
```

- `102` = uniform k-mesh generation
- `1` = Monkhorst-Pack (or Gamma-centered per `GAMMA_CENTERED` in `~/.vaspkit`)
- `0.04` = k-spacing in 1/Å (smaller = denser mesh)

vaspkit writes both `KPOINTS` and `POTCAR` (with recommended potentials)
in one pass. Always verify the chosen POTCAR variants in the vaspkit summary
output — e.g., `Pb_d` (14 valence electrons) vs `Pb` (4 valence electrons)
can dramatically change ENMAX requirements.

### Generate KPOINTS only

```bash
echo -e "102\n1\n0.03" | vaspkit
```

### Generate POTCAR only

```bash
echo -e "103" | vaspkit
```

vaspkit reads the species from POSCAR and concatenates POTCARs from the
configured library path (`PBE_PATH` in `~/.vaspkit`).

### k-spacing guidelines

| System | Spacing (1/Å) | Typical mesh |
|--------|:-------------:|-------------|
| Large supercell (> 100 atoms) | 0.04–0.06 | Γ-only or 1×1×1 |
| Bulk semiconductor (2–8 atoms) | 0.02–0.03 | 11×11×11 – 8×8×8 |
| Metal slab | 0.03 | dense in-plane, 1 out-of-plane |
| NEP labeling (perturbed cells) | 0.04 | coarse is acceptable |

## Runtime-verified example — PbTe 250-atom supercell (NEP labeling)

This example was **runtime-verified** on VASP 6.4.3 (2026-04-16) as part
of a complete DFT → NEP training pipeline test using the PbTe structure
from [GPUMD tutorial 11_NEP_potential_PbTe](https://gpumd.org/tutorials/nep_potential_PbTe.html).

Task: single-point SCF on a 250-atom Pb₁₂₅Te₁₂₅ cell extracted from the
GPUMD PbTe train.xyz dataset, for NEP training data generation.

### Structure preparation

```python
from ase.io import read, write
# Extract one frame from GPUMD training data
atoms = read('train.xyz', index=0, format='extxyz')
# Remove existing calculator results (energy/forces)
atoms.calc = None
atoms.info = {}
atoms.arrays = {k: v for k, v in atoms.arrays.items()
                if k in ('numbers', 'positions')}
# Sort by species for VASP
atoms = atoms[atoms.numbers.argsort()]
write('POSCAR', atoms, format='vasp', vasp5=True, sort=True)
```

### Input files (generated via vaspkit)

**KPOINTS** (vaspkit `102`, spacing 0.04 → Γ-only for this large cell):

```text
K-Spacing Value to Generate K-Mesh: 0.040
0
Monkhorst-Pack
   1   1   1
0.0  0.0  0.0
```

**POTCAR** (vaspkit `103`, recommended potentials):
- `Pb_d` — 14 valence electrons, ENMAX = 237.835 eV
- `Te` — 6 valence electrons, ENMAX = 174.982 eV

**INCAR**:

```text
SYSTEM = PbTe pipeline test
ISTART = 0
ICHARG = 2
ENCUT  = 300          # above max(ENMAX)=237.8 for Pb_d
PREC   = Normal       # low precision for pipeline test
LREAL  = Auto         # 250 atoms — use real-space projection
EDIFF  = 1E-4         # loose SCF for testing
NELM   = 40
ISMEAR = 0
SIGMA  = 0.1
LWAVE  = .FALSE.
LCHARG = .FALSE.
NCORE  = 4
```

### Run

```bash
export OMP_NUM_THREADS=1
mpirun -np 16 vasp_std > vasp.out 2> vasp.err
```

### Verified results

| Metric | Value |
|--------|-------|
| SCF steps | **15** (DAV) |
| Final energy | **−919.062 eV** (= −3.676 eV/atom) |
| Convergence | dE = 1.24×10⁻⁵ eV at step 15 (EDIFF = 1×10⁻⁴) |
| Wall time | ~10 min on 16 cores (single node) |
| POTCAR | Pb_d (recommended) + Te |

### Post-SCF: convert to NEP training data

```bash
# Using dpdata (pip install dpdata)
python3 -c "
import dpdata
ds = dpdata.LabeledSystem('OUTCAR', fmt='vasp/outcar')
ds.to('extxyz', 'train.xyz')
"
```

Or via CLI:

```bash
uvx dpdata OUTCAR -i vasp/outcar -O train.xyz -o extxyz
```

The resulting `train.xyz` contains energy, forces, virial, and lattice in
the extxyz format ready for NEP training. See `nep-gpumd/train` for the
next step.

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
