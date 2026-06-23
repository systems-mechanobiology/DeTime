# License Audit Notes

DeTime is released under the BSD-3-Clause license. The repository-level license
is in `LICENSE`.

## Source Headers

The current source tree does not yet enforce SPDX headers on every `.py`,
`.cpp`, `.hpp`, or `.h` file. For the JMLR-reviewed release, add a CI check that
verifies either:

- an SPDX license identifier in each source file, or
- a documented project-level policy that the repository-level BSD-3-Clause
  license covers files without per-file headers.

## Included Components

- Native C++ sources under `native/` are authored as part of DeTime unless a
  file states otherwise.
- Optional backends are imported as external packages and are not vendored into
  the DeTime wheel.
- The external TSDecompose benchmark bridge downloads benchmark source into a
  local cache at user request; it is not vendored into the wheel or reviewed
  archive.

## Release Gate

Before tagging the release, attach:

1. dependency-license report for the locked reviewer environment,
2. SPDX/header-check result,
3. wheel and sdist manifests,
4. third-party notice file if any vendored component is added.
