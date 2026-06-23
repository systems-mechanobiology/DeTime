from __future__ import annotations

import json
from pathlib import Path

from detime import __version__


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "docs" / "assets" / "generated" / "evidence"
OUTPUT_DIR = ROOT / "submission" / "reviewer_bundle"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    coverage_summary = _read_json(EVIDENCE_DIR / "coverage_summary.json")
    runtime_snapshot = _read_json(EVIDENCE_DIR / "performance_snapshot.json")

    review_matrix = "\n".join(
        [
            "# Software Matrix",
            "",
            f"Generated for release target `{__version__}`.",
            "",
            "| Axis | DeTime |",
            "| --- | --- |",
            "| Primary scope | workflow-oriented decomposition layer |",
            "| Common config object | yes |",
            "| Common result object | yes |",
            "| Machine-readable catalog | yes |",
            "| Batch CLI | yes |",
            "| Profiling path | yes |",
            "| Multivariate support | yes |",
            "| Maturity labeling | explicit |",
            "| Compact result modes | full / summary / meta |",
            "| Machine contract | schemas, compact result views, metadata shortlist, optional local MCP |",
            "",
            "Reference evidence: `docs/assets/generated/evidence/comparison_evidence.json`.",
            "",
        ]
    )

    install_verification = "\n".join(
        [
            "# Install Verification",
            "",
            f"- Release target: `{__version__}`",
            "- Current source install path: `python -m pip install \"git+https://github.com/systems-mechanobiology/DeTime.git\"`",
            "- Planned PyPI install path after release: `pip install de-time`",
            "- Release state: publish from `main` via the release workflow, then run post-publish smoke verification.",
            "- Release smoke script: `scripts/release_smoke_matrix.py`",
            "- Wheel/sdist validation: `scripts/check_dist_contents.py` and `python -m twine check dist/*`",
            "",
        ]
    )

    testing_and_coverage = "\n".join(
        [
            "# Testing and Coverage",
            "",
            "- Core-surface coverage: gated via `.coveragerc` and `fail_under = 90`.",
            "- Package-wide coverage: emitted as a second CI artifact with the broader denominator.",
            f"- Core-surface result: `{coverage_summary['coverage']['core_surface']['percent']:.2f}%`.",
            f"- Package-wide result: `{coverage_summary['coverage']['package_wide']['percent']:.2f}%`.",
            "- Runtime snapshot file: `docs/assets/generated/evidence/performance_snapshot.json`.",
            f"- Runtime snapshot methods: {', '.join(row['method'] for row in runtime_snapshot['summary'])}.",
            "",
        ]
    )

    companion_relationship = "\n".join(
        [
            "# Companion Relationship",
            "",
            "- Main package scope: installable decomposition library under `src/detime/`.",
            "- Compatibility scope: top-level `tsdecomp` import and CLI alias only.",
            "- Companion benchmark repository: `systems-mechanobiology/de-time-bench`.",
            "- Benchmark-derived methods are intentionally absent from the installable DeTime package.",
            "- DeTime should be reviewed as software infrastructure, not as a benchmark artifact bundle.",
            "",
        ]
    )

    machine_contract_overview = "\n".join(
        [
            "# Machine Contract Overview",
            "",
            "- Machine contract version: `0.1`.",
            "- Stable schema assets: `config`, `result`, `meta`, `method-registry`.",
            "- Stable CLI surfaces: `detime run`, `detime batch`, `detime profile`, `detime schema`.",
            "- Metadata shortlist surface: `detime recommend`; this is a catalog-based shortlist, not an empirically validated recommender.",
            "- Optional local MCP tools mirror the same schema/result contract for non-interactive use.",
            "",
        ]
    )

    files = {
        "REVIEWER_SOFTWARE_MATRIX.md": review_matrix,
        "INSTALL_VERIFICATION.md": install_verification,
        "TESTING_AND_COVERAGE.md": testing_and_coverage,
        "COMPANION_RELATIONSHIP.md": companion_relationship,
        "MACHINE_CONTRACT_OVERVIEW.md": machine_contract_overview,
    }
    for name, content in files.items():
        (OUTPUT_DIR / name).write_text(content, encoding="utf-8")
    print(f"wrote reviewer bundle to {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
