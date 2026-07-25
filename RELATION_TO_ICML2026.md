# Relation to the ICML 2026 Decomposition Benchmark

This document records the relationship between DeTime 0.1.3 and the accepted
ICML 2026 paper:

> Zipeng Wu, Jiani Wei, Shiqiao Zhou, Jiajun Chen, Fabian Spill, and James W.
> Andrews. *Time-Series Decomposition as a Standalone Task: A
> Mechanism-Driven Diagnostic Benchmark*. Proceedings of the 43rd
> International Conference on Machine Learning, 2026.

The public camera-ready artifact bundle currently uses the subtitle
*A Mechanism-Identifiable Benchmark*. Both titles refer to the same ICML 2026
work.

## Contribution of the ICML paper

The ICML paper studies decomposition as a component-recovery and diagnostic
task. Its primary contributions are controlled synthetic mechanisms,
method-alignment rules, shape/phase/spectral metrics, empirical capability
maps, and a downstream symbolic-regression evaluation. Its datasets,
leaderboard, benchmark runners, result tables, and paper-specific artifacts
remain in the external benchmark resources:

- [TSDecompose benchmark bundle](https://huggingface.co/datasets/Zipeng365/TSDecompose-Benchmark)
- [Companion benchmark repository](https://github.com/systems-mechanobiology/de-time-bench)

The benchmark was run with the original, Python-only `TSDecompose` /
`tsdecomp` research implementation distributed in that artifact bundle. It
predates, and is not, the DeTime 0.1.3 package submitted to JMLR MLOSS.

## Contribution of DeTime

DeTime 0.1.3 is the subsequent refactoring and extension of that research code
into an independently versioned, installable Python and command-line package.
The software work contributes a reusable decomposition interface centered on:

- `DecompositionConfig`, `decompose(...)`, `DecompResult`, and
  `MethodRegistry`;
- standardized result fields, runtime and backend metadata, JSON schemas, and
  saved artifacts;
- Python, CLI, batch, profiling, schema, and method-metadata commands;
- explicit support boundaries for maintained methods, wrappers, optional
  backends, and experimental operators;
- wheel and source distributions, cross-platform CI, tests, coverage,
  documentation, tutorials, and release-validation evidence; and
- maintained native and Python execution paths for the release-supported
  methods.

These package-level interfaces and software-engineering assets are the subject
of the JMLR MLOSS submission.

## Code and artifact boundary

DeTime retains `tsdecomp` only as a deprecated top-level compatibility alias
for migration during the 0.1.x series; the alias resolves to the current
DeTime implementation rather than vendoring the original benchmark tree.
Benchmark configuration helpers, leaderboard code, and benchmark-derived
methods (`DR_TS_REG`, `DR_TS_AE`, and `SL_LIB`) are excluded from the
installable DeTime package and live in the companion benchmark repository.

The optional `detime benchmark` command is an explicit bridge to a pinned
external benchmark snapshot. It downloads and executes external code only
after user opt-in; the benchmark source, datasets, metrics, results, and
paper-specific artifacts are not vendored into DeTime.

## Version under review

- DeTime version: `0.1.3`
- Release tag: `de-time-v0.1.3`
- Python distribution: `detime-toolkit==0.1.3`
- License: BSD-3-Clause
