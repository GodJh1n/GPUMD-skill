---
name: mechanics
description: >
  Prepare GPUMD mechanics-type workflows: friction, deposition, impact, and
  other group-based interface simulations. Use when the user needs
  `add_spring`, ghost-atom setups, layered 2D material shearing, deposition
  event sampling, or impact/collision dynamics.
compatibility: >
  Requires GPUMD with the potentials needed for the target interface. Layered
  2D-material friction typically needs ILP or a NEP fit covering both layers.
catalog-hidden: true
license: GPL-3.0-only
metadata:
  author: Jhin
  version: 0.2.0
---

# GPUMD Mechanics

Use this subskill for workflows where the physics is dominated by groups,
fixed atoms, external drivers, or interface events rather than bulk
equilibrium dynamics.

## Scope

Covered targets:

- friction / shearing of layered or 2D systems
- deposition / growth onto a fixed substrate
- impact / collision dynamics
- nanoindentation-style loading through ghost atoms or springs
- group-resolved analysis around an interface

Not covered (route elsewhere):

- thermal conductivity across the interface → `gpumd/transport`
- diffusion of adsorbates in the bulk phase → `gpumd/diffusion`
- phonon dispersion of the isolated layers → `gpumd/phonon`

## Agent responsibilities

1. Ask the user which groups are fixed, which groups move, and which groups
   are thermostatted. Mechanics workflows live and die by group bookkeeping.
2. Require an explicit ensemble choice for each group — typically
   `heat_lan` (Langevin) on a thermostat layer and `fix 0` or
   `add_spring ghost_atom` on driver layers.
3. For friction, require an explicit driving velocity or driving force, and
   a stated normal load if applicable.
4. For deposition, require a clear separation between the substrate (fixed
   or thermostatted) and the adatoms (injected over time).
5. Report group definitions alongside the result — a friction number without
   a stated group and load is unfalsifiable.

## Workflow: friction on a layered 2D system

Pattern adapted from `31_Nanoribbon_friction`. See
[assets/examples/friction/run.in](../assets/examples/friction/run.in).

```text
potential   gr_bn_mos2.ilp
potential   nep.txt
velocity    300
time_step   1

# group 0: ghost driver layer (external spring)
# group 1: thermostatted layer
# group 2: production layer
# group 3: fixed bottom

ensemble    heat_lan 300 100 0 1 2      # Langevin only on group 1
fix         3                             # freeze group 3 completely
add_spring  ghost_atom 0 100.0 0.0 0.0 0.0 0 0.0005 0.0 0.0
dump_thermo 100
dump_exyz   10000 0 0
run         1000000
```

- `potential` — may be listed more than once to combine intralayer + interlayer
  potentials (e.g. `nep.txt` for the layers themselves and an ILP file for the
  interlayer term).
- `heat_lan T tau groups...`
  - Applies a Langevin thermostat only to the listed group(s).
- `fix 3`
  - Holds the atoms in group 3 at fixed positions.
- `add_spring ghost_atom g k x0 y0 z0 axis v0 vx vy`
  - Attaches a spring between the centre of mass of group `g` and a ghost
    atom that moves with velocity `(vx, vy, vz)`. This drives shear motion.
- Group indices must match the `group:I:M` columns in `model.xyz`.

Post-process the spring force from `thermo.out` or a group-resolved dump
to recover the friction coefficient.

## Workflow: deposition

Pattern adapted from `16_Deposition` and `27_Carbon_Cu111_deposition`.

```text
potential   nep.txt
velocity    300
time_step   1

# group 0: bottom fixed substrate
# group 1: thermostatted substrate
# group 2: free surface / deposition target
ensemble    heat_lan 300 100 0 1
fix         0
dump_thermo 100
dump_exyz   1000 0 0
run         100000
```

For actual deposition events the tutorial ships a `deposition.py` helper
that repeatedly inserts atoms above the slab and resumes the GPUMD run.
Expose it to the user rather than reinventing a deposition loop.

Key rules:

- the substrate's bottom layer must be fixed to prevent net drift under
  repeated deposition events
- the thermostat layer must be thick enough to absorb the impact energy of
  incoming atoms without heating the reactive region unphysically
- the incoming atoms should not overlap existing atoms when injected

## Workflow: impact / collision

Use initial-velocity conditions on a group:

```text
velocity    300
# after this point the user re-initializes a subset of atoms with a large
# directed velocity via a model.xyz vel:R:3 column, or with a second
# `velocity` call targeted at a group
ensemble    nve
dump_thermo 100
dump_exyz   100 0 0
run         20000
```

The tutorial example uses a prepared initial `model.xyz` with directed
`vel:R:3` columns on the projectile group, rather than modifying velocities
mid-run.

## Group bookkeeping rules

- Groups are declared by adding one or more `group:I:M` columns to the
  `Properties` header of `model.xyz`:

  ```text
  Properties=species:S:1:pos:R:3:group:I:1
  ```

  Each `group:I:M` is a distinct grouping scheme. The `M` tells GPUMD how
  many columns make up this grouping.

- The upstream `add_groups` tool under `GPUMD/tools/Analysis_and_Processing`
  can assign groups automatically from spatial criteria.

## Read first

- [references/mechanics-deposition-friction.md](../references/mechanics-deposition-friction.md)

Read when needed:

- [references/core-files-and-ensembles.md](../references/core-files-and-ensembles.md)
- [references/gpumd-keyword-cheatsheet.md](../references/gpumd-keyword-cheatsheet.md)
- [references/tutorial-map.md](../references/tutorial-map.md)

## Bundled templates

- [assets/examples/friction/run.in](../assets/examples/friction/run.in)
- [assets/examples/friction/model.xyz](../assets/examples/friction/model.xyz)
- [assets/examples/deposition/run.in](../assets/examples/deposition/run.in)
- [assets/examples/deposition/model.xyz](../assets/examples/deposition/model.xyz)

## Expected output

1. a group-resolved `model.xyz` that matches the intended physics
2. a `run.in` with explicit thermostat / fix / spring / driver blocks
3. a list of post-processing quantities (friction force, adsorbate count,
   penetration depth, …) and where they come from

## References

- `fix`: <https://gpumd.org/gpumd/input_parameters/fix.html>
- `add_spring`: <https://gpumd.org/gpumd/input_parameters/add_spring.html>
- `heat_lan`: <https://gpumd.org/gpumd/input_parameters/ensemble.html>
- GPUMD-Tutorials: `16_Deposition`, `20_Impact`, `21_Fatigue`,
  `27_Carbon_Cu111_deposition`, `31_Nanoribbon_friction`
