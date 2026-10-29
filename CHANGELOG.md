# Changelog

All notable changes to DeTime are documented in this file.

The project brand is **DeTime**, the PyPI distribution is `detime-toolkit`, the
preferred Python import path is `detime`, and the legacy `tsdecomp` import/CLI
aliases remain available for compatibility.

## [Unreleased]

### Maintenance

- fixes MSTL Box-Cox conversion with statsmodels 0.15, supports the zero-lambda
  logarithm explicitly, and preserves the original-scale additive result
  contract and nested STL configuration
- forwards CEEMDAN noise settings and the top-level random seed to PyEMD;
  uses serial execution for `n_jobs=1` and bounds worker count for larger values
- introduces the canonical CEEMDAN `epsilon` parameter; legacy `noise_width`
  now maps to `epsilon` with a warning because it previously had no effect
- records effective CEEMDAN settings, returns the documented IMF array, and
  prevents a mode from being assigned to both trend and season
- rejects an explicitly requested native CEEMDAN backend, since this method
  uses the Python upstream integration
- corrects the documented CEEMDAN defaults to the previously used upstream
  values (`trials=100`, `epsilon=0.005`), removes an unsupported MSTL extra
  component listing, and updates MSTL's citation to its 2025 journal version

### Research guides and examples

- adds a source-linked comparison of Python decomposition tools and a
  20-reference research map spanning classical algorithms, tokenization,
  neural modules, training objectives, and evaluation through 2026
- provides matching CSV/BibTeX references and English sharing drafts, with
  implemented methods distinguished from literature candidates
- replaces the ML example's same-time reconstruction regression with
  history-only features and held-out one-step forecasting evaluation
- connects the guides from the README and documentation site, preserves
  generated metadata checks, and adds a live CI badge beside release evidence

These are source-branch changes. The existing `detime-toolkit==0.1.3` wheel
and release tag are unchanged. The
[maintenance note](docs/maintenance/2026-10-29.md) records verification and
the compatibility changes relevant to reproducing prior results.

## [0.1.3] - 2026-07-14

### Contract and provenance corrections

- validates method parameters against the registry-owned parameter contract,
  including clear errors and typo suggestions for unknown keys
- corrects exact native SSA solver metadata and records requested versus
  effective Python SSA speed modes
- vectorizes Python SSA diagonal averaging and regenerates runtime evidence
  with warmups, repeated measurements, dispersion, and environment metadata
- pins the optional external benchmark bridge to an immutable revision and
  verifies the package-owned SHA-256 digest before execution

### Experimental and release boundaries

- adds machine-readable claim scopes and excludes all experimental operators
  from recommendations unless users opt in explicitly
- identifies architecture-named blocks as experimental standalone operators,
  not complete implementations of the cited forecasting architectures
- removes the archived `std_multi.py` placeholder and marks the trained-model
  Gabor path as experimental native-backed software
- replaces pickle-backed Gabor model files with an NPZ+JSON format loaded with
  `allow_pickle=False`
- identifies EMD and CEEMDAN as optional PyEMD wrappers and validates their real
  backend in the optional-integration smoke path
- excludes benchmark-only `DR_TS_REG` native source from the source distribution
- removes the unsupported MCP-like transport from the reviewed distribution
  and public contract
- standardizes `--out-dir` while retaining `--out_dir` as a compatibility alias
- removes unused `numba`, `sympy`, and `tqdm` hard dependencies
- verifies release tag/package equality before publication and checks the public
  GitHub and PyPI records before labeling documentation evidence as verified

## [0.1.2] - 2026-07-04

### Release identity and evidence lock

- aligns the JMLR-MLOSS submission target to a new immutable release candidate
  instead of moving the existing `de-time-v0.1.1` tag
- adds release-manifest, coverage, license-audit, authorship, and artifact-boundary
  evidence for the reviewed software object
- reports coverage from the current checkout source with a guarded import path:
  92.58% core-contract coverage and 88.41% package-wide coverage
- publishes the public PyPI distribution as `detime-toolkit==0.1.2` while
  preserving the `detime` import namespace

### Documentation and package boundary

- moves application-heavy and automation-heavy documentation behind the core
  install, API, method-status, validation, and developer-extension story
- labels neural-architecture-inspired blocks as experimental decomposition-head
  operators and keeps them out of the maintained-package claim
- narrows source-distribution contents so benchmarks, agent evals, trading
  notebooks, and Hot Trend Lab assets are not part of the reviewed archive

## [0.1.1] - 2026-06-10

### Contract and release evidence

- `method-registry` schemas and payloads now carry explicit `package`,
  `version`, and `contract_version` root fields
- packaged schema assets are regenerated from the live Pydantic models and are
  checked in CI with `scripts/generate_schema_assets.py --check`
- release evidence reports both core-surface coverage and
  package-wide coverage from the same `0.1.1` candidate

### Native and optional-backend behavior

- native `SSA` now treats `speed_mode='exact'` as a deterministic exact path
  rather than as an approximate iterative shortcut
- the iterative native SSA kernel remains available under
  `speed_mode='fast'`
- optional `MVMD` / `MEMD` integrations now have dedicated smoke coverage and
  example evidence under the `multivar` extra

### Docs and submission hardening

- API and install docs were rewritten into reviewer-grade reference and
  troubleshooting material
- publishing, reproducibility, and machine-API docs now reflect the `0.1.1`
  candidate and the current machine-contract wording
- submission materials now use an explicit early-adoption framing instead of
  implying a large external community

## [0.1.0] - 2026-04-08

### Public surface

- canonical package metadata and `detime` import surface
- deprecated top-level `tsdecomp` import and CLI aliases
- unified decomposition API centered on `DecompositionConfig`, `DecompResult`,
  and `decompose(...)`
- CLI workflows for `run`, `batch`, `profile`, `version`, `schema`, and
  `recommend`
- native acceleration for `SSA`, `STD`, and `STDR`
- multivariate workflows for `MSSA`, `MVMD`, `MEMD`, and channelwise `STD`
- minimal MCP server for tool-based machine access

### Machine-facing additions

- packaged JSON schemas for `config`, `result`, `meta`, and `method-registry`
- method metadata catalog via `MethodRegistry.list_catalog()`
- low-token `summary` and `meta` serialization modes
- metadata-based method shortlist surface for CLI and MCP workflows

### Packaging and quality

- wheel-first packaging via `scikit-build-core`, `pybind11`, and `cibuildwheel`
- package-level test suite, docs tree, examples, and GitHub Actions workflows
- coverage gate on the canonical core-plus-maintained surface
- artifact-layout checks for wheel and sdist outputs
- documentation consistency checks and release smoke automation
- reproducible performance snapshot generation

### Removed from install artifacts

- benchmark configuration helpers and leaderboard stubs
- benchmark-derived methods in the main package
- transition-era `tsdecomp` submodules outside the top-level import and CLI
  compatibility path
