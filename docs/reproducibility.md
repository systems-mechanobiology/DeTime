# Reproducibility

This repository is focused on the `detime` software package itself.

## Included here

- canonical `detime` source code,
- deprecated `tsdecomp` top-level import and CLI alias,
- tests for the retained public surface,
- examples and tutorials for package workflows,
- documentation for installation, APIs, methods, and migration,
- packaged JSON schemas and a minimal MCP server for machine-facing workflows.

## Moved out

Benchmark orchestration, synthetic benchmark generators, leaderboard helpers,
and benchmark-derived methods belong to the companion repository
[`systems-mechanobiology/de-time-bench`](https://github.com/systems-mechanobiology/de-time-bench).

That split keeps the main package installable and reviewable as software rather
than as a mixed library-plus-benchmark artifact.

The release artifacts also exclude transition-era compatibility submodules such
as `tsdecomp.methods.*`, `tsdecomp.leaderboard`, and `tsdecomp.bench_config`.

## External benchmark bridge

DeTime includes a bridge command for the public Hugging Face bundle
[`Zipeng365/TSDecompose-Benchmark`](https://huggingface.co/datasets/Zipeng365/TSDecompose-Benchmark).
The command downloads the bundle's `code/TSDecompose` source snapshot into a
local cache and invokes its published paper benchmark runner.

Smoke run:

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

This bridge keeps the benchmark source and benchmark-derived methods outside
the installable DeTime package while still giving readers a direct
reproduction path for the benchmark claims.

## Documentation and tutorial surface

The documentation is part of the reviewed software surface, not only a landing
page. It includes executable examples, rendered notebooks, generated method
metadata, schemas, and release evidence files.

| Surface | Evidence |
|---|---|
| Quant Trading tutorial column | 11 applied notebooks plus one roadmap notebook, with captured code cells, stdout, tables, figures, strategy statistics, and audit outputs |
| Hot Trend Lab | 7 case notebooks plus one overview notebook, with source-audit tables, component summaries, residual-event outputs, and publication-context notes |
| Core workflow tutorials | univariate decomposition, multivariate decomposition, CLI export/profiling, visual method comparison, and method-gallery workflows |
| Review artifacts | comparison matrices, release-smoke checks, reproducibility notes, JSON schemas, generated method cards, and evidence snapshots |

## Release Checks

<div class="compact-faq">

<details>
<summary>Commands used for release and docs validation</summary>

The current release and docs were checked with:

- `pytest tests -q`
- `pytest tests/optional/test_multivar_optional_backends.py -q`
- `pytest tests --cov=detime --cov-config=.coveragerc`
- `pytest tests --cov=detime --cov-config=.coveragerc.package`
- `python scripts/generate_schema_assets.py --check`
- `python scripts/generate_schema_assets.py`
- `python scripts/generate_tutorial_assets.py`
- `mkdocs build --strict`
- `python -m build`
- `python scripts/check_dist_contents.py dist/*.tar.gz dist/*.whl`
- `python scripts/check_doc_consistency.py`
- `python scripts/release_smoke_matrix.py`
- `python scripts/generate_performance_snapshot.py`
- `python scripts/generate_method_cards.py`
- `python benchmarks/software_comparison/generate_comparison_evidence.py`
- `python examples/workflow_comparisons/compare_specialist_glue_vs_detime.py`
- `python scripts/generate_reviewer_bundle.py`
- `python -m twine check dist/*`

</details>

</div>

## Coverage boundary

The repository now publishes two coverage views so the denominator is explicit:

- **core-surface coverage**
  - the gated `detime` core-plus-maintained contract
- **package-wide coverage**
  - the broader installable `detime` package, including CLI, I/O,
    visualization, wrappers, and machine-facing helpers

The core gate is applied to the canonical `detime` core-plus-maintained surface.

The core-surface denominator intentionally omits:

- the deprecated `tsdecomp` compatibility layer,
- CLI wrappers,
- I/O helpers,
- visualization helpers,
- optional wrappers and non-core integrations that remain tested but are
  not part of the gated coverage surface.

The 2026-06-22 `0.1.2` release-candidate audit was run against the checkout
source by removing the stale `_de_time_editable` import hook before pytest
startup and putting `src/` first on `sys.path`. It reached `92.58%`
core-contract coverage and `88.41%` package-wide coverage.

Package-wide coverage is emitted separately in CI and uploaded as a second
artifact so release reports can show both the narrow safety gate and the
broader installable surface.

Optional `.[multivar]` integrations are validated separately in a dedicated
smoke path so `MVMD` / `MEMD` execution evidence is published without
broadening the core-method coverage gate.

## Native agreement checks

Native-backed methods are not treated as correctness shortcuts. The test suite
includes numeric agreement checks between native and Python implementations for:

- `SSA`
- `STD`
- `STDR`

The documented tolerances are:

- `SSA`: `atol=1e-6`
- `STD` / `STDR`: `atol=1e-9`

Native correctness status:

| Native path | Reference path | Check type | Public tolerance | Status |
|---|---|---|---:|---|
| `SSA` | Python SSA | numerical agreement | `1e-6` | agreement-tested |
| `STD` | Python STD | numerical agreement | `1e-9` | agreement-tested |
| `STDR` | Python STDR | numerical agreement | `1e-9` | agreement-tested |
| `MA_BASELINE` | Python fallback | callable/schema smoke | n/a | smoke-tested |
| `MSSA` | Python fallback | callable/schema smoke | n/a | smoke-tested |
| `VMD` | Python fallback | callable/schema smoke | n/a | smoke-tested |
| `GABOR_CLUSTER` | experimental native path | callable/schema smoke | n/a | experimental smoke-tested |

Only the agreement-tested rows should be cited as numerical-equivalence
evidence. The remaining rows verify routing, result-shape/schema behavior, and
native availability in the release environment.

## Release-validation runtime snapshot

The following snapshot records selected native-backed release-validation paths
against internal Python fallback paths in one review environment. It verifies
that the native paths are installed, callable, and routed through the same
result contract. It is not a portable runtime ranking against other packages.

| Method | Python mean (ms) | Native mean (ms) | Speedup |
|---|---:|---:|---:|
| `SSA` | 13.925 | 1.906 | 7.31x |
| `STD` | 0.154 | 0.024 | 6.44x |
| `STDR` | 0.175 | 0.018 | 9.81x |
| `MA_BASELINE` | 0.070 | 0.016 | 4.42x |
| `MSSA` | 60.856 | 22.900 | 2.66x |
| `VMD` | 47.856 | 13.812 | 3.46x |
| `GABOR_CLUSTER` (experimental) | 3.304 | 0.181 | 18.22x |

## Experimental neural block table

These operators are exposed through the same DeTime config/result surface for
decomposition-head ablations, reusable result-contract tests, and interface
coverage. They remain experimental package-level operators.

| Block | Source architecture family | Standalone operator exposed in DeTime | Training status |
|---|---|---|---|
| `AMD_BLOCK` | adaptive multiscale decomposition | multiscale smoothing trend with periodic-template seasonal reconstruction | non-learned extractor |
| `AUTOFORMER_BLOCK` | Autoformer | moving-average trend and residual-seasonal split | non-learned extractor |
| `DELELSTM_BLOCK` | DeLELSTM | Holt-style trend with periodic-template seasonality | non-learned extractor |
| `DLINEAR_BLOCK` | DLinear | moving-average decomposition head from linear forecasting blocks | non-learned extractor |
| `FREQMOE_BLOCK` | FreqMoE | frequency-band trend plus multi-band seasonal reconstruction | non-learned extractor |
| `INPARFORMER_BLOCK` | InParformer | moving-average trend with periodic-template seasonal head | non-learned extractor |
| `LEDDAM_BLOCK` | LEDDAM | Gaussian-kernel smoothing operator inspired by learnable decomposition | non-learned extractor |
| `MOVING_AVERAGE_DECOMPOSITION_BLOCK` | Autoformer/DLinear family | generic moving-average neural decomposition head | non-learned extractor |
| `NBEATS_INTERPRETABLE` | N-BEATS interpretable stacks | trend and seasonality basis stacks used as a decomposition prior | torch-backed learned prior |
| `PARSIMONY_BLOCK` | parsimony-oriented decomposition | smooth trend with compact harmonic seasonal projection | non-learned extractor |
| `ST_MTM_BLOCK` | ST-MTM | trend smoothing with smoothed periodic seasonal template | non-learned extractor |
| `TIMEKAN_BLOCK` | TimeKAN | template and harmonic seasonal estimates with smoothed trend | non-learned extractor |
| `TIMES2D_BLOCK` | Times2D | multi-period harmonic decomposition head | non-learned extractor |
| `WAVEFORM_BLOCK` | WaveForM | wavelet multiresolution trend-detail decomposition | non-learned extractor |
| `WAVELETMIXER_BLOCK` | WaveletMixer | mixed wavelet detail-level decomposition | non-learned extractor |
| `XPATCH_BLOCK` | xPatch | exponential smoothing trend with local seasonal residual | non-learned extractor |

## Evidence Artifacts

- [Performance snapshot JSON](assets/generated/evidence/performance_snapshot.json)
- [Performance summary CSV](assets/generated/evidence/performance_snapshot.csv)
- [Core coverage JSON](assets/generated/evidence/coverage_core.json)
- [Package-wide coverage JSON](assets/generated/evidence/coverage_package.json)
- [Coverage summary JSON](assets/generated/evidence/coverage_summary.json)
- [Comparison evidence JSON](assets/generated/evidence/comparison_evidence.json)
- [Workflow comparison demo JSON](assets/generated/evidence/workflow_comparison.json)
- JSON schemas: `src/detime/schema_assets/*.json`

The performance snapshot is reproducible from
`scripts/generate_performance_snapshot.py`. Tutorial outputs are reproducible
from `scripts/generate_tutorial_assets.py`. Schema assets are reproducible from
`scripts/generate_schema_assets.py`. The release smoke report is reproducible
from `scripts/release_smoke_matrix.py`.
