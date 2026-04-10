# Elastic Constants in GPUMD

## When to read this file

Read this file when the target observable is the elastic tensor `C_ij` or
any derived isotropic modulus (bulk `B`, shear `G`, Young's `E`, Poisson
`ν`) at a finite temperature.

## 1. Method overview: strain fluctuation

GPUMD uses the Parrinello-Rahman strain-fluctuation estimator. In an
anisotropic NPT ensemble the simulation box fluctuates in both volume and
shape; the covariance matrix of those shape fluctuations contains `C_ij`
directly, without any finite-difference stress sweep.

Advantages:

- no external strain sweep — only one long trajectory per `(T, P)` point
- naturally produces temperature-dependent `C_ij(T)`
- no finite-difference discretization error

Disadvantages:

- noisier than stress-response methods at the same compute cost
- needs a **fully anisotropic barostat** (all six shape degrees of freedom
  must fluctuate freely)
- requires long trajectories to converge

## 2. Required `run.in` ingredients

A minimal pattern (see `assets/examples/elastic/run.in`):

```text
potential   nep.txt
velocity    300

ensemble    npt_scr 300 300 100 0 0 0 0 0 0 100 100 100 100 100 100 2000
time_step   1
dump_thermo 100
compute_elastic 0.01
run         1100000
```

### The NPT block

The `npt_scr` block is the anisotropic form:

```
npt_scr T_start T_stop tau_T  p_xx p_yy p_zz p_xy p_xz p_yz  C_xx C_yy C_zz C_xy C_xz C_yz  tau_p
```

All six diagonal compressibility-like parameters (`C_xx ... C_yz`) must be
nonzero so that the box shape can fluctuate in every independent direction.
Using isotropic NPT makes the strain-fluctuation method blind to `C_44`.

### The `compute_elastic` keyword

```text
compute_elastic <strain_value>
```

- `strain_value` — strain amplitude used in the fluctuation estimator. `0.01`
  is a robust starting value.
- Takes a single parameter. GPUMD computes the full 6x6 elastic tensor
  automatically — the crystal symmetry determines how many independent
  `C_ij` you should report, but it is not an argument to the keyword.
- Output is written to `elastic.out`.

## 3. Supercell and length guidance

- Cubic semiconductors: typical supercell contains a few thousand atoms.
- Softer materials and molecular liquids: usually need longer trajectories
  than hard crystals.
- The `30_Elastic_constants__strain_fluctuation_method` tutorial uses
  `run 1100000` steps with `time_step 1` — i.e. 1.1 ns — as a starting
  point. Expect similar scales.

## 4. Deriving isotropic moduli

For a cubic system, the Voigt-Reuss-Hill average gives isotropic moduli
from `C_11`, `C_12`, `C_44`:

```
B   = (C_11 + 2 C_12) / 3
G_V = (C_11 - C_12 + 3 C_44) / 5
G_R = 5 (C_11 - C_12) C_44 / (4 C_44 + 3 (C_11 - C_12))
G_VRH = (G_V + G_R) / 2
E   = 9 B G_VRH / (3 B + G_VRH)
ν   = (3 B - 2 G_VRH) / (2 (3 B + G_VRH))
```

For other symmetries consult a mechanics reference — the formulas are
symmetry-specific.

## 5. Born stability

A trustworthy `C_ij` must satisfy Born stability for the symmetry. For a
cubic crystal:

```
C_11 - C_12 > 0
C_11 + 2 C_12 > 0
C_44 > 0
```

If the fit violates these, the trajectory is either not converged or the
structure is not at a mechanical minimum.

## 6. Convergence discipline

| Check                                  | Why it matters                            |
| -------------------------------------- | ----------------------------------------- |
| anisotropic `npt_scr` (all six shape DOFs) | otherwise shear modes are inaccessible |
| relaxed reference structure            | otherwise `C_ij` is biased                |
| trajectory length                      | strain-fluctuation is noisy               |
| supercell large enough                 | shape fluctuations are small for big cells |
| Born stability satisfied               | sanity check on the fit                   |
| temperature clearly stated             | `C_ij(T)` differs from `C_ij(0)`          |

## 7. Alternatives worth mentioning

- **Stress-strain response**: apply known strains and read stresses. Lower
  noise per step but requires multiple runs and finite-difference handling.
  Not the GPUMD `compute_elastic` method.
- **Elastic constants from MD at T = 0**: minimize then deform. This gives
  `C_ij(0)` which is **not** directly comparable to a finite-temperature
  strain-fluctuation result.

## References

- `compute_elastic`: <https://gpumd.org/gpumd/input_parameters/compute_elastic.html>
- Parrinello and Rahman, J. Appl. Phys. 52, 7182 (1981)
- Ray and Rahman, J. Chem. Phys. 80, 4423 (1984)
- GPUMD-Tutorials: `30_Elastic_constants__strain_fluctuation_method`
