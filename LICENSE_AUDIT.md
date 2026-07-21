# License Audit Notes

DeTime is released under the BSD-3-Clause license. The repository-level license
is in `LICENSE`.

## Source Headers

The repository-level BSD-3-Clause license covers project files unless a file
states otherwise. The release boundary is stricter: `scripts/check_dist_contents.py`
rejects any shipped Python or C/C++ source under `examples/`, `native/`,
`scripts/`, `src/`, or `tests/` that lacks an SPDX identifier.

## Included Components

- Native C++ sources under `native/` are authored as part of DeTime unless a
  file states otherwise.
- Optional backends are imported as external packages and are not vendored into
  the DeTime wheel.
- The external TSDecompose benchmark bridge downloads benchmark source into a
  local cache at user request; it is not vendored into the wheel or reviewed
  archive.

## Release Gate

Before tagging, build the wheel and source distribution and run
`scripts/check_dist_contents.py` on both. The check enforces the package
boundary, compatibility-file allowlist, banned benchmark paths, required
experimental-operator files, and SPDX headers for shipped source. Run
`python -m twine check` on the same artifacts and retain their file listings
with the release evidence. Add a third-party notice only if a future release
vendors external source.
