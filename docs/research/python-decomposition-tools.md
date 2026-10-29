---
title: Choosing Python Time-Series Decomposition Tools
description: Compare STL, SSA, wavelets, EMD and VMD libraries by assumptions, outputs, reproducibility and forecasting workflow, with links to official documentation.
---

# STL, SSA, Wavelets, EMD, or VMD? Choosing Python Decomposition Tools

*Source review: 29 October 2026.*

Choose a decomposition method by the structure you want to estimate, the
observations available when you will use it, and the outputs your next step
requires. A package name alone answers none of those questions.

For one known seasonal period, STL is a useful starting point. For several
known periods, consider MSTL. For an explicitly chosen scale representation,
inspect wavelets. For data-adaptive oscillatory components, compare EMD-family
methods or VMD. For a low-rank trajectory representation, examine SSA. These
are conditional starting points, based on the APIs and assumptions described
below; performance on a particular application still requires measurement.

This maintainer-written guide compares official documentation and the DeTime
source. It reports software capabilities and practical evaluation choices.
The existing [comparison evidence](../comparisons.md) separately identifies
which package versions and timings were actually checked. Reading a current
documentation page does not establish that every feature works in an older
installed release.

## 1. A map of the Python ecosystem

The table describes the selected decomposition interfaces, rather than every
feature of each project. The linked documentation is the evidence for each row.

| Tool | Useful starting point | Main output | Choice to make explicitly |
|---|---|---|---|
| [statsmodels STL][stl] | A series with one seasonal period | Trend, seasonal component, residual | Period, smoothing spans, robust weighting |
| [statsmodels MSTL][mstl] | Several seasonal periods in one series | Trend, multiple seasonal components, residual | Periods, seasonal windows, optional Box–Cox transform |
| [PyWavelets][dwt] | Wavelet scale analysis and reconstruction | Approximation/detail coefficients | Wavelet, level, signal extension mode |
| [PyEMD / EMD-signal][pyemd] | EMD, EEMD and CEEMDAN | Intrinsic mode functions and method-specific residual information | Sifting settings; noise and ensemble settings when applicable |
| [emd][emd-api] | EMD with spectral and cycle analysis | IMFs plus separate phase, frequency, amplitude and cycle-analysis outputs | Sift variant and analysis conventions |
| [pyts SSA][pyts-ssa] | Decomposing a collection of univariate series | Per-series reconstructed groups | Embedding window and component grouping |
| [SSALib][ssalib] | Detailed exploration of one series using SSA | SSA objects, grouped reconstructions and diagnostics | Matrix construction, SVD solver and grouping |
| [sktime VmdTransformer][sktime-vmd] | VMD within a time-series estimator workflow | Modes or spectra | Mode count, bandwidth parameter, initialization and tolerance |
| [PySDKit][pysdkit] | Exploring multiple signal-decomposition families | Method-specific modes/results through `fit_transform` interfaces | Method, input layout and reconstruction convention |
| [DeTime][detime-source] | Comparing families while retaining one configuration and result interface | `trend`, `season`, `residual`, optional `components`, `meta` | Method parameters, backend and grouping policy |

Several projects already offer broad catalogs or common estimator interfaces.
DeTime's practical contribution is its combination of a shared decomposition
result, configuration, CLI, saved artifacts and machine-readable metadata.
Those features are useful when a project needs to repeat the same workflow
across families. A specialist library remains a strong choice when its
method-specific diagnostics or controls are central to the analysis.

## 2. What the method choice actually changes

### STL and MSTL: specify the seasonal structure

STL uses LOESS smoothing with a specified period. Its `seasonal` argument is
the seasonal smoother length; it is distinct from `period`. Robust weighting
is available through `robust=True`. For NumPy arrays, the period must be
provided. MSTL extends this workflow to multiple periods and permits an
optional Box–Cox transformation. Its result retains the separate seasonal
components. [STL documentation][stl]; [MSTL documentation][mstl].

For hourly observations, a daily period corresponds to 24 samples only if the
sampling grid is actually hourly. State how gaps, duplicate timestamps and
clock changes were handled before interpreting the components. A period
specified in samples should always be accompanied by the sampling interval.

One naming detail matters in DeTime: `ROBUST_STL` selects the statsmodels STL
wrapper with robust weighting enabled by default. This identifier should not
be cited as an implementation of a different paper merely because that paper
has a similar title. The [wrapper source][detime-stl] and
[method references](../method-references.md) identify the implemented method.

### Wavelets: define scales and boundary behavior

PyWavelets exposes approximation/detail coefficient arrays, multilevel
decomposition and inverse reconstruction. Decimated coefficients generally
have different lengths from the original series. Reconstruct selected levels
before treating them as sample-aligned components. The documented
`waverec` interface supports partial reconstruction by replacing unwanted
coefficient arrays with zeros of matching shape. [DWT][dwt]; [inverse DWT][idwt].

Boundary handling is part of the method specification. PyWavelets documents
several extension modes and explains that the choice can introduce edge
artifacts. Record the same extension convention for analysis and synthesis.
Calling a low-frequency reconstruction “trend” is an interpretation that
should be justified by the application. [Signal extension modes][wavelet-modes].

### EMD-family methods: identify the implementation and randomness

PyEMD and `emd` are separate projects. PyEMD is distributed as `EMD-signal`
and imported as `PyEMD`; its documented classes include EMD, EEMD and CEEMDAN.
The `emd` distribution is imported as `emd` and includes ensemble, complete
ensemble and masked sifts, together with spectral and cycle analysis.
Installation names and import names therefore belong in the experiment
record. [PyEMD introduction][pyemd-intro]; [emd installation][emd-install];
[emd API][emd-api].

Noise-assisted methods need a reproducibility policy. Current PyEMD CEEMDAN
documentation recommends calling `noise_seed()` and using `parallel=False`
for reproducible runs. It documents `epsilon` for adaptive noise scaling;
EEMD documents a separate `noise_width` parameter. Copying parameter names
between the two classes can change the intended experiment.
[CEEMDAN documentation][ceemdan]; [EEMD documentation][eemd].

The application must also specify how IMFs are assigned to the quantities it
will use. A low-frequency group, a selected oscillation and the remaining
signal are different outputs from the raw IMF array. Retain the grouping
rule with the result so another researcher can reconstruct that decision.

### SSA: the grouping rule carries scientific meaning

The pyts SSA interface accepts a matrix of univariate samples and exposes
window size and grouping controls. `groups='auto'` uses documented
frequency-based criteria for trend, seasonal and residual groups. Its `fit`
method is a pass-through; the decomposition happens during `transform`.
`chunksize` batches the collection of series to trade memory for runtime.
It does not turn one long series into an online decomposition.
[pyts SSA documentation][pyts-ssa].

SSALib provides a different SSA workflow: multiple SVD solver options, grouped
reconstruction, weighted-correlation plots and Monte Carlo SSA. Those
diagnostics can matter more than a common interface when the research question
concerns the interpretation of a particular component. [SSALib repository][ssalib].

For an SSA comparison, report window length, rank when truncated, solver and
the exact groups used in reconstruction. Changing any of these can change the
estimated components. A component index is an algorithmic label; assigning a
physical meaning requires additional evidence.

### VMD and multivariate decomposition: fix the output contract

sktime documents `VmdTransformer` as the maintained continuation of `vmdpy`.
The original repository was archived in June 2024 and directs development to
sktime. The transformer supports a specified mode count or an iterative
selection based on its reconstruction-loss criterion. Record `K`, `alpha`,
initialization and stopping tolerance; an automatically selected mode count
is an outcome of that criterion. [VmdTransformer][sktime-vmd];
[vmdpy maintenance notice][vmdpy].

PySDKit documents a broad family of signal decompositions, including MEMD and
MVMD. Its MVMD interface documents mode output with shape `(K, length,
num_channels)`. Check the axis convention before connecting that output to a
plotting or learning pipeline. Shared mode indices across channels do not by
themselves establish that a mode corresponds to a particular physical source.
[PySDKit API][pysdkit]; [MVMD documentation][pysdkit-vmd].

## 3. What a unified result can and cannot establish

DeTime provides one `decompose()` entry point and a `DecompResult` containing
`trend`, `season`, `residual`, `components` and `meta`. Its implementation
mixes maintained in-package methods, native-backed paths and integrations:
STL/MSTL call statsmodels, WAVELET calls PyWavelets, EMD/CEEMDAN use PyEMD,
and optional multivariate wrappers use PySDKit. These relationships are
documented in the [method matrix](../method-matrix.md) and
[source tree][detime-source].

The common fields simplify code that saves, compares or visualizes results.
They do not make the underlying component definitions equivalent. A wavelet
approximation, an SSA group and an STL trend express different assumptions.
In several DeTime methods, the residual is explicitly calculated as the input
minus the selected trend and seasonal components. [SSA implementation][detime-ssa];
[wavelet implementation][detime-wavelet].

Consequently, a near-zero reconstruction error can confirm arithmetic
consistency while providing little evidence about identification. If
`residual = input - trend - season`, then the three fields reconstruct the
input by construction. A useful component evaluation needs a separate target:
known synthetic components, a controlled physical process, external
measurements, or a downstream question with an appropriate held-out test.

DeTime also documents architecture-inspired experimental decomposition
operators. Their identifiers record a source of inspiration. Treat those
operators according to their documented implementation scope; a standalone
moving-average or wavelet block does not reproduce a complete trained
forecasting system. [Experimental method scope][detime-source].

## 4. Keep future observations outside a forecasting feature

For a forecast issued at time `t`, every preprocessing step must use only
information available at `t`. Consider a centered smoother computed once over
an entire record: an estimated trend at an earlier point can depend on later
observations. Slicing its output afterward does not remove that dependence.
This follows from the information used by the computation, regardless of the
package name.

A practical forecasting protocol is:

1. Fix training, validation and test forecast origins before tuning.
2. At each origin, pass only the available history to the decomposition.
3. Construct the input features and forecast using that history.
4. Evaluate against the future observations after prediction is complete.
5. Keep period selection, normalization, missing-value treatment and parameter
   tuning within the corresponding training/validation information boundary.

Refitting on a growing prefix is a valid way to enforce this boundary, but it
can be expensive. A rolling window changes the estimator and should be
declared. A dedicated online method has its own update and latency contract.
For example, PySDKit lists `OnlineEMD`; that capability should be evaluated
through its specific API rather than inferred for every EMD implementation.
[PySDKit catalog][pysdkit].

Offline analysis has a different information budget. Describing a completed
record can legitimately use the whole record. Classifying a fully observed
window can also use that window if it matches the intended deployment input.
The relevant question is whether the evaluation reproduces what will be
available when the output is used.

## 5. A comparison protocol that produces useful evidence

The following is a proposed evaluation protocol, not a report of executed
cross-package experiments.

| Question | Evidence to collect | Interpretation limit |
|---|---|---|
| Does the implementation reconstruct its declared output? | Reconstruction error, shape checks and retained residual policy | Does not identify the true generating components |
| Does it recover components relevant to the task? | Known components or independent reference measurements; grouping rule | A visually smooth curve alone is insufficient |
| Is it stable under reasonable choices? | Perturbations of window, rank, period, mode count, noise and seed | Stability around one configuration can miss other regimes |
| Does it improve a downstream task? | Same splits, model, tuning budget and information boundary | A change in the whole pipeline does not isolate decomposition |
| What resources does it use? | Wall time, peak memory, input dimensions, threads, backend and versions | A small input or one machine cannot establish general scaling |

Measure startup and steady-state execution separately when they affect the
deployment workload. Report failed decompositions and unavailable optional
dependencies alongside successful runs. Do not average them away by silently
changing the compared dataset or method set.

For multivariate data, record whether channels were decomposed jointly or
independently. For stochastic methods, retain the seed and process settings.
For modes that can reorder, compare components using a declared matching
rule; assigning “component 1” the same meaning in every run is an additional
assumption.

## 6. Pick a first workflow

Use statsmodels directly for its seasonal-decomposition and statistical
modeling workflow. Use PyWavelets for detailed transform controls. Compare
PyEMD and `emd` according to the sifting and oscillation-analysis tools needed.
Consider pyts for batched SSA transforms, SSALib for SSA diagnostics, sktime
for estimator composition, and PySDKit for broader signal-decomposition
exploration. These recommendations follow the documented interfaces above.

Use DeTime when the repeated task is to run several families, retain one
result layout, inspect backend metadata, and export results through Python or
the CLI. Start with the [quickstart](../quickstart.md), inspect the
[configuration reference](../config-reference.md), and preserve the exact
configuration with the output. Install the distribution `detime-toolkit` and
import `detime`, as specified in the [installation guide](../install.md).

Source-head maintenance and released wheels have separate version histories.
For example, the CEEMDAN parameter-forwarding and seed-handling corrections
accompanying this guide belong to the unreleased source changes. They should
not be assumed to exist in `detime-toolkit==0.1.3`. Record the installed version
or source commit and consult the [changelog][detime-changelog] when reproducing
a configuration.

For the research behind the methods and newer decomposition-based models,
continue with the [decomposition literature map](decomposition-landscape-2026.md).
For reproducible software comparisons, begin with the
[existing evidence and its stated limits](../comparisons.md).

## Sources

All external sources below are official project documentation or repositories.
Links were reviewed on 29 October 2026. They can change independently of the
package version installed in an experiment.

- [statsmodels STL][stl] and [MSTL][mstl].
- [PyWavelets DWT][dwt], [inverse DWT][idwt], and [signal extension modes][wavelet-modes].
- [PyEMD documentation][pyemd], [installation][pyemd-intro], [CEEMDAN][ceemdan], and [EEMD][eemd].
- [emd API][emd-api] and [installation][emd-install].
- [pyts SingularSpectrumAnalysis][pyts-ssa].
- [SSALib repository][ssalib].
- [sktime VmdTransformer][sktime-vmd] and [vmdpy maintenance notice][vmdpy].
- [PySDKit API][pysdkit] and [VMD/MVMD interfaces][pysdkit-vmd].
- [DeTime source][detime-source], [STL wrapper][detime-stl], [SSA][detime-ssa], and [wavelets][detime-wavelet].

[stl]: https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.STL.html
[mstl]: https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.MSTL.html
[dwt]: https://pywavelets.readthedocs.io/en/stable/ref/dwt-discrete-wavelet-transform.html
[idwt]: https://pywavelets.readthedocs.io/en/stable/ref/idwt-inverse-discrete-wavelet-transform.html
[wavelet-modes]: https://pywavelets.readthedocs.io/en/stable/ref/signal-extension-modes.html
[pyemd]: https://pyemd.readthedocs.io/en/latest/
[pyemd-intro]: https://pyemd.readthedocs.io/en/latest/intro.html
[ceemdan]: https://pyemd.readthedocs.io/en/latest/ceemdan.html
[eemd]: https://pyemd.readthedocs.io/en/latest/eemd.html
[emd-api]: https://emd.readthedocs.io/en/stable/api.html
[emd-install]: https://emd.readthedocs.io/en/latest/install.html
[pyts-ssa]: https://pyts.readthedocs.io/en/latest/generated/pyts.decomposition.SingularSpectrumAnalysis.html
[ssalib]: https://github.com/ADSCIAN/ssalib
[sktime-vmd]: https://www.sktime.net/docs/api-reference/sktimetransformationsvmdvmdtransformer/
[vmdpy]: https://github.com/vrcarva/vmdpy
[pysdkit]: https://pysdkit.readthedocs.io/en/stable/API/pysdkit.html
[pysdkit-vmd]: https://pysdkit.readthedocs.io/en/stable/API/pysdkit._vmd.html
[detime-source]: https://github.com/systems-mechanobiology/DeTime
[detime-stl]: https://github.com/systems-mechanobiology/DeTime/blob/main/src/detime/methods/stl.py
[detime-ssa]: https://github.com/systems-mechanobiology/DeTime/blob/main/src/detime/methods/ssa.py
[detime-wavelet]: https://github.com/systems-mechanobiology/DeTime/blob/main/src/detime/methods/wavelet.py
[detime-changelog]: https://github.com/systems-mechanobiology/DeTime/blob/main/CHANGELOG.md
