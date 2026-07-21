# Release Artifacts

This page summarizes the DeTime `0.1.3` release evidence for software-paper
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

The reviewed source release uses the existing `de-time-v*` convention. The
release is complete only when the `de-time-v0.1.3` tag and the
`detime-toolkit==0.1.3` PyPI record both resolve; the runtime import namespace
remains `detime`. The exact-version install command is:

```bash
python -m pip install detime-toolkit==0.1.3
```

GitHub release assets should use the `detime_toolkit-0.1.3` artifact names.
