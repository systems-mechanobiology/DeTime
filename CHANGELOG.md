# Changelog

All notable changes to DeTime are documented in this file.

The project brand is **DeTime**, the PyPI distribution is `de-time`, the
preferred Python import path is `detime`, and the legacy `tsdecomp` import/CLI
aliases remain available for compatibility.

## [0.1.2] - 2026-06-19

### Release identity and evidence lock

- aligns the JMLR-MLOSS submission target to a new immutable release candidate
  instead of moving the existing `de-time-v0.1.1` tag
- adds release-manifest, coverage, license-audit, authorship, and artifact-boundary
  evidence for the reviewed software object
- reports coverage from the current checkout source with a guarded import path:
  92.58% core-contract coverage and 88.41% package-wide coverage

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

- canonical `de-time` package metadata and `detime` import surface
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
