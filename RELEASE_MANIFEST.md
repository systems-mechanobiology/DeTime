# DeTime 0.1.2 Release Candidate Manifest

This file records the release identity used for the JMLR-MLOSS software-paper
candidate after the 2026-06-19 evidence audit.

## Identity

| Field | Value |
|---|---|
| Software name | DeTime |
| Python distribution | `de-time` |
| Canonical import | `detime` |
| Release target | `0.1.2` |
| Planned tag | `de-time-v0.1.2` |
| Audit date | 2026-06-19 |
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

## External Release Actions Still Required

These actions cannot be completed by editing the repository alone:

1. Build wheel and source distribution from the final release commit.
2. Generate `wheel_contents.txt`, `sdist_contents.txt`, and checksums.
3. Create the immutable GitHub Release `de-time-v0.1.2`.
4. Attach wheel, sdist, source archive, checksums, coverage reports, and a docs snapshot.
5. Optionally archive the release with Zenodo or Software Heritage.

The existing `de-time-v0.1.1` tag is not moved. The 0.1.2 target avoids
rewriting a published tag and provides a clean reviewed snapshot for the
resubmission.
