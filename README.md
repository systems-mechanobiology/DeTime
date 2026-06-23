# DeTime

One Python and CLI interface for trend, oscillation, residual, components, and metadata.

[![License: BSD-3-Clause](https://img.shields.io/badge/license-BSD--3--Clause-0f172a.svg)](LICENSE)
![Status: Beta](https://img.shields.io/badge/status-beta-1d4ed8.svg)
[![Release target: 0.1.2](https://img.shields.io/badge/release%20target-0.1.2-0f766e.svg)](CHANGELOG.md)
[![Docs: GitHub Pages](https://img.shields.io/badge/docs-GitHub_Pages-0b5fff.svg)](https://systems-mechanobiology.github.io/DeTime/)
[![HF Space: DeTime](https://img.shields.io/badge/HF%20Space-DeTime-ffb000.svg)](https://huggingface.co/spaces/Zipeng365/DeTime)
![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-0f766e.svg)
[![PyPI](https://img.shields.io/pypi/v/de-time.svg)](https://pypi.org/project/de-time/)
[![Unit tests: 112 passed](https://img.shields.io/badge/unit%20tests-112%20passed-brightgreen.svg)](tests/)
[![Core coverage: 92.58%](https://img.shields.io/badge/core%20coverage-92.58%25-brightgreen.svg)](README.md#quality-and-evidence)
[![Package coverage: 88.41%](https://img.shields.io/badge/package%20coverage-88.41%25-84cc16.svg)](README.md#quality-and-evidence)
[![Native-backed methods: 7](https://img.shields.io/badge/native--backed%20methods-7-475569.svg)](docs/method-matrix.md)
[![CLI: detime](https://img.shields.io/badge/CLI-detime-2563eb.svg)](docs/quickstart.md)
[![Schemas: JSON](https://img.shields.io/badge/schemas-JSON-0891b2.svg)](docs/machine-api.md)
[![Native kernels: C++](https://img.shields.io/badge/native%20kernels-C%2B%2B-475569.svg)](native/)

<p align="center">
  <img src="docs/assets/brand/detime-logo-color.png" alt="DeTime logo" width="640">
</p>

DeTime provides one stable software surface for decomposition workflows that
would otherwise be split across notebooks, method-specific wrappers, and
one-off scripts. The product name is **DeTime**, the distribution is
`de-time`, the canonical import is `detime`, and the legacy top-level
`tsdecomp` import and CLI remain compatibility-only through `0.1.x`, with
earliest removal planned for `0.2.0`.

The current reviewed release version is `0.1.2`. Install the latest published
package from PyPI with `python -m pip install de-time`, or use the editable
contributor path below for local development against the repository head.

Fast entry points:

- [Documentation site](https://systems-mechanobiology.github.io/DeTime/)
- [Inline method gallery](https://systems-mechanobiology.github.io/DeTime/notebook-gallery/)
- [Beginner notebook method gallery](examples/notebooks/de_time_method_gallery.ipynb)
- [Cross-package comparison](docs/comparisons.md)
- [Method comparison matrix](docs/method-matrix.md)
- [Release manifest](RELEASE_MANIFEST.md)
- [Release evidence tables](docs/reproducibility.md)

## Scope

Use DeTime when you want:

- one `decompose()` entrypoint,
- one `DecompositionConfig` model for Python and CLI usage,
- one `DecompResult` contract for `trend`, `season`, `residual`, `components`,
  and `meta`,
- native acceleration where it materially improves throughput,
- multivariate decomposition workflows where shared structure matters,
- machine-facing workflows that need schemas, metadata-based shortlists, and compact
  result views.

Use a specialist package directly when you only need that package's deepest
family-specific API.

## Core and accelerated methods

The main package is centered on four core maintained methods:

- `SSA`
- `STD`
- `STDR`
- `MSSA`

The current native-backed accelerated set is broader:

- core native paths: `SSA`, `STD`, `STDR`, `MSSA`
- additional native-backed methods: `VMD`, `GABOR_CLUSTER`
- lightweight native-backed baseline: `MA_BASELINE`

Other retained methods are wrappers, Python implementations, or
optional-backend integrations such as `STL`, `MSTL`, `ROBUST_STL`, `EMD`,
`CEEMDAN`, `WAVELET`, `MVMD`, and `MEMD`.

Experimental neural decomposition blocks extracted as standalone DeTime
methods are also available. They are package-level experimental operators for
decomposition-head ablations, reusable result-contract tests, and interface
coverage.

| Block | Source architecture family | Standalone operator exposed in DeTime | Status |
|---|---|---|---|
| `AMD_BLOCK` | adaptive multiscale decomposition | multiscale smoothing trend with periodic-template seasonality | non-learned extractor |
| `AUTOFORMER_BLOCK` | Autoformer | moving-average trend and residual-seasonal split | non-learned extractor |
| `DELELSTM_BLOCK` | DeLELSTM | Holt-style trend with periodic-template seasonality | non-learned extractor |
| `DLINEAR_BLOCK` | DLinear | moving-average decomposition head | non-learned extractor |
| `FREQMOE_BLOCK` | FreqMoE | frequency-band trend plus multi-band seasonality | non-learned extractor |
| `INPARFORMER_BLOCK` | InParformer | moving-average trend with periodic-template seasonal head | non-learned extractor |
| `LEDDAM_BLOCK` | LEDDAM | Gaussian-kernel smoothing decomposition operator | non-learned extractor |
| `MOVING_AVERAGE_DECOMPOSITION_BLOCK` | Autoformer/DLinear family | generic moving-average decomposition head | non-learned extractor |
| `NBEATS_INTERPRETABLE` | N-BEATS interpretable stacks | trend and seasonality basis stacks | torch-backed learned prior |
| `PARSIMONY_BLOCK` | parsimony-oriented decomposition | smooth trend with compact harmonic seasonal projection | non-learned extractor |
| `ST_MTM_BLOCK` | ST-MTM | smoothed trend with smoothed periodic seasonal template | non-learned extractor |
| `TIMEKAN_BLOCK` | TimeKAN | template and harmonic seasonal estimates with smoothed trend | non-learned extractor |
| `TIMES2D_BLOCK` | Times2D | multi-period harmonic decomposition head | non-learned extractor |
| `WAVEFORM_BLOCK` | WaveForM | wavelet multiresolution trend-detail decomposition | non-learned extractor |
| `WAVELETMIXER_BLOCK` | WaveletMixer | mixed wavelet detail-level decomposition | non-learned extractor |
| `XPATCH_BLOCK` | xPatch | exponential smoothing trend with local seasonal residual | non-learned extractor |

Their source-paper links are listed in
[docs/method-references.md](docs/method-references.md).

Benchmark-derived methods `DR_TS_REG`, `DR_TS_AE`, and `SL_LIB` do not ship in
the main package. They belong to the companion benchmark repository
[`systems-mechanobiology/de-time-bench`](https://github.com/systems-mechanobiology/de-time-bench).

## Cross-package comparison

DeTime is positioned as a software-contract and machine-contract layer beside
specialist packages, not as a replacement for all of them.

| Axis | DeTime | [statsmodels](https://www.statsmodels.org/) | [PyEMD](https://github.com/laszukdawid/PyEMD) | [PyWavelets](https://pywavelets.readthedocs.io/en/latest/) | [PySDKit](https://pysdkit.readthedocs.io/en/latest/) | [SSALib](https://github.com/ADSCIAN/ssalib) | [sktime](https://www.sktime.net/en/stable/) |
|---|---|---|---|---|---|---|---|
| Primary role | unified decomposition workflow | classical decomposition/statistics | EMD family | wavelet transforms | broad decomposition toolkit | SSA specialist | broad time-series ecosystem |
| Common config/result contract | yes | partial | no | no | partial | SSA-specific | no |
| CLI, batch, profiling | yes | no | no | no | limited | no | partial |
| Machine-readable catalog/schemas | yes | no | no | no | no | no | no |
| Multivariate under one surface | yes | limited | family-specific | transform-specific | yes | no | partial |
| Where it is deeper | workflow reproducibility | statistical modeling | EMD variants | wavelet tooling | decomposition breadth | SSA workflows | ecosystem breadth |

Full comparison details are in [docs/comparisons.md](docs/comparisons.md);
generated evidence files are kept in
[docs/comparison-evidence.md](docs/comparison-evidence.md).

## Install

Install the latest released package from PyPI:

```bash
python -m pip install de-time
```

Install optional extras as needed:

```bash
python -m pip install "de-time[multivar]"
python -m pip install "de-time[emd,neural]"
python -m pip install "de-time[notebook]"
```

Install directly from GitHub when you need the unreleased `main` branch:

```bash
python -m pip install "git+https://github.com/systems-mechanobiology/DeTime.git"
```

Do not install the unrelated [`detime`](https://pypi.org/project/detime/)
package from PyPI when you want this project; that package is not DeTime.

## Quickstart

```python
import numpy as np

from detime import DecompositionConfig, decompose

t = np.arange(120, dtype=float)
series = 0.03 * t + np.sin(2.0 * np.pi * t / 12.0)

result = decompose(
    series,
    DecompositionConfig(
        method="SSA",
        params={"window": 24, "rank": 6, "primary_period": 12},
    ),
)

print(result.trend.shape)
print(result.meta["backend_used"])
```

```bash
detime run \
  --method STD \
  --series examples/data/example_series.csv \
  --col value \
  --param period=12 \
  --out_dir out/std_run \
  --output-mode summary
```

## CLI surface

The supported commands are:

- `detime run`
- `detime batch`
- `detime profile`
- `detime version`
- `detime schema`
- `detime recommend`
- `detime benchmark`

The legacy `tsdecomp` executable calls the same code path but emits a
deprecation notice.

## TSDecompose benchmark bridge

The benchmark code remains in the external Hugging Face bundle
[`Zipeng365/TSDecompose-Benchmark`](https://huggingface.co/datasets/Zipeng365/TSDecompose-Benchmark).
DeTime provides a bridge API and CLI that downloads the bundle's
`code/TSDecompose` source snapshot into a local cache and runs its published
paper-core runner.

Fast smoke run:

```bash
detime benchmark --out-dir out/tsdecompose-smoke
```

Full paper-core run:

```bash
detime benchmark --full --out-dir out/tsdecompose-paper-core
```

Python API:

```python
from detime import run_tsdecompose_benchmark

result = run_tsdecompose_benchmark(smoke=True, out_dir="out/tsdecompose-smoke")
print(result.leaderboard_path)
```

## Machine-facing surface

DeTime now includes:

- packaged JSON schemas for `config`, `result`, `meta`, and `method-registry`,
- low-token result export modes: `full`, `summary`, and `meta`,
- machine-readable method metadata for registry, docs, and metadata-based shortlists,
- `detime schema` and `detime recommend`,
- a local-first MCP server at `python -m detime.mcp.server`.

These interfaces support non-interactive automation. The maintained software
claim remains the decomposition API, CLI, schemas, result object, metadata, and
validated package boundary.

## Package boundary

This repository ships the reusable decomposition software package, docs, tests,
and examples needed for `detime` itself. Benchmark orchestration, leaderboard
artifacts, benchmark scenario galleries, and benchmark-derived methods are
split into the companion repository
[`systems-mechanobiology/de-time-bench`](https://github.com/systems-mechanobiology/de-time-bench).
The `detime benchmark` command is a bridge to the external TSDecompose
benchmark bundle; it does not vendor benchmark-derived methods into the main
package.

Only the top-level `tsdecomp` import and CLI alias remain packaged for
compatibility.

## Quality and evidence

- Release smoke checks live in `scripts/release_smoke_matrix.py`.
- Documentation consistency checks live in
  `scripts/check_doc_consistency.py`.
- The current performance snapshot is generated by
  `scripts/generate_performance_snapshot.py` and stored under
  `docs/assets/generated/evidence/`.
- Comparison matrices are generated by
  `benchmarks/software_comparison/generate_comparison_evidence.py`.
- The coverage story is intentionally split into core-surface coverage and
  package-wide coverage so the denominator stays explicit.

Coverage from the 2026-06-22 checkout-source audit:

| View | Config | Scope | Result |
|---|---|---|---:|
| Core contract | `.coveragerc` | core-plus-maintained library surface | 92.58% |
| Package-wide | `.coveragerc.package` | installable package including CLI/I/O/wrappers/viz | 88.41% |

The JSON reports are stored in
`docs/assets/generated/evidence/coverage_core.json`,
`docs/assets/generated/evidence/coverage_package.json`, and
`docs/assets/generated/evidence/coverage_summary.json`.

Release-validation runtime snapshot for selected native-backed paths in the
reviewed environment. These values compare DeTime native-backed paths against
internal Python fallback paths in one environment; they are not a portable
cross-package benchmark.

| Method | Python mean (ms) | Native mean (ms) | Speedup |
|---|---:|---:|---:|
| `SSA` | 13.925 | 1.906 | 7.31x |
| `STD` | 0.154 | 0.024 | 6.44x |
| `STDR` | 0.175 | 0.018 | 9.81x |
| `MA_BASELINE` | 0.070 | 0.016 | 4.42x |
| `MSSA` | 60.856 | 22.900 | 2.66x |
| `VMD` | 47.856 | 13.812 | 3.46x |
| `GABOR_CLUSTER` (experimental) | 3.304 | 0.181 | 18.22x |

Documentation and tutorial evidence:

| Surface | Evidence |
|---|---|
| Quant Trading tutorial column | 11 applied notebooks plus one roadmap notebook, with captured tables, figures, strategy stats, and audit outputs |
| Hot Trend Lab | 7 case notebooks plus one overview notebook, with source-audit and component-output tables |
| Core workflow tutorials | univariate, multivariate, CLI/profiling, visual comparison, and method-gallery workflows |
| Review artifacts | comparison matrices, reproducibility notes, schemas, generated method cards, and release evidence files |

## Documentation

Core docs:
- Homepage: <https://systems-mechanobiology.github.io/DeTime/>
- Hugging Face Space mirror: <https://huggingface.co/spaces/Zipeng365/DeTime>
- Install: <https://systems-mechanobiology.github.io/DeTime/install/>
- Quickstart: <https://systems-mechanobiology.github.io/DeTime/quickstart/>
- Methods overview: <https://systems-mechanobiology.github.io/DeTime/methods/>
- Notebook gallery: <https://systems-mechanobiology.github.io/DeTime/notebook-gallery/>
- Tutorials: <https://systems-mechanobiology.github.io/DeTime/tutorials/univariate/>
- Quant Trading column: <https://systems-mechanobiology.github.io/DeTime/tutorials/quant-trading/>
- Hot Trend Lab: <https://systems-mechanobiology.github.io/DeTime/tutorials/hot-trend-lab/>
- API: <https://systems-mechanobiology.github.io/DeTime/api/>

Reference and review:
- Method matrix: <https://systems-mechanobiology.github.io/DeTime/method-matrix/>
- Config reference: <https://systems-mechanobiology.github.io/DeTime/config-reference/>
- Method references: <https://systems-mechanobiology.github.io/DeTime/method-references/>
- Machine API: <https://systems-mechanobiology.github.io/DeTime/machine-api/>
- Comparisons: <https://systems-mechanobiology.github.io/DeTime/comparisons/>
- Reproducibility: <https://systems-mechanobiology.github.io/DeTime/reproducibility/>

## Project files

- Citation metadata: [`CITATION.cff`](CITATION.cff)
- Changelog: [`CHANGELOG.md`](CHANGELOG.md)
- Design notes: [`DESIGN.md`](DESIGN.md)
- Contributing guide: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Security policy: [`SECURITY.md`](SECURITY.md)
- Publishing notes: [`PUBLISHING.md`](PUBLISHING.md)
- Release manifest: [`RELEASE_MANIFEST.md`](RELEASE_MANIFEST.md)
- Source/archive boundary: [`SOURCE_ARCHIVE_BOUNDARY.md`](SOURCE_ARCHIVE_BOUNDARY.md)
- Third-party licenses: [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md)
- License audit notes: [`LICENSE_AUDIT.md`](LICENSE_AUDIT.md)
- Authors and credit: [`AUTHORS.md`](AUTHORS.md), [`CREDIT.md`](CREDIT.md)
