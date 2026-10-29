---
title: Reproducing DeTime Method Animations
description: Rebuild and audit the numerical teaching animations, source arrays, and English method explanations included in DeTime's existing gallery.
---

# Reproducing the Method Animations

All **31 registered method entries** have a numerical teaching animation and
an English explanation in the [method gallery](../methods.md#animated-method-explanations).
Each animation follows **four stages**, uses **32 frames** by default, and
places four plots in a **1280 × 820** frame. The coverage includes eight
classical entries, seven adaptive or time-frequency entries, and sixteen
experimental block entries. Aliases remain separate registry entries; this
count does not imply 31 independent algorithms.

The inputs are deterministic synthetic signals chosen to make an operation
visible. The plots show calculations such as constructing a trajectory
matrix, averaging seasonal phases, updating a mode, or applying a frequency
mask. These teaching traces are separate from the project's real-data
tutorials and benchmark results.

## Files and recorded evidence

The generated files live in `docs/assets/generated/method-animations/`.
Every method has a looping GIF, a static PNG, a compressed NumPy archive
(`.npz`), and JSON metadata. The
[complete manifest](../assets/generated/method-animations/manifest.json)
assembles the per-method records and reports registry coverage.

| Record | What it contains |
|---|---|
| GIF and PNG | The animated computation and a still frame suitable for reading without playback. |
| NPZ archive | The actual inputs, intermediate arrays, and outputs used by that method's trace. |
| Per-method JSON | Four explanations, parameter effects, references, trace scope, example configuration, numerical checks, array names and shapes, artifact hashes, and render provenance. |
| Manifest | All method records, their source hashes, and the Python/dependency environments captured during rendering. |

The source baseline for this addition is
`c209d81fc9f9624fddf04c922c091bc86c820b60`. The per-render SHA-256 hashes
identify the actual implementation and generator files used to produce an
asset; the baseline identifies the starting revision.

## Install the generation environment

Run these commands from the repository root, using Python 3.10 or later:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install ".[dev,docs,emd,multivar,vmd]"
```

In Windows Command Prompt, activate with `.venv\Scripts\activate.bat` instead.
The optional extras supply the EMD, VMD, and multivariate backends used by
the traces. The generator imports the current checkout's source, so run it
from the repository whose files you intend to publish. Exact versions used
for an existing artifact are recorded in its `render_provenance`.

Generation runs on CPU with small signals. It does not train a neural model
and does not require a GPU, Torch, or a learned Gabor codebook. Allow roughly
five minutes for a complete run as a planning estimate; the measured time
depends on the machine, dependencies, and rendering settings. These timings
describe documentation generation.

## Regenerate and assemble

### Rebuild every method

```bash
python scripts/generate_method_animations.py
```

This computes all traces, renders the assets, writes per-method metadata,
assembles the manifest, and updates the generated explanation sections in
the gallery and the existing Methods index. The default is 32 frames; use
`--frames 32` to state it explicitly. Keep source files stable during a run:
the renderer checks that their hashes have not changed before writing the
completed metadata.

### Rebuild selected methods

```bash
python scripts/generate_method_animations.py --methods SSA STL
python scripts/generate_method_animations.py --group classical
```

`--methods` accepts registry names. `--group` accepts `classical`, `adaptive`,
or `neural`. Selection controls the assets that are written; trace
specifications are built together by group, so the group's optional
dependencies must still be available. In a directory with a complete set
of per-method metadata, the command also attempts final assembly.

The source hashes determine how much to regenerate. Editing
`scripts/method_animations/classical.py`, for example, invalidates all eight
classical assets because they share that source file. Editing the common
renderer or a shared implementation file can invalidate all methods. Use
the errors reported by `--check` to identify the affected records, then
regenerate that group or the complete set.

For an isolated preview without updating the gallery:

```bash
python scripts/generate_method_animations.py --methods SSA --output-dir /tmp/detime-animation-preview --no-docs
```

A directory containing only selected methods remains a partial render until
every registered entry has metadata.

### Assemble existing, current artifacts

```bash
python scripts/generate_method_animations.py --assemble
```

Assembly rebuilds the manifest and generated Markdown from existing
per-method JSON files. It does not recompute numerical traces or render
images. Every registered method must have metadata, and each record must
contain captured render provenance whose source hashes match the current
checkout. A stale record causes assembly to fail with the affected method
and source path.

Regenerate an affected trace before assembling. Assembly preserves the
Python version and dependency versions captured when each asset was
rendered; it does not substitute the current environment or relabel older
assets with new source hashes.

## Audit and build the website

```bash
python scripts/generate_method_animations.py --check
python -m pytest tests/docs/test_method_animations.py -q
python -m mkdocs build --strict
```

`--check` audits existing files without running optional algorithm backends.
It checks exact registry coverage, source provenance, agreement between
per-method metadata and the manifest, artifact hashes, GIF dimensions and
frame availability, the 3 MiB per-GIF budget, finite source arrays with
matching names and shapes, and current English explanation sections.

The documentation tests also verify that plot content changes across
stages and that alias and untrained-model explanations remain available in
static Markdown. During rendering, every encoded GIF frame is decoded and
compared with the planned palette frame, so the compact GIF encoding is
checked for visual consistency.

Numerical checks are method-specific values in the metadata. Some compare
an instrumented trace with the public implementation; others check a basis
formula, reconstruction identity, or an upstream checkpoint. Read the
record's `trace_note` and `checks` together: an additive identity alone does
not establish useful component recovery or forecasting performance.

## Inspect the source arrays

Use NumPy with `allow_pickle=False`. This example lists every stored SSA
array, checks its shape against the metadata, and inspects the additive
identity:

```python
import json
from pathlib import Path

import numpy as np

assets = Path("docs/assets/generated/method-animations")
metadata = json.loads((assets / "ssa.json").read_text())
print(metadata["trace_kind"])
print(metadata["trace_note"])
print(metadata["checks"])

with np.load(assets / "ssa.npz", allow_pickle=False) as arrays:
    print(sorted(arrays.files))
    for name in sorted(arrays.files):
        values = arrays[name]
        assert list(values.shape) == metadata["source_arrays"][name]
        print(name, values.shape, values.dtype)

    reconstructed = arrays["trend"] + arrays["season"] + arrays["residual"]
    error = np.max(np.abs(arrays["observed"] - reconstructed))
    print("Maximum additive reconstruction error:", float(error))
```

The SSA archive contains `t`, `observed`, `trajectory`, `singular_values`,
`rank_one_matrices`, `reconstructed_modes`, `dominant_frequencies`,
`trend_indices`, `season_indices`, `trend`, `season`, and `residual`.
Other methods have different inventories: STL stores fit checkpoints,
STDR stores cycle normalization and phase counts, and Gabor stores complex
Fourier coefficients and codebook assignments. Use each JSON record's
`source_arrays` rather than assuming that every archive has SSA's keys or
array dimensions.

### Understand the kind of trace

| Example | What is computed |
|---|---|
| SSA, MSSA, STD/STDR, moving-average baseline | Source-level operations and final components, with numerical comparisons against the configured implementation. |
| STL and robust STL | Actual statsmodels iteration checkpoints. STL's separate local-regression panel illustrates LOESS and identifies the internal details it omits. |
| MSTL | The alternating upstream STL procedure, including separate seasonal estimates before DeTime aggregates them. |
| Experimental blocks and aliases | The operator implemented in this repository. The explanation identifies its relationship to the named architecture and any shared implementation. |
| `NBEATS_INTERPRETABLE` | Polynomial/Fourier bases with explicitly chosen, untrained teaching coefficients and separate backcast/output bookkeeping. |
| `GABOR_CLUSTER` | Repository windowing, Fourier features, nearest-centroid assignment, and masked overlap-add reconstruction using a fixed teaching codebook. |

For **N-BEATS**, the generator saves the basis arrays and all chosen
coefficients. It does not execute the optional Torch fitting path. Running
the public method configuration on that page starts a separate fitting
experiment and will not reproduce the illustration's selected coefficients.

For **Gabor clustering**, the archive includes `feature_mean`,
`feature_scale`, `standardized_demo_centroids`, the window, and numeric
window/hop/FFT settings. These specify the fixed codebook and normalization
used in the trace, so they can be used to construct a `GaborClusterModel`.
The public decomposition call requires that model object or a model archive
written by its `save()` method. The trace's NPZ is an inspection archive,
with a different schema from a saved model. Its centroids are teaching
constants; no codebook training is performed. See the
[Gabor explanation](../gallery/gabor-cluster.md#how-it-works) and the
[model implementation](https://github.com/systems-mechanobiology/DeTime/blob/main/src/detime/methods/gabor_cluster.py)
for the matching fields.

## MVMD input-layout correction

Tracing MVMD exposed a wrapper issue with the optional PySDKit backend.
DeTime accepts multivariate input as `(time, channels)`, while
[PySDKit's MVMD implementation](https://pysdkit.readthedocs.io/en/stable/_modules/pysdkit/_vmd/mvmd.html)
reads its input as `(channels, time)` and returns modes as
`(modes, time, channels)`. The wrapper now transposes the input before its
selected backend call and keeps DeTime's public output layout.

This matters because a backend can accept both shapes while performing
its temporal operations along the wrong axis. Transposing a returned array
cannot repair such a fit. The corrected wrapper also propagates a solver
error from the selected entry point instead of retrying with another
orientation or interface.

Six regression cases cover two- and four-channel permissive backends,
callable dispatch, unchanged solver-error propagation, and direct numerical
comparisons with real PySDKit for both channel counts:

```bash
python -m pytest tests/wrappers/test_mvmd_orientation.py -q
```

The real-backend comparisons require the `multivar` extra installed above.
The wrapper-focused validation run passed 37 tests, including these six
regressions. The
[regression source](https://github.com/systems-mechanobiology/DeTime/blob/main/tests/wrappers/test_mvmd_orientation.py)
records the bounded solver settings used for the comparisons.

## Website behavior

The existing MkDocs navigation groups and gallery URLs are retained. The
Methods page links to all registered entries, including the experimental
blocks. Generated sections are enclosed by marker comments so that
regeneration updates the explanations within the existing pages.

Each page initially displays a static frame. **Play animation** loads the
GIF; **Show still frame** returns to the PNG. The control is a keyboard
accessible button with a playback-state label. Direct image links and the
surrounding explanation work without JavaScript, including when viewed on
GitHub. Playback is opt-in, and enabling a reduced-motion preference during
playback returns the figure to its still frame.

Local integrity checks cover the generated assets, static image links,
explanation sections, and changing plot content. After deployment, record
the live browser playback and keyboard-control checks on the deployment
pull request.

## Verification record

| Check | Recorded result |
|---|---|
| Registry coverage | 31 method entries, four stages and 32 frames per animation. |
| GIF size | Approximately 13.34 MiB across the complete GIF set; each file is below the 3 MiB budget. |
| Focused wrapper/backend tests | 37 passed, including six MVMD input-layout regression cases. |
| Strict documentation build | Passed with 103 documentation pages. |
| Animation integrity tests | 3 passed; generated assets, changing plot content, explanations, and stale-provenance rejection are covered. |
| Final full test suite | 193 passed, 1 skipped (optional Torch), and 3 warnings in 62.40 seconds. |
| Source-distribution build | Passed with isolated build dependencies; distribution-content checks passed, including all animation assets and generation sources. |

The manifest and per-method metadata contain the detailed array inventories,
numerical checks, dependency versions, and artifact hashes for this record.
