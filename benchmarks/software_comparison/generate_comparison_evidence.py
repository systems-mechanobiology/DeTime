# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import argparse
import csv
import json
from datetime import date, datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from _repo_source import prefer_repo_source

prefer_repo_source(ROOT)

from detime import __version__

OUTPUT_DIR = ROOT / "docs" / "assets" / "generated" / "evidence"
DEFAULT_RELEASE_STATE = "local-unverified"
RELEASE_STATES = (DEFAULT_RELEASE_STATE, "verified-public")
COMPARATOR_VERSIONS = {
    "statsmodels": "0.14.6",
    "PyEMD/EMD-signal": "not installed in local audit environment",
    "PyWavelets": "1.9.0",
    "PySDKit": "0.4.25",
    "SSALib": "not installed in local audit environment",
    "sktime": "not installed in local audit environment",
}


CAPABILITY_MATRIX = [
    {
        "package": "DeTime",
        "primary_scope": "standalone cross-family time-series decomposition",
        "unified_config_object": "yes",
        "unified_result_object": "yes",
        "machine_readable_catalog": "yes",
        "batch_cli": "yes",
        "profiling_path": "yes",
        "multivariate_support": "yes",
        "maturity_labeling": "explicit",
        "compact_output": "yes",
    },
    {
        "package": "statsmodels",
        "primary_scope": "classical decomposition and modeling",
        "unified_config_object": "per-method constructors",
        "unified_result_object": "shared for STL/MSTL",
        "machine_readable_catalog": "library metadata",
        "batch_cli": "library API",
        "profiling_path": "external tooling",
        "multivariate_support": "limited",
        "maturity_labeling": "implicit",
        "compact_output": "method result",
    },
    {
        "package": "PyEMD",
        "primary_scope": "EMD-family toolkit",
        "unified_config_object": "family classes",
        "unified_result_object": "IMF arrays",
        "machine_readable_catalog": "method state",
        "batch_cli": "library API",
        "profiling_path": "external tooling",
        "multivariate_support": "family-specific",
        "maturity_labeling": "family-specific",
        "compact_output": "IMF arrays",
    },
    {
        "package": "PyWavelets",
        "primary_scope": "wavelet toolkit",
        "unified_config_object": "function arguments",
        "unified_result_object": "coefficient trees",
        "machine_readable_catalog": "transform metadata",
        "batch_cli": "library API",
        "profiling_path": "external tooling",
        "multivariate_support": "transform-specific",
        "maturity_labeling": "family-specific",
        "compact_output": "coefficients",
    },
    {
        "package": "PySDKit",
        "primary_scope": "signal decomposition toolkit",
        "unified_config_object": "method-family classes",
        "unified_result_object": "method-specific",
        "machine_readable_catalog": "method documentation",
        "batch_cli": "library API",
        "profiling_path": "external tooling",
        "multivariate_support": "yes",
        "maturity_labeling": "less explicit",
        "compact_output": "method-specific",
    },
    {
        "package": "SSALib",
        "primary_scope": "SSA specialist toolkit",
        "unified_config_object": "SSA-specific",
        "unified_result_object": "SSA-specific",
        "machine_readable_catalog": "SSA metadata",
        "batch_cli": "library API",
        "profiling_path": "external tooling",
        "multivariate_support": "no",
        "maturity_labeling": "focused",
        "compact_output": "SSA results",
    },
    {
        "package": "sktime",
        "primary_scope": "broad time-series ecosystem",
        "unified_config_object": "estimator parameters",
        "unified_result_object": "task-specific",
        "machine_readable_catalog": "runtime estimator registry",
        "batch_cli": "library API",
        "profiling_path": "external tooling",
        "multivariate_support": "partial",
        "maturity_labeling": "ecosystem-level",
        "compact_output": "task-specific",
    },
]

INSTALL_MATRIX = [
    {
        "package": "DeTime",
        "public_release_story": "local source state; publication status unverified",
        "pypi_path": "not verified",
        "github_release": "not verified",
        "wheels": "yes",
        "ci_platforms": "ubuntu, macOS, windows",
        "docs_website": "GitHub Pages",
        "tutorials": "yes",
        "api_docs": "yes",
        "coverage_disclosure": "dual report",
        "reproducibility_script": "yes",
    },
    {
        "package": "statsmodels",
        "public_release_story": "yes",
        "pypi_path": "yes",
        "github_release": "yes",
        "wheels": "yes",
        "ci_platforms": "yes",
        "docs_website": "yes",
        "tutorials": "yes",
        "api_docs": "yes",
        "coverage_disclosure": "project-dependent",
        "reproducibility_script": "project-dependent",
    },
    {
        "package": "PyEMD",
        "public_release_story": "yes",
        "pypi_path": "yes",
        "github_release": "yes",
        "wheels": "partial",
        "ci_platforms": "project-dependent",
        "docs_website": "partial",
        "tutorials": "partial",
        "api_docs": "partial",
        "coverage_disclosure": "project-dependent",
        "reproducibility_script": "no",
    },
    {
        "package": "PyWavelets",
        "public_release_story": "yes",
        "pypi_path": "yes",
        "github_release": "yes",
        "wheels": "yes",
        "ci_platforms": "yes",
        "docs_website": "yes",
        "tutorials": "yes",
        "api_docs": "yes",
        "coverage_disclosure": "project-dependent",
        "reproducibility_script": "no",
    },
    {
        "package": "PySDKit",
        "public_release_story": "yes",
        "pypi_path": "yes",
        "github_release": "yes",
        "wheels": "partial",
        "ci_platforms": "project-dependent",
        "docs_website": "yes",
        "tutorials": "partial",
        "api_docs": "partial",
        "coverage_disclosure": "project-dependent",
        "reproducibility_script": "no",
    },
    {
        "package": "SSALib",
        "public_release_story": "yes",
        "pypi_path": "yes",
        "github_release": "yes",
        "wheels": "partial",
        "ci_platforms": "project-dependent",
        "docs_website": "yes",
        "tutorials": "partial",
        "api_docs": "partial",
        "coverage_disclosure": "project-dependent",
        "reproducibility_script": "no",
    },
    {
        "package": "sktime",
        "public_release_story": "yes",
        "pypi_path": "yes",
        "github_release": "yes",
        "wheels": "yes",
        "ci_platforms": "yes",
        "docs_website": "yes",
        "tutorials": "yes",
        "api_docs": "yes",
        "coverage_disclosure": "project-dependent",
        "reproducibility_script": "project-dependent",
    },
]

FAMILY_FAIRNESS = [
    {
        "family": "classical decomposition",
        "specialist": "statsmodels",
        "specialist_deeper_strength": "deeper classical decomposition and statistical modeling",
        "de_time_position": "wraps STL and MSTL under one config/result/CLI layer",
    },
    {
        "family": "SSA",
        "specialist": "SSALib",
        "specialist_deeper_strength": "deeper SSA-only environment with SSA-specific tooling",
        "de_time_position": "uses SSA as one core method inside a cross-family workflow layer",
    },
    {
        "family": "EMD family",
        "specialist": "PyEMD",
        "specialist_deeper_strength": "deeper EMD-family tooling",
        "de_time_position": "exposes EMD and CEEMDAN through the same contract used for other families",
    },
    {
        "family": "wavelet workflows",
        "specialist": "PyWavelets",
        "specialist_deeper_strength": "deeper wavelet transforms and transform-specific APIs",
        "de_time_position": "uses wavelets as one workflow option rather than a wavelet-first toolkit",
    },
    {
        "family": "unified toolkit layer",
        "specialist": "PySDKit",
        "specialist_deeper_strength": "broader signal-decomposition toolkit with optional multivariate backends",
        "de_time_position": "focuses on time-series decomposition workflows, machine-facing contracts, and compact outputs",
    },
]

MACHINE_CONTRACT_MATRIX = [
    {
        "package": "DeTime",
        "json_schema_assets": "yes",
        "compact_result_modes": "full/summary/meta",
        "metadata_shortlist_interface": "yes",
        "machine_readable_catalog": "yes",
        "cli_schema_command": "yes",
        "artifact_contract": "yes",
    },
    {
        "package": "statsmodels",
        "json_schema_assets": "no",
        "compact_result_modes": "no",
        "metadata_shortlist_interface": "no",
        "machine_readable_catalog": "no",
        "cli_schema_command": "no",
        "artifact_contract": "no",
    },
    {
        "package": "PyEMD",
        "json_schema_assets": "no",
        "compact_result_modes": "no",
        "metadata_shortlist_interface": "no",
        "machine_readable_catalog": "no",
        "cli_schema_command": "no",
        "artifact_contract": "no",
    },
    {
        "package": "PyWavelets",
        "json_schema_assets": "no",
        "compact_result_modes": "no",
        "metadata_shortlist_interface": "no",
        "machine_readable_catalog": "no",
        "cli_schema_command": "no",
        "artifact_contract": "no",
    },
    {
        "package": "PySDKit",
        "json_schema_assets": "no",
        "compact_result_modes": "no",
        "metadata_shortlist_interface": "no",
        "machine_readable_catalog": "no",
        "cli_schema_command": "no",
        "artifact_contract": "no",
    },
    {
        "package": "SSALib",
        "json_schema_assets": "no",
        "compact_result_modes": "no",
        "metadata_shortlist_interface": "no",
        "machine_readable_catalog": "no",
        "cli_schema_command": "no",
        "artifact_contract": "no",
    },
    {
        "package": "sktime",
        "json_schema_assets": "no",
        "compact_result_modes": "no",
        "metadata_shortlist_interface": "no",
        "machine_readable_catalog": "yes-runtime-registry",
        "cli_schema_command": "no",
        "artifact_contract": "no",
    },
]


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _iso_date(value: str) -> str:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"invalid ISO date {value!r}; expected YYYY-MM-DD"
        ) from exc
    if parsed.isoformat() != value:
        raise argparse.ArgumentTypeError(
            f"invalid ISO date {value!r}; expected YYYY-MM-DD"
        )
    return value


def _resolve_audit_date(
    explicit_date: str | None,
    *,
    today: date | None = None,
) -> tuple[str, str]:
    if explicit_date is not None:
        return explicit_date, "explicit"
    current_date = today or datetime.now(timezone.utc).date()
    return current_date.isoformat(), "utc-current"


def _build_install_matrix(
    release_state: str,
    *,
    version: str = __version__,
) -> list[dict[str, object]]:
    if release_state not in RELEASE_STATES:
        choices = ", ".join(RELEASE_STATES)
        raise ValueError(f"unknown release state {release_state!r}; choose from {choices}")

    rows = [row.copy() for row in INSTALL_MATRIX]
    detime_release = rows[0]
    if release_state == "verified-public":
        detime_release.update(
            {
                "public_release_story": f"{version} verified public PyPI/GitHub release",
                "pypi_path": "detime-toolkit",
                "github_release": f"de-time-v{version}",
            }
        )
    else:
        detime_release.update(
            {
                "public_release_story": (
                    f"{version} local source state; publication status unverified"
                ),
                "pypi_path": "not verified",
                "github_release": "not verified",
            }
        )
    return rows


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the curated software-comparison evidence bundle."
    )
    parser.add_argument(
        "--release-state",
        choices=RELEASE_STATES,
        default=DEFAULT_RELEASE_STATE,
        help=(
            "DeTime release state. The safe default is local-unverified; select "
            "verified-public only after the matching PyPI and GitHub releases have "
            "been checked."
        ),
    )
    parser.add_argument(
        "--audit-date",
        type=_iso_date,
        help=(
            "Audit date in YYYY-MM-DD form. If omitted, the current UTC date is "
            "recorded explicitly in the output."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Output directory (defaults to the committed evidence directory).",
    )
    return parser.parse_args(argv)


def _markdown_table(rows: list[dict[str, object]]) -> list[str]:
    headers = list(rows[0].keys())
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[key]) for key in headers) + " |")
    return lines


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    audit_date, audit_date_source = _resolve_audit_date(args.audit_date)
    install_matrix = _build_install_matrix(args.release_state)
    runtime_snapshot_csv = OUTPUT_DIR / "performance_snapshot.csv"

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "release_target_version": __version__,
        "release_state": args.release_state,
        "evidence_type": "curated feature audit",
        "audit_date": audit_date,
        "audit_date_source": audit_date_source,
        "comparator_versions": COMPARATOR_VERSIONS,
        "runtime_memory_boundary": "Feature audit only; no cross-package runtime or peak-memory ranking is claimed.",
        "capability_matrix": CAPABILITY_MATRIX,
        "install_matrix": install_matrix,
        "family_fairness": FAMILY_FAIRNESS,
        "machine_contract_matrix": MACHINE_CONTRACT_MATRIX,
        "runtime_snapshot_csv": str(runtime_snapshot_csv.relative_to(ROOT)),
    }

    json_path = output_dir / "comparison_evidence.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_csv(output_dir / "comparison_capability_matrix.csv", CAPABILITY_MATRIX)
    _write_csv(output_dir / "comparison_install_matrix.csv", install_matrix)
    _write_csv(output_dir / "comparison_family_fairness.csv", FAMILY_FAIRNESS)
    _write_csv(output_dir / "comparison_machine_contract_matrix.csv", MACHINE_CONTRACT_MATRIX)

    markdown_lines = [
        "# Curated Comparison Evidence",
        "",
        f"Curated for DeTime `{__version__}` on {payload['generated_at']}.",
        "",
        f"Release state: `{args.release_state}`.",
        "",
        f"Audit date: {audit_date} ({audit_date_source}).",
        "",
        "Comparator versions:",
        "",
        *[f"- {name}: {version}" for name, version in COMPARATOR_VERSIONS.items()],
        "",
        "Runtime and memory boundary: feature audit only; no cross-package runtime or peak-memory ranking is claimed.",
        "",
        "## Capability matrix",
        "",
        *_markdown_table(CAPABILITY_MATRIX),
        "",
        "## Install and reproducibility matrix",
        "",
        *_markdown_table(install_matrix),
        "",
        "## Family-fairness notes",
        "",
        *_markdown_table(FAMILY_FAIRNESS),
        "",
        "## Machine-contract matrix",
        "",
        *_markdown_table(MACHINE_CONTRACT_MATRIX),
        "",
        "## Runtime snapshot source",
        "",
        f"- `{runtime_snapshot_csv.relative_to(ROOT)}`",
        "",
    ]
    (output_dir / "comparison_evidence.md").write_text(
        "\n".join(markdown_lines).strip() + "\n",
        encoding="utf-8",
    )
    print(f"wrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
