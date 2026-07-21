# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "benchmarks" / "software_comparison" / "generate_comparison_evidence.py"


def _run_generator(output_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(GENERATOR),
            "--output-dir",
            str(output_dir),
            *args,
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def _load_payload(output_dir: Path) -> dict[str, object]:
    return json.loads((output_dir / "comparison_evidence.json").read_text(encoding="utf-8"))


def _detime_install_row(payload: dict[str, object]) -> dict[str, object]:
    rows = payload["install_matrix"]
    assert isinstance(rows, list)
    return next(row for row in rows if row["package"] == "DeTime")


def test_default_release_state_does_not_claim_a_public_release(tmp_path: Path) -> None:
    result = _run_generator(tmp_path, "--audit-date", "2026-07-14")

    assert result.returncode == 0, result.stderr
    payload = _load_payload(tmp_path)
    row = _detime_install_row(payload)
    assert payload["release_state"] == "local-unverified"
    assert payload["audit_date"] == "2026-07-14"
    assert payload["audit_date_source"] == "explicit"
    assert "verified public" not in row["public_release_story"]
    assert row["pypi_path"] == "not verified"
    assert row["github_release"] == "not verified"


def test_only_verified_public_state_emits_public_release_identifiers(tmp_path: Path) -> None:
    result = _run_generator(
        tmp_path,
        "--release-state",
        "verified-public",
        "--audit-date",
        "2026-07-14",
    )

    assert result.returncode == 0, result.stderr
    payload = _load_payload(tmp_path)
    row = _detime_install_row(payload)
    version = payload["release_target_version"]
    assert payload["release_state"] == "verified-public"
    assert row["public_release_story"] == (
        f"{version} verified public PyPI/GitHub release"
    )
    assert row["pypi_path"] == "detime-toolkit"
    assert row["github_release"] == f"de-time-v{version}"


def test_omitted_audit_date_records_current_utc_date(tmp_path: Path) -> None:
    before = datetime.now(timezone.utc).date().isoformat()
    result = _run_generator(tmp_path)
    after = datetime.now(timezone.utc).date().isoformat()

    assert result.returncode == 0, result.stderr
    payload = _load_payload(tmp_path)
    assert payload["audit_date"] in {before, after}
    assert payload["audit_date_source"] == "utc-current"


def test_invalid_audit_date_fails_clearly_without_writing_outputs(tmp_path: Path) -> None:
    result = _run_generator(tmp_path, "--audit-date", "14-07-2026")

    assert result.returncode == 2
    assert "invalid ISO date" in result.stderr
    assert not (tmp_path / "comparison_evidence.json").exists()
