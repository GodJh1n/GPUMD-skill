---
name: transport
description: >
  Prepare GPUMD thermal-transport workflows for EMD / HNEMD / NEMD / SHC /
  HNEMDEC. Use when the user needs `compute_hac`, `compute_hnemd`,
  `compute_hnemdec`, `compute_shc`, thermal-conductivity extraction, or
  transport-specific sampling and convergence guidance.
compatibility: Requires GPUMD and a potential that is numerically stable in the target state.
catalog-hidden: true
license: LGPL-3.0-or-later
metadata:
  author: Codex
  version: 0.2.0
---

# GPUMD Thermal Transport

Use this subskill for heat-transport calculations in GPUMD. Diffusion,
viscosity, and ionic conductivity are related observables but live in
`gpumd/diffusion`.

## Quick method picker

| Target                                         | Method                 | Keyword            |
| ---------------------------------------------- | ---------------------- | ------------------ |
| bulk κ in a single-component crystal / liquid  | HNEMD                  | `compute_hnemd`    |
| bulk κ via Green-Kubo                          | EMD                    | `compute_hac`      |
| length dependence or interface κ               | NEMD                   | see docs           |
| spectral decomposition of κ                    | spectral heat current  | `compute_shc`      |
| multi-component coupled transport              | HNEMDEC                | `compute_hnemdec`  |

## Agent responsibilities

1. Pick the method from the observable and justify the pick explicitly.
2. Require an explicit equilibration stage before production.
3. Enforce linear-response discipline for HNEMD: start at a small driving
   field and only increase if the result is field-independent within
   uncertainty.
4. For low-dimensional systems, require an explicit thickness convention
   before reporting `W m^-1 K^-1`.
5. Report the number of seeds, production length, and uncertainty next to
   the κ value.

## Workflow

### Step 1. Equilibrate

Always start from a short NVT / NPT equilibration to the target state, then
switch ensemble for production. Do not keep an aggressive thermostat on
during a Green-Kubo production segment.

### Step 2. EMD / Green-Kubo via `compute_hac`

Annotated pattern (see [assets/examples/transport/emd/run.in](../assets/examples/transport/emd/run.in)):

```text
potential   nep.txt
velocity    300
time_step   1

# equilibrate
ensemble    npt_scr 300 300 100 0 0 0 100 100 100 1000
dump_thermo 100
run         100000

# production in NVE
ensemble    nve
dump_thermo 100
compute_hac 20 200 2
run         2000000
```

- `compute_hac sample_interval Nc output_interval`
  - `sample_interval` — store heat-current samples every N steps
  - `Nc` — number of correlation points retained in `hac.out`
  - `output_interval` — how often the running integral is written

Inspect `hac.out` and the running integral of the correlation function, not
just the peak. Use multiple seeds when the noise level matters.

### Step 3. HNEMD via `compute_hnemd`

Annotated pattern (see [assets/examples/transport/hnemd/run.in](../assets/examples/transport/hnemd/run.in)):

```text
potential   nep.txt
velocity    300
time_step   1

# equilibrate
ensemble    npt_scr 300 300 100 0 0 0 100 100 100 1000
dump_thermo 100
run         100000

# HNEMD production (thermostatted)
ensemble    nvt_nhc 300 300 100
compute_hnemd 1000 0.00001 0 0
dump_thermo 1000
run         1000000
```

- `compute_hnemd output_interval Fe_x Fe_y Fe_z`
  - `Fe_x`, `Fe_y`, `Fe_z` are the driving-field components in `1/Å`.
  - Start at ~`1e-5 1/Å` for stiff crystalline solids and verify
    field-independence before trusting the result.

Post-process with the bundled helper:

```bash
python scripts/average_hnemd_kappa.py kappa.out --discard-frac 0.2
```

### Step 4. SHC / spectral decomposition

For spectral heat-current decomposition use `compute_shc` with appropriate
group definitions. Groups are set up in `model.xyz` via `group:I:M` in the
`Properties` header, or by `add_groups` preprocessing.

### Step 5. HNEMDEC (multi-component coupled transport)

For multi-component systems with cross-coupling between mass and heat flux
(molten salts, ionic conductors, mixed liquids), use `compute_hnemdec`. Do
not apply the single-component HNEMD formula to a multi-component system
without checking the cross-coupling.

Relevant tutorial anchor: `29_thermal_transport_multicomponent_HNEMDEC`.

### Step 6. Report

For a publishable transport number, report at least:

- number of independent seeds or replicas
- production length per seed
- cell size
- uncertainty estimate
- whether the result was tested against a different driving field or a second
  cell size

## Common pitfalls

- leaving a strong thermostat on during Green-Kubo production
- treating a short HNEMD trajectory as converged
- reporting `W m^-1 K^-1` for a monolayer without a stated thickness convention
- using `compute_hnemd` in a regime where the flux is no longer linear in the
  field

## Read first

- [references/thermal-transport-workflow.md](../references/thermal-transport-workflow.md)

Read when needed:

- [references/core-files-and-ensembles.md](../references/core-files-and-ensembles.md)
- [references/gpumd-keyword-cheatsheet.md](../references/gpumd-keyword-cheatsheet.md)
- [references/tutorial-map.md](../references/tutorial-map.md)

## Bundled templates and helpers

- [assets/examples/transport/emd/run.in](../assets/examples/transport/emd/run.in)
- [assets/examples/transport/hnemd/run.in](../assets/examples/transport/hnemd/run.in)
- [scripts/average_hnemd_kappa.py](../scripts/average_hnemd_kappa.py)
- [scripts/parse_thermo.py](../scripts/parse_thermo.py)

## Expected output

1. an explicit method choice with the reason
2. a transport-specific GPUMD input template
3. linear-response / convergence / reporting caveats that match the method

## References

- `compute_hac`: <https://gpumd.org/gpumd/input_parameters/compute_hac.html>
- `compute_hnemd`: <https://gpumd.org/gpumd/input_parameters/compute_hnemd.html>
- `compute_shc`: <https://gpumd.org/gpumd/input_parameters/compute_shc.html>
- `compute_hnemdec`: <https://gpumd.org/gpumd/input_parameters/compute_hnemdec.html>
- Fan et al., Phys. Rev. B 99, 064308 (2019)
- Fan et al., Phys. Rev. B 92, 094301 (2015)
