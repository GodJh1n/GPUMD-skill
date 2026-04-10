# GPUMD Core Files And Ensembles

## When to read this file

Read this file when the task is about ordinary GPUMD setup:

- preparing `model.xyz`
- writing or checking `run.in`
- choosing an ensemble
- deciding timestep and dump cadence
- interpreting the main GPUMD outputs

## 1. `model.xyz`

GPUMD expects an extxyz-style structure file.

Minimum requirements:

- line 1: atom count
- line 2: header with `Lattice="..."` and `Properties=...`
- remaining lines: atom rows consistent with the declared properties

Recommended header fields:

- `Lattice="a1 a2 a3 b1 b2 b3 c1 c2 c3"`
- `pbc="T T T"` or the correct mixed periodicity such as `T T F`
- `Properties=species:S:1:pos:R:3`

Useful optional fields:

- `group:I:M` for group-resolved analyses such as `compute_shc`
- `vel:R:3` if restarting from prepared velocities

Minimal example:

```text
2
Lattice="5.43 0 0 0 5.43 0 0 0 5.43" pbc="T T T" Properties=species:S:1:pos:R:3
Si 0.000000 0.000000 0.000000
Si 1.357500 1.357500 1.357500
```

Sanity checks that matter:

- The number of atom rows must equal the first-line count.
- The number of columns in each row must match `Properties`.
- `Lattice` must contain exactly 9 numbers.
- `pbc` must match the intended physics. For example, many 2D materials should use `T T F`, not `T T T`.

Use `tools/gpumd-tools/scripts/validate_extxyz_headers.py model.xyz --mode model` for a fast header check.

## 2. `run.in`

`run.in` is an ordered command file. Order is physically meaningful.

A common safe order is:

1. load potential
1. prepare velocities if needed
1. define timestep
1. define ensemble
1. define dumps or computes
1. run equilibration
1. switch ensemble or compute settings if needed
1. run production

Example minimal NVT template:

```text
potential      nep.txt
velocity       300
time_step      1
ensemble       nvt_nhc 300 300 100
dump_thermo    100
dump_position  1000
run            10000
```

## 3. Time step and ensemble guidance

### Timestep

GPUMD uses femtoseconds for `time_step`.

Conservative starting points:

- `1.0 fs` for many NEP-based solid-state MD runs
- `0.2-0.5 fs` for lighter elements, hot reactive states, or unusually stiff bonds

If the total energy drifts badly in a short NVE sanity test, the timestep is often too large, the model is unstable in that region, or both.

### Ensemble selection

Use the ensemble to match the actual stage of the workflow.

Typical pattern:

- equilibration: `nvt_nhc`, `npt_scr`, or another thermostat/barostat
- production dynamics without external driving: usually `nve`
- HNEMD production: thermostatting is typically retained, but the field must stay in the linear-response regime

Do not leave a thermostat on during a Green-Kubo production segment unless the method specifically calls for it.

## 4. Main outputs

Common outputs include:

- `thermo.out`: temperature, energy, stress, box evolution
- `movie.xyz`: trajectory snapshots if `dump_position` is enabled
- `restart.xyz`: restart state when requested by workflow
- method-specific files such as `omega2.out`, `hac.out`, or `kappa.out`

At minimum, a new workflow should always inspect:

- early `thermo.out` lines for startup pathologies
- late `thermo.out` lines for drift or target-condition failure
- trajectory snapshots if melting, fracture, deposition, or diffusion are involved

## 5. Ensemble-specific caution points

### NVT and NPT

Use these to thermalize or relax the box.

Check:

- temperature reaches the target without violent oscillation
- pressure is physically sensible for the system
- box dimensions do not drift unphysically

### NVE

Use this when you need conservative production dynamics.

Check:

- energy drift is acceptably small
- the structure is already equilibrated before switching to NVE

### Low-dimensional systems

For slabs, ribbons, and monolayers:

- make the nonperiodic direction explicit in `pbc`
- do not report bulk-like transport units without stating the adopted thickness convention

## 6. High-value local templates

- `assets/examples/minimal/`
- `assets/examples/phonon/`
- `assets/examples/transport/emd/`
- `assets/examples/transport/hnemd/`

## References

- GPUMD manual: <https://gpumd.org/>
- GPUMD input files: <https://gpumd.org/gpumd/input_files/index.html>
- GPUMD output files: <https://gpumd.org/gpumd/output_files/index.html>

