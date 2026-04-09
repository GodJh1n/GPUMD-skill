# Tutorial And Workflow Map

## When to read this file

Read this file when you need to locate the best local example rapidly.

## 1. Best local anchors by task

| Task | Example anchor |
| --- | --- |
| basic harmonic phonons | `06_Silicon_phonon_dispersion` |
| EMD thermal conductivity | `03_Carbon_thermal_transport_emd` |
| HNEMD and SHC | `04_Carbon_thermal_transport_nemd_and_hnemd` |
| first NEP model | `11_NEP_potential_PbTe` |
| NEP fine-tuning from NEP89 | `26_fine_tune_NEP89` |
| ionic conductivity | `24_Ionic_Conductivity` |
| multicomponent HNEMDEC | `29_thermal_transport_multicomponent_HNEMDEC` |
| friction / interface dynamics | `31_Nanoribbon_friction` |

## 2. Searching local sources

Use the bundled search helper when the local tool and tutorial trees are available:

```bash
python scripts/index_local_gpumd_sources.py phonon
python scripts/index_local_gpumd_sources.py hnemd --category tutorial
python scripts/index_local_gpumd_sources.py vasp2xyz --category tool
```

The script searches:

- local GPUMD-Tutorials tree
- local GPUMD upstream tree
- local `GPUMD/tools`

## 3. Bootstrapping sources

If the local trees are missing:

```bash
bash scripts/bootstrap_gpumd_tool_sources.sh
```

That fetches:

- GPUMD
- GPUMD-Tutorials
- GPUMDkit
- NepTrain
- NepTrainKit

