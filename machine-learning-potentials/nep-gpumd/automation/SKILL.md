---
name: automation
description: Prepare dataset-curation and active-learning workflows around NepTrain and NepTrainKit. Use when the user needs perturbation, representative-structure selection, automated NEP project scaffolding, or interactive outlier inspection rather than a single manual NEP fit.
compatibility: Requires NepTrain and/or NepTrainKit when those workflows are executed.
catalog-hidden: true
license: LGPL-3.0-or-later
metadata:
  author: Codex
  version: 0.1.0
---

# NEP Automation

## Scope

Use this subskill for tooling around iterative NEP workflows.

It should cover:

- NepTrain project initialization
- perturbation and selection loops
- job-template editing
- NepTrainKit-assisted dataset inspection

## Read first

- `references/fine-tuning-playbook.md`

Read when needed:

- `references/dataset-and-inputs.md`
- `references/training-evaluation-deployment.md`

## Bundled templates

- `assets/examples/neptrain/job.yaml`

## Expected output

1. a conservative automation plan with explicit selection and labeling stages
1. the required control files and commands
1. warnings about unstable or under-constrained active-learning loops

