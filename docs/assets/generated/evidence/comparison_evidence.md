# Comparison Evidence

Generated for DeTime `0.1.2` on 2026-06-19T18:21:25.250889+00:00.

Audit date: 2026-06-19.

Comparator versions:

- statsmodels: 0.14.5
- PyEMD/EMD-signal: 1.6.4
- PyWavelets: 1.9.0
- PySDKit: 0.4.23
- SSALib: not installed in local audit environment
- sktime: 0.33.2

Runtime and memory boundary: feature audit only; no cross-package runtime or peak-memory ranking is claimed.

## Capability matrix

| package | primary_scope | unified_config_object | unified_result_object | machine_readable_catalog | batch_cli | profiling_path | multivariate_support | maturity_labeling | compact_output | mcp_tool_surface |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DeTime | Python/CLI decomposition package with a shared software contract | yes | yes | yes | yes | yes | yes | explicit | yes | yes |
| statsmodels | classical decomposition and modeling | no | partial | no | no | no | limited | implicit | no | no |
| PyEMD | EMD-family toolkit | no | no | no | no | no | family-specific | family-specific | no | no |
| PyWavelets | wavelet toolkit | no | no | no | no | no | transform-specific | family-specific | no | no |
| PySDKit | signal decomposition toolkit | partial | partial | no | limited | no | yes | less explicit | no | no |
| SSALib | SSA specialist toolkit | SSA-specific | SSA-specific | no | no | no | no | focused | no | no |
| sktime | broad time-series ecosystem | no | no | no | no | no | partial | ecosystem-level | no | no |

## Install and reproducibility matrix

| package | public_release_story | pypi_path | github_release | wheels | ci_platforms | docs_website | tutorials | api_docs | coverage_disclosure | reproducibility_script |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DeTime | 0.1.2 release target from main | tag-driven publish workflow | de-time-v0.1.2 | yes | ubuntu, macOS, windows | GitHub Pages | yes | yes | dual report | yes |
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

| package | json_schema_assets | compact_result_modes | metadata_shortlist_interface | machine_readable_catalog | cli_schema_command | artifact_contract | mcp_surface |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DeTime | yes | full/summary/meta | yes | yes | yes | yes | optional local-first |
| statsmodels | no | no | no | no | no | no | no |
| PyEMD | no | no | no | no | no | no | no |
| PyWavelets | no | no | no | no | no | no | no |
| PySDKit | no | no | no | no | no | no | no |
| SSALib | no | no | no | no | no | no | no |
| sktime | no | no | no | no | no | no | no |

## Runtime snapshot source

- `docs\assets\generated\evidence\performance_snapshot.csv`
