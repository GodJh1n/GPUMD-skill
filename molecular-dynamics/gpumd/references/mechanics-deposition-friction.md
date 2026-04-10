# Mechanics, Deposition, and Friction Workflows in GPUMD

## When to read this file

Read this file when the task is about mechanics-type workflows where groups,
external drivers, and interface conditions dominate the physics: friction,
deposition, impact, indentation, or any simulation with a moving driver and
a fixed anchor.

## 1. Group bookkeeping is load-bearing

For mechanics workflows, group indices are the primary physical knobs.
Every group has a distinct role: fixed anchor, thermostat bath, production
region, driver. Getting the group layout wrong silently breaks the physics.

Declare groups in `model.xyz` with the extxyz `group` column:

```text
N
Lattice="..." pbc="T T T" Properties=species:S:1:pos:R:3:group:I:1
C 0.000 0.000 0.000 0
C 1.420 0.000 0.000 0
...
```

Multiple independent grouping schemes use `group:I:M` with `M > 1`:

```
Properties=species:S:1:pos:R:3:group:I:2
```

Then each atom row carries two trailing integers, one per grouping scheme.

The upstream tool `GPUMD/tools/Analysis_and_Processing/add_groups` can
assign groups from spatial criteria (e.g. atoms below a z-threshold become
group 3, atoms above become group 0, …). Use it when the structure is
large.

## 2. Friction workflows

Friction workflows usually layer a driving group on top of a thermostatted
layer on top of a fixed substrate. The canonical recipe adapted from
`31_Nanoribbon_friction`:

- group 0 — ghost driver (spring-driven, not directly thermostatted)
- group 1 — Langevin thermostat layer
- group 2 — production / measurement layer
- group 3 — fixed bottom layer

```text
potential   gr_bn_mos2.ilp
potential   nep.txt
velocity    300
time_step   1

ensemble    heat_lan 300 100 0 1 2
fix         3
add_spring  ghost_atom 0 100.0 0.0 0.0 0.0 0 0.0005 0.0 0.0
dump_thermo 100
dump_exyz   10000 0 0
run         1000000
```

- `heat_lan T tau grp_fix grp_thm grp_prod` — applies Langevin to the
  thermostat layer and leaves the production layer dynamic.
- `fix 3` — freezes the bottom layer entirely so there is no net drift.
- `add_spring ghost_atom g k x0 y0 z0 axis v0 vx vy` — attaches a spring
  between the centre-of-mass of group `g` and a ghost point that moves at
  velocity `(vx, vy, vz)`. This provides the shearing drive.

The friction force is read off the spring extension (or equivalently from
the group-resolved stress in `thermo.out`).

Key points to state with any friction result:

- normal load
- sliding velocity
- thermostat placement
- layer thicknesses
- potential(s) used — including any interlayer term

## 3. Deposition workflows

Deposition simulates atoms landing onto a substrate. Adapted from
`16_Deposition` and `27_Carbon_Cu111_deposition`:

- group 0 — fixed bottom substrate (prevents rigid drift)
- group 1 — Langevin thermostat slab (absorbs impact energy)
- group 2 — free surface + deposited atoms (microcanonical)

```text
potential   nep.txt
velocity    300
time_step   1

ensemble    heat_lan 300 100 0 1
fix         0
dump_thermo 100
dump_exyz   1000 0 0
run         100000
```

The actual deposition loop is typically driven externally. The tutorial
ships a `deposition.py` script that:

1. inserts one or more atoms above the slab with a given velocity
2. restarts the GPUMD run
3. repeats at a configurable cadence

Rules:

- inserted atoms must not overlap existing atoms
- the thermostat layer must be thick enough to absorb the impact without
  heating the reactive region unphysically
- the bottom layer must be frozen so the slab does not drift under repeated
  momentum injection

## 4. Impact / collision workflows

For impact events the simplest setup uses a pre-initialized `model.xyz`
where the projectile group already has a directed initial velocity
(`vel:R:3` column in extxyz):

```text
N
Lattice="..." pbc="T T T" Properties=species:S:1:pos:R:3:vel:R:3:group:I:1
...
```

Then run NVE and dump position / force frequently:

```text
ensemble    nve
dump_thermo 100
dump_exyz   100 0 0
run         20000
```

This separates the projectile kinetics from the dynamics of the target.

For repeated impacts, a script-level loop (like `deposition.py`) is more
ergonomic than trying to re-seed velocities inside a single `run.in`.

## 5. General rules for mechanics results

- always report group layout alongside the number (a friction force with
  no group / load / velocity is unfalsifiable)
- thermostats should be applied to absorb energy, not to hide instabilities
  in the driver layer
- `fix` freezes atoms completely — do not `fix` a group you still want to
  thermostat; the two are incompatible in intent
- the ghost-atom driver pattern is deterministic; random velocity kicks
  are not a substitute

## References

- `add_spring`: <https://gpumd.org/gpumd/input_parameters/add_spring.html>
- `fix`: <https://gpumd.org/gpumd/input_parameters/fix.html>
- `ensemble heat_lan`: <https://gpumd.org/gpumd/input_parameters/ensemble.html>
- GPUMD-Tutorials: `16_Deposition`, `20_Impact`, `21_Fatigue`,
  `27_Carbon_Cu111_deposition`, `31_Nanoribbon_friction`
