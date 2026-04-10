# GPUMD Agent Skills

A focused skill collection for the **GPUMD** and **NEP** ecosystem,
designed for AI-assisted molecular dynamics and machine-learning
potential workflows.

It follows the same architecture as `computational-chemistry-agent-skills`:

- keep each skill narrow and reusable
- keep routing logic in `SKILL.md`
- keep detailed knowledge in `references/`
- keep reusable templates in `assets/examples/`
- keep deterministic helpers in `scripts/`

## Skill map

### `molecular-dynamics/gpumd`

GPUMD task router with subskills for:

| Subskill    | Scope                                                          |
| ----------- | -------------------------------------------------------------- |
| `md`        | General MD: `model.xyz`, `run.in`, ensembles, dump, potentials |
| `phonon`    | Phonon dispersion and DOS via `compute_phonon`                 |
| `transport` | Thermal transport: EMD (Green-Kubo), HNEMD, NEMD, SHC          |
| `diffusion` | MSD-based diffusion, ionic conductivity, viscosity             |
| `elastic`   | Elastic constants via strain-fluctuation or stress-strain      |
| `mechanics` | Non-equilibrium mechanics: friction, deposition, indentation   |

**References**: keyword cheatsheet, core files & ensembles, phonon workflow,
thermal transport workflow, diffusion/viscosity, elastic constants,
mechanics/deposition/friction, tutorial map.

**Scripts**: `average_hnemd_kappa.py`, `parse_thermo.py`,
`fit_msd_diffusion.py`.

### `machine-learning-potentials/nep-gpumd`

NEP task router with subskills for:

| Subskill     | Scope                                                       |
| ------------ | ----------------------------------------------------------- |
| `train`      | First NEP potential from labeled extxyz data                |
| `fine-tune`  | Prediction mode, NEP89 evaluation, fine-tuning from restart |
| `automation` | NepTrain / NepTrainKit active-learning and dataset curation |

**References**: dataset & inputs, training/evaluation/deployment,
fine-tuning playbook, keyword cheatsheet, auxiliary properties
(dipole/polarizability), labels from DFT.

**Scripts**: `summarize_nep_loss.py`, `split_train_test.py`,
`parity_from_nep_outputs.py`.

**Templates**: baseline, prediction, fine-tune, nep89, dipole,
polarizability, neptrain.

### `tools/gpumd-tools`

Tooling layer for:

- DFT-to-extxyz format conversion (VASP, CP2K, ABACUS, SIESTA, etc.)
- Dataset curation (splitting, frame selection, group labels)
- Upstream `GPUMD/tools` inventory
- GPUMDkit, calorine, gpyumd, PyNEP ecosystem
- Tutorial and example lookup

**Scripts**: `validate_extxyz_headers.py` (shared),
`bootstrap_gpumd_tool_sources.sh`, `index_local_gpumd_sources.py`.

## File tree overview

```text
molecular-dynamics/gpumd/
├── SKILL.md                    # router
├── md/SKILL.md                 # general MD
├── phonon/SKILL.md             # phonon
├── transport/SKILL.md          # thermal transport
├── diffusion/SKILL.md          # diffusion / viscosity
├── elastic/SKILL.md            # elastic constants
├── mechanics/SKILL.md          # friction / deposition
├── references/                 # 8 reference docs
├── assets/examples/            # run.in + model.xyz templates
└── scripts/                    # 4 helper scripts

machine-learning-potentials/nep-gpumd/
├── SKILL.md                    # router
├── train/SKILL.md              # training
├── fine-tune/SKILL.md          # prediction + fine-tune
├── automation/SKILL.md         # NepTrain / NepTrainKit
├── references/                 # 6 reference docs
├── assets/examples/            # nep.in + extxyz templates
└── scripts/                    # 4 helper scripts

tools/gpumd-tools/
├── SKILL.md                    # tooling router
├── references/                 # 3 reference docs
└── scripts/                    # 2 helper scripts
```

## Design choices

- The old monolithic GPUMD+NEP skill has been split by workflow boundary
  instead of by software name alone.
- Large upstream example repositories are treated as references, not
  vendored wholesale into the skill tree.
- Only small, high-reuse templates are bundled into `assets/examples/`.
- Local tool-source checkouts remain reproducible through
  `tools/gpumd-tools/scripts/bootstrap_gpumd_tool_sources.sh`.
- Each subskill follows the same pattern: agent checklist, annotated
  workflow, bundled templates, references, and expected output.

## Reference sources

- GPUMD upstream repository (<https://github.com/brucefan1983/GPUMD>)
- GPUMD documentation (<https://gpumd.org>)
- GPUMD-Tutorials (<https://github.com/brucefan1983/GPUMD-Tutorials>)
- NepTrain (<https://github.com/aboys-cb/NepTrain>)
- NepTrainKit (<https://github.com/aboys-cb/NepTrainKit>)
- `computational-chemistry-agent-skills`
