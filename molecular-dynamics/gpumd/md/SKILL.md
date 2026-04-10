---
name: md
description: >
  Prepare and run equilibrium GPUMD molecular dynamics. Use when the user needs
  a `model.xyz`, a `run.in`, an ensemble choice (NVE/NVT/NPT), timestep and
  dump-cadence guidance, or interpretation of `thermo.out` and `movie.xyz`. This
  is the general-purpose MD subskill; specialized observables (phonons,
  transport, diffusion, elastic, mechanics) have their own subskills.
compatibility: Requires GPUMD and a valid potential file such as `nep.txt`, `nep89_*.txt`, Tersoff, or any other GPUMD-supported potential.
catalog-hidden: true
license: LGPL-3.0-or-later
metadata:
  author: Codex
  version: 0.2.0
---

# GPUMD MD

Use this subskill for ordinary equilibrium GPUMD molecular dynamics. It owns
the generic `model.xyz` + `run.in` generation path and the shared ensemble
logic used by most downstream observables.

## Quick start

```bash
gpumd < run.in | tee gpumd.log
```

## Agent responsibilities

1. Confirm the minimum inputs:
   - structure (`model.xyz` in extxyz format)
   - potential file (`nep.txt`, `nep89_*.txt`, Tersoff, …)
   - target ensemble (NVE, NVT, NPT, …)
   - target temperature and, if NPT, target pressure
   - timestep and production length
2. Write `run.in` yourself instead of asking the user to hand-write it.
3. Validate the structure file before running:
   ```bash
   python ../../../tools/gpumd-tools/scripts/validate_extxyz_headers.py model.xyz --mode model
   ```
4. Always propose a short smoke test (`run 100`) before the production segment
   to catch missing files, bad species order, or unstable dynamics.
5. Report the exact command used, the list of files produced, and the first
   sanity checks on `thermo.out`.

## Workflow

### Step 1. Prepare `model.xyz`

GPUMD expects an extxyz-style file. A minimal diamond-silicon example:

```text
2
Lattice="5.43 0 0 0 5.43 0 0 0 5.43" pbc="T T T" Properties=species:S:1:pos:R:3
Si 0.000000 0.000000 0.000000
Si 1.357500 1.357500 1.357500
```

Key rules:

- line 1 = atom count
- line 2 = header with at least `Lattice`, `pbc`, and `Properties`
- `Lattice` must contain exactly 9 numbers
- `pbc` must match the physics (`T T T` bulk, `T T F` 2D monolayer, …)
- species order must be consistent with the potential file

Use `../../../tools/gpumd-tools/scripts/validate_extxyz_headers.py --mode model` before trusting the file.

### Step 2. Write `run.in`

`run.in` is an ordered command file. Order is physically meaningful: each
`run` consumes the current state.

Annotated minimal NVT example (see [assets/examples/minimal/](../assets/examples/minimal/)):

```text
potential      nep.txt
velocity       300
time_step      1
ensemble       nvt_nhc 300 300 100
dump_thermo    100
dump_position  1000
run            10000
```

Line-by-line meaning:

- `potential nep.txt`
  - Loads the NEP potential file. Replace with the actual filename. The
    species order in the header of this potential must match the species
    appearing in `model.xyz`.
- `velocity 300`
  - Assigns initial velocities drawn from a Maxwell-Boltzmann distribution at
    300 K. Omit this line when continuing from an equilibrated restart.
- `time_step 1`
  - Sets the MD timestep in **femtoseconds**. `1.0 fs` is a conservative
    starting point for NEP-based solid-state MD. Use `0.2-0.5 fs` for lighter
    elements, hot states, or stiff bonds.
- `ensemble nvt_nhc 300 300 100`
  - Nose-Hoover chain NVT thermostat.
  - Arguments: `T_start T_stop tau_T` (the time constant `tau_T` is in units
    of the timestep, so here 100 * 1 fs = 100 fs).
- `dump_thermo 100`
  - Writes temperature, energy, stress, and box info to `thermo.out` every
    100 steps.
- `dump_position 1000`
  - Writes atomic coordinates to `movie.xyz` every 1000 steps. Use
    `dump_exyz` instead if you want full extxyz headers on every frame.
- `run 10000`
  - Integrates the equations of motion for 10000 steps. With a 1 fs timestep
    this is 10 ps of MD.

### Step 3. Run

```bash
gpumd < run.in | tee gpumd.log
```

If the local GPUMD build takes the input filename as a positional argument,
use that instead — ask the user which form their binary expects.

### Step 4. Inspect outputs

Always inspect at least:

- the first and last 10 lines of `thermo.out` for startup pathologies and
  drift
- the final frame of `movie.xyz` if the system should preserve its topology
- whether the target temperature (and pressure, for NPT) was reached without
  violent oscillation

Helper:

```bash
python scripts/parse_thermo.py thermo.out --last 50
```

## Common ensemble modifications

### NVE

Replace the ensemble line with:

```text
ensemble nve
```

Use this only after equilibration in NVT or NPT. NVE is the preferred ensemble
for Green-Kubo style production segments where an active thermostat would
contaminate the heat or stress autocorrelation.

### NVT alternatives

- `ensemble nvt_nhc T_start T_stop tau_T` — Nose-Hoover chain (recommended
  default)
- `ensemble nvt_lan T_start T_stop tau_T` — Langevin
- `ensemble nvt_bdp T_start T_stop tau_T` — Bussi-Donadio-Parrinello
- `ensemble nvt_ber T_start T_stop tau_T` — Berendsen (equilibration only)

### NPT

Isotropic stochastic-rescaling NPT:

```text
ensemble npt_scr 300 300 100 0 0 0 0 0 0 100 100 100 100 100 100 2000
```

The block is:

```
T_start T_stop tau_T  p_xx p_yy p_zz p_xy p_xz p_yz  C_xx C_yy C_zz C_xy C_xz C_yz  tau_p
```

All pressures are in GPa. `C_ij` are compressibility-like barostat parameters
(larger = softer). `tau_p` is the barostat time constant in timesteps. For a
cubic system with isotropic pressure, the minimal form is:

```text
ensemble npt_scr 300 300 100 0 50 1000
```

which is short-hand for `T_start T_stop tau_T p_hydro C tau_p` in isotropic
mode. Always confirm the exact argument count against the current GPUMD docs,
because the keyword has evolved between versions.

### Restart / continuation

Use `dump_restart` in the first run and then start the second run from the
produced restart file. Do not repeat `velocity` on the continuation run.

## Output checklist

After a run, report at least:

- exact command executed
- `run.in` path
- `model.xyz` path
- potential path
- main log path (`gpumd.log`)
- `thermo.out` existence and last line
- trajectory file existence (`movie.xyz` or `dump.xyz`)
- whether the run completed without errors or NaN
- first sanity observation from `thermo.out`

## What this subskill does NOT own

- harmonic phonon workflows → `gpumd/phonon`
- thermal conductivity → `gpumd/transport`
- diffusion / viscosity / ionic conductivity → `gpumd/diffusion`
- elastic constants → `gpumd/elastic`
- friction / deposition / impact → `gpumd/mechanics`
- NEP training itself → `machine-learning-potentials/nep-gpumd/train`

## Read first

- [references/core-files-and-ensembles.md](../references/core-files-and-ensembles.md)
- [references/gpumd-keyword-cheatsheet.md](../references/gpumd-keyword-cheatsheet.md)

Read when needed:

- [references/tutorial-map.md](../references/tutorial-map.md)

## Bundled templates

- [assets/examples/minimal/model.xyz](../assets/examples/minimal/model.xyz)
- [assets/examples/minimal/run.in](../assets/examples/minimal/run.in)
- [assets/examples/melting/run.in](../assets/examples/melting/run.in)

## Bundled helpers

- [validate_extxyz_headers.py](../../../tools/gpumd-tools/scripts/validate_extxyz_headers.py)
- [scripts/parse_thermo.py](../scripts/parse_thermo.py)

## Expected output

1. a physically consistent `model.xyz` (or a conversion plan if one is not yet
   available)
2. a `run.in` matched to the requested ensemble and observable
3. explicit assumptions about timestep, thermostat/barostat, and production
   length
4. a short sanity-check plan built around `thermo.out`

## References

- GPUMD manual: <https://gpumd.org/>
- Input files: <https://gpumd.org/gpumd/input_files/index.html>
- Output files: <https://gpumd.org/gpumd/output_files/index.html>
- `ensemble` keyword: <https://gpumd.org/gpumd/input_parameters/ensemble.html>
