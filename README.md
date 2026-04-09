# GPUMD Agent Skills

This repository is a focused skill collection for the GPUMD and NEP ecosystem.

It follows the same basic design used in `computational-chemistry-agent-skills`:

- keep each top-level skill narrow and reusable
- keep routing logic in `SKILL.md`
- keep detailed knowledge in `references/`
- keep reusable templates in `assets/examples/`
- keep deterministic helpers in `scripts/`

## Included skills

- `molecular-dynamics/gpumd`
  - GPUMD task router with subskills for `md`, `phonon`, and `transport`
- `machine-learning-potentials/nep-gpumd`
  - NEP task router with subskills for `train`, `fine-tune`, and `automation`
- `tools/gpumd-tools`
  - GPUMDkit, upstream `GPUMD/tools`, and tutorial/example lookup guidance

## Design choices

- The old monolithic GPUMD+NEP skill has been split by workflow boundary instead of by software name alone.
- Large upstream example repositories are treated as references, not vendored wholesale into the skill tree.
- Only small, high-reuse templates are bundled into `assets/examples/`.
- Local tool-source checkouts remain reproducible through `tools/gpumd-tools/scripts/bootstrap_gpumd_tool_sources.sh`.

## Reference sources used to build this collection

- GPUMD upstream repository
- GPUMD-Tutorials
- GPUMD upstream `tools/`
- NepTrain
- NepTrainKit
- `computational-chemistry-agent-skills`

