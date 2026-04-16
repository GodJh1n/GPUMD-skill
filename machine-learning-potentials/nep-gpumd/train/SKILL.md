---
name: train
description: >
  Train a first NEP potential from labeled extxyz data. Use when the user
  needs `nep.in`, `train.xyz`, `test.xyz`, parameter guidance, loss.out
  interpretation, or deployment of the resulting `nep.txt` back into GPUMD.
  NEP is the native machine-learning potential for GPUMD and plays the role
  that DeePMD plays for LAMMPS.
compatibility: Requires a NEP-capable GPUMD build with the `nep` executable and labeled training/test extxyz datasets.
catalog-hidden: true
license: GPL-3.0-only
metadata:
  author: Jhin
  version: 0.2.0
---

# NEP Train

Train a baseline NEP potential from labeled data. This is the general-purpose
training subskill for the energy + force (+ virial) model. For dipole or
polarizability auxiliary properties, the same `nep` executable is used but
with a different `model_type` — see the auxiliary-properties reference.

## Quick start

```bash
nep
```

The `nep` binary reads `nep.in`, `train.xyz`, and (optionally) `test.xyz`
from the current directory and writes `nep.txt`, `loss.out`, and the
parity files. Some HPC builds wrap this as `srun -n 1 --gpus=1 nep` or
equivalent — ask the user.

## Agent responsibilities

1. Confirm the environment has the `nep` executable and that the user has
   supplied labeled training data.
2. Collect the minimum required information:
   - labeled training dataset path(s) (`train.xyz`)
   - labeled test dataset path (`test.xyz`, optional but recommended)
   - full species list in the exact order the user wants in `type`
   - target observable(s) for post-training validation
3. Validate dataset headers before training:
   ```bash
   python ../scripts/validate_extxyz_headers.py train.xyz --mode train
   python ../scripts/validate_extxyz_headers.py test.xyz --mode train
   ```
4. Write `nep.in` yourself and explain the hyperparameters that matter.
5. Run training and monitor `loss.out`.
6. Deploy the trained `nep.txt` back into a GPUMD sanity MD run before
   calling the training "done".

## Workflow

### Step 1. Prepare datasets

`train.xyz` and `test.xyz` are concatenations of labeled extxyz frames.
Each frame must contain:

- atom count line
- header with `Lattice="..."`, `energy=...`, `Properties=species:S:1:pos:R:3:force:R:3`
- N rows of `species x y z fx fy fz`

Optional but important header fields:

- `virial="..."` — full 9-component virial if stress-fit is desired
- `stress="..."` — some converters write stress instead of virial; be explicit
- `config_type=...` — free-form label used for per-group weights
- `weight=...` — frame-level loss weight

Minimal frame:

```text
2
Lattice="5.43 0 0 0 5.43 0 0 0 5.43" pbc="T T T" energy=-10.860000 Properties=species:S:1:pos:R:3:force:R:3
Si 0.000000 0.000000 0.000000  0.0010 -0.0020  0.0030
Si 1.357500 1.357500 1.357500 -0.0010  0.0020 -0.0030
```

Keep units consistent:

- positions in Å
- total energy in eV (not per atom)
- forces in eV/Å
- virial/stress: confirm sign convention and whether the header carries the
  full tensor or a normalized quantity

For help generating these files from DFT output, see
[references/labels-from-dft.md](../references/labels-from-dft.md).

### Step 2. Write `nep.in`

Annotated baseline (see
[assets/examples/baseline/nep.in](../assets/examples/baseline/nep.in)):

```text
type         2 Si O
version      4
cutoff       8 4
n_max        4 4
basis_size   8 8
l_max        4 2 0
neuron       30
lambda_e     1.0
lambda_f     1.0
lambda_v     0.1
batch        1000
population   50
generation   100000
```

- `type 2 Si O`
  - First integer = number of element types. Remaining = species names in
    the order they will appear everywhere downstream. This order is
    load-bearing: it must match `train.xyz`, `test.xyz`, the potential
    header, and the `model.xyz` used in the deployed GPUMD MD.
- `version 4`
  - NEP4 syntax. Default unless reproducing a legacy NEP3 fit.
- `cutoff 8 4`
  - Radial / angular cutoffs in Å. `8 4` is a robust starting point for
    most condensed-phase systems.
- `n_max 4 4`, `basis_size 8 8`, `l_max 4 2 0`, `neuron 30`
  - Descriptor and network complexity. Start here, only increase after
    dataset quality is confirmed.
- `lambda_e`, `lambda_f`, `lambda_v`
  - Loss weights on energy / force / virial. Set `lambda_v 0` when the
    dataset has no virial labels or when the convention is uncertain.
- `batch 1000`, `population 50`, `generation 100000`
  - Training control. `generation 5000` is only useful for a quick smoke
    test — it is almost never enough for convergence. Production fits
    typically need 50000–200000 generations. Start with 100000 and increase
    if the `loss.out` curve has not plateaued.

### Step 3. Run training

```bash
nep
```

Outputs in the current directory:

- `nep.txt` — the trained potential
- `nep.restart` — restart state (needed for later fine-tuning)
- `loss.out` — training and validation losses per generation
- `energy_train.out`, `energy_test.out` — parity data
- `force_train.out`, `force_test.out` — parity data
- `virial_train.out`, `virial_test.out` — parity data (when virials used)

Monitor `loss.out` with the bundled helper:

```bash
python scripts/summarize_nep_loss.py loss.out
```

### Step 4. Inspect parity and loss

Look at the final rows of `loss.out`:

- all losses should be finite (no NaN / inf)
- training loss should be lower than or comparable to validation loss — if
  validation is dramatically worse, the dataset coverage or labeling is
  suspect
- a good train parity with a bad test parity points to dataset gap

Quantitative guidance for diagnosing overfitting:

- If test RMSE is more than 2x the training RMSE for energy or force,
  suspect overfitting or a train/test distribution mismatch.
- If the loss curve shows training loss still decreasing but test loss
  increasing or plateauing for more than ~10% of total generations,
  training should be stopped or the model complexity reduced.
- Compare force RMSE against the physical force scale: for a bulk solid
  at equilibrium, force RMSE above 50 meV/Å typically indicates a problem;
  for liquids or reactive systems, 100–200 meV/Å may be acceptable.
- If energy RMSE per atom exceeds ~5 meV/atom for a well-behaved bulk
  system, check dataset consistency before increasing model complexity.

Compute parity metrics from the parity outputs:

```bash
python scripts/parity_from_nep_outputs.py --prefix energy_test
python scripts/parity_from_nep_outputs.py --prefix force_test
```

### Step 5. Downstream validation

RMSE alone is not enough. Before calling the fit "done":

1. drop `nep.txt` into a GPUMD MD run at the target state
2. verify numerical stability in a short NVE segment (no runaway energy)
3. check at least one target-state observable (lattice constant, RDF,
   diffusion, conductivity, …)

If the short MD diverges but the parity plot looks fine, the model is not
yet fit for production.

### Step 6. Deploy into GPUMD

```text
potential nep.txt
```

That's it at the syntax level — but see the GPUMD `md` subskill for the
full deployment workflow.

## Runtime-verified end-to-end example — PbTe (DFT → NEP)

This complete pipeline was **runtime-verified** on 2026-04-16 using a
250-atom PbTe supercell from [GPUMD tutorial 11_NEP_potential_PbTe](https://gpumd.org/tutorials/nep_potential_PbTe.html).
It demonstrates the full DFT → format conversion → NEP training → loss
plotting workflow.

### Overview

```text
train.xyz (GPUMD tutorial)
    │
    ▼  ASE: extract 1 frame, strip labels
POSCAR (250 atoms, Pb₁₂₅Te₁₂₅)
    │
    ▼  vaspkit: KPOINTS + POTCAR
    ▼  VASP static SCF (16 cores)
OUTCAR (E = −919.06 eV, forces, stress)
    │
    ▼  dpdata: vasp/outcar → extxyz
train.xyz (1 frame, energy + forces + virial)
    │
    ▼  nep (GPU, 2000 generations)
nep.txt + loss.out
    │
    ▼  matplotlib
loss_plot.png
```

### Step 1: Extract structure

```python
from ase.io import read, write
atoms = read('path/to/gpumd/train.xyz', index=0, format='extxyz')
atoms.calc = None; atoms.info = {}
atoms.arrays = {k: v for k, v in atoms.arrays.items()
                if k in ('numbers', 'positions')}
atoms = atoms[atoms.numbers.argsort()]
write('POSCAR', atoms, format='vasp', vasp5=True, sort=True)
```

### Step 2: VASP static SCF

Generate inputs via vaspkit:

```bash
echo -e "102\n1\n0.04" | vaspkit   # → KPOINTS (Γ-only) + POTCAR (Pb_d + Te)
```

INCAR (low-precision test):

```text
SYSTEM = PbTe pipeline test
ISTART = 0; ICHARG = 2
ENCUT  = 300          # above Pb_d ENMAX=237.8
PREC   = Normal; LREAL = Auto; EDIFF = 1E-4
NELM   = 40; ISMEAR = 0; SIGMA = 0.1
LWAVE = .FALSE.; LCHARG = .FALSE.; NCORE = 4
```

```bash
OMP_NUM_THREADS=1 mpirun -np 16 vasp_std > vasp.out 2> vasp.err
```

**Result**: converged in **15 DAV steps**, E = **−919.062 eV** (−3.676 eV/atom).

### Step 3: Convert to extxyz

```python
import dpdata
ds = dpdata.LabeledSystem('OUTCAR', fmt='vasp/outcar')
ds.to('extxyz', 'train.xyz')
# → 1 frame, 250 atoms, energy + forces + virial
```

### Step 4: NEP training

`nep.in`:

```text
type          2 Pb Te
version       4
cutoff        8 4
n_max         4 4
basis_size    8 8
l_max         4 2 0
neuron        30
generation    2000
batch         1000
population    50
lambda_e      1.0
lambda_f      1.0
lambda_v      0.1
```

```bash
nep    # reads nep.in + train.xyz, writes nep.txt + loss.out
```

**Result** (RTX 4090, 35.4 s):

| Metric | Value |
|--------|-------|
| Total loss | 0.137 |
| Energy RMSE | 0.000 eV/atom (1 frame → perfect fit) |
| Force RMSE | 0.068 eV/Å |
| L1 regularization | 0.028 |
| L2 regularization | 0.036 |

### Step 5: Plot loss curve

```python
import matplotlib.pyplot as plt
import numpy as np

data = np.loadtxt('loss.out')
gen = data[:, 0]

fig, axes = plt.subplots(2, 2, figsize=(12, 9))
fig.suptitle('NEP Training Loss')

axes[0,0].semilogy(gen, data[:,1], 'b-'); axes[0,0].set_title('Total Loss')
axes[0,1].semilogy(gen, data[:,4], 'r-'); axes[0,1].set_title('Energy RMSE')
axes[1,0].semilogy(gen, data[:,5], 'g-'); axes[1,0].set_title('Force RMSE')
axes[1,1].semilogy(gen, data[:,2], 'm-', label='L1')
axes[1,1].semilogy(gen, data[:,3], 'c-', label='L2')
axes[1,1].set_title('Regularization'); axes[1,1].legend()

for ax in axes.flat:
    ax.set_xlabel('Generation'); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig('loss_plot.png', dpi=150)
```

### loss.out column reference

| Col | Field | Description |
|:---:|-------|-------------|
| 0 | generation | training step (logged every 100) |
| 1 | loss_total | total weighted loss |
| 2 | loss_L1 | L1 regularization |
| 3 | loss_L2 | L2 regularization |
| 4 | RMSE_e_train | energy RMSE on train (eV/atom) |
| 5 | RMSE_f_train | force RMSE on train (eV/Å) |
| 6 | RMSE_v_train | virial RMSE on train (eV/atom) |
| 7 | RMSE_e_test | energy RMSE on test (eV/atom) |
| 8 | RMSE_f_test | force RMSE on test (eV/Å) |
| 9 | RMSE_v_test | virial RMSE on test (eV/atom) |

### Notes on this single-frame test

- Energy RMSE = 0 is expected — one frame is trivially fit.
- Force RMSE = 0.068 eV/Å is acceptable for a pipeline test but too high
  for production. Real training needs hundreds of diverse frames.
- No test set was used (`test.xyz` absent), so test columns are all zero.
- This example validates the **workflow plumbing**, not the potential quality.

## Key hyperparameters

### Descriptor

| Keyword       | Description                                       | Conservative default |
| ------------- | ------------------------------------------------- | -------------------- |
| `version`     | NEP generation / syntax                            | `4`                  |
| `cutoff`      | radial / angular cutoff in Å                      | `8 4`                |
| `n_max`       | radial / angular expansion depth                  | `4 4`                |
| `basis_size`  | radial / angular basis resolution                 | `8 8`                |
| `l_max`       | angular body complexity (3b / 4b / 5b)            | `4 2 0`              |
| `neuron`      | hidden-layer width of the fitting network          | `30`                 |

### Loss weights

| Keyword     | Target           | Typical                          |
| ----------- | ---------------- | -------------------------------- |
| `lambda_e`  | energy            | `1.0`                            |
| `lambda_f`  | force             | `1.0`                            |
| `lambda_v`  | virial            | `0.1` (or `0` if no virial data) |

### Training control

| Keyword      | Description               | Typical              |
| ------------ | ------------------------- | -------------------- |
| `batch`      | batch size                | `1000`               |
| `population` | evolutionary population   | `50`                 |
| `generation` | total generations         | `5000-200000`        |
| `zbl`        | ZBL short-range cap      | `0`=off, `1`=flexible, `2`=fixed universal |

**`zbl` values**: ZBL adds a universal repulsive core for close-range
encounters. Use `0` (off) for well-sampled equilibrium systems. Use `1`
for a flexible short-range correction fitted during training. Use `2` for
the fixed Ziegler-Biersack-Littmark universal potential — recommended for
reactive or radiation-damage datasets where atoms may approach very closely
but training data may not fully cover those configurations.

## Conservative tuning order

1. fix dataset quality first (coverage, label consistency, species order)
2. confirm headers parse (`validate_extxyz_headers.py`)
3. train a baseline with the defaults above
4. inspect `loss.out` and parity
5. run a short MD sanity test
6. **only then** change descriptor complexity or loss weights

Skipping steps 1-5 and jumping straight to bigger `neuron` or `l_max` almost
always makes the model larger without making it better.

## Agent checklist

- [ ] `train.xyz` and `test.xyz` header-validated
- [ ] species order in `type` matches the dataset and any downstream GPUMD
      `model.xyz`
- [ ] units consistent (Å, eV, eV/Å)
- [ ] virial convention stated (or `lambda_v 0`)
- [ ] `nep.in` baseline matches conservative defaults
- [ ] `loss.out` free of NaN / inf
- [ ] short downstream MD sanity test passed
- [ ] `nep.txt` and `nep.restart` saved for later fine-tuning

## Read first

- [references/dataset-and-inputs.md](../references/dataset-and-inputs.md)
- [references/training-evaluation-deployment.md](../references/training-evaluation-deployment.md)

Read when needed:

- [references/nep-keyword-cheatsheet.md](../references/nep-keyword-cheatsheet.md)
- [references/labels-from-dft.md](../references/labels-from-dft.md)
- [references/auxiliary-properties.md](../references/auxiliary-properties.md)

## Bundled templates and helpers

- [assets/examples/baseline/nep.in](../assets/examples/baseline/nep.in)
- [assets/examples/baseline/train.xyz](../assets/examples/baseline/train.xyz)
- [assets/examples/baseline/test.xyz](../assets/examples/baseline/test.xyz)
- [validate_extxyz_headers.py](../scripts/validate_extxyz_headers.py)
- [scripts/summarize_nep_loss.py](../scripts/summarize_nep_loss.py)
- [scripts/split_train_test.py](../scripts/split_train_test.py)
- [scripts/parity_from_nep_outputs.py](../scripts/parity_from_nep_outputs.py)

## References

- NEP documentation: <https://gpumd.org/nep/index.html>
- `nep.in`: <https://gpumd.org/nep/input_files/nep_in.html>
- `train.xyz` / `test.xyz`: <https://gpumd.org/nep/input_files/train_test_xyz.html>
- GPUMD-Tutorials: `11_NEP_potential_PbTe`
