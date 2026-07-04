# Release Artifacts

This page summarizes the DeTime `0.1.2` release evidence for software-paper
review.

| Artifact | Repository path |
|---|---|
| Release manifest | `RELEASE_MANIFEST.md` |
| Source/archive boundary | `SOURCE_ARCHIVE_BOUNDARY.md` |
| Third-party license summary | `THIRD_PARTY_LICENSES.md` |
| License audit notes | `LICENSE_AUDIT.md` |
| Authors | `AUTHORS.md` |
| CRediT draft | `CREDIT.md` |
| Core coverage JSON | `docs/assets/generated/evidence/coverage_core.json` |
| Package-wide coverage JSON | `docs/assets/generated/evidence/coverage_package.json` |
| Coverage summary JSON | `docs/assets/generated/evidence/coverage_summary.json` |

The existing `de-time-v0.1.1` tag is not moved. The reviewed source tag follows
the existing `de-time-v*` convention, and the public Python package is published
as `detime-toolkit==0.1.2`. Install with:

```bash
python -m pip install detime-toolkit==0.1.2
```

The runtime import namespace remains `detime`.
