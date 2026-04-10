# GPUMD Agent Skills

This repository is a focused skill collection for the **GPUMD** and **NEP**
ecosystem, designed for AI-assisted molecular dynamics, lattice dynamics,
thermal transport, and NEP potential workflows.

It follows the same basic architecture as
`computational-chemistry-agent-skills`:

- keep each top-level skill narrow and reusable
- keep routing logic in `SKILL.md`
- keep detailed knowledge in `references/`
- keep reusable templates in `assets/examples/`
- keep deterministic helpers in `scripts/`

## Install the skills

You only need to install the **three top-level skills** in this repository:

- `molecular-dynamics/gpumd`
- `machine-learning-potentials/nep-gpumd`
- `tools/gpumd-tools`

### Option 1: clone the repository

```bash
git clone https://github.com/GodJh1n/GPUMD-skill.git
cd GPUMD-skill
```

### Option 2: download ZIP

1. Download: <https://github.com/GodJh1n/GPUMD-skill/archive/refs/heads/main.zip>
2. Unzip it to get the repository folder
3. Enter the repository root

### Install into OpenClaw / skills runtime

From the repository root, run:

```bash
npx -y skills add ./molecular-dynamics/gpumd -a openclaw -y
npx -y skills add ./machine-learning-potentials/nep-gpumd -a openclaw -y
npx -y skills add ./tools/gpumd-tools -a openclaw -y
```

Notes:

- Omit `-g` to install into the current workspace's local `./skills/`
  directory.
- Add `-g` if you explicitly want a global install.
- Start a **new** OpenClaw / Codex session after installation so the skills are
  reloaded.

### Verify installation

```bash
openclaw skills list --eligible
```

If your runtime does not expose `openclaw`, use the equivalent `skills list`
command provided by your host environment.

## Use the skills

The intended usage pattern is **route by scientific objective**, not by
repository folder.

### Example prompts

- `Use GPUMD to prepare a 300 K NVT -> NVE thermal conductivity workflow for graphene with compute_hac.`
- `Write a GPUMD compute_phonon input set for silicon, including model.xyz, run.in, and kpoints.in.`
- `Prepare a baseline NEP4 training workflow from train.xyz and test.xyz, then explain which nep.in parameters matter first.`
- `Evaluate whether NEP89 is good enough for MoS2 thermal conductivity before fine-tuning.`
- `Convert VASP outputs to NEP-compatible extxyz and tell me whether the virial convention is safe to mix with my current dataset.`

### Optional: bootstrap local upstream tool sources

If you want the local mirrors of GPUMD, GPUMD-Tutorials, GPUMDkit, NepTrain,
and NepTrainKit:

```bash
bash tools/gpumd-tools/scripts/bootstrap_gpumd_tool_sources.sh
```

This is optional. The installable skills are the three directories listed
above, not the mirrored upstream repositories.

## Skills summary

### Top-level skills

| Skill | Description | Version | Compatibility |
| --- | --- | --- | --- |
| [gpumd](molecular-dynamics/gpumd/SKILL.md) | Route GPUMD requests to task-specific subskills. GPUMD is a GPU-accelerated molecular dynamics code that pairs naturally with NEP machine-learning potentials. Use when the user asks for GPUMD MD, `model.xyz`, `run.in`, harmonic phonons via `compute_phonon`, thermal transport via EMD/HNEMD/NEMD, diffusion and ionic conductivity, elastic constants, melting, friction, or deposition workflows. | 0.2.0 | Requires a runnable GPUMD environment. The user must supply the `gpumd` executable path, HPC module, or container entry point. A compatible potential file (`nep.txt`, `nep89_*.txt`, Tersoff, etc.) is required. |
| [nep-gpumd](machine-learning-potentials/nep-gpumd/SKILL.md) | Route NEP requests to task-specific subskills. NEP (Neuroevolution Potential) is the native machine-learning potential family of the GPUMD ecosystem — analogous to DeePMD-kit for LAMMPS. Use when the user asks for `nep.in`, `train.xyz`, `test.xyz`, NEP training, NEP89 reuse, prediction mode, fine-tuning, dipole / polarizability auxiliary models, or automation via NepTrain / NepTrainKit. | 0.2.0 | Requires a NEP-capable GPUMD build providing the `nep` executable (usually shipped together with `gpumd` in modern releases). Training needs labeled datasets in NEP-compatible extxyz format. |
| [gpumd-tools](tools/gpumd-tools/SKILL.md) | Tooling layer for GPUMD helper repositories, format converters, dataset curation, and local example discovery. Use when the user needs GPUMDkit, upstream `GPUMD/tools`, GPUMD-Tutorials lookup, DFT-to-extxyz conversion, frame selection, dataset splitting, or bootstrapping the local GPUMD tool-source ecosystem. | 0.2.0 | Optional local checkouts of GPUMD, GPUMD-Tutorials, GPUMDkit, NepTrain, and NepTrainKit. If absent, use the bundled bootstrap script to clone them. |

### GPUMD subskills

| Skill | Description | Version | Compatibility |
| --- | --- | --- | --- |
| [md](molecular-dynamics/gpumd/md/SKILL.md) | Prepare and run equilibrium GPUMD molecular dynamics. Use when the user needs a `model.xyz`, a `run.in`, an ensemble choice (NVE/NVT/NPT), timestep and dump-cadence guidance, or interpretation of `thermo.out` and `movie.xyz`. This is the general-purpose MD subskill; specialized observables (phonons, transport, diffusion, elastic, mechanics) have their own subskills. | 0.2.0 | Requires GPUMD and a valid potential file such as `nep.txt`, `nep89_*.txt`, Tersoff, or any other GPUMD-supported potential. |
| [phonon](molecular-dynamics/gpumd/phonon/SKILL.md) | Prepare GPUMD harmonic phonon-dispersion calculations using `compute_phonon`, `kpoints.in`, and supercell replication. Use when the user needs harmonic phonons, `omega2.out`, `D.out`, phonon DOS, or a GPUMD-based starting point for lattice-dynamics analysis. | 0.2.0 | Requires GPUMD and a potential stable for the target crystalline structure. For DOS workflows, also supports `compute_dos` from NVE trajectories. |
| [transport](molecular-dynamics/gpumd/transport/SKILL.md) | Prepare GPUMD thermal-transport workflows for EMD / HNEMD / NEMD / SHC / HNEMDEC. Use when the user needs `compute_hac`, `compute_hnemd`, `compute_hnemdec`, `compute_shc`, thermal-conductivity extraction, or transport-specific sampling and convergence guidance. | 0.2.0 | Requires GPUMD and a potential that is numerically stable in the target state. |
| [diffusion](molecular-dynamics/gpumd/diffusion/SKILL.md) | Prepare GPUMD workflows for self-diffusion, ionic conductivity, and viscosity. Use when the user needs `compute_msd`, `compute_sdc`, `compute_viscosity`, Nernst-Einstein ionic conductivity, Arrhenius fitting, or species-selective diffusion through group indices. | 0.1.0 | Requires GPUMD and a potential stable in the target fluid / ionic state. |
| [elastic](molecular-dynamics/gpumd/elastic/SKILL.md) | Prepare GPUMD elastic-constant calculations using the strain-fluctuation method. Use when the user needs `compute_elastic`, `C_ij` extraction for cubic / hexagonal / tetragonal / orthorhombic systems, or elastic moduli (bulk, shear, Young's) from an NPT trajectory. | 0.1.0 | Requires GPUMD and a potential that is stable under the anisotropic NPT used for strain-fluctuation sampling. |
| [mechanics](molecular-dynamics/gpumd/mechanics/SKILL.md) | Prepare GPUMD mechanics-type workflows: friction, deposition, impact, and other group-based interface simulations. Use when the user needs `add_spring`, ghost-atom setups, layered 2D material shearing, deposition event sampling, or impact/collision dynamics. | 0.1.0 | Requires GPUMD with the potentials needed for the target interface. Layered 2D-material friction typically needs ILP or a NEP fit covering both layers. |

### NEP subskills

| Skill | Description | Version | Compatibility |
| --- | --- | --- | --- |
| [train](machine-learning-potentials/nep-gpumd/train/SKILL.md) | Train a first NEP potential from labeled extxyz data. Use when the user needs `nep.in`, `train.xyz`, `test.xyz`, parameter guidance, loss.out interpretation, or deployment of the resulting `nep.txt` back into GPUMD. NEP is the native machine-learning potential for GPUMD and plays the role that DeePMD plays for LAMMPS. | 0.2.0 | Requires a NEP-capable GPUMD build with the `nep` executable and labeled training/test extxyz datasets. |
| [fine-tune](machine-learning-potentials/nep-gpumd/fine-tune/SKILL.md) | Prepare NEP prediction and fine-tuning workflows from an existing model or foundation model such as NEP89. Use when the user wants out-of-the-box evaluation, targeted MD sampling, `prediction 1`, or `fine_tune` from an existing `nep.txt` + `nep.restart`. | 0.2.0 | Requires an existing NEP model. True fine-tuning also requires the matching restart file. |
| [automation](machine-learning-potentials/nep-gpumd/automation/SKILL.md) | Prepare dataset-curation and active-learning workflows around NepTrain and NepTrainKit. Use when the user needs perturbation-based sampling, representative-structure selection (FPS / max-min), automated NEP project scaffolding, interactive outlier inspection, or iterative retrain loops rather than a single manual NEP fit. | 0.2.0 | Requires NepTrain (`pip install neptrain`) and/or NepTrainKit when those workflows are executed. |

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
├── references/                 # detailed workflow notes
├── assets/examples/            # run.in + model.xyz templates
└── scripts/                    # deterministic helpers

machine-learning-potentials/nep-gpumd/
├── SKILL.md                    # router
├── train/SKILL.md              # baseline training
├── fine-tune/SKILL.md          # prediction + fine-tune
├── automation/SKILL.md         # NepTrain / NepTrainKit
├── references/                 # dataset + fitting notes
├── assets/examples/            # nep.in + extxyz templates
└── scripts/                    # deterministic helpers

tools/gpumd-tools/
├── SKILL.md                    # tooling router
├── references/                 # converter + tutorial map
└── scripts/                    # bootstrap + local indexing
```

## Design choices

- The old monolithic GPUMD+NEP skill was split by workflow boundary instead of
  by software name alone.
- Large upstream example repositories are treated as references, not vendored
  wholesale into the installable skill tree.
- Only small, high-reuse templates are bundled into `assets/examples/`.
- Local tool-source checkouts remain reproducible through
  `tools/gpumd-tools/scripts/bootstrap_gpumd_tool_sources.sh`.
- Each subskill follows the same pattern: agent checklist, annotated workflow,
  bundled templates, references, and expected output.

## Reference sources

- GPUMD upstream repository (<https://github.com/brucefan1983/GPUMD>)
- GPUMD documentation (<https://gpumd.org>)
- GPUMD-Tutorials (<https://github.com/brucefan1983/GPUMD-Tutorials>)
- NepTrain (<https://github.com/aboys-cb/NepTrain>)
- NepTrainKit (<https://github.com/aboys-cb/NepTrainKit>)
- `computational-chemistry-agent-skills`

## License

This repository includes the same license text used by the upstream GPUMD
repository in [LICENCE](LICENCE): GNU General Public License version 3.
