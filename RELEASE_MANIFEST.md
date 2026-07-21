# DeTime 0.1.3 Release Manifest

This file records the reviewed release identity prepared for the JMLR-MLOSS
software-paper submission after the 2026-07-14 evidence audit.

## Identity

| Field | Value |
|---|---|
| Software name | DeTime |
| Python distribution | `detime-toolkit` |
| Canonical import | `detime` |
| Reviewed version | `0.1.3` |
| Source tag | `de-time-v0.1.3` |
| Evidence audit date | 2026-07-14 |
| License | BSD-3-Clause |
| Python versions checked | 3.11.9 locally; CI tests 3.10/3.12 on Ubuntu Linux, macOS, and Windows |
| Reviewed surface | library, CLI, schemas, method metadata, docs, tests, release evidence |

## Evidence Files

| Evidence | Path |
|---|---|
| Core coverage JSON | `docs/assets/generated/evidence/coverage_core.json` |
| Package-wide coverage JSON | `docs/assets/generated/evidence/coverage_package.json` |
| Coverage summary | `docs/assets/generated/evidence/coverage_summary.json` |
| Runtime snapshot | `docs/assets/generated/evidence/performance_snapshot.json` |
| Related-software evidence | `docs/assets/generated/evidence/comparison_evidence.json` |
| Source/package boundary | `SOURCE_ARCHIVE_BOUNDARY.md` |
| Third-party license audit | `THIRD_PARTY_LICENSES.md` and `LICENSE_AUDIT.md` |
| Software authorship and credit | `AUTHORS.md` and `CREDIT.md` |

## Release Record and Verification

The exact-version install command is:

```bash
python -m pip install detime-toolkit==0.1.3
```

The runtime import remains:

```python
import detime
```

Before tagging, the release smoke matrix is run from isolated installs of the
built wheel and source distribution. Public-release evidence is marked
`verified-public` only after the GitHub release tag and exact PyPI version both
resolve.

The `de-time-v0.1.3` source tag and the `detime-toolkit==0.1.3` PyPI
distribution are required to describe the same reviewed 0.1.3 release
identity. The package is installed as `detime-toolkit` and imported as
`detime`; GitHub release assets use the `detime_toolkit-0.1.3` artifact names.
