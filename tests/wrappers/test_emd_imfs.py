# SPDX-License-Identifier: BSD-3-Clause
"""EMD must return its IMFs, not only the grouped trend/season/residual."""
from __future__ import annotations

import numpy as np
import pytest

from detime import DecompositionConfig, decompose
from detime.methods import emd


def _two_tones(length: int = 512) -> np.ndarray:
    t = np.arange(length, dtype=float)
    return np.sin(2 * np.pi * t / 64) + 0.5 * np.sin(2 * np.pi * t / 8) + 0.002 * t


def test_emd_returns_backend_imfs_in_mode_time_channel_layout(monkeypatch):
    class FakeEMD:
        def emd(self, y, max_imf=None):
            arr = np.asarray(y, dtype=float)
            return np.vstack([0.6 * arr, 0.3 * arr, 0.1 * arr])

    monkeypatch.setattr(emd, "_HAS_PYEMD", True)
    monkeypatch.setattr(emd, "EMD", FakeEMD, raising=False)
    y = _two_tones(96)
    result = decompose(y, DecompositionConfig(method="EMD", params={"primary_period": 8}))

    imfs = result.components["imfs"]
    assert imfs.shape == (3, len(y), 1)
    assert result.meta["component_layouts"]["imfs"] == "mode,time,channel"
    np.testing.assert_array_equal(imfs[:, :, 0], np.vstack([0.6 * y, 0.3 * y, 0.1 * y]))
    np.testing.assert_allclose(result.trend + result.season + result.residual, y, atol=1e-14)


def test_emd_imfs_match_pyemd_and_reconstruct_the_input():
    upstream = pytest.importorskip("PyEMD")
    y = _two_tones()
    expected = np.asarray(upstream.EMD().emd(y), dtype=float)

    result = decompose(y, DecompositionConfig(method="EMD", params={"primary_period": 64}))

    imfs = result.components["imfs"]
    assert imfs.shape == (expected.shape[0], len(y), 1)
    np.testing.assert_allclose(imfs[:, :, 0], expected, rtol=0, atol=1e-12)
    # EMD is complete: the IMFs (with the final residue row) sum to the input.
    np.testing.assert_allclose(imfs[:, :, 0].sum(axis=0), y, atol=1e-10)
    # The fastest IMF carries the period-8 tone.
    assert abs(result.meta["dominant_frequencies"][0] - 1 / 8) < 1 / len(y)
