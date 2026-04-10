---
name: fine-tune
description: >
  Prepare NEP prediction and fine-tuning workflows from an existing model or
  foundation model such as NEP89. Use when the user wants out-of-the-box
  evaluation, targeted MD sampling, `prediction 1`, or `fine_tune` from an
  existing `nep.txt` + `nep.restart`.
compatibility: Requires an existing NEP model. True fine-tuning also requires the matching restart file.
catalog-hidden: true
license: LGPL-3.0-or-later
metadata:
  author: Codex
  version: 0.2.0
---

# NEP Fine-Tune

Use this subskill for model reuse rather than fitting a new potential from
scratch. This covers three scenarios:

1. evaluate an existing NEP (e.g. NEP89) out of the box on a new system
2. run prediction mode to get parity against new labels before retraining
3. fine-tune a pre-existing NEP for a specific material or observable

## Quick decision tree

```
Has the user already decided they want to retrain?
├── No  → start with scenario 1 (out-of-box) or scenario 2 (prediction)
└── Yes
    ├── Does the user have only `nep.txt`?          → can only retrain, not fine-tune
    └── Does the user have `nep.txt` + `nep.restart`? → can truly fine-tune
```

## Agent responsibilities

1. Confirm which scenario applies. Do not jump to fine-tuning if the user
   has not yet checked whether the base model is already good enough.
2. Require that the descriptor-defining parameters (`cutoff`, `n_max`,
   `basis_size`, `l_max`, `neuron`, `zbl`, and the species subset) remain
   compatible with the restart. Changing them invalidates the restart.
3. For species-subset reuse (e.g. NEP89 → MoS2 only), ensure the `type`
   line lists exactly the species that will appear in the new dataset, in
   an order that matches the base model's convention.
4. Require a downstream validation step after fine-tuning — improved RMSE
   alone does not count.

## Scenario 1: out-of-the-box evaluation

Before fine-tuning, ask whether the base model is already good enough for
the target observable.

1. Run the existing model on the target system in GPUMD.
2. Use the intended cell geometry and the intended ensemble.
3. Compare the result against reference data or a specialized model.

Bundled templates:

- [assets/examples/fine-tune/model.xyz](../assets/examples/fine-tune/model.xyz)
- [assets/examples/fine-tune/out-of-box-hnemd-run.in](../assets/examples/fine-tune/out-of-box-hnemd-run.in)

If the out-of-the-box result is within tolerance, stop. Fine-tuning is not
always necessary.

## Scenario 2: prediction mode

Prediction mode runs `nep` on a labeled dataset without training, giving
parity data against the existing model. Use it to:

- quantify the mismatch between the current model and new labels
- decide whether fine-tuning is justified
- identify which config types or states are failing most

`nep.in` for prediction:

```text
prediction 1
```

The dataset file (`train.xyz` by convention, even though no training
happens) is read in the usual way, and parity outputs are written as
normal.

Bundled template:

- [assets/examples/prediction/nep.in](../assets/examples/prediction/nep.in)

## Scenario 3: fine-tuning

Fine-tuning requires both `nep.txt` and the matching `nep.restart`. The
canonical recipe adapted from tutorial `26_fine_tune_NEP89`:

```text
fine_tune  nep89_20250409.txt nep89_20250409.restart
type       2 Mo S
version    4
zbl        2
cutoff     6 5
n_max      4 4
basis_size 8 8
l_max      4 2 1
neuron     80
lambda_e   1.0
lambda_f   1.0
lambda_v   0.1
batch      1000
population 50
generation 5000
```

Important rules:

- `cutoff`, `n_max`, `basis_size`, `l_max`, `neuron`, `zbl` must match the
  base model — they define the descriptor and network shape stored in the
  restart. If you change them, the restart cannot be loaded.
- `type` may be a **subset** of the base model's species, provided the new
  labels only contain those species.
- Only training-control parameters (`lambda_*`, `batch`, `population`,
  `generation`) should typically vary between the base fit and the
  fine-tune.

Bundled template:

- [assets/examples/fine-tune/nep.in](../assets/examples/fine-tune/nep.in)
- [assets/examples/nep89/nep.in](../assets/examples/nep89/nep.in)

## Recommended sequence for a full fine-tuning study

Adapted from tutorial `26_fine_tune_NEP89`:

1. run the existing model on the target system
2. compute the target property out of the box
3. sample target-state configurations with the existing model (use
   [assets/examples/fine-tune/sampling-run.in](../assets/examples/fine-tune/sampling-run.in))
4. select a manageable set of representative frames (FPS or error-based)
5. label them with a consistent DFT setup — cross-reference the
   quantum-chemistry `dft-*` skills if help is needed here
6. run prediction mode to quantify the baseline mismatch
7. fine-tune
8. rerun the target property and compare

Separating the workflow this way keeps model inadequacy, dataset
inadequacy, and workflow inadequacy from being confused with each other.

## DFT labeling consistency

Fine-tuning quality is capped by label quality. Keep the DFT single-point
workflow internally consistent:

- same functional family across all new labels
- same dispersion treatment
- same stress / virial convention if virials are fit
- same k-point density / basis set within each config_type

If the new labels use a different DFT convention from the base NEP, state
that clearly and expect the parity to be shifted.

## Deciding whether fine-tuning worked

Do not stop at improved RMSE. Fine-tuning worked only if:

- prediction error on new labels improves
- the target physical observable improves
- the fine-tuned model is numerically stable in a short MD sanity run

## Agent checklist

- [ ] the base model and its restart are both available
- [ ] descriptor parameters preserved from the base model
- [ ] species list in `type` is a subset compatible with the new labels
- [ ] prediction-mode mismatch was measured before training
- [ ] DFT labeling is internally consistent
- [ ] downstream MD sanity run performed after fine-tuning

## Read first

- [references/fine-tuning-playbook.md](../references/fine-tuning-playbook.md)

Read when needed:

- [references/dataset-and-inputs.md](../references/dataset-and-inputs.md)
- [references/training-evaluation-deployment.md](../references/training-evaluation-deployment.md)
- [references/nep-keyword-cheatsheet.md](../references/nep-keyword-cheatsheet.md)
- [references/labels-from-dft.md](../references/labels-from-dft.md)

## Bundled templates

- [assets/examples/prediction/nep.in](../assets/examples/prediction/nep.in)
- [assets/examples/fine-tune/nep.in](../assets/examples/fine-tune/nep.in)
- [assets/examples/fine-tune/model.xyz](../assets/examples/fine-tune/model.xyz)
- [assets/examples/fine-tune/out-of-box-hnemd-run.in](../assets/examples/fine-tune/out-of-box-hnemd-run.in)
- [assets/examples/fine-tune/sampling-run.in](../assets/examples/fine-tune/sampling-run.in)
- [assets/examples/nep89/nep.in](../assets/examples/nep89/nep.in)

## Expected output

1. a reproducible plan tied to the target property
2. the exact files needed for prediction or fine-tuning
3. an explicit comparison between out-of-the-box and fine-tuned behavior

## References

- NEP fine-tuning: <https://gpumd.org/nep/input_files/nep_in.html>
- GPUMD-Tutorials: `26_fine_tune_NEP89`
- NEP89 foundation model release notes
