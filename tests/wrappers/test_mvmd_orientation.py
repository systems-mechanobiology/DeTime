# SPDX-License-Identifier: BSD-3-Clause
"""MVMD must receive channels by time before any numerical decomposition."""
from __future__ import annotations

import numpy as np
import pytest

from detime import DecompositionConfig, decompose
from detime.methods import mvmd


def _panel(channels: int, length: int = 96) -> np.ndarray:
    t = np.arange(length, dtype=float)
    return np.column_stack([
        0.003 * (channel + 1) * t
        + (0.9 - 0.12 * channel) * np.sin(2 * np.pi * t / 24 + 0.3 * channel)
        + (0.2 + 0.03 * channel) * np.cos(2 * np.pi * t / 7 - 0.2 * channel)
        for channel in range(channels)
    ])


def _accept_either_layout(signal: np.ndarray) -> np.ndarray:
    """Mimic a backend that always treats its last axis as time.

    Both input orientations are accepted and produce a coercible output shape,
    but temporal averaging makes their numerical results different.
    """
    mean = np.broadcast_to(signal.mean(axis=-1, keepdims=True), signal.shape)
    return np.stack([mean, signal - mean], axis=0).transpose(0, 2, 1)


@pytest.mark.parametrize("channels", [2, 4])
def test_mvmd_passes_channels_by_time_to_a_permissive_backend(monkeypatch, channels):
    calls = []

    class AcceptEitherLayout:
        def __init__(self, **kwargs):
            pass

        def fit_transform(self, signal):
            calls.append(signal.copy())
            return _accept_either_layout(signal)

    monkeypatch.setattr(mvmd, "_load_optional_backend", lambda method: AcceptEitherLayout)
    y = _panel(channels)
    result = decompose(y, DecompositionConfig(method="MVMD", backend="python"))

    assert len(calls) == 1
    np.testing.assert_array_equal(calls[0], y.T)
    expected_mean = np.broadcast_to(y.mean(axis=0), y.shape)
    np.testing.assert_array_equal(result.components["modes"][0], expected_mean)
    np.testing.assert_array_equal(result.components["modes"][1], y - expected_mean)


def test_mvmd_preserves_a_backend_error_without_retrying(monkeypatch):
    calls = []
    solver_error = ValueError("MVMD solver rejected its configuration")

    class FailingSolver:
        def __init__(self, **kwargs):
            pass

        def fit_transform(self, signal):
            calls.append(("fit_transform", signal.shape))
            raise solver_error

        def transform(self, signal):
            calls.append(("transform", signal.shape))
            return _accept_either_layout(signal)

        def __call__(self, signal):
            calls.append(("__call__", signal.shape))
            return _accept_either_layout(signal)

    monkeypatch.setattr(mvmd, "_load_optional_backend", lambda method: FailingSolver)
    y = _panel(2)
    with pytest.raises(ValueError, match="solver rejected") as exc_info:
        decompose(y, DecompositionConfig(method="MVMD", backend="python"))

    assert exc_info.value is solver_error
    assert calls == [("fit_transform", (2, len(y)))]


def test_mvmd_callable_backend_uses_the_same_documented_layout(monkeypatch):
    calls = []

    def backend(signal):
        calls.append(signal.copy())
        return _accept_either_layout(signal)

    monkeypatch.setattr(mvmd, "_load_optional_backend", lambda method: backend)
    y = _panel(2)
    result = decompose(y, DecompositionConfig(method="MVMD", backend="python"))

    assert len(calls) == 1
    np.testing.assert_array_equal(calls[0], y.T)
    np.testing.assert_array_equal(result.components["modes"], _accept_either_layout(y.T))


@pytest.mark.parametrize("channels", [2, 4])
def test_real_pysdkit_matches_a_direct_channels_by_time_call(monkeypatch, channels):
    upstream = pytest.importorskip("pysdkit")
    y = _panel(channels)
    # Bound the real solver without adding undocumented public config keys.
    # All signal processing still runs through PySDKit's fit_transform.
    trace_settings = {"init": "uniform", "tol": 1e-7, "max_iter": 20}

    class BoundedMVMD(upstream.MVMD):
        def __init__(self, **kwargs):
            super().__init__(**kwargs, **trace_settings)

    monkeypatch.setattr(mvmd, "_load_optional_backend", lambda method: BoundedMVMD)
    expected = upstream.MVMD(K=3, alpha=1500.0, tau=0.0, **trace_settings).fit_transform(y.T)
    result = decompose(
        y,
        DecompositionConfig(
            method="MVMD", backend="python",
            params={"K": 3, "alpha": 1500.0, "primary_period": 24},
            channel_names=[f"channel_{channel}" for channel in range(channels)],
        ),
    )

    modes = result.components["modes"]
    assert modes.shape == (3, len(y), channels)
    assert np.isfinite(modes).all()
    np.testing.assert_allclose(modes, expected, rtol=1e-6, atol=1e-7)
    np.testing.assert_allclose(result.trend + result.season + result.residual, y, atol=1e-14)


FS = 0.5  # samples per second, e.g. a 2 s sampling interval
TONES = (0.03, 0.2)  # cycles per second; exact FFT bins at length 500


def _two_tone_panel(channels: int = 6, length: int = 500) -> tuple[np.ndarray, np.ndarray]:
    t = np.arange(length, dtype=float) / FS
    parts = np.stack([
        np.column_stack([
            amp * np.sin(2 * np.pi * freq * t + phase * channel)
            for channel in range(channels)
        ])
        for freq, amp, phase in zip(TONES, (1.0, 0.6), (0.4, -0.3))
    ])
    return parts.sum(axis=0), parts


def _uniform_init_mvmd(upstream):
    # PySDKit's default zero initialization is kept by DeTime; this test
    # subclass only selects the upstream uniform start for a known answer.
    class UniformInitMVMD(upstream.MVMD):
        def __init__(self, **kwargs):
            super().__init__(**kwargs, init="uniform")

    return UniformInitMVMD


def _two_tone_mvmd(monkeypatch):
    upstream = pytest.importorskip("pysdkit")
    monkeypatch.setattr(mvmd, "_load_optional_backend", lambda method: _uniform_init_mvmd(upstream))
    y, parts = _two_tone_panel()
    result = decompose(
        y,
        DecompositionConfig(
            method="MVMD", backend="python",
            params={"K": 2, "alpha": 2000.0, "fs": FS},
        ),
    )
    return y, parts, result


def test_real_pysdkit_documented_layout_recovers_two_tones_in_every_channel(monkeypatch):
    y, parts, result = _two_tone_mvmd(monkeypatch)

    modes = result.components["modes"]
    assert modes.shape == (2, *y.shape)
    order = np.argsort(result.meta["dominant_frequencies"])
    np.testing.assert_allclose(np.asarray(result.meta["dominant_frequencies"])[order], TONES, rtol=1e-12)
    for mode, part in zip(modes[order], parts):
        for channel in range(y.shape[1]):
            assert np.corrcoef(mode[:, channel], part[:, channel])[0, 1] > 0.99


def test_real_pysdkit_center_frequencies_are_reported_in_sampling_units(monkeypatch):
    _, _, result = _two_tone_mvmd(monkeypatch)

    center = np.asarray(result.meta["center_frequencies"])
    assert center.shape == (2,)
    order = np.argsort(result.meta["dominant_frequencies"])
    # Shared solver centres, in the same unit as fs and dominant_frequencies.
    np.testing.assert_allclose(center[order], TONES, rtol=0.02)


def test_mvmd_documented_defaults_reach_the_backend_unchanged(monkeypatch):
    settings = []

    class RecordingMVMD:
        def __init__(self, **kwargs):
            settings.append(kwargs)

        def fit_transform(self, signal):
            return _accept_either_layout(signal)

    monkeypatch.setattr(mvmd, "_load_optional_backend", lambda method: RecordingMVMD)
    decompose(_panel(3), DecompositionConfig(method="MVMD", backend="python"))

    # No initialization override: PySDKit's own default ("zero") applies.
    assert settings == [{"alpha": 2000.0, "K": 3, "tau": 0.0}]


MODE_INDEX_ALIASES = [
    ("trend_imfs", "trend_modes", "trend_components"),
    ("season_imfs", "season_modes", "season_components"),
]


@pytest.mark.parametrize("alias, canonical, meta_key", MODE_INDEX_ALIASES)
def test_mvmd_mode_index_aliases_group_modes_without_reaching_the_backend(
    monkeypatch, alias, canonical, meta_key
):
    settings = []

    class StrictMVMD:
        # PySDKit's MVMD constructor: unknown keywords raise TypeError.
        def __init__(self, alpha, K, tau, init="zero", DC=False, tol=1e-7, max_iter=100):
            settings.append({"alpha": alpha, "K": K, "tau": tau})

        def fit_transform(self, signal):
            return _accept_either_layout(signal)

    monkeypatch.setattr(mvmd, "_load_optional_backend", lambda method: StrictMVMD)
    y = _panel(3)
    by_alias = decompose(y, DecompositionConfig(method="MVMD", backend="python", params={"K": 2, alias: [1]}))
    by_name = decompose(y, DecompositionConfig(method="MVMD", backend="python", params={"K": 2, canonical: [1]}))

    assert settings == [{"alpha": 2000.0, "K": 2, "tau": 0.0}] * 2
    assert by_alias.meta[meta_key] == by_name.meta[meta_key] == [1]
    for part in ("trend", "season", "residual"):
        np.testing.assert_array_equal(getattr(by_alias, part), getattr(by_name, part))


@pytest.mark.parametrize("alias, canonical, meta_key", MODE_INDEX_ALIASES)
def test_real_pysdkit_accepts_documented_mode_index_aliases(alias, canonical, meta_key):
    pytest.importorskip("pysdkit")
    y = _panel(2)
    by_alias = decompose(y, DecompositionConfig(method="MVMD", backend="python", params={"K": 2, alias: [0]}))
    by_name = decompose(y, DecompositionConfig(method="MVMD", backend="python", params={"K": 2, canonical: [0]}))

    assert by_alias.meta[meta_key] == [0]
    np.testing.assert_array_equal(by_alias.components["modes"], by_name.components["modes"])
    for part in ("trend", "season", "residual"):
        np.testing.assert_array_equal(getattr(by_alias, part), getattr(by_name, part))
