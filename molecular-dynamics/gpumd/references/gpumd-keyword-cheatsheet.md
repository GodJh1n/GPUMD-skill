# GPUMD Keyword Cheatsheet

A compact lookup table for the most-used `run.in` keywords. It is not a
replacement for the current GPUMD documentation — keywords and their argument
lists have changed between minor versions. Always cross-check syntax at
<https://gpumd.org/gpumd/input_parameters/index.html>.

## Setup

| Keyword       | Purpose                                | Typical form                                   |
| ------------- | -------------------------------------- | ---------------------------------------------- |
| `potential`   | load a potential file                  | `potential nep.txt`                            |
| `velocity`    | assign Maxwell-Boltzmann velocities    | `velocity 300`                                 |
| `time_step`   | set integration step (fs)              | `time_step 1`                                  |
| `replicate`   | expand primitive cell into a supercell | `replicate 4 4 4`                              |
| `neighbor`    | neighbor-list control (build-dependent)| consult docs for the current version           |

Multiple `potential` lines are allowed when combining intralayer and
interlayer potentials (e.g. a NEP layer potential plus an ILP interlayer
term for 2D heterostructures).

## Ensembles

| Keyword                | Meaning                                           |
| ---------------------- | ------------------------------------------------- |
| `ensemble nve`         | microcanonical — use for Green-Kubo production    |
| `ensemble nvt_nhc T0 T1 tau`   | Nose-Hoover chain — recommended default NVT |
| `ensemble nvt_lan T0 T1 tau`   | Langevin NVT                               |
| `ensemble nvt_bdp T0 T1 tau`   | Bussi-Donadio-Parrinello NVT               |
| `ensemble nvt_ber T0 T1 tau`   | Berendsen NVT — equilibration only         |
| `ensemble npt_scr T0 T1 tau_T p...  C... tau_p` | stochastic-rescaling NPT (anisotropic form) |
| `ensemble npt_ber T0 T1 tau_T p_xx p_yy p_zz C_xx C_yy C_zz tau_p` | Berendsen NPT  |
| `ensemble npt_mttk ...` | Martyna-Tuckerman-Tobias-Klein NPT               |
| `ensemble heat_lan T tau fix_grp thm_grp prod_grp` | Langevin on specific groups |

For anisotropic NPT the full block is:

```
npt_scr T_start T_stop tau_T  p_xx p_yy p_zz p_xy p_xz p_yz  C_xx C_yy C_zz C_xy C_xz C_yz  tau_p
```

All pressures are in GPa. `C_ij` are compressibility-like barostat parameters.
For the isotropic short form (`T_start T_stop tau_T p_hydro C tau_p`) confirm
against the current docs for the installed GPUMD version.

## Dumps

| Keyword        | Writes                                    |
| -------------- | ----------------------------------------- |
| `dump_thermo`  | `thermo.out` (T, E, P, box, stress tensor)|
| `dump_position`| `movie.xyz` — positions only              |
| `dump_exyz`    | extxyz trajectory with full headers       |
| `dump_restart` | restart snapshot                          |
| `dump_force`   | per-atom forces                           |
| `dump_velocity`| per-atom velocities                       |

## Computes (observables)

| Keyword            | Target observable                               |
| ------------------ | ----------------------------------------------- |
| `compute_phonon`   | harmonic phonons (finite displacement)          |
| `compute_dos`      | vibrational DOS from NVE VAC                    |
| `compute_hac`      | heat autocorrelation (EMD / Green-Kubo)         |
| `compute_hnemd`    | HNEMD thermal conductivity                      |
| `compute_hnemdec`  | multi-component HNEMDEC thermal conductivity    |
| `compute_shc`      | spectral heat current                           |
| `compute_msd`      | mean-square displacement                        |
| `compute_sdc`      | self-diffusion coefficient from VAC             |
| `compute_viscosity`| Green-Kubo shear viscosity                      |
| `compute_elastic`  | elastic constants via strain fluctuation → `elastic.out` |
| `compute`          | general per-group observables                   |

## Group-based controls

| Keyword       | Purpose                                     |
| ------------- | ------------------------------------------- |
| `fix g`       | freeze group `g`                            |
| `add_spring`  | attach a spring between a group and a target|
| `add_force`   | apply a constant force on a group           |

## Flow control

| Keyword | Purpose                         |
| ------- | ------------------------------- |
| `run N` | integrate N steps with current settings |

Remember: `run.in` is ordered. Each `run` consumes the current ensemble and
compute settings. Redefine them between blocks if you want a different
segment (for example: equilibrate in NPT, then switch to NVE for production).

## When to read the full docs instead

Open the upstream docs page for the specific keyword any time:

- the number of arguments looks off
- a tutorial uses a syntax that doesn't parse in the installed GPUMD
- the observable depends sensitively on an argument you are unsure about
- you're about to make physical claims from the result

Root: <https://gpumd.org/gpumd/input_parameters/index.html>
