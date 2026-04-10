# NEP Keyword Cheatsheet

## When to read this file

Read this file when you need a quick lookup of every `nep.in` keyword,
its syntax, and its default value.

## Model definition

| Keyword      | Syntax                        | Default    | Notes |
| ------------ | ----------------------------- | ---------- | ----- |
| `type`       | `type N sp1 sp2 …`           | (required) | N = number of species. Species order is load-bearing — must match dataset and downstream GPUMD `model.xyz`. |
| `version`    | `version V`                   | `4`        | NEP generation. Use `4` unless reproducing legacy NEP3. |
| `model_type` | `model_type M`                | `0`        | `0` = potential (E/F/V), `1` = dipole, `2` = polarizability. |

## Descriptor

| Keyword      | Syntax                        | Default    | Notes |
| ------------ | ----------------------------- | ---------- | ----- |
| `cutoff`     | `cutoff r_rad r_ang`          | `8 4`      | Radial / angular cutoff in Å. |
| `n_max`      | `n_max n_rad n_ang`           | `4 4`      | Radial / angular expansion order. |
| `basis_size` | `basis_size b_rad b_ang`      | `8 8`      | Number of basis functions per channel. |
| `l_max`      | `l_max l3 l4 l5`             | `4 2 0`    | Max angular order for 3-body / 4-body / 5-body. Set `l5=1` for reactive systems. |

## Network

| Keyword  | Syntax       | Default | Notes |
| -------- | ------------ | ------- | ----- |
| `neuron` | `neuron N`   | `30`    | Hidden-layer width. 30–100 is the typical range. |

## Loss weights

| Keyword    | Syntax          | Default | Notes |
| ---------- | --------------- | ------- | ----- |
| `lambda_e` | `lambda_e W`    | `1.0`   | Energy loss weight. |
| `lambda_f` | `lambda_f W`    | `1.0`   | Force loss weight. |
| `lambda_v` | `lambda_v W`    | `0.1`   | Virial loss weight. Set `0` if no virial labels. |
| `lambda_shear` | `lambda_shear W` | `1.0` | Weight for shear components of the virial (NEP4). |

## Training control

| Keyword      | Syntax             | Default  | Notes |
| ------------ | ------------------ | -------- | ----- |
| `batch`      | `batch B`          | `1000`   | Mini-batch size (frames). |
| `population` | `population P`     | `50`     | Evolutionary population size. |
| `generation` | `generation G`     | `100000` | Total training generations. 5000 for quick tests, 100k–200k for production. |

## Short-range correction

| Keyword | Syntax    | Default | Notes |
| ------- | --------- | ------- | ----- |
| `zbl`   | `zbl Z`   | `0`     | `0` = off, `1` = flexible inner cutoff, `2` = fixed universal ZBL. Use `2` for reactive / radiation-damage data. |

## Fine-tuning

| Keyword     | Syntax                                  | Notes |
| ----------- | --------------------------------------- | ----- |
| `fine_tune` | `fine_tune base.txt base.restart`       | Initializes weights from a pre-trained model. Descriptor parameters must match. |
| `prediction`| `prediction 1`                          | Evaluates the existing model without training. Writes parity outputs. |

## Multi-GPU / parallelism

NEP training uses a single GPU. Multi-GPU parallelism is not currently
supported in the `nep` binary (it is available in `gpumd` for MD).

## Output files

| File                 | Content |
| -------------------- | ------- |
| `nep.txt`            | Trained model (portable). |
| `nep.restart`        | Internal state for fine-tuning / restart. |
| `loss.out`           | Per-generation training and test loss. |
| `energy_train.out`   | Energy parity (DFT vs. NEP) on training set. |
| `energy_test.out`    | Energy parity on test set. |
| `force_train.out`    | Force parity on training set. |
| `force_test.out`     | Force parity on test set. |
| `virial_train.out`   | Virial parity (if virials used). |
| `virial_test.out`    | Virial parity on test set. |
| `dipole_train.out`   | Dipole parity (model_type 1). |
| `polarizability_train.out` | Polarizability parity (model_type 2). |

## References

- `nep.in` documentation: <https://gpumd.org/nep/input_files/nep_in.html>
- `train.xyz` / `test.xyz`: <https://gpumd.org/nep/input_files/train_test_xyz.html>
