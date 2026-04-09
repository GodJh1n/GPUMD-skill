# GPUMD Phonon Workflow

## When to read this file

Read this file when the user wants:

- harmonic phonon dispersion
- `compute_phonon`
- `kpoints.in`
- interpretation of `omega2.out` or `D.out`
- a GPUMD-based entry point into larger lattice-dynamics workflows

## 1. Core GPUMD phonon workflow

The minimal GPUMD finite-displacement pattern is:

```text
replicate       8 8 8
potential       Si_Fan_2019.txt
compute_phonon  0.005
```

Required inputs:

- a valid crystalline `model.xyz`
- a potential that is stable for the target structure
- `kpoints.in` if a path-resolved dispersion is requested

Bundled example:

- `assets/examples/phonon/model.xyz`
- `assets/examples/phonon/run.in`
- `assets/examples/phonon/kpoints.in`

## 2. `kpoints.in`

`kpoints.in` defines the reciprocal-space path.

Each nonblank line should contain:

- three fractional coordinates
- one label

Example:

```text
0.000 0.000 0.000 G
0.500 0.000 0.500 X
0.375 0.375 0.750 K
0.000 0.000 0.000 G
0.500 0.500 0.500 L
```

Use blank lines when two path segments should not be connected.

## 3. Convergence issues that matter

### Supercell size

`replicate` is not decorative. It sets the real-space range available for force-constant extraction.

If the supercell is too small:

- acoustic branches can be distorted
- optical branches can shift
- imaginary modes can appear spuriously

Therefore:

- increase the supercell until the dispersion is stable to the needed tolerance
- do not recycle a supercell from another material or another potential without checking

### Displacement amplitude

`compute_phonon 0.005` means a displacement amplitude of `0.005 Å`.

Typical safe starting range:

- `0.005-0.01 Å`

If the displacement is too small, numerical noise can dominate.
If it is too large, the calculation leaves the harmonic regime.

### Relaxed reference structure

The input structure should already represent the intended equilibrium geometry under the chosen potential.

If the structure is not relaxed:

- Γ-point acoustic modes may not approach zero correctly
- soft or imaginary modes may reflect residual stress instead of true instability

## 4. Outputs

Main files:

- `D.out`
- `omega2.out`

Interpretation:

- negative `omega^2` values correspond to imaginary frequencies
- persistent imaginary branches can mean a true structural instability, but they can also come from poor relaxation or poor convergence

Do not interpret imaginary modes before checking:

- relaxation quality
- supercell convergence
- displacement amplitude

## 5. What GPUMD phonons do and do not give you

This workflow gives harmonic phonon information from the chosen potential.

It does not, by itself, give:

- converged lattice thermal conductivity
- temperature-renormalized anharmonic force constants
- a full Boltzmann transport solution

For those, a broader lattice-dynamics workflow is needed.

## 6. Extended path: lattice dynamics with fitted IFCs

The local GPUMD tutorial collection contains a more advanced example:

- `examples/25_lattice_dynamics_kappa`

That tutorial combines:

- NEP
- GPUMD sampling
- HiPhive
- Phonopy / Phono3py

Use that path when the user explicitly wants:

- IFC fitting beyond the built-in `compute_phonon`
- anharmonic transport from fitted `fc2` and `fc3`
- temperature-dependent effective-potential style extensions

## 7. Recommended reporting discipline

When reporting or comparing dispersions:

- state the potential used
- state the supercell size
- state the displacement amplitude
- state whether the input structure was relaxed under the same potential

## References

- GPUMD phonon docs: <https://gpumd.org/gpumd/input_parameters/compute_phonon.html>
- GPUMD-Tutorials silicon phonon example
- GPUMD-Tutorials lattice-dynamics PbTe example

