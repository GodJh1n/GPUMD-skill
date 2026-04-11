---
name: nep-gpumd
description: >
  Route NEP requests to task-specific subskills. NEP (Neuroevolution
  Potential) is the native machine-learning potential family of the GPUMD
  ecosystem — analogous to DeePMD-kit for LAMMPS. Use when the user asks for
  `nep.in`, `train.xyz`, `test.xyz`, NEP training, NEP89 reuse, prediction
  mode, fine-tuning, dipole / polarizability auxiliary models, or automation
  via NepTrain / NepTrainKit.
compatibility: >
  Requires a NEP-capable GPUMD build providing the `nep` executable (usually
  shipped together with `gpumd` in modern releases). Training needs labeled
  datasets in NEP-compatible extxyz format.
license: GPL-3.0-only
metadata:
  author: Jhin
  version: 0.2.0
  repository: https://github.com/brucefan1983/GPUMD
  documentation: https://gpumd.org/nep/
---

# NEP Task Router

Use this skill as the top-level routing layer for NEP work in the GPUMD
ecosystem. NEP is tightly coupled to GPUMD: a trained `nep.txt` file is
loaded by `gpumd` through `potential nep.txt`, and the labeled datasets used
for training are concatenated extxyz files just like GPUMD's `model.xyz`.

If the task is about running MD with an existing NEP potential rather than
training one, route to `molecular-dynamics/gpumd` instead.

## Subskill map

| Subskill                   | Use when the user wants                                           |
| -------------------------- | ----------------------------------------------------------------- |
| `nep-gpumd/train`          | a first NEP model from labeled extxyz data                        |
| `nep-gpumd/fine-tune`      | prediction mode, NEP89 evaluation, or fine-tuning from a restart  |
| `nep-gpumd/automation`     | NepTrain / NepTrainKit active-learning and dataset curation       |

## Agent responsibilities

1. Confirm the execution mode.
   - Ask for the exact `nep` command, e.g. `nep`, `nep-3.9`, an HPC module
     load, or `srun -n 1 --gpus=1 nep`. Do not invent a binary.
2. Classify the request into one subskill path.
3. Collect the minimum shared context before dispatching:
   - labeled dataset file(s) in NEP extxyz format
   - species list (and the exact species order that will appear in `type`)
   - target observable(s) for downstream validation
4. Write `nep.in` yourself and explain every block.
5. Validate headers before training:
   ```bash
   python scripts/validate_extxyz_headers.py train.xyz --mode train
   python scripts/validate_extxyz_headers.py test.xyz --mode train
   ```
6. Report final files (`nep.txt`, `loss.out`, parity outputs) and a short
   downstream validation plan.

## Shared policy

- Default to `version 4` unless the user is explicitly reproducing legacy
  syntax.
- The species order in `type` must match the species order used in the
  dataset **and** must match the order expected by any downstream GPUMD
  potential reuse (e.g. NEP89 subsets).
- Treat training RMSE as necessary but not sufficient; require at least one
  downstream MD or property validation before declaring success.
- Make virial / stress conventions explicit before mixing datasets from
  different DFT labelers.
- For auxiliary-property models (dipole, polarizability), state the
  `model_type` explicitly and remember that the loss structure is
  different from the energy+force model. The dataset format also differs:
  for `model_type 1` (dipole), each frame MUST include `dipole="dx dy dz"`
  in the extxyz header (total cell dipole in e·Å); for `model_type 2`
  (polarizability), each frame MUST include
  `polarizability="xx yy zz xy yz zx"` (Voigt order, in Å³).
  See [references/auxiliary-properties.md](references/auxiliary-properties.md).

## Where labeled data comes from

NEP training data is usually generated from DFT single-point calculations.
The upstream `GPUMD/tools/Format_Conversion/` directory has converters for
VASP, CP2K, ABACUS, SIESTA, ORCA, CASTEP, RUNNER, and DeepMD datasets.

If the user also needs help preparing those DFT calculations themselves,
cross-reference the quantum-chemistry skills in this collection
(`dft-vasp`, `dft-cp2k`, `dft-qe`, `dft-siesta`, `dft-abinit`) for
static / relax single-point recipes. NEP training then starts from their
outputs via the relevant `*2xyz` converter.

See [references/labels-from-dft.md](references/labels-from-dft.md) for a
focused walkthrough.

## Resource map

- Dataset and input rules: [references/dataset-and-inputs.md](references/dataset-and-inputs.md)
- Training, evaluation, deployment: [references/training-evaluation-deployment.md](references/training-evaluation-deployment.md)
- Fine-tuning playbook: [references/fine-tuning-playbook.md](references/fine-tuning-playbook.md)
- NEP keyword cheatsheet: [references/nep-keyword-cheatsheet.md](references/nep-keyword-cheatsheet.md)
- Auxiliary properties (dipole / polarizability): [references/auxiliary-properties.md](references/auxiliary-properties.md)
- Labels from DFT: [references/labels-from-dft.md](references/labels-from-dft.md)
- Templates: [assets/examples/](assets/examples/)
- Deterministic helpers: [scripts/](scripts/)

## Cross-skill pointers

- Running MD with the trained NEP → `molecular-dynamics/gpumd`
- Generating labeled DFT data → quantum-chemistry `dft-*` skills
- Format conversion + dataset curation → `tools/gpumd-tools`
- Frame selection / perturbation automation → `nep-gpumd/automation`
- HPC job submission for NEP training → `dpdisp-submit`
