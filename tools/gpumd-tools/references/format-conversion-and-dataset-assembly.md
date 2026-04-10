# Format Conversion And Dataset Assembly

## When to read this file

Read this file when the user needs to turn another code's output into GPUMD or NEP input.

## 1. Target formats

The common targets are:

- GPUMD `model.xyz`
- NEP `train.xyz`
- NEP `test.xyz`

The important point is not the filename but the header semantics:

- cell
- periodicity
- total energy
- forces
- virial or stress convention if used

## 2. Common source-to-target routes

| Source code | Likely tool path |
| --- | --- |
| VASP | `GPUMD/tools/Format_Conversion/vasp2xyz` or GPUMDkit wrappers |
| CP2K | `GPUMD/tools/Format_Conversion/cp2k2xyz` |
| ABACUS | `GPUMD/tools/Format_Conversion/abacus2xyz` |
| SIESTA | `GPUMD/tools/Format_Conversion/siesta2xyz` |
| DeepMD datasets | `GPUMD/tools/Format_Conversion/dp2xyz` |

### Alternative: `dpdata-cli`

`dpdata` (`dpdata-cli` skill) is a widely-used alternative for format
conversion. It supports reading from VASP, CP2K, QE, DeepMD, and 50+
other formats, and can export to extxyz via `System.to('extxyz')`. Use
alongside or instead of the native GPUMD converters when dpdata is
already in the workflow.

**Note**: verify the virial sign convention after dpdata conversion —
VASP stress is −virial/V, and while dpdata handles the conversion, the
result should be cross-checked against a known simple system before
training.

## 3. Practical conversion rules

Before trusting a converted dataset:

- inspect one or two frames manually
- verify species order
- verify total energy, not per-atom energy, is what the labeler produced
- verify force units are `eV/Å`
- verify virial or stress conventions before merging datasets

Then run a header validator from the relevant installed skill:

- `scripts/validate_extxyz_headers.py` for both `train.xyz`/`test.xyz` (`--mode train`) and `model.xyz` (`--mode model`)

## 4. Group labels and workflow-specific preprocessing

Some GPUMD workflows need more than bare coordinates.

Examples:

- layered-system transport may need `group:I:M`
- SHC workflows may need group definitions consistent with `compute_shc`
- frame-selection workflows may need dataset splitting or FPS-like selection

Relevant upstream helpers:

- `add_groups`
- `select_xyz_frames`
- `split_xyz`
- `pca_sampling`

## 5. What not to vendor into the skill tree

Do not copy large raw training datasets into the skill repository unless they are intentionally part of the skill output.

Instead:

- keep small example frames in `assets/examples/`
- keep the large source dataset external
- document the conversion or extraction path in references
