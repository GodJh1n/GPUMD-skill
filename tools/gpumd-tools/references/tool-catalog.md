# GPUMD Tool Catalog

## When to read this file

Read this file when the task is primarily about tooling rather than GPUMD physics.

## 1. Three tooling layers

### Upstream `GPUMD/tools`

This is the most direct layer.

Main categories from upstream:

- `Format_Conversion`
- `Analysis_and_Processing`
- `Miscellaneous`

Use it when:

- you want the original script, not a wrapper
- you need to inspect exact converter behavior
- GPUMDkit hides too much

### GPUMDkit

This is the convenience-wrapper layer.

Use it when:

- there is already a mature wrapper for the needed conversion or plotting task
- the task is routine and you want less command plumbing

### Tutorial repositories

Use GPUMD-Tutorials when:

- you need a complete runnable example
- you need a parameter pattern for a specific observable

Do not confuse tutorials with formal documentation. Always recheck syntax against current docs.

## 2. High-value upstream tool categories

### Format conversion

Useful subdirectories include:

- `vasp2xyz`
- `cp2k2xyz`
- `abacus2xyz`
- `dp2xyz`
- `orca2xyz`
- `siesta2xyz`

Use these when the main task is moving labeled data into NEP-compatible extxyz.

### Analysis and processing

Useful subdirectories include:

- `add_groups`
- `pca_sampling`
- `select_xyz_frames`
- `split_xyz`
- `shift_energy_to_zero`
- `get_max_rmse_xyz`

Use these when dataset curation or frame selection is the goal.

## 3. Adjacent packages worth knowing

The upstream GPUMD tools README also points to related packages:

- `calorine`
- `gpyumd`
- `GPUMDkit`
- `NepTrain`
- `NepTrainKit`
- `PyNEP`

These are complementary, not interchangeable.

## 4. How to choose the layer

Choose the lightest layer that still matches the task:

1. direct upstream script if the transformation is simple
1. GPUMDkit if an established wrapper exists
1. tutorial repository if you need a complete workflow example

## 5. Local helper scripts

- bootstrap missing repositories: `scripts/bootstrap_gpumd_tool_sources.sh`
- search local tool and tutorial trees: `scripts/index_local_gpumd_sources.py`

