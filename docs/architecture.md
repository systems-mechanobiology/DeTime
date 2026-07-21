# Architecture

## Package layout

The canonical implementation lives under `src/detime`.

- `core.py`: public data models.
- `registry.py`: method registration, metadata catalog, and `decompose()` dispatch.
- `io.py`: loading series and saving decomposition outputs.
- `serialization.py`: `full`, `summary`, and `meta` result views.
- `recommend.py`: metadata-based method shortlist logic.
- `schemas.py`: packaged JSON schema generation and loading.
- `profile.py`: runtime profiling helpers.
- `viz.py`: plotting helpers.
- `methods/`: core methods and retained wrappers.
- `_native.py`: native extension discovery and capability checks.

## Compatibility layer

`src/tsdecomp` is now a thin compatibility package. It re-exports the package-
level DeTime surface and emits deprecation warnings for imports and CLI usage.
Only the top-level import path and CLI alias remain packaged; transition-era
submodules are intentionally not shipped in install artifacts. The compatibility
window is the `0.1.x` series, with earliest removal planned for `0.2.0`.

## Machine-facing boundary

Machine-oriented workflows use:

- packaged JSON schemas under `src/detime/schema_assets`,
- machine-readable method metadata from `MethodRegistry.list_catalog()`,
- `detime schema` and the metadata-based `detime recommend` shortlist command,
- low-token result exports via `summary` and `meta` modes.

## Native boundary

Native kernels are built and loaded under the DeTime naming path first. The
release-timed paths are SSA, STD, STDR, MA baseline, MSSA, and VMD. The
experimental Gabor-cluster operator also has a native-backed path but is
excluded from release timing because it requires a trained model and optional
clustering backend. Benchmark-derived `DR_TS_REG` code is excluded from both
the compiled extension and the source distribution.
