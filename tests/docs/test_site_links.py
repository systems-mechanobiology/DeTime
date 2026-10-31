# SPDX-License-Identifier: BSD-3-Clause
"""Prevent missing media and cross-page anchors from reaching Pages."""
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("site_link_checks", ROOT / "scripts/check_site_links.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_local_files_fragments_and_encoded_paths(tmp_path):
    (tmp_path / "index.html").write_text(
        '<a href="gallery/#four-steps">Steps</a><img src="static%20image.png">'
        '<a href="https://example.org/unrelated#unknown">External</a>'
    )
    (tmp_path / "gallery").mkdir()
    (tmp_path / "gallery/index.html").write_text('<h1 id="four-steps">Steps</h1>')
    (tmp_path / "static image.png").write_bytes(b"image")
    checked, errors = MODULE.check_site_links(tmp_path)
    assert checked == 2
    assert errors == []


def test_missing_image_and_cross_page_fragment_are_reported(tmp_path):
    (tmp_path / "index.html").write_text('<a href="other.html#absent">More</a><img src="missing.gif">')
    (tmp_path / "other.html").write_text('<h1 id="present">Other</h1>')
    _, errors = MODULE.check_site_links(tmp_path)
    assert len(errors) == 2
    assert any("missing.gif" in error and "missing local target" in error for error in errors)
    assert any("other.html#absent" in error and "missing HTML fragment" in error for error in errors)


def test_absolute_site_asset_and_self_fragment(tmp_path):
    (tmp_path / "index.html").write_text(
        '<h1 id="title">Title</h1><a href="#title">Top</a>'
        '<img src="https://systems-mechanobiology.github.io/DeTime/absent.png">'
    )
    checked, errors = MODULE.check_site_links(tmp_path)
    assert checked == 2
    assert len(errors) == 1 and "absent.png" in errors[0]
