# DeTime 0.1.2 Release Manifest

This file records the release identity used for the JMLR-MLOSS software-paper
candidate after the 2026-06-19 evidence audit and the 2026-07-04 public PyPI
publication.

## Identity

| Field | Value |
|---|---|
| Software name | DeTime |
| Python distribution | `detime-toolkit` |
| Canonical import | `detime` |
| Released version | `0.1.2` |
| Source tag | `de-time-v0.1.2` |
| Evidence audit date | 2026-06-19 |
| PyPI publication date | 2026-07-04 |
| Base commit before this evidence-lock patch | `a3716aba40162fe1be03dcbdb43962c8cbd4fe8c` |
| License | BSD-3-Clause |
| Python versions checked | 3.11.9 locally; CI matrix is documented for 3.10/3.12 |
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

## Public Release Record

The public install command is:

```bash
python -m pip install detime-toolkit==0.1.2
```

The runtime import remains:

```python
import detime
```

The release smoke matrix has been validated from the public PyPI package.

The existing `de-time-v0.1.1` tag is not moved. The 0.1.2 target avoids
rewriting a published tag and provides a clean reviewed snapshot for the
resubmission.
