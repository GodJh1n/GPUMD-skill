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
   python ../../../tools/gpumd-tools/scripts/validate_extxyz_headers.py train.xyz --mode train
   python ../../../tools/gpumd-tools/scripts/validate_extxyz_headers.py test.xyz --mode train
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
generation   5000
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
- `batch 1000`, `population 50`, `generation 5000`
  - Training control. Increase `generation` for a final production fit
    after hyperparameters are settled.

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
| `zbl`        | ZBL short-range cap      | `2` for reactive data |

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
- [validate_extxyz_headers.py](../../../tools/gpumd-tools/scripts/validate_extxyz_headers.py)
- [scripts/summarize_nep_loss.py](../scripts/summarize_nep_loss.py)
- [scripts/split_train_test.py](../scripts/split_train_test.py)
- [scripts/parity_from_nep_outputs.py](../scripts/parity_from_nep_outputs.py)

## References

- NEP documentation: <https://gpumd.org/nep/index.html>
- `nep.in`: <https://gpumd.org/nep/input_files/nep_in.html>
- `train.xyz` / `test.xyz`: <https://gpumd.org/nep/input_files/train_test_xyz.html>
- GPUMD-Tutorials: `11_NEP_potential_PbTe`
