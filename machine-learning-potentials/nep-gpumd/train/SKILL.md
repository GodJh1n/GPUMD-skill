---
name: train
description: Prepare baseline NEP training workflows from labeled extxyz datasets. Use when the user needs `nep.in`, `train.xyz`, `test.xyz`, parameter guidance, `loss.out` interpretation, or deployment of `nep.txt` back into GPUMD.
compatibility: Requires the `nep` executable and labeled training/test datasets in NEP-compatible extxyz format.
catalog-hidden: true
license: LGPL-3.0-or-later
metadata:
  author: Codex
  version: 0.1.0
---

# NEP Train

## Scope

Use this subskill for baseline NEP training from labeled data.

It should prepare:

- `nep.in`
- `train.xyz`
- `test.xyz`
- a validation plan for `loss.out`, parity files, and downstream MD use

## Read first

- `references/dataset-and-inputs.md`
- `references/training-evaluation-deployment.md`

## Bundled templates and helpers

- `assets/examples/baseline/nep.in`
- `assets/examples/baseline/train.xyz`
- `assets/examples/baseline/test.xyz`
- `scripts/validate_extxyz_headers.py`
- `scripts/summarize_nep_loss.py`

## Expected output

1. a NEP-ready dataset and input file set
1. parameter choices with explicit assumptions
1. training and evaluation checks before deployment

