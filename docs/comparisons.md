---
title: Compare Python Time-Series Decomposition Libraries
description: Compare DeTime with specialist Python decomposition libraries, including PySDKit, SSALib and sktime. Review workflow differences and measured native-path timings.
---

# Compare Python Time-Series Decomposition Libraries

DeTime is useful when the project needs one decomposition workflow across
Python, CLI, saved artifacts, and machine-readable metadata. Specialist
packages remain the better choice when you only need their deepest family-
specific API.

For method assumptions, library-specific controls, and a forecasting evaluation
protocol, read [Choosing Python Decomposition Tools](research/python-decomposition-tools.md).
The [research map](research/decomposition-landscape-2026.md) connects these
interfaces to the literature through 2026.

## Before and after

<div class="pipeline-panel">
  <div class="pipeline-flow">
    <div class="pipeline-step">
      <strong>Specialist glue</strong>
      <span>different configs, result objects, filenames, and backend rules per package</span>
    </div>
    <div class="pipeline-step">
      <strong>DeTime layer</strong>
      <span>one <code>DecompositionConfig</code>, one <code>DecompResult</code>, one CLI artifact contract</span>
    </div>
    <div class="pipeline-step">
      <strong>Reviewable output</strong>
      <span>summary/meta/full JSON modes, method catalog, schemas, and reproducible figures</span>
    </div>
  </div>
</div>

## Software matrix

Audit date: 2026-07-14. Local comparator packages available in the final audit
environment were `statsmodels==0.14.6`, `PyWavelets==1.9.0`, and
`PySDKit==0.4.25`. `EMD-signal`, `SSALib`, and `sktime` were not installed in
that environment, so their positions use package papers and public
documentation rather than local import checks. The feature matrix records
workflow/API characteristics; it is not a runtime or memory ranking.

| Axis | DeTime | [`statsmodels`](https://www.statsmodels.org/) | [`PyEMD`](https://github.com/laszukdawid/PyEMD) | [`PyWavelets`](https://pywavelets.readthedocs.io/en/latest/) | [`PySDKit`](https://pysdkit.readthedocs.io/en/latest/) | [`SSALib`](https://github.com/ADSCIAN/ssalib) | [`sktime`](https://www.sktime.net/en/stable/) |
|---|---|---|---|---|---|---|---|
| Best fit | cross-method workflow | classical decomposition/statistics | EMD-family work | wavelet transforms | broad signal decomposition | SSA-focused work | broader time-series ecosystem |
| Config/result surface | shared config and normalized result | per-method constructors; shared `DecomposeResult` for STL/MSTL | classes and IMF arrays | functions and coefficient trees | method-family classes/results | SSA-specific configuration/results | estimator/transformer API |
| CLI and profiling | package API, CLI, batch, and profiles | library API | library API | library API | library API | library API | library API |
| Schemas and metadata | JSON schemas plus method/runtime metadata | result fields and documentation | IMF arrays and method state | coefficient metadata | method-specific outputs | SSA diagnostics/results | estimator parameters, tags, and registry |
| Multivariate under one surface | yes | limited | family-specific | transform-specific | yes | no | partial |
| Where it is deeper | workflow reproducibility | statistical modeling | EMD variants | wavelet tooling | decomposition breadth | SSA workflows | ecosystem breadth |

## Package-by-package reading

| Package | Use it directly when | Use DeTime when |
|---|---|---|
| [`statsmodels`](https://www.statsmodels.org/) | you need the full statistical modeling stack | you want `STL` / `MSTL` output in the same contract as other methods |
| [`PyEMD`](https://github.com/laszukdawid/PyEMD) | you need deeper EMD-family controls | you want `EMD` / `CEEMDAN` beside SSA, STD, VMD, and CLI artifacts |
| [`PyWavelets`](https://pywavelets.readthedocs.io/en/latest/) | you need transform-specific wavelet APIs | you want wavelet decomposition as one option in a broader workflow |
| [`PySDKit`](https://pysdkit.readthedocs.io/en/latest/) | you need its broad signal-decomposition catalog | you want selected optional multivariate backends behind DeTime metadata and I/O |
| [`SSALib`](https://github.com/ADSCIAN/ssalib) | you only need SSA-family tooling | you want `SSA` as one core method in a cross-family package |
| [`sktime`](https://www.sktime.net/en/stable/) | you need a large time-series ML ecosystem | you want decomposition outputs with DeTime's artifact and schema contract |

Broader ecosystems provide complementary abstractions:
[Darts](https://unit8co.github.io/darts/) supports forecasting and time-series
modelling, [aeon](https://www.aeon-toolkit.org/) provides estimator interfaces
for time-series machine learning, and
[StatsForecast](https://nixtlaverse.nixtla.io/statsforecast/) focuses on
scalable statistical forecasting. DeTime's narrower scope is a standalone
decomposition package with one configuration, execution, normalized result,
metadata, schema, CLI, profiling, and artifact contract across families.

## Runtime snapshot

The release evidence includes a reproducible runtime snapshot generated by
`scripts/generate_performance_snapshot.py`. The current committed snapshot was
generated on Windows 10, Python 3.11.9, AMD64, with native `SSA`, `STD`,
`STDR`, `MA_BASELINE`, `MSSA`, and `VMD` capabilities available. Experimental
`GABOR_CLUSTER` timing is excluded from release-validation performance evidence
because it depends on a trained model object and optional clustering backend
availability.

| Method | Python median runtime (ms) | Native median runtime (ms) | Python/native ratio | Repeats / warmup |
|---|---:|---:|---:|---:|
| `SSA` | 0.526 | 3.523 | 0.149x | 50 / 10 |
| `STD` | 0.138 | 0.111 | 1.244x | 50 / 10 |
| `STDR` | 0.176 | 0.118 | 1.496x | 50 / 10 |
| `MA_BASELINE` | 0.071 | 0.064 | 1.104x | 50 / 10 |
| `MSSA` | 42.933 | 16.053 | 2.674x | 50 / 10 |
| `VMD` | 125.270 | 464.513 | 0.270x | 50 / 10 |

A ratio above 1 means that the native path was faster in this snapshot. Native
execution was faster for STD, STDR, MA baseline, and MSSA, while Python was
faster for SSA and VMD on this input. These numbers are a release-validation
snapshot, not a universal benchmark.

## Runtime and memory boundary

The current comparison evidence does not claim cross-package runtime or memory
superiority. Runtime rows above compare DeTime native-backed paths with DeTime
Python fallback paths in one environment. Peak-memory and direct same-method
comparisons against external packages are future comparison work unless a
release artifact explicitly records them.

## Evidence appendix

<div class="compact-faq">

<details>
<summary>Curated comparison files</summary>

<ul>
<li><a href="../assets/generated/evidence/comparison_evidence.json"><code>comparison_evidence.json</code></a></li>
<li><a href="../assets/generated/evidence/comparison_capability_matrix.csv"><code>comparison_capability_matrix.csv</code></a></li>
<li><a href="../assets/generated/evidence/comparison_install_matrix.csv"><code>comparison_install_matrix.csv</code></a></li>
<li><a href="../assets/generated/evidence/comparison_family_fairness.csv"><code>comparison_family_fairness.csv</code></a></li>
<li><a href="../assets/generated/evidence/comparison_machine_contract_matrix.csv"><code>comparison_machine_contract_matrix.csv</code></a></li>
<li><a href="../assets/generated/evidence/workflow_comparison.json"><code>workflow_comparison.json</code></a></li>
</ul>

<p>Regenerate them with:</p>

<pre><code>python benchmarks/software_comparison/generate_comparison_evidence.py
python examples/workflow_comparisons/compare_specialist_glue_vs_detime.py
</code></pre>

<p>The comparison generator defaults to <code>local-unverified</code>; use
<code>--release-state verified-public</code> only after checking the matching
GitHub and PyPI release.</p>

</details>

<details>
<summary>Quality and packaging checks</summary>

<ul>
<li><code>python scripts/check_doc_consistency.py</code></li>
<li><code>mkdocs build --strict</code></li>
<li><code>python -m build</code></li>
<li><code>python scripts/check_dist_contents.py dist/*.tar.gz dist/*.whl</code></li>
<li><code>python -m twine check dist/*</code></li>
<li><code>python scripts/release_smoke_matrix.py</code></li>
</ul>

</details>

</div>
