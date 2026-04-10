# NEP Dataset And Inputs

## When to read this file

Read this file when the task is about:

- `nep.in`
- `train.xyz`
- `test.xyz`
- extxyz labeling conventions for NEP
- unit and header consistency

## 1. `nep.in`

`nep.in` is the control file for NEP training or prediction.

Absolute minimum:

```text
type 1 Si
```

A conservative baseline for a first NEP4 fit is:

```text
type         1 Si
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

> **Note**: `generation 5000` is only useful as a quick smoke test.
> Production fits typically need 50000–200000 generations. Start with
> `100000` and increase if the `loss.out` curve has not plateaued.

Key rule:

- the species order in `type` must match the species naming used in the dataset

## 2. `train.xyz` and `test.xyz`

These are concatenated labeled extxyz frames.

Minimum useful requirements for supervised fitting:

- atom count
- `Lattice="..."`
- total `energy=...` or equivalent header field
- `Properties=species:S:1:pos:R:3:force:R:3`

Optional but important fields:

- `virial="..."`
- `stress="..."`
- `config_type=...`
- `weight=...`

Minimal example:

```text
2
Lattice="5.43 0 0 0 5.43 0 0 0 5.43" pbc="T T T" energy=-10.860000 Properties=species:S:1:pos:R:3:force:R:3
Si 0.000000 0.000000 0.000000  0.0010 -0.0020  0.0030
Si 1.357500 1.357500 1.357500 -0.0010  0.0020 -0.0030
```

Bundled small examples:

- `assets/examples/baseline/train.xyz`
- `assets/examples/baseline/test.xyz`

## 3. Units and conventions

Keep units consistent across the whole dataset:

- positions: `Å`
- total energy: `eV`
- forces: `eV/Å`

Virials and stresses are the most common place where datasets become inconsistent.

Before merging datasets from different converters:

- confirm sign convention
- confirm whether the header is stress or virial
- confirm whether the quantity is total-cell or normalized

## 4. Dataset quality rules

The first thing to fix is data quality, not hyperparameters.

A training dataset should cover the states that matter downstream:

- near-equilibrium bulk
- strained cells if elasticity matters
- finite-temperature snapshots if MD is the target
- defects, surfaces, interfaces, or chemistry changes if the intended application needs them

## 5. Header validation

Use the bundled checker before training:

```bash
python tools/gpumd-tools/scripts/validate_extxyz_headers.py train.xyz --mode train
python tools/gpumd-tools/scripts/validate_extxyz_headers.py test.xyz --mode train
```

This catches:

- missing `Lattice`
- malformed `Properties`
- missing training energies
- missing force columns
- row/column mismatches

## 6. Prediction mode

Prediction mode is a special use of `nep.in`:

```text
prediction 1
```

Use it to evaluate an existing model on a labeled dataset before deciding whether fine-tuning is justified.

## References

- NEP docs: <https://gpumd.org/nep/index.html>
- `nep.in` docs: <https://gpumd.org/nep/input_files/nep_in.html>
- `train.xyz` / `test.xyz` docs: <https://gpumd.org/nep/input_files/train_test_xyz.html>
