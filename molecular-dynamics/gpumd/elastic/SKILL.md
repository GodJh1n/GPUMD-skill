---
name: elastic
description: >
  Prepare GPUMD elastic-constant calculations using the strain-fluctuation
  method. Use when the user needs `compute_elastic`, `C_ij` extraction for
  cubic / hexagonal / tetragonal / orthorhombic systems, or elastic moduli
  (bulk, shear, Young's) from an NPT trajectory.
compatibility: Requires GPUMD and a potential that is stable under the anisotropic NPT used for strain-fluctuation sampling.
catalog-hidden: true
license: GPL-3.0-only
metadata:
  author: Codex
  version: 0.1.0
---

# GPUMD Elastic Constants

Use this subskill when the target observable is the elastic tensor `C_ij`.
GPUMD uses the strain-fluctuation method: an anisotropic NPT trajectory is
sampled at the target temperature, and `compute_elastic` extracts `C_ij` from
the box-shape fluctuations without a finite-difference stress sweep.

## Quick start

```bash
gpumd < run.in | tee gpumd.log
python scripts/parse_thermo.py thermo.out --last 1
```

## Agent responsibilities

1. Confirm the crystal symmetry (cubic, hexagonal, tetragonal, orthorhombic).
   The symmetry label is an argument to `compute_elastic` and changes how
   many independent `C_ij` are extracted.
2. Confirm the structure is relaxed under the chosen potential. Unrelaxed
   inputs produce biased `C_ij`.
3. Use an anisotropic NPT barostat (e.g. `npt_scr` with separate diagonal
   parameters). Isotropic NPT cannot sample shear modes.
4. Run long enough for the strain-fluctuation average to converge. The
   strain-fluctuation method is noisier than direct stress-response.
5. Report `C_ij` plus derived moduli (`B`, `G`, `E`, `ν`) if requested, and
   state the temperature and averaging window.

## Workflow

### Step 1. Prepare the structure

- primitive or conventional cell — the strain-fluctuation method is sensitive
  to the cell choice
- use a supercell large enough to suppress shape-fluctuation noise (for cubic
  semiconductors, a few thousand atoms is typical)
- relax under the same potential before sampling

### Step 2. Write `run.in`

Annotated example (see
[assets/examples/elastic/run.in](../assets/examples/elastic/run.in)):

```text
potential   nep.txt
velocity    300

ensemble    npt_scr 300 300 100 0 0 0 0 0 0 100 100 100 100 100 100 2000
time_step   1
dump_thermo 100
compute_elastic 0.01 cubic
run         1100000
```

- `ensemble npt_scr` block
  - `T_start T_stop tau_T  p_xx p_yy p_zz p_xy p_xz p_yz  C_xx C_yy C_zz C_xy C_xz C_yz  tau_p`
  - Using six target pressures and six compressibility-like barostat
    parameters is what makes the barostat anisotropic. All six diagonal
    compressibilities (`C_xx ... C_yz`) must be nonzero so that the box
    shape is free to fluctuate.
- `compute_elastic amplitude symmetry`
  - `amplitude` — strain scale used in the fluctuation estimator (0.01 is a
    robust default)
  - `symmetry` — one of `cubic`, `hexagonal`, `tetragonal`, `orthorhombic`
- `run 1100000`
  - Long trajectories are required. 10^6 steps is a practical minimum.

### Step 3. Extract `C_ij`

At the end of the run, GPUMD prints the fitted elastic constants to
`thermo.out` / the main log. Read them with:

```bash
python scripts/parse_thermo.py thermo.out --last 1
```

For cubic crystals the report should contain `C_11`, `C_12`, `C_44`. Derive
isotropic moduli via the Voigt-Reuss-Hill average if requested by the user.

### Step 4. Convergence

- [ ] tested that the box shape actually fluctuates (not pinned by a rigid
      barostat)
- [ ] trajectory length increased until `C_ij` is stable to the needed
      tolerance
- [ ] supercell size is not so small that shape noise dominates
- [ ] `C_ij` is positive-definite and satisfies Born stability for the
      symmetry

## Common pitfalls

- using isotropic `npt_scr` — the method cannot sample `C_44`
- taking a single short trajectory as the final answer
- reporting `C_ij` at 300 K when the input was only relaxed at 0 K and never
  equilibrated under the chosen potential
- mixing temperature-dependent `C_ij(T)` with static DFT `C_ij(0)` in the
  same table without labeling

## Read first

- [references/elastic-constants.md](../references/elastic-constants.md)

Read when needed:

- [references/core-files-and-ensembles.md](../references/core-files-and-ensembles.md)
- [references/gpumd-keyword-cheatsheet.md](../references/gpumd-keyword-cheatsheet.md)

## Bundled templates and helpers

- [assets/examples/elastic/run.in](../assets/examples/elastic/run.in)
- [assets/examples/elastic/model.xyz](../assets/examples/elastic/model.xyz)
- [scripts/parse_thermo.py](../scripts/parse_thermo.py)

## Expected output

1. a GPUMD `run.in` configured for the correct crystal symmetry
2. an anisotropic NPT block that allows box-shape fluctuations
3. a post-processing plan for `C_ij` and, if requested, derived moduli
4. explicit convergence and reporting notes

## References

- `compute_elastic`: <https://gpumd.org/gpumd/input_parameters/compute_elastic.html>
- GPUMD-Tutorials example `30_Elastic_constants__strain_fluctuation_method`
- Parrinello and Rahman, J. Appl. Phys. 52, 7182 (1981)
