# Curated Comparison Evidence

Curated for DeTime `0.1.3` on 2026-07-14T15:15:44.279658+00:00.

Release state: `local-unverified`.

Audit date: 2026-07-14 (utc-current).

Comparator versions:

- statsmodels: 0.14.6
- PyEMD/EMD-signal: not installed in local audit environment
- PyWavelets: 1.9.0
- PySDKit: 0.4.25
- SSALib: not installed in local audit environment
- sktime: not installed in local audit environment

Runtime and memory boundary: feature audit only; no cross-package runtime or peak-memory ranking is claimed.

## Capability matrix

| package | primary_scope | unified_config_object | unified_result_object | machine_readable_catalog | batch_cli | profiling_path | multivariate_support | maturity_labeling | compact_output |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DeTime | standalone cross-family time-series decomposition | yes | yes | yes | yes | yes | yes | explicit | yes |
| statsmodels | classical decomposition and modeling | per-method constructors | shared for STL/MSTL | library metadata | library API | external tooling | limited | implicit | method result |
| PyEMD | EMD-family toolkit | family classes | IMF arrays | method state | library API | external tooling | family-specific | family-specific | IMF arrays |
| PyWavelets | wavelet toolkit | function arguments | coefficient trees | transform metadata | library API | external tooling | transform-specific | family-specific | coefficients |
| PySDKit | signal decomposition toolkit | method-family classes | method-specific | method documentation | library API | external tooling | yes | less explicit | method-specific |
| SSALib | SSA specialist toolkit | SSA-specific | SSA-specific | SSA metadata | library API | external tooling | no | focused | SSA results |
| sktime | broad time-series ecosystem | estimator parameters | task-specific | runtime estimator registry | library API | external tooling | partial | ecosystem-level | task-specific |

## Install and reproducibility matrix

| package | public_release_story | pypi_path | github_release | wheels | ci_platforms | docs_website | tutorials | api_docs | coverage_disclosure | reproducibility_script |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DeTime | 0.1.3 local source state; publication status unverified | not verified | not verified | yes | ubuntu, macOS, windows | GitHub Pages | yes | yes | dual report | yes |
| statsmodels | yes | yes | yes | yes | yes | yes | yes | yes | project-dependent | project-dependent |
| PyEMD | yes | yes | yes | partial | project-dependent | partial | partial | partial | project-dependent | no |
| PyWavelets | yes | yes | yes | yes | yes | yes | yes | yes | project-dependent | no |
| PySDKit | yes | yes | yes | partial | project-dependent | yes | partial | partial | project-dependent | no |
| SSALib | yes | yes | yes | partial | project-dependent | yes | partial | partial | project-dependent | no |
| sktime | yes | yes | yes | yes | yes | yes | yes | yes | project-dependent | project-dependent |

## Family-fairness notes

| family | specialist | specialist_deeper_strength | de_time_position |
| --- | --- | --- | --- |
| classical decomposition | statsmodels | deeper classical decomposition and statistical modeling | wraps STL and MSTL under one config/result/CLI layer |
| SSA | SSALib | deeper SSA-only environment with SSA-specific tooling | uses SSA as one core method inside a cross-family workflow layer |
| EMD family | PyEMD | deeper EMD-family tooling | exposes EMD and CEEMDAN through the same contract used for other families |
| wavelet workflows | PyWavelets | deeper wavelet transforms and transform-specific APIs | uses wavelets as one workflow option rather than a wavelet-first toolkit |
| unified toolkit layer | PySDKit | broader signal-decomposition toolkit with optional multivariate backends | focuses on time-series decomposition workflows, machine-facing contracts, and compact outputs |

## Machine-contract matrix

| package | json_schema_assets | compact_result_modes | metadata_shortlist_interface | machine_readable_catalog | cli_schema_command | artifact_contract |
| --- | --- | --- | --- | --- | --- | --- |
| DeTime | yes | full/summary/meta | yes | yes | yes | yes |
| statsmodels | no | no | no | no | no | no |
| PyEMD | no | no | no | no | no | no |
| PyWavelets | no | no | no | no | no | no |
| PySDKit | no | no | no | no | no | no |
| SSALib | no | no | no | no | no | no |
| sktime | no | no | no | yes-runtime-registry | no | no |

## Runtime snapshot source

- `docs\assets\generated\evidence\performance_snapshot.csv`
