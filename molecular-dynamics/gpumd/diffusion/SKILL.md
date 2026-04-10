---
name: diffusion
description: >
  Prepare GPUMD workflows for self-diffusion, ionic conductivity, and
  viscosity. Use when the user needs `compute_msd`, `compute_sdc`,
  `compute_viscosity`, Nernst-Einstein ionic conductivity, Arrhenius fitting,
  or species-selective diffusion through group indices.
compatibility: Requires GPUMD and a potential stable in the target fluid / ionic state.
catalog-hidden: true
license: GPL-3.0-only
metadata:
  author: Jhin
  version: 0.2.0
---

# GPUMD Diffusion, Viscosity, Ionic Conductivity

Use this subskill for mass-transport and viscous observables. These live
separately from `gpumd/transport` because the physics, the averaging scheme,
and the expected outputs differ from thermal conductivity.

## Observable picker

| Target                      | Keyword              | Output file       |
| --------------------------- | -------------------- | ----------------- |
| mean-square displacement    | `compute_msd`        | `msd.out`         |
| self-diffusion coefficient  | `compute_sdc`        | `sdc.out`         |
| shear viscosity (GK)        | `compute_viscosity`  | `viscosity.out`   |
| ionic conductivity          | `compute_msd group`  | `msd.out` + NE formula |

## Agent responsibilities

1. Confirm the user's target observable and pick the right keyword. Do not
   assume diffusion implies ionic conductivity or vice versa.
2. Equilibrate in NPT (or NVT if cell is fixed), then switch to NVE for
   production. Active thermostats should not be left on during a Green-Kubo
   viscosity or equilibrium MSD segment.
3. For ionic conductivity, require the user to specify which species are the
   mobile carriers and set up group labels in `model.xyz` accordingly.
4. For Arrhenius analysis, require at least three temperatures.
5. For low-dimensional or confined systems, explicitly state the geometry
   convention before reporting conductivity.

## Workflow: self-diffusion via MSD + VAC

Annotated example (see
[assets/examples/diffusion/run.in](../assets/examples/diffusion/run.in)):

```text
potential   nep.txt
velocity    2500
time_step   2

# equilibrate at 2500 K (above melting) then cool to target
ensemble    npt_scr 2500 2500 100 0 50 1000
dump_thermo 100
run         10000

ensemble    npt_scr 1800 1800 100 0 50 1000
dump_thermo 100
run         10000

# production in NVE, both MSD and VAC running simultaneously
ensemble    nve
dump_thermo 100
compute_msd 1 2000
compute_sdc 1 2000
run         20000
```

- `compute_msd sample_interval Nc` — writes `msd.out` with the mean-square
  displacement up to `Nc` time-lags, sampled every `sample_interval` steps.
- `compute_sdc sample_interval Nc` — writes `sdc.out` with velocity
  autocorrelation and its running integral, from which the diffusion
  coefficient is read off as the long-time plateau.

Fit the diffusion coefficient from the linear region of `msd.out`:

```bash
python scripts/fit_msd_diffusion.py msd.out --start-frac 0.3 --end-frac 0.9
```

### Rules for a trustworthy diffusion number

- use an NVE production segment unless the physics demands a thermostat
- the MSD must reach a linear-in-time region long enough to fit with
  statistical confidence
- the VAC running integral should plateau — if it does not, the run is too
  short
- multiple seeds or initializations are encouraged for fluids

## Workflow: shear viscosity

Annotated example (see
[assets/examples/viscosity/run.in](../assets/examples/viscosity/run.in)):

```text
potential   nep.txt
velocity    2500
time_step   2

ensemble    npt_scr 2500 2500 100 0 50 1000
dump_thermo 100
run         10000

ensemble    npt_scr 1600 1600 100 0 50 1000
dump_thermo 100
run         10000

ensemble          nve
dump_thermo       100
compute_viscosity 1 1000
run               50000
```

- `compute_viscosity sample_interval Nc` — writes `viscosity.out` with the
  off-diagonal stress autocorrelation and its running integral.

The Green-Kubo viscosity is the long-time plateau of the integral; inspect
it like a heat-flux autocorrelation. Multiple seeds are strongly recommended
because stress fluctuations are noisy.

## Workflow: ionic conductivity

Species-selective MSD plus the Nernst-Einstein relation (see the
`24_Ionic_Conductivity` tutorial for a complete LLZO example).

1. Build `model.xyz` with a `group:I:M` column flagging the mobile species.
2. Run multi-temperature NPT → NVE with species-resolved MSD:
   ```text
   compute_msd 1 2000 group 0 0
   ```
   The `group 0 0` syntax means "compute MSD for group method 0, group index
   0", i.e. the first grouping scheme, first label. Adjust to the mobile
   species' label.
3. Extract the diffusion coefficient `D_ion` from the linear region.
4. Apply Nernst-Einstein:
   ```
   σ = (N_ion * q^2) / (V * k_B * T) * D_ion
   ```
5. Repeat at 3+ temperatures and fit an Arrhenius line to estimate the
   activation energy.

## Convergence checklist

- [ ] structure is equilibrated in the target state
- [ ] production is in NVE (or the target ensemble explicitly justified)
- [ ] MSD is linear over the fit window
- [ ] VAC integral has plateaued
- [ ] for ionic conductivity: group labels match the intended carrier
- [ ] for Arrhenius: at least three temperatures
- [ ] low-dimensional geometry convention stated if applicable

## Read first

- [references/diffusion-viscosity-ionic.md](../references/diffusion-viscosity-ionic.md)

Read when needed:

- [references/core-files-and-ensembles.md](../references/core-files-and-ensembles.md)
- [references/gpumd-keyword-cheatsheet.md](../references/gpumd-keyword-cheatsheet.md)
- [references/tutorial-map.md](../references/tutorial-map.md)

## Bundled templates and helpers

- [assets/examples/diffusion/run.in](../assets/examples/diffusion/run.in)
- [assets/examples/diffusion/model.xyz](../assets/examples/diffusion/model.xyz)
- [assets/examples/viscosity/run.in](../assets/examples/viscosity/run.in)
- [scripts/fit_msd_diffusion.py](../scripts/fit_msd_diffusion.py)
- [scripts/parse_thermo.py](../scripts/parse_thermo.py)

## Expected output

1. an equilibration + production input file for the selected observable
2. an extraction recipe for `msd.out`, `sdc.out`, or `viscosity.out`
3. the convergence and uncertainty discussion
4. (ionic) group definition and Nernst-Einstein post-processing

## Cross-skill pointers

- For generating initial configurations of liquid or molten systems
  (mixtures, melts, solutions), use `packmol-generate-mixture` to pack
  molecules into a simulation box before converting to `model.xyz`.
- For structure manipulation (supercells, substitutions) →
  `pymatgen-structure`.

## References

- `compute_msd`: <https://gpumd.org/gpumd/input_parameters/compute_msd.html>
- `compute_sdc`: <https://gpumd.org/gpumd/input_parameters/compute_sdc.html>
- `compute_viscosity`: <https://gpumd.org/gpumd/input_parameters/compute_viscosity.html>
- GPUMD-Tutorials: `09_Silicon_diffusion`, `10_Silicon_viscosity`,
  `24_Ionic_Conductivity`, `28_thermal_transport_superionic_EMD`
