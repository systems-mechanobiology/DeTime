# Cover Letter for JMLR MLOSS Submission

Dear Editors,

We submit **DeTime** for consideration in the *Journal of Machine Learning
Research* Machine Learning Open Source Software track.

The software is released under the BSD 3-Clause License and is available at
<https://github.com/systems-mechanobiology/DeTime>. The version under review is
DeTime `0.1.2`.

DeTime is Python and CLI research software for reproducible time-series
decomposition. Its novelty is practical: it makes decomposition a consistent
workflow across method families that are usually used through separate
packages, notebook conventions, and output formats. Researchers can use the
same Python API, command-line interface, result object, metadata fields,
serialization format, and JSON schemas across retained decomposition methods.
This makes decomposition outputs easier to reproduce, compare, inspect, and
reuse in downstream machine-learning workflows.

The current implementation is centered on four maintained decomposition
methods: singular spectrum analysis (`SSA`), seasonal-trend-dispersion
decomposition (`STD`), its robust variant (`STDR`), and multivariate singular
spectrum analysis (`MSSA`). Additional methods are available as wrappers,
optional backends, or experimental paths with explicit maturity labels.

The reviewed repository contains the reusable decomposition package, rather
than a combined package-and-benchmark artifact. Benchmark-oriented artifact
code, synthetic benchmark generators, leaderboard tooling, and
benchmark-derived methods are kept outside the main package in the companion
repository `systems-mechanobiology/de-time-bench`. The DeTime repository itself
includes:

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
- a dedicated `.[multivar]` smoke path for optional `MVMD` / `MEMD` backends.

The release evidence includes pytest coverage reports: `92.58%` for the core
`detime` modules used in the release gate and `88.41%` for the package-wide
run. It also includes a small reproducible runtime snapshot showing native
speedups of `7.31x` for `SSA`, `6.44x` for `STD`, and `9.81x` for `STDR`
relative to the Python fallback on one Windows / Python 3.11 installation.
These release details are summarized in `submission/software_evidence.md`.

We do not position DeTime as a replacement for specialist libraries such as
`statsmodels`, `PyEMD`, `PyWavelets`, `PySDKit`, `SSALib`, or the maintained
`sktime` VMD path. Instead, DeTime contributes a reproducible software layer
that standardizes configuration, result objects, package-level ergonomics, and
selected native acceleration across a fragmented decomposition ecosystem.
Primary method citations and official upstream package links are enumerated in
`submission/software_evidence.md` and the generated docs reference page
`docs/method-references.md`.

Current community and openness evidence includes the public GitHub repository,
public documentation site, contributor guide, issue templates, GitHub
Discussions, and release/publishing documentation. The repository currently has
52 GitHub stars and 37 forks, and its commit history includes five commit
authors. We present these as early evidence of visibility and maintainability,
not as a claim of broad external adoption.

Sincerely,

Zipeng Wu
