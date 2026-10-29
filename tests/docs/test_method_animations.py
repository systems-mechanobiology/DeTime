# SPDX-License-Identifier: BSD-3-Clause
"""Acceptance checks for the educational artifact boundary, without backends."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image

from detime import MethodRegistry


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "docs/assets/generated/method-animations"


def test_every_registered_method_has_a_readable_animation_and_source_arrays():
    manifest = json.loads((ASSETS / "manifest.json").read_text(encoding="utf-8"))
    rows = manifest["methods"]
    assert {row["method"] for row in rows} == {entry["name"] for entry in MethodRegistry.list_catalog()}
    assert len(rows) == len({row["method"] for row in rows})
    for row in rows:
        for artifact in row["artifacts"].values():
            path = ASSETS / artifact["file"]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == artifact["sha256"]
        with Image.open(ASSETS / row["artifacts"]["gif"]["file"]) as gif:
            assert gif.n_frames >= 16
            assert gif.size == (1280, 820)
            # The plot area must change, independently of the header/progress bar.
            visible_states = set()
            for index in [0, gif.n_frames // 3, 2 * gif.n_frames // 3, gif.n_frames - 1]:
                gif.seek(index)
                pixels = gif.convert("RGB").crop((50, 175, 1250, 685)).tobytes()
                visible_states.add(hashlib.sha256(pixels).hexdigest())
            assert len(visible_states) >= 3, row["method"]
        with np.load(ASSETS / row["artifacts"]["data"]["file"], allow_pickle=False) as arrays:
            assert arrays.files
            for name in arrays.files:
                assert np.isfinite(arrays[name]).all(), (row["method"], name)


def test_explanations_survive_static_markdown_and_cover_alias_scope():
    rows = json.loads((ASSETS / "manifest.json").read_text(encoding="utf-8"))["methods"]
    for row in rows:
        page = (ROOT / "docs/gallery" / f"{row['slug']}.md").read_text(encoding="utf-8")
        assert "## How it works" in page
        assert f"{row['slug']}.gif" in page
        assert f"{row['slug']}.png" in page
        assert f"{row['slug']}.npz" in page
        assert "### Follow the four steps" in page
        assert "### What this animation computes" in page
        assert len(row["steps"]) == 4
        assert row["references"] and row["trace_note"]
    by_name = {row["method"]: row for row in rows}
    assert "untrained" in json.dumps(by_name["NBEATS_INTERPRETABLE"]).lower()
    for name in ["AUTOFORMER_BLOCK", "DLINEAR_BLOCK"]:
        assert "MOVING_AVERAGE_DECOMPOSITION_BLOCK" in json.dumps(by_name[name])


def test_assembly_cannot_relabel_stale_assets_with_current_source_hashes(tmp_path):
    rows = json.loads((ASSETS / "manifest.json").read_text(encoding="utf-8"))["methods"]
    for index, row in enumerate(rows):
        if index == 0:
            hashes = row["render_provenance"]["source_hashes"]
            hashes[next(iter(hashes))] = "0" * 64
        (tmp_path / f"{row['slug']}.json").write_text(json.dumps(row), encoding="utf-8")
    # The CLI selects repository sources by clearing imported detime modules.
    # Keep that setup in a child process so existing class identities and
    # monkeypatch targets in the test runner remain intact.
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/generate_method_animations.py"),
         "--assemble", "--no-docs", "--output-dir", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True, timeout=60, check=False,
    )
    assert result.returncode != 0, result.stdout + result.stderr
    assert "Cannot assemble stale animation assets" in result.stderr, result.stderr
    assert not (tmp_path / "manifest.json").exists()
