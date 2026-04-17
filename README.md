# GPUMD Agent Skills

<!-- SKILLS_BADGE_START -->
[![Skills](https://img.shields.io/badge/skills-43-blue?style=for-the-badge)](#skills-summary)
<!-- SKILLS_BADGE_END -->

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

The **core GPUMD/NEP skills** are:

- `molecular-dynamics/gpumd`
- `machine-learning-potentials/nep-gpumd`
- `tools/gpumd-tools`

**Companion skills** (DFT labeling, phonon analysis, data processing, HPC
submission, workflow orchestration) are available in their respective
directories and can be installed individually as needed.

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

From the repository root, install the core skills:

```bash
npx -y skills add ./molecular-dynamics/gpumd -a openclaw -y
npx -y skills add ./machine-learning-potentials/nep-gpumd -a openclaw -y
npx -y skills add ./tools/gpumd-tools -a openclaw -y
```

Install companion skills as needed:

```bash
# DFT labeling
npx -y skills add ./quantum-chemistry/dft-vasp -a openclaw -y
npx -y skills add ./quantum-chemistry/dft-cp2k -a openclaw -y
npx -y skills add ./quantum-chemistry/dft-qe -a openclaw -y
npx -y skills add ./quantum-chemistry/dft-siesta -a openclaw -y
npx -y skills add ./quantum-chemistry/dft-abinit -a openclaw -y
# Analysis
npx -y skills add ./analysis/phonopy -a openclaw -y
npx -y skills add ./analysis/reacnetgenerator -a openclaw -y
# Data processing
npx -y skills add ./data-processing/dpdata-cli -a openclaw -y
npx -y skills add ./data-processing/pymatgen-structure -a openclaw -y
npx -y skills add ./data-processing/openbabel -a openclaw -y
npx -y skills add ./data-processing/packmol-generate-mixture -a openclaw -y
npx -y skills add ./data-processing/rdkit-conf -a openclaw -y
# Tools
npx -y skills add ./tools/dpdisp-submit -a openclaw -y
npx -y skills add ./tools/search-species -a openclaw -y
# Workflow orchestration
npx -y skills add ./agent-workflow/agent-taskboard-manifest -a openclaw -y
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
- `Set up a VASP static single-point calculation for labeling NEP training frames, then submit it to my Slurm cluster.`
- `Use phonopy with finite displacements to compute the phonon band structure of BN, then compare with GPUMD compute_phonon.`
- `Pack 100 water and 50 ethanol molecules with Packmol, convert to model.xyz, and prepare a GPUMD diffusion workflow.`

### Optional: bootstrap local upstream tool sources

If you want the local mirrors of GPUMD, GPUMD-Tutorials, GPUMDkit, NepTrain,
and NepTrainKit:

```bash
bash tools/gpumd-tools/scripts/bootstrap_gpumd_tool_sources.sh
```

This is optional. The installable skills are the three directories listed
above, not the mirrored upstream repositories.

<!-- SKILLS_TABLE_START -->
## Skills summary

### Top-level skills

| Skill | Description | Version | Compatibility |
| --- | --- | --- | --- |
| [nep-gpumd](machine-learning-potentials/nep-gpumd/SKILL.md) | Route NEP requests to task-specific subskills. NEP (Neuroevolution Potential) is the native machine-learning potential family of the GPUMD ecosystem — analogous to DeePMD-kit for LAMMPS. Use when the user asks for `nep.in`, `train.xyz`, `test.xyz`, NEP training, NEP89 reuse, prediction mode, fine-tuning, dipole / polarizability auxiliary models, or automation via NepTrain / NepTrainKit. | 0.2.0 | Requires a NEP-capable GPUMD build providing the `nep` executable (usually shipped together with `gpumd` in modern releases). Training needs labeled datasets in NEP-compatible extxyz format. |
| [gpumd](molecular-dynamics/gpumd/SKILL.md) | Route GPUMD requests to task-specific subskills. GPUMD is a GPU-accelerated molecular dynamics code that pairs naturally with NEP machine-learning potentials. Use when the user asks for GPUMD MD, `model.xyz`, `run.in`, harmonic phonons via `compute_phonon`, thermal transport via EMD/HNEMD/NEMD, diffusion and ionic conductivity, elastic constants, melting, friction, or deposition workflows. | 0.2.0 | Requires a runnable GPUMD environment. The user must supply the `gpumd` executable path, HPC module, or container entry point. A compatible potential file (`nep.txt`, `nep89_*.txt`, Tersoff, etc.) is required. |
| [gpumd-tools](tools/gpumd-tools/SKILL.md) | Tooling layer for GPUMD helper repositories, format converters, dataset curation, and local example discovery. Use when the user needs GPUMDkit, upstream `GPUMD/tools`, GPUMD-Tutorials lookup, DFT-to-extxyz conversion, frame selection, dataset splitting, or bootstrapping the local GPUMD tool-source ecosystem. | 0.2.0 | Optional local checkouts of GPUMD, GPUMD-Tutorials, GPUMDkit, NepTrain, and NepTrainKit. If absent, use the bundled bootstrap script to clone them. |

### GPUMD subskills

| Skill | Description | Version | Compatibility |
| --- | --- | --- | --- |
| [diffusion](molecular-dynamics/gpumd/diffusion/SKILL.md) | Prepare GPUMD workflows for self-diffusion, ionic conductivity, and viscosity. Use when the user needs `compute_msd`, `compute_sdc`, `compute_viscosity`, Nernst-Einstein ionic conductivity, Arrhenius fitting, or species-selective diffusion through group indices. | 0.2.0 | Requires GPUMD and a potential stable in the target fluid / ionic state. |
| [elastic](molecular-dynamics/gpumd/elastic/SKILL.md) | Prepare GPUMD elastic-constant calculations using the strain-fluctuation method. Use when the user needs `compute_elastic`, the full `C_ij` tensor, or elastic moduli (bulk, shear, Young's) from an anisotropic NPT trajectory. | 0.2.0 | Requires GPUMD and a potential that is stable under the anisotropic NPT used for strain-fluctuation sampling. |
| [md](molecular-dynamics/gpumd/md/SKILL.md) | Prepare and run equilibrium GPUMD molecular dynamics. Use when the user needs a `model.xyz`, a `run.in`, an ensemble choice (NVE/NVT/NPT), timestep and dump-cadence guidance, or interpretation of `thermo.out` and `movie.xyz`. This is the general-purpose MD subskill; specialized observables (phonons, transport, diffusion, elastic, mechanics) have their own subskills. | 0.2.0 | Requires GPUMD and a valid potential file such as `nep.txt`, `nep89_*.txt`, Tersoff, or any other GPUMD-supported potential. |
| [mechanics](molecular-dynamics/gpumd/mechanics/SKILL.md) | Prepare GPUMD mechanics-type workflows: friction, deposition, impact, and other group-based interface simulations. Use when the user needs `add_spring`, ghost-atom setups, layered 2D material shearing, deposition event sampling, or impact/collision dynamics. | 0.2.0 | Requires GPUMD with the potentials needed for the target interface. Layered 2D-material friction typically needs ILP or a NEP fit covering both layers. |
| [phonon](molecular-dynamics/gpumd/phonon/SKILL.md) | Prepare GPUMD harmonic phonon-dispersion calculations using `compute_phonon`, `kpoints.in`, and supercell replication. Use when the user needs harmonic phonons, `omega2.out`, `D.out`, phonon DOS, or a GPUMD-based starting point for lattice-dynamics analysis. | 0.2.0 | Requires GPUMD and a potential stable for the target crystalline structure. For DOS workflows, also supports `compute_dos` from NVE trajectories. |
| [transport](molecular-dynamics/gpumd/transport/SKILL.md) | Prepare GPUMD thermal-transport workflows for EMD / HNEMD / NEMD / SHC / HNEMDEC. Use when the user needs `compute_hac`, `compute_hnemd`, `compute_hnemdec`, `compute_shc`, thermal-conductivity extraction, or transport-specific sampling and convergence guidance. | 0.2.0 | Requires GPUMD and a potential that is numerically stable in the target state. |

### NEP subskills

| Skill | Description | Version | Compatibility |
| --- | --- | --- | --- |
| [automation](machine-learning-potentials/nep-gpumd/automation/SKILL.md) | Prepare dataset-curation and active-learning workflows around NepTrain and NepTrainKit. Use when the user needs perturbation-based sampling, representative-structure selection (FPS / max-min), automated NEP project scaffolding, interactive outlier inspection, or iterative retrain loops rather than a single manual NEP fit. | 0.2.0 | Requires NepTrain (pip install neptrain) and/or NepTrainKit when those workflows are executed. |
| [fine-tune](machine-learning-potentials/nep-gpumd/fine-tune/SKILL.md) | Prepare NEP prediction and fine-tuning workflows from an existing model or foundation model such as NEP89. Use when the user wants out-of-the-box evaluation, targeted MD sampling, `prediction 1`, or `fine_tune` from an existing `nep.txt` + `nep.restart`. | 0.2.0 | Requires an existing NEP model. True fine-tuning also requires the matching restart file. |
| [train](machine-learning-potentials/nep-gpumd/train/SKILL.md) | Train a first NEP potential from labeled extxyz data. Use when the user needs `nep.in`, `train.xyz`, `test.xyz`, parameter guidance, loss.out interpretation, or deployment of the resulting `nep.txt` back into GPUMD. NEP is the native machine-learning potential for GPUMD and plays the role that DeePMD plays for LAMMPS. | 0.2.0 | Requires a NEP-capable GPUMD build with the `nep` executable and labeled training/test extxyz datasets. |

### DFT skills (quantum-chemistry)

| Skill | Description | Subskills |
| --- | --- | --- |
| [dft-abinit](quantum-chemistry/dft-abinit/SKILL.md) | Route ABINIT requests to task-specific subskills based on user intent. Use when the user asks for ABINIT workflows and you must decide between static, relaxation, molecular dynamics, or electronic-analysis preparation. This orchestration skill dispatches to the correct ABINIT subskill and enforces consistent handoff to submission skills. | electronic, md, relax, static |
| [dft-cp2k](quantum-chemistry/dft-cp2k/SKILL.md) | Route CP2K requests to task-specific subskills based on user intent. Use when the user asks for CP2K workflows and you must decide between static, relaxation, molecular dynamics, or electronic-analysis preparation. This orchestration skill dispatches to the correct CP2K subskill and enforces consistent handoff to submission skills. | electronic, md, relax, static |
| [dft-qe](quantum-chemistry/dft-qe/SKILL.md) | Generate Quantum ESPRESSO DFT input tasks from a user-provided structure plus user-specified DFT settings. Use when the user wants to prepare QE calculations such as SCF, NSCF, relax, vc-relax, MD, bands, DOS, or phonons starting from a structure file or coordinates together with pseudopotentials, functional choice, cutoffs, k-point settings, smearing, spin/charge, and convergence parameters. This skill prepares the QE task only; use a separate submission skill such as dpdisp-submit to submit the generated task. | — |
| [dft-siesta](quantum-chemistry/dft-siesta/SKILL.md) | Route SIESTA requests to task-specific subskills based on user intent. Use when the user asks for SIESTA workflows and you must decide between static, relaxation, molecular dynamics, or electronic-analysis preparation. This orchestration skill dispatches to the correct SIESTA subskill and enforces consistent handoff to submission skills. | electronic, md, relax, static |
| [dft-vasp](quantum-chemistry/dft-vasp/SKILL.md) | Route VASP DFT requests to task-specific subskills based on user intent. Use when the user asks for VASP workflows and you must decide between static SCF, relaxation, DOS, or band-structure task preparation. This orchestration skill does not own detailed input generation logic; it dispatches to the correct VASP subskill and enforces consistent handoff to submission skills. | band, dos, relax, static |

### Analysis skills

| Skill | Description |
| --- | --- |
| [phonopy](analysis/phonopy/SKILL.md) | General phonon-workflow skill built around phonopy, independent of force backend. USE WHEN you need to prepare finite-displacement phonon calculations, build force constants, and analyze phonon properties (band structure, DOS, thermal quantities) while obtaining forces from different engines such as VASP, Quantum ESPRESSO, or ML force fields. |
| [reacnetgenerator](analysis/reacnetgenerator/SKILL.md) | Run ReacNetGenerator on reactive MD trajectories to generate reaction networks and reports. Use when the user wants to analyze LAMMPS dump/xyz/bond trajectories with ReacNetGenerator. Handles LAMMPS dump quirks like x/y/z vs xs/ys/zs by converting to x/y/z (orthorhombic + triclinic supported via reacnet-md-tools). Can infer atomname order from a LAMMPS data file. Runs via local reacnetgenerator if available or via `uvx --from reacnetgenerator ...`. Writes outputs into `out/<input_basename>/` with logs and a summary. |

### Data-processing skills

| Skill | Description |
| --- | --- |
| [dpdata-cli](data-processing/dpdata-cli/SKILL.md) | A command-line utility for converting and manipulating over 50 atomic simulation data formats, including outputs from DFT and MD software (VASP, LAMMPS, Gaussian, QE, CP2K, ABACUS, etc.). USE WHEN you need to convert structural or trajectory files between different computational chemistry formats, or when parsing raw simulation outputs into structured training datasets (e.g., deepmd/raw, deepmd/npy, deepmd/hdf5) for DeePMD-kit. |
| [openbabel](data-processing/openbabel/SKILL.md) | A versatile CLI tool for converting molecular file formats, generating 3D atomic coordinates from SMILES, rendering 2D chemical structure images, and preparing or extracting structures for computational workflows. USE WHEN you need to convert between chemical file formats (e.g., xyz, pdb, mol, smi, gjf), generate 3D structures from SMILES using `--gen3d`, render molecule images (PNG/SVG), or extract geometries from simulation logs to build new inputs. |
| [packmol-generate-mixture](data-processing/packmol-generate-mixture/SKILL.md) | A tool for generating initial packed molecular configurations (XYZ format) from single-molecule structures by calculating box dimensions, writing input scripts, and executing Packmol. USE WHEN you need to randomly pack a specific number of molecules into a simulation box (defined by target density or fixed lengths) to create starting geometries for molecular dynamics or related computational chemistry workflows. |
| [pymatgen-structure](data-processing/pymatgen-structure/SKILL.md) | Structure manipulation and crystal analysis workflows based on pymatgen. USE WHEN you need to read/write common atomistic formats (CIF, POSCAR, XYZ), build supercells, perform site substitution/doping, inspect symmetry (space group), or compute local structure descriptors for materials tasks. |
| [rdkit-conf](data-processing/rdkit-conf/SKILL.md) | A standardized CLI wrapper for RDKit 3D/2D conformer generation that samples multiple conformers per molecule (ETKDGv3, default 10), optimizes each with a force field (MMFF94s/UFF), keeps the lowest-energy conformer, automatically falls back to 2D layout on total embedding failure with a printed warning, and writes results to SDF or XYZ format. USE WHEN you need to generate 3D (or 2D fallback) molecular geometries from SMILES datasets (.csv/.smi) for downstream tasks such as docking, visualization, or 3D-descriptor computation. |

### Additional tools

| Skill | Description |
| --- | --- |
| [dpdisp-submit](tools/dpdisp-submit/SKILL.md) | Run Shell commands as computational jobs, on local machines or HPC clusters, through Shell, Slurm, PBS, LSF, Bohrium, etc. USE WHEN the user needs to submit batch jobs to a cluster, run commands on a remote server, execute tasks via job schedulers (Slurm, PBS, LSF), or safely run long-term/background shell commands that require state tracking and auto-recovery. |
| [search-species](tools/search-species/SKILL.md) | USE WHEN requesting core chemical structural data (SMILES, formula, mass, 2D images) via IUPAC, common, or multilingual names. You MUST actively retrieve the data using this skill; DO NOT hallucinate or generate structures yourself. DO NOT USE WHEN asking for physical properties (melting point, solubility), safety/toxicity data (MSDS), or synthesis pathways. |

### Workflow orchestration

| Skill | Description |
| --- | --- |
| [agent-taskboard-manifest](agent-workflow/agent-taskboard-manifest/SKILL.md) | It is a specification for semantic workflows used by agents to plan, generate, formalize, summarize, and execute complex tasks, projects, experiments,and research efforts for agents, requiring explicit structure, lazy loading,scoped context, evidence-grounded routing, and human review at critical checkpoints. USE WHEN the user asks for a complex task, project, experiment, or research effort that needs to be carefully planned before execution USE WHEN the user provides a text-based plan and wants it to be made more detailed and formalized according to this specification. USE WHEN the user asks to summarize ongoing or completed work into a reusable workflow manifest. USE WHEN the user specifies the location of an existing agent workflow and wants it loaded and executed according to the specification. |

<!-- SKILLS_TABLE_END -->

## File tree overview

```text
molecular-dynamics/gpumd/          # core GPUMD MD skills
├── SKILL.md                       # router
├── md/SKILL.md                    # general MD
├── phonon/SKILL.md                # phonon
├── transport/SKILL.md             # thermal transport
├── diffusion/SKILL.md             # diffusion / viscosity
├── elastic/SKILL.md               # elastic constants
├── mechanics/SKILL.md             # friction / deposition
├── references/                    # detailed workflow notes
├── assets/examples/               # run.in + model.xyz templates
└── scripts/                       # deterministic helpers

machine-learning-potentials/nep-gpumd/  # core NEP skills
├── SKILL.md                       # router
├── train/SKILL.md                 # baseline training
├── fine-tune/SKILL.md             # prediction + fine-tune
├── automation/SKILL.md            # NepTrain / NepTrainKit
├── references/                    # dataset + fitting notes
├── assets/examples/               # nep.in + extxyz templates
└── scripts/                       # deterministic helpers

quantum-chemistry/                 # DFT labeling for NEP
├── dft-vasp/                      # VASP router + static/relax/dos/band
├── dft-cp2k/                      # CP2K router + static/relax/md/electronic
├── dft-qe/                        # QE (single skill)
├── dft-siesta/                    # SIESTA router + subskills
└── dft-abinit/                    # ABINIT router + subskills

analysis/                          # phonon + post-processing
├── phonopy/                       # phonon workflows
└── reacnetgenerator/              # reactive MD analysis

data-processing/                   # format conversion + structure prep
├── dpdata-cli/                    # 50+ format converter
├── pymatgen-structure/            # crystal structure manipulation
├── openbabel/                     # molecular format conversion
├── packmol-generate-mixture/      # liquid packing
└── rdkit-conf/                    # conformer generation

tools/                             # utilities
├── gpumd-tools/                   # GPUMD-specific tooling
├── dpdisp-submit/                 # HPC job submission
└── search-species/                # chemical data lookup

agent-workflow/                    # workflow orchestration
└── agent-taskboard-manifest/      # semantic workflow spec
```

## Design choices

- The core GPUMD+NEP skills are split by workflow boundary.
- Companion skills (DFT, phonon, data processing, HPC submission) are adapted
  from `computational-chemistry-agent-skills` with GPUMD integration notes.
- Large upstream example repositories are treated as references, not vendored
  wholesale into the installable skill tree.
- Only small, high-reuse templates are bundled into `assets/examples/`.
- Local tool-source checkouts remain reproducible through
  `tools/gpumd-tools/scripts/bootstrap_gpumd_tool_sources.sh`.
- Each subskill follows the same pattern: agent checklist, annotated workflow,
  bundled templates, references, and expected output.
- Repository engineering conventions are adapted from
  `computational-chemistry-agent-skills`.

## Reference sources

- GPUMD upstream repository (<https://github.com/brucefan1983/GPUMD>)
- GPUMD documentation (<https://gpumd.org>)
- GPUMD-Tutorials (<https://github.com/brucefan1983/GPUMD-Tutorials>)
- NepTrain (<https://github.com/aboys-cb/NepTrain>)
- NepTrainKit (<https://github.com/aboys-cb/NepTrainKit>)
- `computational-chemistry-agent-skills` (<https://github.com/deepmodeling/computational-chemistry-agent-skills>)

## License

This repository includes the same license text used by the upstream GPUMD
repository in [LICENCE](LICENCE): GNU General Public License version 3.
