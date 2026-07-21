# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import argparse
import glob
import sys
import tarfile
import zipfile
from pathlib import PurePosixPath

ALLOWED_TSDECOMP_SDIST = {
    "src/tsdecomp/__init__.py",
    "src/tsdecomp/__main__.py",
    "src/tsdecomp/_compat.py",
    "src/tsdecomp/cli.py",
}

ALLOWED_TSDECOMP_WHEEL = {
    "tsdecomp/__init__.py",
    "tsdecomp/__main__.py",
    "tsdecomp/_compat.py",
    "tsdecomp/cli.py",
}

REQUIRED_NEURAL_BLOCK_SDIST = {
    "src/detime/methods/neural_blocks/__init__.py",
    "src/detime/methods/neural_blocks/forecasting_blocks.py",
    "src/detime/methods/neural_blocks/learned_priors.py",
    "src/detime/methods/neural_blocks/leddam_block.py",
    "src/detime/methods/neural_blocks/neural_block_portfolio.py",
    "src/detime/methods/neural_blocks/xpatch_block.py",
}

REQUIRED_NEURAL_BLOCK_WHEEL = {
    "detime/methods/neural_blocks/__init__.py",
    "detime/methods/neural_blocks/forecasting_blocks.py",
    "detime/methods/neural_blocks/learned_priors.py",
    "detime/methods/neural_blocks/leddam_block.py",
    "detime/methods/neural_blocks/neural_block_portfolio.py",
    "detime/methods/neural_blocks/xpatch_block.py",
}

BANNED_COMMON = {
    "detime/bench_config.py",
    "detime/leaderboard.py",
}

BANNED_SDIST = {
    "src/detime/bench_config.py",
    "src/detime/leaderboard.py",
    "native/src/dr_ts_reg.cpp",
    "docs/tutorials/visual-benchmark.md",
}

BANNED_SDIST_PREFIXES = (
    ".pytest_cache/",
    "benchmarks/",
    "docs/assets/generated/evidence/agent_",
    "docs/assets/generated/evidence/token_",
    "docs/assets/generated/tutorials/visual-benchmark/",
    "docs/tutorials/hot-trend-lab/notebooks/",
    "docs/tutorials/quant-trading/notebooks/",
    "evals/",
    "examples/hot_trends/",
    "examples/notebooks/",
    "examples/quant_trading/",
)


def _normalize_sdist_member(name: str) -> str:
    parts = PurePosixPath(name).parts
    if len(parts) <= 1:
        return ""
    return PurePosixPath(*parts[1:]).as_posix()


def _check_entries(
    entries: set[str],
    allowed_tsdecomp: set[str],
    banned: set[str],
    label: str,
    banned_prefixes: tuple[str, ...] = (),
    required: set[str] | None = None,
) -> list[str]:
    failures: list[str] = []
    required = required or set()

    for path in sorted(banned):
        if path in entries:
            failures.append(f"{label}: banned path present: {path}")
    for prefix in banned_prefixes:
        for path in sorted(entry for entry in entries if entry.startswith(prefix)):
            failures.append(f"{label}: banned path present: {path}")

    tsdecomp_entries = {entry for entry in entries if entry.startswith("tsdecomp/") or entry.startswith("src/tsdecomp/")}
    unexpected = tsdecomp_entries - allowed_tsdecomp
    missing = allowed_tsdecomp - tsdecomp_entries

    for path in sorted(unexpected):
        failures.append(f"{label}: unexpected compatibility file present: {path}")
    for path in sorted(missing):
        failures.append(f"{label}: expected compatibility file missing: {path}")
    for path in sorted(required - entries):
        failures.append(f"{label}: expected package file missing: {path}")

    return failures


def _inspect_sdist(path: str) -> list[str]:
    with tarfile.open(path, "r:gz") as archive:
        members = {
            _normalize_sdist_member(member.name): member
            for member in archive.getmembers()
            if _normalize_sdist_member(member.name)
        }
        names = set(members)
        failures = _check_entries(
            names,
            ALLOWED_TSDECOMP_SDIST,
            BANNED_SDIST,
            path,
            banned_prefixes=BANNED_SDIST_PREFIXES,
            required=REQUIRED_NEURAL_BLOCK_SDIST,
        )
        source_prefixes = ("examples/", "native/", "scripts/", "src/", "tests/")
        source_suffixes = (".cc", ".cpp", ".cxx", ".h", ".hpp", ".py")
        for name, member in sorted(members.items()):
            if not name.startswith(source_prefixes) or not name.endswith(source_suffixes):
                continue
            stream = archive.extractfile(member)
            if stream is None or b"SPDX-License-Identifier:" not in stream.read(4096):
                failures.append(f"{path}: shipped source lacks SPDX header: {name}")
    return failures


def _inspect_wheel(path: str) -> list[str]:
    with zipfile.ZipFile(path) as archive:
        names = {name for name in archive.namelist() if not name.endswith("/")}
    return _check_entries(
        names,
        ALLOWED_TSDECOMP_WHEEL,
        BANNED_COMMON,
        path,
        required=REQUIRED_NEURAL_BLOCK_WHEEL,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate built wheel and sdist contents.")
    parser.add_argument("artifacts", nargs="+", help="Paths to built .whl or .tar.gz artifacts")
    args = parser.parse_args(argv)

    expanded_artifacts: list[str] = []
    for pattern in args.artifacts:
        matches = sorted(glob.glob(pattern))
        if matches:
            expanded_artifacts.extend(matches)
        else:
            expanded_artifacts.append(pattern)

    failures: list[str] = []
    for artifact in expanded_artifacts:
        if artifact.endswith(".whl"):
            failures.extend(_inspect_wheel(artifact))
        elif artifact.endswith(".tar.gz"):
            failures.extend(_inspect_sdist(artifact))
        else:
            failures.append(f"{artifact}: unsupported artifact type")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    for artifact in expanded_artifacts:
        print(f"checked {artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
