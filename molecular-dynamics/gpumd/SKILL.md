---
name: gpumd
description: >
  Route GPUMD requests to task-specific subskills. GPUMD is a GPU-accelerated
  molecular dynamics code that pairs naturally with NEP machine-learning
  potentials. Use when the user asks for GPUMD MD, `model.xyz`, `run.in`,
  harmonic phonons via `compute_phonon`, thermal transport via EMD/HNEMD/NEMD,
  diffusion and ionic conductivity, elastic constants, melting, friction, or
  deposition workflows.
compatibility: >
  Requires a runnable GPUMD environment. The user must supply the `gpumd`
  executable path, HPC module, or container entry point. A compatible potential
  file (`nep.txt`, `nep89_*.txt`, Tersoff, etc.) is required.
license: GPL-3.0-only
metadata:
  author: Codex
  version: 0.2.0
  repository: https://github.com/brucefan1983/GPUMD
  documentation: https://gpumd.org/
---

# GPUMD Task Router

Use this skill as the top-level routing layer for GPUMD work. GPUMD is
analogous to LAMMPS but focused on GPU execution and tight integration with the
NEP potential family. If the task is about fitting a NEP potential rather than
running MD with one, route to `machine-learning-potentials/nep-gpumd` instead.

## Subskill map

| Subskill              | Use when the target observable is                                         |
| --------------------- | ------------------------------------------------------------------------- |
| `gpumd/md`            | equilibrium MD, ensemble setup, `thermo.out`, general trajectory output   |
| `gpumd/phonon`        | harmonic phonons via `compute_phonon`, `kpoints.in`, `omega2.out`         |
| `gpumd/transport`     | thermal conductivity via EMD / HNEMD / NEMD / SHC                         |
| `gpumd/diffusion`     | self-diffusion, ionic conductivity, viscosity via `compute_msd`/`_sdc`/`_viscosity` |
| `gpumd/elastic`       | elastic constants via the strain-fluctuation method                       |
| `gpumd/mechanics`     | friction, deposition, impact, and group-based interface workflows         |

## Agent responsibilities

1. Confirm the execution mode.
   - Ask the user for the exact `gpumd` command, for example
     `gpumd`, `gpumd-3.9`, an HPC module load, or
     `srun -n 1 --gpus=1 gpumd`.
   - Do not invent a binary or module name.
2. Classify the request into one subskill path. If the request spans more than
   one area, start from the dominant observable and only open the extra
   subskill files that are needed.
3. Collect the minimum shared context before dispatching:
   - the atomistic structure (preferred: `model.xyz` in extxyz format)
   - the potential file (for example `nep.txt`, `nep89_20250409.txt`,
     `Si_2022_NEP3_4body.txt`, or an upstream Tersoff file)
   - the target ensemble / temperature / pressure
   - the target observable
4. Write the input files yourself instead of asking the user to hand-write
   them. Keep the example readable and explain every block.
5. Validate structures before trusting downstream runs:
   ```bash
   python ../../tools/gpumd-tools/scripts/validate_extxyz_headers.py model.xyz --mode model
   ```
6. Report clearly which command was run, which files were used, where outputs
   were written, and which sanity checks should be performed next.

## Shared policy for all GPUMD subskills

- Do not invent missing physical parameters.
- Keep the timestep, ensemble, and target observable physically consistent.
- Treat transport, elastic, and diffusion results as provisional until size,
  sampling, and method-specific convergence are explicitly discussed.
- For low-dimensional systems (monolayers, ribbons, slabs) require an explicit
  thickness convention before reporting bulk-like intensive quantities.
- For restarts from another NEP or GPUMD version, re-check keyword syntax
  against the current docs at <https://gpumd.org/>.

## Execution templates

### Direct local run

```bash
gpumd < run.in | tee gpumd.log
```

Many builds take input from stdin. Some custom wrappers accept `gpumd run.in`
directly; the user should confirm.

### HPC / Slurm

Ask the user for the exact module and wrapper. A typical pattern looks like:

```bash
module load gpumd/3.9.5 cuda/12.2
srun -n 1 --gpus=1 gpumd < run.in > gpumd.log
```

Do not use this exact command without confirming the module names.

### Smoke test before production

Before a long transport or phonon run, always do a short stability test:

```text
run 100
```

This catches:

- missing potential file
- malformed `model.xyz`
- immediately divergent dynamics (bad structure, wrong species order, wrong
  potential)
- wrong timestep for the chosen system

## Resource map

- Core files and ensembles: [references/core-files-and-ensembles.md](references/core-files-and-ensembles.md)
- GPUMD keyword cheatsheet: [references/gpumd-keyword-cheatsheet.md](references/gpumd-keyword-cheatsheet.md)
- Phonon workflow: [references/phonon-workflow.md](references/phonon-workflow.md)
- Thermal transport workflow: [references/thermal-transport-workflow.md](references/thermal-transport-workflow.md)
- Diffusion, viscosity, ionic conductivity: [references/diffusion-viscosity-ionic.md](references/diffusion-viscosity-ionic.md)
- Elastic constants: [references/elastic-constants.md](references/elastic-constants.md)
- Mechanics (friction / deposition / impact): [references/mechanics-deposition-friction.md](references/mechanics-deposition-friction.md)
- Tutorial map: [references/tutorial-map.md](references/tutorial-map.md)
- Reusable templates: [assets/examples/](assets/examples/)
- Deterministic helpers: [scripts/](scripts/)

## Cross-skill pointers

- Need to fit a NEP potential first? → `machine-learning-potentials/nep-gpumd`
- Need to convert VASP / CP2K / QE output into NEP extxyz? → `tools/gpumd-tools`
- Need to generate labeled DFT data before training a NEP? → refer to the
  quantum-chemistry DFT skills (`dft-vasp`, `dft-cp2k`, `dft-qe`, `dft-siesta`,
  `dft-abinit`) for static/relax single-point workflows.
