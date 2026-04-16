---
name: dft-abacus
description: Route ABACUS requests to task-specific subskills based on user intent. Use when the user asks for any ABACUS DFT calculation and you need to determine whether the task is SCF, relaxation, MD, or electronic analysis.
compatibility: Requires a user-provided structure, compatible pseudopotentials/orbital files, and runnable ABACUS environment.
license: GPL-3.0-only
catalog-hidden: true
metadata:
  author: qqgu
  version: 0.2.0
  repository: https://github.com/deepmodeling/abacus-develop
---

# DFT with ABACUS

ABACUS (Atomic-orbital Based Ab-initio Computation at UStc) is an
open-source DFT code supporting both **PW** (plane-wave) and **LCAO**
(linear combination of atomic orbitals / numerical atomic orbital)
basis sets. It is developed by the DeepModeling community and is
tightly integrated with the DeePMD / NEP / dpdata ecosystem.

## Routing

| User intent | Subskill |
|-------------|----------|
| Single-point / total energy | `dft-abacus/static` |
| Relaxation (ion / cell) | `dft-abacus/relax` (planned) |
| Molecular dynamics | `dft-abacus/md` (planned) |
| Band / DOS / electronic | `dft-abacus/electronic` (planned) |

## Key differentiators from other DFT codes

- **LCAO basis** with numerical atomic orbitals: smaller basis size than
  plane-wave for large systems, but requires orbital files per element.
- **PW basis** mode: uses `basis_type pw`, behaves like QE.
- Native `dpdata` output support via `out_level ie` for NEP/DeePMD
  training data generation.
- Three-file input convention: `INPUT`, `STRU`, `KPT` (not a single
  input file like QE or CP2K).
