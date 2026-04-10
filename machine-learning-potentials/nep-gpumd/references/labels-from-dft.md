# Labels From DFT

## When to read this file

Read this file when the task involves:

- generating labeled training data for NEP from DFT calculations
- choosing a DFT code and settings for NEP labeling
- converting DFT output to NEP-compatible extxyz format
- ensuring label consistency across a dataset

## 1. What NEP needs from DFT

NEP training needs per-frame labels in extxyz format:

| Label           | Required? | DFT output source |
| --------------- | --------- | ----------------- |
| Total energy    | Yes       | SCF total energy (consistent zero reference) |
| Forces          | Yes       | Hellmann-Feynman forces |
| Virial / stress | Optional  | Stress tensor × cell volume (sign matters) |
| Dipole          | For `model_type 1` | Berry phase, Wannier centers, or DFPT |
| Polarizability  | For `model_type 2` | DFPT or finite-field |

## 2. Supported DFT codes and converters

GPUMD ships converters in `GPUMD/tools/Format_Conversion/`:

| DFT code | Converter directory         | Notes |
| -------- | --------------------------- | ----- |
| VASP     | `vasp2xyz/`                 | Reads OUTCAR. Most tested path. |
| CP2K     | `cp2k2xyz/`                 | Reads CP2K output + force files. |
| ABACUS   | `abacus2xyz/`               | Reads ABACUS output. |
| SIESTA   | `siesta2xyz/`               | Reads SIESTA `.out` + `.FA`. |
| CASTEP   | `castep2xyz/`               | Reads CASTEP output. |
| ORCA     | `orca2xyz/`                 | Molecular (cluster) calculations. |
| DeepMD   | `deepmd2xyz/`               | Converts DeepMD `raw` format. |
| RUNNER   | `runner2xyz/`               | Converts RUNNER format. |

Third-party tools that also produce NEP extxyz:

- **calorine** (Python): `calorine.tools.convert` for VASP, CP2K, QE
- **ASE**: write extxyz from any ASE-supported calculator
- **dpdata**: convert from DeePMD/VASP/CP2K to extxyz

## 3. DFT workflow requirements

### Energy consistency

- Use the same XC functional family across the entire dataset.
- If you use a hybrid (e.g. HSE06) for some frames and GGA (PBE) for
  others, the energy zero shifts and forces may be biased.
- Include dispersion corrections consistently (all frames or no frames).

### Force convergence

- SCF must converge tightly enough that forces are meaningful.
- For VASP: `EDIFF = 1e-6` or tighter, `PREC = Accurate`.
- For CP2K: `EPS_SCF 1e-7` or tighter.
- Check that the maximum force residual is small compared to the force
  scale in the system.

### Stress / virial convention

This is the most common source of dataset corruption:

- VASP `OUTCAR` reports stress in kB. The converter must multiply by
  cell volume and flip sign to get virial in eV.
- CP2K reports stress in GPa by default.
- The NEP extxyz header expects `virial="v1 v2 v3 v4 v5 v6 v7 v8 v9"`
  with values in eV (total cell virial, not per-atom).
- Alternatively, `stress="s1 s2 ... s9"` is accepted but the sign and
  unit convention must be stated.

**Rule**: before merging datasets from different codes, convert
everything to the same convention and verify with a known simple system.

### k-point density

- Use a consistent k-point density across all frames of the same cell
  size.
- When the cell size varies (e.g. strained cells), use the same
  k-point spacing (e.g. 0.03 Å⁻¹) rather than the same k-point grid.

## 4. Recommended single-point workflow

For each frame to be labeled:

1. Extract atomic positions from the MD snapshot or perturbation.
2. Set up a single-point DFT calculation with locked settings.
3. Run to convergence.
4. Extract energy, forces, and (optionally) stress/virial.
5. Convert to extxyz using the appropriate converter.

Automate steps 2–5 per frame. The `dft-vasp`, `dft-cp2k`, `dft-qe`,
`dft-siesta`, and `dft-abinit` skills in the parent collection can
help set up the DFT input.

## 5. Validation before training

After conversion, validate the dataset:

```bash
python scripts/validate_extxyz_headers.py train.xyz --mode train
```

Also check:

- energy distribution: no extreme outliers (plot histogram)
- force magnitudes: consistent scale across config types
- virial values: physically sensible for the cell volume

## 6. Mixing datasets

When combining data from multiple sources:

| Concern | Check |
| ------- | ----- |
| Energy zero | Same functional, same pseudopotential set |
| Force convention | Same sign, same units |
| Virial sign | Consistent after conversion |
| Species ordering | Same order in all frames |
| Cell convention | Row-major vs. column-major in Lattice field |

If in doubt, compute a few frames with both codes and compare energy
differences and forces before mixing.

## 7. How many frames?

There is no universal rule, but guidelines:

- **Bulk, single phase**: 100–500 frames cover equilibrium well.
- **Phase transitions**: 500–2000 frames spanning both phases.
- **Reactive systems**: 1000+ frames with varied bond configurations.
- **Fine-tuning from NEP89**: as few as 50–200 high-quality frames can
  be sufficient for a targeted property.

Quality beats quantity. 200 well-chosen, consistently labeled frames
outperform 5000 inconsistent ones.

## References

- GPUMD format converters: `GPUMD/tools/Format_Conversion/`
- calorine: <https://calorine.materialsmodeling.org/>
- ASE: <https://wiki.fysik.dtu.dk/ase/>
- dpdata: <https://github.com/deepmodeling/dpdata>
