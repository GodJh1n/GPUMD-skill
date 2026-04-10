---
name: automation
description: >
  Prepare dataset-curation and active-learning workflows around NepTrain and
  NepTrainKit. Use when the user needs perturbation-based sampling,
  representative-structure selection (FPS / max-min), automated NEP project
  scaffolding, interactive outlier inspection, or iterative retrain loops
  rather than a single manual NEP fit.
compatibility: Requires NepTrain (pip install neptrain) and/or NepTrainKit when those workflows are executed.
catalog-hidden: true
license: GPL-3.0-only
metadata:
  author: Codex
  version: 0.2.0
---

# NEP Automation

Use this subskill when the user wants to go beyond a single manual
`nep` invocation and into iterative dataset curation, active-learning
loops, or GUI-assisted inspection of training data.

Two tools dominate the NEP automation ecosystem:

| Tool         | Role                                                        |
| ------------ | ----------------------------------------------------------- |
| **NepTrain** | CLI-driven active-learning loop: perturb → sample → label → retrain |
| **NepTrainKit** | GUI / notebook tool for dataset inspection, outlier detection, and frame selection |

## Agent responsibilities

1. Confirm which tool is installed and its version.
2. Do not set up an active-learning loop until the user has a working
   baseline NEP (from the `train` or `fine-tune` subskill).
3. Explain the perturbation → selection → labeling → retrain cycle
   before generating config files.
4. Warn the user about loop stability: an active-learning loop that
   adds low-quality frames or frames outside the DFT convergence
   envelope will degrade the model, not improve it.

## NepTrain workflow

### Concept

NepTrain orchestrates an iterative loop:

```
┌──────────────────────────────────────────────┐
│  1. Start with a baseline NEP + train.xyz    │
│  2. Run short GPUMD MD at target conditions  │
│  3. Select representative frames (FPS)       │
│  4. Label selected frames with DFT           │
│  5. Append to train.xyz                      │
│  6. Retrain NEP                              │
│  7. Repeat until convergence                 │
└──────────────────────────────────────────────┘
```

### Project layout

```
project/
├── job.yaml           # NepTrain control file
├── nep.in             # NEP training input
├── nep.txt            # current best model
├── train.xyz          # growing training set
├── test.xyz           # held-out test set
├── structure/         # GPUMD model.xyz seed structures
│   └── model.xyz
├── run.in             # GPUMD sampling run.in
└── cache/             # NepTrain working directory
```

### job.yaml anatomy

Annotated example (see
[assets/examples/neptrain/job.yaml](../assets/examples/neptrain/job.yaml)):

```yaml
version: 2.0.0
work_path: ./cache
current_job: nep
init_train_xyz: ./train.xyz      # starting training set
init_nep_txt: ./nep.txt          # starting model

nep:
  nep_restart: true              # use nep.restart for warm-start
  nep_restart_step: 10000        # generations per retrain cycle
  nep_in_path: ./nep.in
  test_xyz_path: ./test.xyz
  machine:                       # execution backend
    context_type: LazyLocal
    batch_type: Shell
    local_root: ./
    remote_root: ./
  resources:
    number_node: 1
    gpu_per_node: 1
    group_size: 1

gpumd:
  step_times:                    # MD timesteps per sampling stage
  - 10
  - 50
  - 100
  temperature_every_step:        # temperatures to sample (K)
  - 300
  - 600
  model_path: ./structure        # directory containing model.xyz
  run_in_path: ./run.in          # GPUMD run.in for sampling
  machine:
    context_type: LazyLocal
    batch_type: Shell
    local_root: ./
    remote_root: ./
  resources:
    number_node: 1
    gpu_per_node: 1
    group_size: 1

select:
  max_selected: 20               # max frames to select per iteration
  min_distance: 0.01             # FPS min-distance threshold
  filter: 0.6                   # descriptor-space diversity filter
```

Key parameters:

- `nep_restart_step`: keep low (5000–20000) during exploration, increase
  for final refinement.
- `step_times`: list of MD durations per cycle. Longer runs explore more
  phase space but risk model-driven artifacts.
- `temperature_every_step`: temperatures to scan. Cover the range of
  interest for your target property.
- `max_selected`: cap on new frames per iteration. Too many frames per
  cycle risks adding correlated data.
- `min_distance` / `filter`: control descriptor-space diversity. Lower
  `min_distance` → more aggressive pruning; higher `filter` → stricter
  outlier rejection.

### Running NepTrain

```bash
# Initialize project
neptrain init

# Run the active-learning loop
neptrain run job.yaml
```

NepTrain manages the retrain/sample/select loop automatically. Monitor
the `cache/` directory for per-iteration outputs.

### When to stop

Stop the loop when:

- prediction RMSE on the test set plateaus across iterations
- new iterations add fewer than 2–3 frames
- the target physical observable converges (check with a downstream MD)

Do **not** rely on training loss alone — it always decreases.

## NepTrainKit workflow

NepTrainKit provides an interactive GUI for:

- visualizing descriptor space (PCA / t-SNE of NEP descriptors)
- identifying outlier frames
- manually accepting / rejecting frames before retraining
- comparing parity across config types

### Typical usage

```python
from NepTrainKit import NepTrainKit

kit = NepTrainKit()
kit.load_dataset("train.xyz")
kit.load_model("nep.txt")
kit.visualize()          # opens interactive window
kit.export("curated.xyz")  # save after manual curation
```

Or via the CLI:

```bash
NepTrainKit
```

### When to use NepTrainKit vs. NepTrain

| Scenario | Recommended |
| -------- | ----------- |
| Automated loop, many iterations | NepTrain |
| Manual inspection of a suspicious dataset | NepTrainKit |
| Post-loop cleanup before final production fit | NepTrainKit |
| Debugging why a model is unstable | NepTrainKit (outlier detection) |

## Stability warnings

Active-learning loops can diverge. Common failure modes:

1. **Snowball effect**: the model samples unphysical states, which get
   labeled and added, making the next model worse.
   *Fix*: set conservative `step_times` and validate each cycle's MD
   with a short NVE sanity check.

2. **DFT inconsistency**: different iterations use different DFT
   settings (k-points, functional, convergence).
   *Fix*: lock the DFT workflow before starting the loop.

3. **Correlated frames**: selecting too many frames from a single
   trajectory adds redundant data.
   *Fix*: keep `max_selected` low and `min_distance` high.

4. **Under-constrained loop**: no test set, no validation, just
   training loss.
   *Fix*: always hold out a test set and check a physical observable
   every few iterations.

## Agent checklist

- [ ] baseline NEP is already working before starting automation
- [ ] `job.yaml` covers the target temperature and pressure range
- [ ] DFT labeling workflow is locked and documented
- [ ] `max_selected` and `min_distance` are conservative
- [ ] test set is held out and not contaminated by the loop
- [ ] downstream observable checked every few iterations
- [ ] final curated dataset inspected with NepTrainKit before production fit

## Read first

- [references/fine-tuning-playbook.md](../references/fine-tuning-playbook.md)

Read when needed:

- [references/dataset-and-inputs.md](../references/dataset-and-inputs.md)
- [references/training-evaluation-deployment.md](../references/training-evaluation-deployment.md)
- [references/labels-from-dft.md](../references/labels-from-dft.md)

## Bundled templates

- [assets/examples/neptrain/job.yaml](../assets/examples/neptrain/job.yaml)

## Expected output

1. a conservative automation plan with explicit selection and labeling stages
2. the required control files (`job.yaml`, `nep.in`, `run.in`)
3. warnings about unstable or under-constrained active-learning loops
4. a validation strategy for each iteration

## References

- NepTrain: <https://github.com/aboys-cb/NepTrain>
- NepTrainKit: <https://github.com/aboys-cb/NepTrainKit>
- GPUMD-Tutorials: active-learning examples
