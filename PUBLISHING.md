# Publishing DeTime

This file describes the standalone release flow for the `detime-toolkit`
distribution, the `detime` import path, and the legacy `tsdecomp`
compatibility aliases.

## Current release target

The current reviewed release is `0.1.2`. The public PyPI distribution is
`detime-toolkit==0.1.2`, while the import namespace remains `detime`. The
reviewed GitHub source tag uses the existing `de-time-v*` convention.

Release contract:

- product brand: `DeTime`
- PyPI distribution: `detime-toolkit`
- preferred import path: `detime`
- legacy import path: `tsdecomp`
- preferred CLI: `detime`
- legacy CLI alias: `tsdecomp`

The packaged compatibility scope is intentionally narrow: only top-level
`import tsdecomp` and the `tsdecomp` CLI alias remain. Transition-era
submodules such as `tsdecomp.methods.*`, `tsdecomp.leaderboard`, and
`tsdecomp.bench_config` are not part of the release payload.

## Maintainer checklist for the next release

1. Update the version in `pyproject.toml`, `CHANGELOG.md`, and `CITATION.cff`.
2. Regenerate and check schema assets.
3. Regenerate tutorial assets and release evidence files.
4. Run the documentation consistency check and strict docs build.
5. Run local tests, including the dedicated `.[multivar]` smoke path.
6. Build a source distribution and wheel.
7. Run the release smoke matrix and distribution-content checks.
8. Commit the release changes.
9. Tag the release using the `de-time-v*` source-tag convention.
10. Push the branch and tag.
11. Publish the GitHub release.
12. Let the release workflow publish to PyPI.
13. Verify the docs deployment and installation path.

## Local release commands

```bash
python -m pip install -U pip build twine
python -m pip install -e .[dev,multivar,docs]
python -m pytest tests -q
python -m pytest tests/optional/test_multivar_optional_backends.py -q
python scripts/generate_schema_assets.py --check
python scripts/generate_schema_assets.py
python scripts/generate_tutorial_assets.py
python scripts/generate_performance_snapshot.py
python benchmarks/software_comparison/generate_comparison_evidence.py
python examples/workflow_comparisons/compare_specialist_glue_vs_detime.py
python benchmarks/token_benchmarks/generate_token_benchmarks.py
python evals/agent/run_agent_evals.py
python scripts/generate_method_cards.py
python scripts/check_doc_consistency.py
python -m mkdocs build --strict
python -m build
python scripts/check_dist_contents.py dist/*.tar.gz dist/*.whl
python scripts/release_smoke_matrix.py
python -m twine check dist/*
```

## Tagging convention

Use release tags that match the standalone product:

```bash
git tag de-time-v0.1.2
git push origin de-time-v0.1.2
```

The wheel workflow is configured around `de-time-v*` tags.

## GitHub Actions expectations

The standalone repository contains:

- `.github/workflows/ci.yml`
- `.github/workflows/wheels.yml`
- `.github/workflows/docs.yml`

Those workflows assume this package directory is the repository root.

## PyPI and trusted publishing

If you use GitHub Actions for publishing:

- configure PyPI trusted publishing for the standalone repository,
- ensure the release workflow has `id-token: write`,
- publish only from release tags or GitHub releases.

## Docs deployment

The docs workflow builds MkDocs and deploys to GitHub Pages. Before using it:

- enable GitHub Pages for the repository,
- allow Pages deployment from GitHub Actions,
- confirm `site_url` in `mkdocs.yml`.

## Notes on compatibility

The canonical implementation lives under `src/detime/`. The `src/tsdecomp/`
tree retains only the top-level compatibility entrypoints needed for
`import tsdecomp` and the legacy CLI alias. Transition-era submodules are
intentionally omitted from the packaged artifacts.
