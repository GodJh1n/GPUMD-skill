# GPUMD Thermal Transport Workflow

## When to read this file

Read this file when the task involves:

- EMD / Green-Kubo conductivity
- HNEMD conductivity
- NEMD or spectral heat current workflows
- interpretation of `hac.out`, `kappa.out`, or `shc.out`

## 1. Method choice

Choose the method from the observable and the system size.

| Method | GPUMD keywords | Best use | Main risk |
| --- | --- | --- | --- |
| EMD / Green-Kubo | `compute_hac` | equilibrium conductivity in well-equilibrated systems | noisy long-time tails and insufficient sampling |
| HNEMD | `compute_hnemd` | faster convergence for many solids and liquids | leaving the linear-response regime |
| NEMD / spectral workflows | `compute_shc` and related setup | length-dependent transport or spectral decomposition | strong finite-size and boundary effects |

## 2. EMD / Green-Kubo

Typical pattern:

1. equilibrate in NVT or NPT
1. switch to NVE
1. accumulate `hac.out`

Bundled template:

- `assets/examples/transport/emd/run.in`

Operational rules:

- do not treat a short trajectory as a converged Green-Kubo result
- inspect the running integral, not just the autocorrelation curve
- use multiple seeds when the noise level matters

## 3. HNEMD

Typical pattern:

1. equilibrate near target state
1. run production with `compute_hnemd`
1. average the stable region of `kappa.out`

Bundled template:

- `assets/examples/transport/hnemd/run.in`

Bundled helper:

```bash
python scripts/average_hnemd_kappa.py kappa.out --discard-frac 0.2
```

The critical physical requirement is linear response.

Start conservatively:

- stiff crystalline solids: often around `1e-5 1/Å`
- only increase the driving field if the signal is too noisy and the result stays field-independent within uncertainty

If the reported conductivity depends materially on the field strength, do not trust the result yet.

## 4. NEMD and spectral workflows

Use these only when the user explicitly needs:

- length dependence
- interface transport
- spectral decomposition

These workflows are more sensitive to:

- group definitions
- boundary conditions
- cell length
- thermostat placement

Do not retrofit a generic EMD script into NEMD logic.

## 5. Convergence and reporting rules

### Independent sampling

For publishable transport numbers, the minimum discussion should include:

- number of independent seeds or replicas
- production length
- cell size
- uncertainty estimate

### Size effects

The required size depends on phonon mean free paths and the method.

At minimum:

- test more than one cell size for NEMD-like conclusions
- do not assume EMD or HNEMD is fully size-converged without checking

### Low-dimensional materials

For monolayers or nanoribbons:

- specify whether conductivity is reported using a conventional thickness
- do not compare directly to bulk `W m^-1 K^-1` values unless the thickness convention matches

### Multicomponent or ionic systems

Heat and mass transport can couple.

If the user asks about multicomponent systems, note that the GPUMD tutorial set includes a dedicated HNEMDEC example. Do not assume the single-component HNEMD formula applies unchanged.

## 6. High-value local tutorial anchors

- `examples/03_Carbon_thermal_transport_emd`
- `examples/04_Carbon_thermal_transport_nemd_and_hnemd`
- `examples/24_Ionic_Conductivity`
- `examples/29_thermal_transport_multicomponent_HNEMDEC`

Use those as workflow seeds, not as unquestioned default parameters.

## References

- GPUMD `compute_hac`: <https://gpumd.org/gpumd/input_parameters/compute_hac.html>
- GPUMD `compute_hnemd`: <https://gpumd.org/gpumd/input_parameters/compute_hnemd.html>
- Fan et al., Phys. Rev. B 99, 064308 (2019)
- Fan et al., Phys. Rev. B 92, 094301 (2015)

