# GPUMD Tutorial Map

Use this file when you need a concrete local example quickly.

## Core examples from GPUMD-Tutorials

| Example | Best use | Notes |
| --- | --- | --- |
| `02_Carbon_density_of_states` | phonon DOS | simple carbon example with direct GPUMD outputs |
| `03_Carbon_thermal_transport_emd` | Green-Kubo / `compute_hac` | clean equilibrium transport template |
| `04_Carbon_thermal_transport_nemd_and_hnemd` | HNEMD, NEMD, SHC | best starting point for transport method comparisons |
| `06_Silicon_phonon_dispersion` | `compute_phonon` | minimal harmonic phonon example |
| `07_Silicon_thermal_expansion` | NPT thermal expansion | useful barostat pattern |
| `08_Silicon_melt` | two-phase melting workflow | useful for phase-coexistence logic |
| `09_Silicon_diffusion` | diffusion coefficient extraction | demonstrates VAC and MSD usage |
| `10_Silicon_viscosity` | Green-Kubo viscosity | useful for generic correlation-function workflows |
| `11_NEP_potential_PbTe` | first NEP training example | strong baseline for `nep.in` and dataset structure |
| `24_Ionic_Conductivity` | ionic transport | useful when charge-carrying diffusion matters |
| `25_lattice_dynamics_kappa` | fitted IFC + transport | broader lattice-dynamics workflow beyond bare GPUMD phonons |
| `26_fine_tune_NEP89` | NEP89 reuse and fine-tuning | best local reference for foundation-model-style reuse |
| `29_thermal_transport_multicomponent_HNEMDEC` | multicomponent heat transport | do not replace with single-component formulas |
| `31_Nanoribbon_friction` | friction and layered-system workflow | useful for group and interface logic |

## How to use the tutorial map

- Start from the example closest to the observable, not the material.
- Replace geometry, potential, and convergence settings explicitly.
- Recheck syntax against current GPUMD docs before treating an older tutorial as canonical.

