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
