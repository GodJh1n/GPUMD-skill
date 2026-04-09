# NEP Training, Evaluation, And Deployment

## When to read this file

Read this file when the task is about:

- choosing NEP hyperparameters
- interpreting `loss.out`
- deciding whether a fit is usable
- deploying `nep.txt` into GPUMD

## 1. Parameters that matter first

These are the parameters worth discussing before deeper tuning:

| Keyword | Why it matters | Conservative default |
| --- | --- | --- |
| `version` | NEP generation and syntax | `4` |
| `cutoff` | spatial range of the descriptor | `8 4` is a robust starting point |
| `n_max` | radial/angular expansion depth | `4 4` |
| `basis_size` | basis resolution | `8 8` |
| `l_max` | angular-body complexity | `4 2 0` |
| `neuron` | model width | `30` for a first baseline |
| `lambda_e` | energy weight | `1.0` |
| `lambda_f` | force weight | `1.0` |
| `lambda_v` | virial weight | `0.1` unless stress response is central |
| `batch` | training batch size | `1000` |

Conservative tuning order:

1. fix dataset quality
1. confirm label consistency
1. train a baseline
1. inspect validation behavior
1. only then change descriptor or network complexity

## 2. Outputs that should be checked

Primary outputs:

- `nep.txt`
- `loss.out`
- `energy_train.out`, `energy_test.out`
- `force_train.out`, `force_test.out`
- `virial_*` outputs if virials were fitted

Bundled helper:

```bash
python scripts/summarize_nep_loss.py loss.out
```

## 3. What makes a model usable

A usable NEP is not defined by one small scalar RMSE.

Minimum hierarchy:

1. training runs complete and produce a stable `loss.out`
1. test error is not catastrophically worse than train error
1. short MD runs are numerically stable in the target state
1. the target property or observable improves relative to the previous model

If the model has a good parity plot but breaks during short NVE or NVT tests, it is not yet fit for production MD.

## 4. Deployment into GPUMD

Deployment is simple in syntax:

```text
potential nep.txt
```

But deployment is only justified after at least one downstream validation check.

Recommended minimum:

- short MD stability test
- one target-state sanity observable such as lattice constant, RDF, diffusion, or conductivity trend

## 5. Common failure modes

### Apparent underfitting

Before increasing `neuron`, check whether:

- the dataset covers the relevant configurations
- species ordering is correct
- the virial convention is consistent

### Good train error, poor test error

Usually points to:

- insufficient coverage
- inconsistent labels
- excessive model complexity relative to dataset diversity

### Good fit, wrong target property

This is common for transport, phase behavior, and defect energetics.

In that case:

- add labels closer to the target state
- do not rely on a generic bulk dataset to fix a specialized observable

## 6. NEP as part of a workflow, not the whole workflow

For scientific work, NEP fitting is one stage in a larger loop:

- dataset construction
- fit
- MD/property validation
- failure analysis
- targeted data enrichment

The skill should preserve that loop instead of stopping at `loss.out`.

