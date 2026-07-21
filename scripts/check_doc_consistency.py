# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

BANNED_PATTERNS: dict[str, list[str]] = {
    "docs/comparisons.md": ["not erase them", "What DeTime does not claim"],
}

REQUIRED_PATTERNS: dict[str, list[str]] = {
    "README.md": [
        'python -m pip install "git+https://github.com/systems-mechanobiology/DeTime.git"',
        "examples/notebooks/de_time_method_gallery.ipynb",
        "docs/method-matrix.md",
        "detime schema",
        "detime recommend",
    ],
    "docs/install.md": [
        "python -m pip install detime-toolkit",
        'python -m pip install "git+https://github.com/systems-mechanobiology/DeTime.git"',
        "tsdecomp` executable",
    ],
    "docs/notebook-gallery.md": ["de_time_method_gallery.ipynb", "generate_notebook_gallery.py"],
    "docs/method-matrix.md": ["Required/common params", "Optional deps", "Output components"],
    "docs/config-reference.md": ["Top-level fields", "Method-specific parameters", "Univariate SSA"],
    "docs/reproducibility.md": [
        "selected `detime` core algorithm contract",
        "release_smoke_matrix.py",
        "generate_performance_snapshot.py",
    ],
    "docs/comparisons.md": ["PySDKit", "SSALib", "sktime"],
    "docs/tutorials/visual-univariate.md": ["$env:PYTHONPATH='src'", "python examples/visual_univariate_walkthrough.py"],
    "docs/tutorials/visual-multivariate.md": ["$env:PYTHONPATH='src'", "python examples/visual_multivariate_walkthrough.py"],
    "docs/tutorials/visual-comparison.md": ["$env:PYTHONPATH='src'", "python examples/visual_method_comparison.py"],
    "docs/tutorials/quant-trading.md": [
        "examples/notebooks/quant_trading/",
        "examples/quant_trading/requirements.txt",
        "captured outputs directly",
        "quant-trading/notebooks/01_market_data_and_decomposition_feature_factory.md",
    ],
    "docs/tutorials/hot-trend-lab.md": [
        "examples/notebooks/hot_trends/",
        "source coverage, freshness, query context",
        "captured outputs directly",
        "hot-trend-lab/notebooks/01_arxiv_category_pulse.md",
    ],
    "docs/tutorials/quant-trading/notebooks/01_market_data_and_decomposition_feature_factory.md": [
        "Executed tutorial notebook",
        "notebook-cell",
        "notebook-output",
        "```python",
    ],
    "docs/tutorials/quant-trading/notebooks/index.md": [
        "Quant Trading Tutorial Notebooks",
        "code cells, stdout, tables",
        "01_market_data_and_decomposition_feature_factory.md",
    ],
    "docs/tutorials/hot-trend-lab/notebooks/03_huggingface_open_model_pulse.md": [
        "Executed tutorial notebook",
        "notebook-cell",
        "notebook-output",
        "```python",
    ],
    "docs/tutorials/hot-trend-lab/notebooks/index.md": [
        "Hot Trend Lab Notebooks",
        "code cells, stdout, tables",
        "01_arxiv_category_pulse.md",
    ],
    "docs/tutorials/hot-trend-lab/data-sources.md": ["Source registry", "Source snapshot rules"],
}

PUBLIC_DOCS = [
    "README.md",
    "docs/index.md",
    "docs/why.md",
    "docs/install.md",
    "docs/comparisons.md",
    "docs/methods.md",
    "docs/method-matrix.md",
    "docs/config-reference.md",
    "docs/notebook-gallery.md",
    "docs/tutorials/quant-trading.md",
    "docs/tutorials/hot-trend-lab.md",
    "docs/tutorials/hot-trend-lab/data-sources.md",
    "docs/api.md",
]

PUBLIC_BENCHMARK_BANS = [
    "visual-benchmark",
    "leaderboard walkthrough",
    "Benchmark heatmap walkthrough",
]

TUTORIAL_PLACEHOLDER_BANS = {
    "docs/tutorials/cli-and-profiling.md": [
        "data/monthly.csv",
        "data/panel.csv",
        "data/*.csv",
    ],
}

POSIX_ONLY_VISUAL_BANS = {
    "docs/tutorials/visual-univariate.md": [
        "PYTHONPATH=src python3",
    ],
    "docs/tutorials/visual-multivariate.md": [
        "PYTHONPATH=src python3",
    ],
    "docs/tutorials/visual-comparison.md": [
        "PYTHONPATH=src python3",
    ],
}

NEW_COLUMN_LINK_BANS = {
    "docs/tutorials/hot-trend-lab.md": [
        'href="hot-trend-lab/',
    ],
}

DOC_INDEX_PATH_CHECKS = [
    "DOCS_INDEX.md",
]

DISTRIBUTION_BANS = {
    "README.md": [
        "pip install de-time",
        "de-time[",
    ],
    "docs/install.md": [
        "pip install de-time",
        "de-time[",
    ],
    "docs/quickstart.md": [
        "pip install de-time",
        "de-time[",
    ],
}


def _check_patterns(path: Path, patterns: list[str], *, expect_present: bool) -> list[str]:
    if not path.exists():
        if expect_present:
            return [f"{path}: required file missing"]
        return []
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    for pattern in patterns:
        found = pattern in text
        if expect_present and not found:
            failures.append(f"{path}: required pattern missing: {pattern}")
        if not expect_present and found:
            failures.append(f"{path}: banned pattern present: {pattern}")
    return failures


def _check_backticked_repo_paths(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    for candidate in re.findall(r"`([^`\n]+)`", text):
        if "://" in candidate or "*" in candidate:
            continue
        if "/" not in candidate:
            continue
        repo_path = ROOT / candidate
        if not repo_path.exists():
            failures.append(f"{path}: referenced path does not exist: {candidate}")
    return failures


def _check_release_evidence_alignment() -> list[str]:
    failures: list[str] = []
    coverage_summary = json.loads(
        (ROOT / "docs" / "assets" / "generated" / "evidence" / "coverage_summary.json").read_text(
            encoding="utf-8"
        )
    )
    test_result = str(coverage_summary["tests"]["result"])
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if test_result not in readme:
        failures.append(f"README.md: unit-test badge/text does not include coverage_summary result: {test_result}")

    core_denominator = str(coverage_summary["coverage"]["core_surface"]["denominator"])
    if "core-plus-maintained" in core_denominator:
        failures.append("coverage_summary.json: stale core-plus-maintained denominator wording")

    comparison = json.loads(
        (ROOT / "docs" / "assets" / "generated" / "evidence" / "comparison_evidence.json").read_text(
            encoding="utf-8"
        )
    )
    sktime_rows = [
        row
        for row in comparison.get("machine_contract_matrix", [])
        if row.get("package") == "sktime"
    ]
    if sktime_rows and sktime_rows[0].get("machine_readable_catalog") == "no":
        failures.append("comparison_evidence.json: sktime has a runtime estimator registry; do not mark catalog as plain no")

    performance_json_path = ROOT / "docs" / "assets" / "generated" / "evidence" / "performance_snapshot.json"
    performance_csv_path = ROOT / "docs" / "assets" / "generated" / "evidence" / "performance_snapshot.csv"
    performance = json.loads(performance_json_path.read_text(encoding="utf-8"))
    if performance.get("summary_statistic") != "median_ms":
        failures.append("performance_snapshot.json: summary_statistic must be median_ms")
    if "GABOR_CLUSTER" not in performance.get("experimental_excluded_by_default", []):
        failures.append("performance_snapshot.json: GABOR_CLUSTER must be excluded from default release evidence")
    for row in performance.get("summary", []):
        if row.get("method") == "GABOR_CLUSTER":
            failures.append("performance_snapshot.json: GABOR_CLUSTER appears in default summary")
        if "python_median_ms" not in row or "native_median_ms" not in row:
            failures.append(f"performance_snapshot.json: median runtime fields missing for {row.get('method')}")
        if int(row.get("repeat", 0)) < 50 or int(row.get("warmup", 0)) < 10:
            failures.append(f"performance_snapshot.json: insufficient repeat/warmup for {row.get('method')}")

    with performance_csv_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        expected_fields = ["method", "python_median_ms", "native_median_ms", "speedup", "repeat", "warmup"]
        if reader.fieldnames != expected_fields:
            failures.append(f"performance_snapshot.csv: expected header {expected_fields}, got {reader.fieldnames}")
        for row in reader:
            if row.get("method") == "GABOR_CLUSTER":
                failures.append("performance_snapshot.csv: GABOR_CLUSTER appears in default summary")

    method_runtime = json.loads(
        (ROOT / "docs" / "assets" / "generated" / "evidence" / "method_runtime_matrix.json").read_text(
            encoding="utf-8"
        )
    )
    if "GABOR_CLUSTER" not in method_runtime.get("experimental_excluded_by_default", []):
        failures.append("method_runtime_matrix.json: GABOR_CLUSTER must be excluded by default")
    if any(row.get("method") == "GABOR_CLUSTER" for row in method_runtime.get("rows", [])):
        failures.append("method_runtime_matrix.json: GABOR_CLUSTER appears in default runtime rows")
    return failures


def _check_release_identity() -> list[str]:
    failures: list[str] = []
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"\s*$', pyproject, flags=re.MULTILINE)
    if match is None:
        return ["pyproject.toml: project version could not be read"]
    version = match.group(1)

    expected = {
        "README.md": [f"release%20target-{version}", f"reviewed release version is `{version}`"],
        "CITATION.cff": [f'version: "{version}"'],
        "CHANGELOG.md": [f"## [{version}]"],
        "src/detime/_metadata.py": [f'FALLBACK_VERSION = "{version}"'],
        "docs/method-cards.md": [f"Current package version target: `{version}`."],
        "docs/method-matrix.md": [f"Current package version target: `{version}`."],
        "docs/method-references.md": [f"Current package version target: `{version}`."],
        "docs/config-reference.md": [f"Current package version target: `{version}`."],
    }
    for relative_path, patterns in expected.items():
        failures.extend(_check_patterns(ROOT / relative_path, patterns, expect_present=True))
    return failures


def main() -> int:
    failures: list[str] = []

    for relative_path, patterns in BANNED_PATTERNS.items():
        path = ROOT / relative_path
        failures.extend(_check_patterns(path, patterns, expect_present=False))

    for relative_path, patterns in REQUIRED_PATTERNS.items():
        path = ROOT / relative_path
        failures.extend(_check_patterns(path, patterns, expect_present=True))

    for relative_path in PUBLIC_DOCS:
        path = ROOT / relative_path
        failures.extend(_check_patterns(path, PUBLIC_BENCHMARK_BANS, expect_present=False))

    for relative_path, patterns in TUTORIAL_PLACEHOLDER_BANS.items():
        path = ROOT / relative_path
        failures.extend(_check_patterns(path, patterns, expect_present=False))

    for relative_path, patterns in POSIX_ONLY_VISUAL_BANS.items():
        path = ROOT / relative_path
        failures.extend(_check_patterns(path, patterns, expect_present=False))

    for relative_path, patterns in NEW_COLUMN_LINK_BANS.items():
        path = ROOT / relative_path
        failures.extend(_check_patterns(path, patterns, expect_present=False))

    for relative_path, patterns in DISTRIBUTION_BANS.items():
        path = ROOT / relative_path
        failures.extend(_check_patterns(path, patterns, expect_present=False))

    for relative_path in DOC_INDEX_PATH_CHECKS:
        path = ROOT / relative_path
        failures.extend(_check_backticked_repo_paths(path))

    failures.extend(_check_release_evidence_alignment())
    failures.extend(_check_release_identity())

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("documentation consistency checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
