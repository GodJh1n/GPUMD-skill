# GPUMD Tool Catalog

## When to read this file

Read this file when the task is primarily about tooling rather than
GPUMD physics. It provides a comprehensive inventory of available tools
across the GPUMD ecosystem.

## 1. Three tooling layers

### Upstream `GPUMD/tools`

The most direct layer. Contains original scripts maintained alongside
the GPUMD source code.

Main categories:

- `Format_Conversion/` — DFT output → extxyz
- `Analysis_and_Processing/` — dataset curation, group labels, frame
  selection
- `Miscellaneous/` — utility scripts

Use it when:

- you want the original script, not a wrapper
- you need to inspect exact converter behavior
- GPUMDkit hides too much

### GPUMDkit

Convenience-wrapper layer providing a unified Python interface for
common GPUMD/NEP workflows.

Use it when:

- a mature wrapper already exists for the needed conversion or plotting
- the task is routine and you want less command plumbing
- you need combined workflows (convert + validate + split in one call)

### Tutorial repositories

GPUMD-Tutorials provides complete runnable examples.

Use it when:

- you need a complete workflow reference
- you need a parameter pattern for a specific observable

Do not confuse tutorials with formal documentation. Always recheck
syntax against current docs.

## 2. Full upstream tool inventory

### Format conversion (`Format_Conversion/`)

| Subdirectory    | Source → Target                        | Key files |
| --------------- | -------------------------------------- | --------- |
| `vasp2xyz`      | VASP OUTCAR → extxyz                   | `outcar2xyz.py` |
| `cp2k2xyz`      | CP2K output → extxyz                   | `cp2k2xyz.py` |
| `abacus2xyz`    | ABACUS output → extxyz                 | `abacus2xyz.py` |
| `siesta2xyz`    | SIESTA `.out` + `.FA` → extxyz         | `siesta2xyz.py` |
| `castep2xyz`    | CASTEP output → extxyz                 | `castep2xyz.py` |
| `orca2xyz`      | ORCA output → extxyz (molecular)       | `orca2xyz.py` |
| `dp2xyz`        | DeepMD `raw` / `npy` → extxyz          | `dp2xyz.py` |
| `runner2xyz`    | RUNNER format → extxyz                 | `runner2xyz.py` |
| `xyz2gro`       | extxyz → GROMACS `.gro`                | `xyz2gro.py` |
| `cif2xyz`       | CIF → extxyz                           | `cif2xyz.py` |

### Analysis and processing (`Analysis_and_Processing/`)

| Subdirectory           | Purpose                                                |
| ---------------------- | ------------------------------------------------------ |
| `add_groups`           | Add `group:I:M` to model.xyz for SHC / NEMD grouping  |
| `pca_sampling`         | PCA-based farthest-point sampling of descriptor space  |
| `select_xyz_frames`    | Select frames by index, range, or stride               |
| `split_xyz`            | Split concatenated extxyz into multiple files           |
| `shift_energy_to_zero` | Shift energy reference to zero (for mixing datasets)   |
| `get_max_rmse_xyz`     | Find frames with highest NEP prediction error          |
| `merge_xyz`            | Merge multiple extxyz files                            |
| `sample_xyz`           | Random sampling of frames                              |
| `compute_rdf`          | Compute radial distribution function from extxyz       |

### Miscellaneous

| Tool                   | Purpose                                                |
| ---------------------- | ------------------------------------------------------ |
| `create_xyz`           | Build simple crystal structures in extxyz format       |
| `perturb_xyz`          | Apply random perturbations to atomic positions         |

## 3. Adjacent ecosystem packages

| Package        | Role                                    | Language | Install |
| -------------- | --------------------------------------- | -------- | ------- |
| **calorine**   | Python interface for NEP + GPUMD I/O    | Python   | `pip install calorine` |
| **gpyumd**     | Python wrapper for GPUMD input/output   | Python   | `pip install gpyumd` |
| **GPUMDkit**   | Dataset curation + workflow automation  | Python   | `pip install GPUMDkit` |
| **NepTrain**   | Active-learning loop automation         | Python   | `pip install neptrain` |
| **NepTrainKit**| GUI dataset inspector + outlier finder  | Python   | `pip install NepTrainKit` |
| **PyNEP**      | Python bindings for NEP inference       | Python   | `pip install pynep` |
| **GPUMD**      | Core MD engine + NEP trainer            | C++/CUDA | Build from source |

### When to use each package

| Task | Recommended |
| ---- | ----------- |
| Quick NEP inference in Python | PyNEP or calorine |
| Read/write GPUMD files in Python | gpyumd or calorine |
| Automated active-learning loop | NepTrain |
| Interactive dataset inspection | NepTrainKit |
| Workflow automation + conversion wrappers | GPUMDkit |
| Production MD + NEP training | GPUMD (native) |

## 4. Choosing the right layer

Choose the lightest layer that still matches the task:

1. **Direct upstream script** — if the transformation is simple and
   deterministic (e.g. one-off VASP → extxyz conversion)
2. **GPUMDkit** — if an established wrapper exists and its assumptions
   match
3. **calorine / gpyumd** — for programmatic access from Python scripts
4. **Tutorial repository** — for complete workflow examples

## 5. Local helper scripts

| Script | Purpose |
| ------ | ------- |
| `scripts/bootstrap_gpumd_tool_sources.sh` | Clone missing repositories (GPUMD, Tutorials, GPUMDkit, NepTrain, NepTrainKit) |
| `scripts/index_local_gpumd_sources.py` | Search local tool and tutorial trees by keyword |

Usage:

```bash
# Bootstrap all sources
bash scripts/bootstrap_gpumd_tool_sources.sh

# Search for a tool or tutorial
python scripts/index_local_gpumd_sources.py phonon
python scripts/index_local_gpumd_sources.py hnemd --category tutorial
python scripts/index_local_gpumd_sources.py vasp2xyz --category tool
```
