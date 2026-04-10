# GPUMD Tutorial Map

Use this file when you need a concrete local example quickly.

## Core examples from GPUMD-Tutorials

### General MD

| Example                          | Best use                        | Subskill    |
| -------------------------------- | ------------------------------- | ----------- |
| `07_Silicon_thermal_expansion`   | NPT thermal expansion           | `md`        |
| `08_Silicon_melt`                | Two-phase melting workflow       | `md`        |

### Phonon

| Example                          | Best use                        | Subskill    |
| -------------------------------- | ------------------------------- | ----------- |
| `02_Carbon_density_of_states`    | Phonon DOS                      | `phonon`    |
| `06_Silicon_phonon_dispersion`   | `compute_phonon` harmonic       | `phonon`    |
| `25_lattice_dynamics_kappa`      | Fitted IFC + transport          | `phonon`    |

### Thermal transport

| Example                                            | Best use                        | Subskill    |
| -------------------------------------------------- | ------------------------------- | ----------- |
| `03_Carbon_thermal_transport_emd`                  | Green-Kubo / `compute_hac`      | `transport` |
| `04_Carbon_thermal_transport_nemd_and_hnemd`       | HNEMD, NEMD, SHC                | `transport` |
| `29_thermal_transport_multicomponent_HNEMDEC`      | Multicomponent heat transport   | `transport` |

### Diffusion and viscosity

| Example                          | Best use                        | Subskill    |
| -------------------------------- | ------------------------------- | ----------- |
| `09_Silicon_diffusion`           | MSD-based diffusion coefficient | `diffusion` |
| `10_Silicon_viscosity`           | Green-Kubo viscosity            | `diffusion` |
| `24_Ionic_Conductivity`          | Ionic transport                 | `diffusion` |

### Elastic constants

| Example                                            | Best use                        | Subskill    |
| -------------------------------------------------- | ------------------------------- | ----------- |
| `30_Elastic_constants__strain_fluctuation_method`  | Strain-fluctuation elastic      | `elastic`   |

### Mechanics (friction, deposition)

| Example                          | Best use                        | Subskill    |
| -------------------------------- | ------------------------------- | ----------- |
| `31_Nanoribbon_friction`         | Friction / layered-system       | `mechanics` |

### NEP training and fine-tuning

| Example                          | Best use                        | Subskill    |
| -------------------------------- | ------------------------------- | ----------- |
| `11_NEP_potential_PbTe`          | First NEP training example      | `train`     |
| `26_fine_tune_NEP89`            | NEP89 reuse and fine-tuning     | `fine-tune` |

## How to use the tutorial map

- Start from the example closest to the observable, not the material.
- Replace geometry, potential, and convergence settings explicitly.
- Recheck syntax against current GPUMD docs before treating an older
  tutorial as canonical.

## Searching local sources

Use the bundled search helper when the local tutorial tree is available:

```bash
python scripts/index_local_gpumd_sources.py phonon
python scripts/index_local_gpumd_sources.py hnemd --category tutorial
python scripts/index_local_gpumd_sources.py elastic --category tutorial
```
