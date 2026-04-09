---
name: nep-gpumd
description: Route NEP requests to task-specific subskills based on user intent. Use when the user asks for `nep.in`, `train.xyz`, `test.xyz`, NEP training, prediction mode, fine-tuning from NEP89 or an existing restart, dataset sanity checks, or NepTrain/NepTrainKit-based automation.
compatibility: Requires a runnable `nep` environment, or a user-provided GPUMD build containing the `nep` executable.
license: LGPL-3.0-or-later
metadata:
  author: Codex
  version: 0.1.0
  repository: https://github.com/brucefan1983/GPUMD
---

# NEP Task Router

Use this skill as the top-level routing layer for NEP work in the GPUMD ecosystem.

## Purpose

This router chooses one NEP subskill path:

- `nep-gpumd/train`
- `nep-gpumd/fine-tune`
- `nep-gpumd/automation`

## Shared policy

- Default to `version 4` unless the user is explicitly reproducing legacy syntax.
- Require strict agreement between species order in `type` and species labels in the dataset.
- Treat training RMSE as necessary but not sufficient; downstream MD or property validation still matters.
- Make virial/stress conventions explicit before mixing datasets from different labelers.

## Routing rules

1. If the user wants a first NEP model from labeled data, route to `nep-gpumd/train`.
1. If the user wants prediction mode, NEP89 evaluation, or fine-tuning from a restart/foundation model, route to `nep-gpumd/fine-tune`.
1. If the user wants active learning, perturbation, structure selection, job templates, or dataset inspection with NepTrain/NepTrainKit, route to `nep-gpumd/automation`.

## Resource map

- Dataset and input rules: `references/dataset-and-inputs.md`
- Training, evaluation, deployment: `references/training-evaluation-deployment.md`
- Fine-tuning playbook: `references/fine-tuning-playbook.md`
- Templates: `assets/examples/`
- Deterministic helpers: `scripts/validate_extxyz_headers.py`, `scripts/summarize_nep_loss.py`

