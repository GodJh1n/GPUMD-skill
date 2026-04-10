# Diffusion, Viscosity, and Ionic Conductivity in GPUMD

## When to read this file

Read this file when the target observable is a mass-transport or viscous
quantity — self-diffusion coefficients, species-selective diffusion, shear
viscosity, or ionic conductivity.

## 1. Observable map

| Physical target                | GPUMD keyword           | Expected output file        |
| ------------------------------ | ----------------------- | --------------------------- |
| mean-square displacement (MSD) | `compute_msd`           | `msd.out`                   |
| self-diffusion via VAC         | `compute_sdc`           | `sdc.out`                   |
| shear viscosity (Green-Kubo)   | `compute_viscosity`     | `viscosity.out`             |
| ionic conductivity             | `compute_msd group ...` | `msd.out` + Nernst-Einstein |

Pair `compute_msd` and `compute_sdc` when both the MSD slope and the VAC
running integral are of interest — they cross-validate each other.

## 2. Equilibration recipe

1. Start with `velocity <T>` matching the target temperature.
2. Equilibrate with NPT long enough that `thermo.out` shows stationary
   pressure and temperature. For fluids, 10-50 ps is typical.
3. Switch to NVE for the production segment. Do not leave a strong
   thermostat on during Green-Kubo viscosity or MSD production — it changes
   the stress and velocity autocorrelations.

A clean two-ensemble pattern:

```text
ensemble    npt_scr 1800 1800 100 0 50 1000
run         10000

ensemble    nve
compute_msd 1 2000
compute_sdc 1 2000
run         20000
```

## 3. Self-diffusion coefficient

From the MSD slope:

```
D = (1/(2d)) * lim_{t → ∞} d(MSD(t))/dt
```

where `d = 3` for 3D bulk, `d = 2` for in-plane 2D diffusion, `d = 1` for
confined 1D. Fit the **linear region** only — include neither the ballistic
short-time regime nor the noise-dominated long-time tail.

The bundled helper performs this fit:

```bash
python scripts/fit_msd_diffusion.py msd.out --start-frac 0.3 --end-frac 0.9
```

From the VAC running integral (`sdc.out`):

```
D = ∫_0^∞ <v(0) · v(t)> dt / d
```

The plateau value of the running integral is `D`. If the integral does not
plateau before the end of the run, the production segment is too short.

## 4. Species-selective diffusion

Use the `Properties=species:S:1:pos:R:3:group:I:1` header in `model.xyz` to
label each atom with an integer group index. Inside `run.in`:

```text
compute_msd   1 2000 group 0 0
```

The `group` trailer picks one group within the first grouping method (index
0). Adjust the second index to select another group.

Use this for:

- Li+ in a solid electrolyte
- ions in a molten salt
- mobile adsorbates on a fixed substrate
- one species inside a mixture

The upstream helper `GPUMD/tools/Analysis_and_Processing/add_groups` can
assign group indices from spatial criteria automatically.

## 5. Shear viscosity (Green-Kubo)

`compute_viscosity sample_interval Nc` writes `viscosity.out` with the
off-diagonal stress autocorrelation and its running integral. The Green-Kubo
viscosity is the long-time plateau of the integral.

Rules:

- run long (10^5 - 10^6 steps in an NVE segment for moderate-viscosity
  liquids)
- average over multiple independent initial velocity seeds — stress
  autocorrelations are noisy
- inspect the running integral, not just the instantaneous
  autocorrelation

Pattern:

```text
ensemble          npt_scr 1600 1600 100 0 50 1000
run               10000

ensemble          nve
compute_viscosity 1 1000
run               50000
```

## 6. Ionic conductivity via Nernst-Einstein

The Nernst-Einstein relation converts a species diffusion coefficient to a
conductivity:

```
σ = (N_ion * q^2 * D_ion) / (V * k_B * T)
```

- `N_ion` — number of mobile ions
- `q` — carrier charge (in SI units)
- `D_ion` — species-selective diffusion coefficient from `compute_msd group`
- `V` — average simulation box volume during the production segment
- `T` — temperature
- `k_B` — Boltzmann constant

Caveats:

- Nernst-Einstein assumes uncorrelated ionic motion. For concentrated
  electrolytes, correlation corrections (Haven ratio, Onsager coefficients)
  are usually necessary. State clearly whether the reported conductivity is
  "ideal NE" or "corrected".
- Extract `V` from `thermo.out`, not from the initial `model.xyz`, because
  NPT changes the box.

## 7. Temperature dependence: Arrhenius fit

For activation energies:

1. Repeat the full workflow at three or more temperatures.
2. Plot `ln(D)` (or `ln(σ)`) against `1/T`.
3. Fit a straight line. The slope gives `-E_a / k_B`.

Use an Arrhenius fit only where it is physically justified (ionic
transport with one dominant hopping mechanism over the fitted range). Do
not extrapolate past the phase-transition temperature of the system.

## 8. Convergence discipline

| Check                                 | Why it matters                          |
| ------------------------------------- | --------------------------------------- |
| MSD linear region long enough         | fit slope is the diffusion coefficient  |
| VAC running integral plateaus         | cross-validates the MSD slope           |
| Production in NVE (or justified NVT)  | active thermostats distort correlations |
| Multiple seeds for viscosity          | stress correlations are noisy           |
| Group labels match mobile species     | wrong group → wrong `D_ion`             |
| Box volume from production, not init  | NPT changes the box                     |
| Arrhenius fit spans enough T          | at least three points, stay in one regime |

## References

- `compute_msd`: <https://gpumd.org/gpumd/input_parameters/compute_msd.html>
- `compute_sdc`: <https://gpumd.org/gpumd/input_parameters/compute_sdc.html>
- `compute_viscosity`: <https://gpumd.org/gpumd/input_parameters/compute_viscosity.html>
- GPUMD-Tutorials: `09_Silicon_diffusion`, `10_Silicon_viscosity`,
  `24_Ionic_Conductivity`, `28_thermal_transport_superionic_EMD`
