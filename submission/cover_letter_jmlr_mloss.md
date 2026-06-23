# Cover Letter for JMLR MLOSS Submission

Dear Editors,

We submit **DeTime** for consideration in the *Journal of Machine Learning
Research* Machine Learning Open Source Software track.

DeTime is Python and CLI research software for reproducible time-series
decomposition. It provides a clean software surface for configuring, running,
profiling, saving, and validating decomposition runs that would otherwise
be spread across notebook code, method-specific wrappers, and one-off scripts.

The canonical package namespace is `detime`. The older `tsdecomp` namespace is
retained only as a deprecated top-level import and CLI alias. The public
software surface is intentionally narrow and centers on four core maintained
workflows: `SSA`, `STD`, `STDR`, and `MSSA`.

This revision also makes a package-boundary change that we consider essential
for software review. Benchmark-oriented artifact code, synthetic benchmark
generators, leaderboard tooling, and benchmark-derived methods were separated
into a companion repository, `systems-mechanobiology/de-time-bench`, so that
the main submission is a clean software package rather than a mixed benchmark
artifact.

This submission is aligned to the `0.1.2` release candidate. Repository
metadata, citation metadata, docs, and submission materials are aligned to that
candidate; the existing `de-time-v0.1.1` tag is not moved, and the next public
release should be cut as `de-time-v0.1.2`. The repository includes:

- tests for the retained public interface,
- strict documentation builds,
- wheel and source-distribution validation,
- artifact-layout checks that verify removed benchmark stubs and transition-era
  compatibility submodules are absent from wheel and sdist payloads,
- a coverage gate of `fail_under = 90` on the canonical core-plus-maintained
  coverage scope,
- schema freshness checks for the packaged JSON schemas,
- native-backed acceleration for selected maintained paths,
- deterministic exact native `SSA` behavior in `speed_mode='exact'`,
- packaged JSON schemas, compact result modes, metadata-based method
  shortlists, and an optional local MCP server for tool-based access,
- a dedicated `.[multivar]` smoke path for optional `MVMD` / `MEMD` backends,
- migration guidance from the deprecated `tsdecomp` namespace.

In the 2026-06-22 local release review run, the gated `detime` core-contract
coverage report reached `92.58%`, while the separate package-wide report
reached `88.41%`. We also include a reproducible runtime snapshot showing
native speedups of `7.31x` for `SSA`, `6.44x` for `STD`, and `9.81x` for
`STDR` relative to the Python fallback on one Windows / Python 3.11
installation. Those release details are summarized in
`submission/software_evidence.md`.

We do not position DeTime as a replacement for specialist libraries such as
`statsmodels`, `PyEMD`, `PyWavelets`, `PySDKit`, `SSALib`, or the maintained
`sktime` VMD path. Instead, we position it as a reproducible software-contract layer
that standardizes configuration, result objects, package-level ergonomics, and
selected native acceleration across a fragmented decomposition ecosystem.
Primary method citations and official upstream package links are enumerated in
`submission/software_evidence.md` and the generated docs reference page
`docs/method-references.md`.

Adoption is still early, and we do not claim a large external user community at
this stage. We instead present the public repository, contributor
documentation, issue templates, GitHub Discussions, the documentation site, and
the release/publishing pipeline as auditable openness evidence while broader
usage evidence accumulates.

Sincerely,

Zipeng Wu
