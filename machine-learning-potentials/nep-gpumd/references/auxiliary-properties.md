# NEP Auxiliary Properties: Dipole And Polarizability

## When to read this file

Read this file when the task involves:

- training a dipole model (`model_type 1`)
- training a polarizability model (`model_type 2`)
- computing IR or Raman spectra from NEP-driven MD
- understanding how auxiliary property models differ from the standard
  energy+force NEP

## 1. What are auxiliary-property NEP models?

The same `nep` executable and the same descriptor can be used to fit
properties other than energy, forces, and virials. The two supported
auxiliary model types are:

| `model_type` | Target quantity       | Use case                       |
| ------------ | --------------------- | ------------------------------ |
| `1`          | Dipole (3-component)  | IR spectra, dielectric response |
| `2`          | Polarizability (6-component, Voigt) | Raman spectra, optical response |

These models are trained on per-frame dipole or polarizability labels
obtained from DFT (e.g. DFPT, Berry phase, or Wannier center analysis).

## 2. Dataset format

### Dipole labels

Each frame must include a `dipole="dx dy dz"` field in the extxyz
header. The dipole is the **total cell dipole** in units of e·Å.

```text
2
Lattice="5.43 0 0 0 5.43 0 0 0 5.43" pbc="T T T" dipole="0.012 -0.003 0.008" Properties=species:S:1:pos:R:3
Si 0.000 0.000 0.000
Si 1.358 1.358 1.358
```

Note: forces are **not required** in the dipole dataset. The
`Properties` line does not need force columns.

### Polarizability labels

Each frame must include a `polarizability="xx yy zz xy yz zx"` field
(6 Voigt components) in units of Å³.

```text
2
Lattice="5.43 0 0 0 5.43 0 0 0 5.43" pbc="T T T" polarizability="11.2 11.2 11.2 0.0 0.0 0.0" Properties=species:S:1:pos:R:3
Si 0.000 0.000 0.000
Si 1.358 1.358 1.358
```

## 3. `nep.in` for auxiliary models

The key difference is `model_type`:

### Dipole model

```text
model_type   1
type         1 Si
version      4
cutoff       8 4
n_max        4 4
basis_size   8 8
l_max        4 2 0
neuron       30
lambda_e     1.0
batch        1000
population   50
generation   50000
```

- `lambda_e` acts as the loss weight for the dipole (since dipole
  replaces energy in the loss hierarchy).
- `lambda_f` and `lambda_v` are not used for dipole models.

### Polarizability model

```text
model_type   2
type         1 Si
version      4
cutoff       8 4
n_max        4 4
basis_size   8 8
l_max        4 2 0
neuron       30
lambda_e     1.0
lambda_v     0.1
batch        1000
population   50
generation   50000
```

- `lambda_e` controls the isotropic part.
- `lambda_v` controls the anisotropic (off-diagonal) part.

## 4. Output files

| Model type | Parity output                  |
| ---------- | ------------------------------ |
| `1` (dipole) | `dipole_train.out`, `dipole_test.out` |
| `2` (polar.) | `polarizability_train.out`, `polarizability_test.out` |

These are read the same way as `energy_*.out` — predicted vs. reference
columns.

## 5. Deployment in GPUMD

An auxiliary NEP model is loaded alongside the main potential:

```text
potential       nep.txt
potential_polar polar.txt
```

or, for dipole:

```text
potential       nep.txt
potential_dipole dipole.txt
```

The auxiliary model runs on every MD step and writes the time-series
needed for spectral analysis (IR autocorrelation for dipole, Raman
autocorrelation for polarizability).

## 6. Spectral workflow

The typical workflow for IR or Raman from NEP:

1. Train the energy+force NEP (standard `model_type 0`)
2. Generate MD trajectories at the target temperature
3. From the MD snapshots, compute DFT dipole / polarizability labels
4. Train the auxiliary NEP (`model_type 1` or `2`)
5. Rerun MD with both potentials loaded
6. Compute the spectrum from the time-series autocorrelation

Step 6 is usually done with a post-processing script or the GPUMD
built-in tools.

## 7. Common pitfalls

- **Mixing model types**: do not put `model_type 1` labels in a
  `model_type 0` dataset or vice versa.
- **Dipole convention**: the cell dipole must be total, not per-atom.
  Some DFT codes output per-atom Born effective charges instead.
- **Polarizability convention**: confirm Voigt ordering (xx yy zz xy yz
  zx) and units (Å³).
- **Cell size**: dipole models are sensitive to the cell size used
  during label generation. Use the same supercell size consistently.

## References

- NEP `model_type`: <https://gpumd.org/nep/input_files/nep_in.html>
- GPUMD-Tutorials: IR / Raman examples
- Polarizability from DFPT: consult the relevant `dft-*` skill
