---
name: fine-tune
description: Prepare NEP prediction and fine-tuning workflows from an existing model or foundation model such as NEP89. Use when the user needs out-of-the-box evaluation, targeted MD sampling, `prediction 1`, or `fine_tune <model> <restart>` configuration.
compatibility: Requires an existing NEP model and, for true fine-tuning, the matching restart/state files supported by the current NEP implementation.
catalog-hidden: true
license: LGPL-3.0-or-later
metadata:
  author: Codex
  version: 0.1.0
---

# NEP Fine-Tune

## Scope

Use this subskill for model reuse rather than first-principles baseline fitting.

It should cover:

- out-of-the-box property checks
- prediction-mode diagnostics
- target-state MD sampling for new labels
- fine-tuning from an existing NEP model and restart file

## Read first

- `references/fine-tuning-playbook.md`

Read when needed:

- `references/dataset-and-inputs.md`
- `references/training-evaluation-deployment.md`

## Bundled templates

- `assets/examples/prediction/nep.in`
- `assets/examples/fine-tune/model.xyz`
- `assets/examples/fine-tune/out-of-box-hnemd-run.in`
- `assets/examples/fine-tune/sampling-run.in`
- `assets/examples/fine-tune/nep.in`

## Expected output

1. a reproducible fine-tuning plan tied to the target property
1. the exact files needed for prediction or fine-tuning
1. a comparison plan between out-of-the-box and fine-tuned behavior

