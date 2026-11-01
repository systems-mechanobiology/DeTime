# SPDX-License-Identifier: BSD-3-Clause
"""VMD centre-frequency units and odd-length input, checked on known tones."""
from __future__ import annotations

import numpy as np
import pytest

from detime import DecompositionConfig, decompose, native_capabilities

FS = 0.5  # samples per second, e.g. a 2 s sampling interval
TONES = (0.03, 0.2)  # cycles per second; exact FFT bins at length 400
AMPLITUDES = (1.0, 0.6)


def _two_tones(length: int) -> np.ndarray:
    t = np.arange(length, dtype=float) / FS
    return sum(a * np.sin(2 * np.pi * f * t) for f, a in zip(TONES, AMPLITUDES))


def _backends():
    native = pytest.mark.skipif(
        not native_capabilities().get("vmd_decompose", False),
        reason="VMD native kernel is unavailable in this environment.",
    )
    return ["python", pytest.param("native", marks=native)]


def _vmd(y: np.ndarray, backend: str):
    if backend == "python":
        pytest.importorskip("vmdpy")
    params = {"K": 2, "alpha": 2000.0, "init": 1, "fs": FS}
    return decompose(y, DecompositionConfig(method="VMD", params=params, backend=backend))


def _modes_by_frequency(result) -> np.ndarray:
    return result.components["modes"][np.argsort(result.meta["center_frequencies"])]


@pytest.mark.parametrize("backend", _backends())
def test_vmd_center_frequencies_are_in_sampling_frequency_units(backend):
    result = _vmd(_two_tones(400), backend)

    center = np.sort(result.meta["center_frequencies"])
    dominant = np.sort(result.meta["dominant_frequencies"])
    # Same unit as fs and as the FFT-peak dominant_frequencies: cycles per
    # unit time (Hz when fs is in Hz), not cycles/sample divided by 2*pi.
    np.testing.assert_allclose(dominant, TONES, rtol=1e-12)
    np.testing.assert_allclose(center, TONES, rtol=0.02)
    assert result.meta["padded_samples"] == 0


@pytest.mark.parametrize("backend", _backends())
@pytest.mark.parametrize("length", [401, 97])
def test_vmd_accepts_odd_length_series(backend, length):
    y = _two_tones(length)
    result = _vmd(y, backend)

    assert result.trend.shape == result.season.shape == result.residual.shape == (length,)
    assert result.components["modes"].shape == (2, length)
    assert result.meta["padded_samples"] == 1
    np.testing.assert_allclose(result.trend + result.season + result.residual, y, atol=1e-12)
    np.testing.assert_allclose(np.sort(result.meta["center_frequencies"]), TONES, rtol=0.02)

    modes = _modes_by_frequency(result)
    t = np.arange(length, dtype=float) / FS
    for mode, freq, amp in zip(modes, TONES, AMPLITUDES):
        assert np.corrcoef(mode, amp * np.sin(2 * np.pi * freq * t))[0, 1] > 0.97

    # No sample is dropped or shifted: away from the boundaries, the modes
    # agree with those of the even-length series without the final sample.
    # A one-sample shift would move the 0.2 Hz mode by about 1.1 here.
    even = _modes_by_frequency(_vmd(y[:-1], backend))
    np.testing.assert_allclose(modes[:, 20:-21], even[:, 20:-20], atol=0.06)
