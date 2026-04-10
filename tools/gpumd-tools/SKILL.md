---
name: gpumd-tools
description: >
  Tooling layer for GPUMD helper repositories, format converters, dataset
  curation, and local example discovery. Use when the user needs GPUMDkit,
  upstream `GPUMD/tools`, GPUMD-Tutorials lookup, DFT-to-extxyz conversion,
  frame selection, dataset splitting, or bootstrapping the local GPUMD
  tool-source ecosystem.
compatibility: >
  Optional local checkouts of GPUMD, GPUMD-Tutorials, GPUMDkit, NepTrain,
  and NepTrainKit. If absent, use the bundled bootstrap script to clone them.
license: LGPL-3.0-or-later
metadata:
  author: Codex
  version: 0.2.0
---

# GPUMD Tooling

Use this skill when the task is primarily about auxiliary tooling rather
than GPUMD physics or NEP fitting alone. This covers:

- DFT output → NEP extxyz conversion
- Dataset inspection, splitting, and frame selection
- Group-label manipulation for GPUMD workflows
- Locating upstream tools and tutorial examples
- Bootstrapping and indexing local GPUMD source trees

## Agent responsibilities

1. Identify which tooling layer is appropriate for the task.
2. Prefer the lightest tool that solves the problem.
3. Validate converted datasets before passing them to NEP training.
4. Warn when mixing datasets from different DFT codes or conventions.

## Three tooling layers

| Layer | What it is | When to use |
| ----- | ---------- | ----------- |
| **Upstream `GPUMD/tools`** | Original scripts from the GPUMD repo | Direct conversion, inspection of exact behavior |
| **GPUMDkit** | Python convenience wrappers | Routine tasks where a mature wrapper exists |
| **Tutorial repositories** | Complete runnable examples | Parameter patterns, workflow reference |

### Source priority

When tools disagree or wrappers hide details, follow this order:

1. Current official GPUMD documentation
2. The upstream script or README in `GPUMD/tools`
3. GPUMDkit wrapper behavior
4. Tutorial notebooks and third-party blog posts

## Upstream `GPUMD/tools` directory

### Format conversion (`Format_Conversion/`)

| Subdirectory    | Source code | Notes |
| --------------- | ----------- | ----- |
| `vasp2xyz`      | VASP        | Reads OUTCAR. Most tested path. |
| `cp2k2xyz`      | CP2K        | Reads CP2K output + force files. |
| `abacus2xyz`    | ABACUS      | Reads ABACUS output. |
| `siesta2xyz`    | SIESTA      | Reads SIESTA `.out` + `.FA`. |
| `castep2xyz`    | CASTEP      | Reads CASTEP output. |
| `orca2xyz`      | ORCA        | Molecular (cluster) calculations. |
| `dp2xyz`        | DeepMD      | Converts DeepMD `raw` / `npy` format. |
| `runner2xyz`    | RUNNER      | Converts RUNNER format. |

### Analysis and processing (`Analysis_and_Processing/`)

| Subdirectory         | Purpose |
| -------------------- | ------- |
| `add_groups`         | Add group labels to `model.xyz` for SHC / transport workflows. |
| `pca_sampling`       | PCA-based frame selection from descriptor space. |
| `select_xyz_frames`  | Select specific frames by index or criterion. |
| `split_xyz`          | Split a concatenated extxyz into subsets. |
| `shift_energy_to_zero` | Shift energy reference (normalize). |
| `get_max_rmse_xyz`   | Find frames with highest prediction error. |

### Adjacent ecosystem packages

| Package        | Role | Install |
| -------------- | ---- | ------- |
| **calorine**   | Python interface for NEP + GPUMD | `pip install calorine` |
| **gpyumd**     | Python wrapper for GPUMD I/O | `pip install gpyumd` |
| **GPUMDkit**   | Dataset curation + workflow wrappers | `pip install GPUMDkit` |
| **NepTrain**   | Active-learning loop automation | `pip install neptrain` |
| **NepTrainKit**| GUI dataset inspector | `pip install NepTrainKit` |
| **PyNEP**      | Python bindings for NEP inference | `pip install pynep` |

## Dataset curation playbook

### Step 1. Convert from DFT

Use the appropriate converter from `Format_Conversion/`. Verify:

- species order matches your intended `type` line
- energy is total (not per-atom)
- forces are in eV/Å
- virial/stress sign and unit convention

### Step 2. Validate headers

```bash
python scripts/validate_extxyz_headers.py all.xyz --mode train
```

### Step 3. Split train/test

```bash
python scripts/split_train_test.py all.xyz --ratio 0.9 --seed 42
```

(The `split_train_test.py` script is in the NEP skill's `scripts/` dir.)

### Step 4. Inspect distribution

Check for:

- energy outliers (histogram)
- force magnitude consistency
- frame count per config_type
- spatial coverage (if PCA tools available)

### Step 5. Select representative frames (optional)

For large datasets, use FPS or PCA sampling:

```bash
# upstream tool
python GPUMD/tools/Analysis_and_Processing/pca_sampling/pca_sampling.py \
    train.xyz --n-select 500
```

Or use NepTrainKit for interactive selection.

### Step 6. Add group labels (if needed)

For transport workflows needing spatial grouping:

```bash
python GPUMD/tools/Analysis_and_Processing/add_groups/add_groups.py \
    model.xyz --direction z --n-groups 10
```

## Working rules

- Prefer lightweight upstream scripts when the transformation is simple
  and deterministic.
- Prefer GPUMDkit when a wrapper already exists and its assumptions
  match the task.
- Use tutorial examples as seeds, not as unquestioned canonical inputs.
- Do not silently mix datasets converted with incompatible energy or
  virial conventions.
- Always validate after conversion, not just before training.

## Read only what is needed

- Tool inventory: [references/tool-catalog.md](references/tool-catalog.md)
- DFT-to-extxyz conversion: [references/format-conversion-and-dataset-assembly.md](references/format-conversion-and-dataset-assembly.md)
- Tutorial map: [references/tutorial-and-workflow-map.md](references/tutorial-and-workflow-map.md)

## Bundled scripts

- [scripts/bootstrap_gpumd_tool_sources.sh](scripts/bootstrap_gpumd_tool_sources.sh) — clone missing repos
- [scripts/index_local_gpumd_sources.py](scripts/index_local_gpumd_sources.py) — search local tool/tutorial trees

## Cross-skill pointers

- NEP training from labeled data → `nep-gpumd/train`
- DFT labeling workflow → `nep-gpumd` references: `labels-from-dft.md`
- Running MD with converted `model.xyz` → `molecular-dynamics/gpumd`
