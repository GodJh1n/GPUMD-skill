# NEP Fine-Tuning Playbook

## When to read this file

Read this file when the user wants:

- out-of-the-box use of NEP89 or another pre-existing NEP
- prediction-mode evaluation before retraining
- targeted fine-tuning for one material or one observable
- NepTrain or manual active-learning style loops

## 1. Recommended sequence

The local `26_fine_tune_NEP89` tutorial suggests a sound order:

1. run the existing model on the target system
1. check the target property out of the box
1. sample target-state configurations with the current model
1. select a manageable set of representative frames
1. label them with a consistent DFT setup
1. evaluate prediction mode
1. fine-tune
1. rerun the target property and compare

This order matters because it separates:

- model inadequacy
- dataset inadequacy
- workflow inadequacy

## 2. Out-of-the-box evaluation

Before fine-tuning, first ask whether the base model is already good enough.

For transport or thermodynamic properties, that means:

- run the target ensemble
- use the intended cell geometry
- compare the result with either trusted reference data or a specialized model

The bundled templates include:

- `assets/examples/fine-tune/model.xyz`
- `assets/examples/fine-tune/out-of-box-hnemd-run.in`

## 3. Target-state sampling

If out-of-the-box performance is not sufficient, generate new configurations near the target operating state.

Examples:

- target temperature and pressure for transport
- interface configurations for adhesion or friction
- defect-rich states for defect energetics

The sampling template is:

- `assets/examples/fine-tune/sampling-run.in`

Key rule:

- sample with a cell size that remains affordable for the later single-point labeler

## 4. Frame selection

Do not label every frame blindly.

Selection strategies can include:

- farthest-point sampling
- error-based selection
- manual outlier inspection

The local tutorial uses FPS on MD frames before DFT labeling.

## 5. DFT labeling consistency

Fine-tuning quality is capped by label quality.

Make sure the single-point workflow is internally consistent:

- same functional family across all new labels
- same dispersion treatment across the set
- same stress/virial convention if virials are used

If dispersion corrections matter physically, do not mix corrected and uncorrected labels without documenting it.

## 6. Prediction mode before fine-tuning

Prediction mode establishes the baseline mismatch between the current model and the new labels.

Use:

- `assets/examples/prediction/nep.in`

This stage tells you whether fine-tuning is justified and where the model is failing.

## 7. Fine-tune input rules

A typical fine-tuning control block looks like:

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
```

Important rule:

- descriptor-defining parameters must remain compatible with the original model and restart state

The local tutorial explicitly keeps these fixed and only changes training-related settings such as:

- `lambda_*`
- `batch`
- `population`
- `generation`

## 8. Deciding whether fine-tuning worked

Do not stop at improved training RMSE.

Fine-tuning worked only if:

- prediction error on the new labeled set improves
- the target physical observable improves
- the fine-tuned model remains stable in MD

## 9. NepTrain and NepTrainKit

When the task becomes iterative rather than one-shot:

- use NepTrain for perturbation, selection, and project scaffolding
- use NepTrainKit for interactive outlier and parity inspection

Use those tools conservatively. A fast active-learning loop with bad labels only amplifies error faster.

