# Source, Wheel, and Reviewed-Archive Boundary

This project distinguishes four artifacts that are often conflated during
software-paper review.

| Artifact | Purpose | Included | Excluded |
|---|---|---|---|
| GitHub source tree | Maintainer workspace and full documentation source | package source, tests, docs, examples, submission notes, generation scripts | none by design |
| Wheel | End-user install artifact | `detime`, top-level `tsdecomp` compatibility alias, packaged schemas, native extension | docs, tests, notebooks, benchmarks, submission materials |
| PyPI sdist | Source build artifact | package source, native source, tests, core docs, minimal examples, release scripts needed to validate package contents | benchmarks, agent evals, quant-trading assets, Hot Trend Lab assets, generated site, submission bundle |
| JMLR reviewed archive | Frozen review artifact | source, tests, core docs, schema assets, evidence JSON, release manifest, minimal examples | application notebooks, external benchmark orchestration, generated website, draft submission files |

## Policy

- Benchmark orchestration belongs in a companion benchmark repository or in
  clearly labeled release evidence, not in the installable package claim.
- Quant-trading and Hot Trend Lab material are applications and documentation
  examples. They are useful for users but are not part of the core maintained
  software claim.
- Agent-oriented, token-budget, and MCP material is treated as optional
  automation support. It must not dominate the reviewed software identity.
- Final release artifacts should publish machine-readable manifests:
  `wheel_contents.txt`, `sdist_contents.txt`, and `jmlr_archive_contents.txt`.
