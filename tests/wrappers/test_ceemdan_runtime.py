# SPDX-License-Identifier: BSD-3-Clause
"""Regression checks for CEEMDAN's public controls and optional backend."""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd
import pytest

from detime import DecompositionConfig, decompose
from detime.io import save_result
from detime.methods import ceemdan


@pytest.fixture
def recording_backend(monkeypatch):
    calls = []

    class RecordingCEEMDAN:
        def __init__(self, **kwargs):
            self.settings = kwargs
            self.seed = None
            calls.append(self)

        def noise_seed(self, seed):
            self.seed = seed

        def __call__(self, y):
            return np.vstack([0.7 * y, 0.3 * y])

    monkeypatch.setattr(ceemdan, "_HAS_CEEMDAN", True)
    monkeypatch.setattr(ceemdan, "CEEMDAN", RecordingCEEMDAN, raising=False)
    return calls


@pytest.mark.parametrize("n_jobs", [1, 2])
def test_public_seed_noise_and_process_limit_reach_backend(recording_backend, n_jobs):
    y = np.sin(2 * np.pi * np.arange(48) / 12)
    result = decompose(
        y,
        DecompositionConfig(
            method="CEEMDAN",
            params={"trials": 7, "epsilon": 0.02, "primary_period": 12},
            seed=73,
            n_jobs=n_jobs,
        ),
    )
    backend = recording_backend[0]
    assert backend.settings["trials"] == 7
    assert backend.settings["epsilon"] == 0.02
    assert backend.settings["parallel"] is (n_jobs > 1)
    assert backend.settings.get("processes") == (n_jobs if n_jobs > 1 else None)
    assert backend.seed == 73
    assert result.meta["seed"] == 73
    assert result.meta["n_jobs"] == n_jobs
    assert result.meta["epsilon"] == 0.02
    assert result.meta["trials"] == 7
    assert result.components["imfs"].shape == (2, len(y), 1)
    assert result.meta["component_layouts"]["imfs"] == "mode,time,channel"
    np.testing.assert_array_equal(result.components["imfs"][:, :, 0], np.vstack([0.7 * y, 0.3 * y]))
    np.testing.assert_allclose(result.trend + result.season + result.residual, y, atol=1e-14)


def test_defaults_are_serial_and_match_documented_noise_controls(recording_backend):
    decompose(np.arange(48, dtype=float), DecompositionConfig(method="CEEMDAN"))
    backend = recording_backend[0]
    assert backend.settings == {"trials": 100, "epsilon": 0.005, "parallel": False}
    assert backend.seed == 42


def test_explicit_native_request_fails_before_starting_python(recording_backend):
    with pytest.raises(ValueError, match="CEEMDAN only provides a python backend"):
        decompose(
            np.arange(48, dtype=float),
            DecompositionConfig(method="CEEMDAN", backend="native"),
        )
    assert recording_backend == []


def test_legacy_noise_width_is_an_effective_warned_alias(recording_backend):
    with pytest.warns(FutureWarning, match="noise_width.*epsilon"):
        result = decompose(
            np.arange(48, dtype=float),
            DecompositionConfig(method="CEEMDAN", params={"noise_width": 0.03}),
        )
    assert recording_backend[0].settings["epsilon"] == 0.03
    assert result.meta["epsilon"] == 0.03


@pytest.mark.parametrize(
    "params",
    [
        {"trials": 0},
        {"trials": 2.5},
        {"epsilon": -0.1},
        {"epsilon": float("nan")},
        {"noise_width": -0.1},
        {"epsilon": 0.02, "noise_width": 0.03},
    ],
)
def test_invalid_noise_controls_fail_before_backend_execution(params):
    with pytest.raises(ValueError, match="CEEMDAN"):
        DecompositionConfig(method="CEEMDAN", params=params)


def test_frequency_groups_do_not_assign_one_mode_twice():
    trend, season = ceemdan.assign_imfs_to_components(
        np.array([0.0]), 1.0 / 12, {}
    )
    assert trend.tolist() == [True]
    assert season.tolist() == [False]


def _assert_full_export(out_dir, name, y, expected_imfs):
    frame = pd.read_csv(out_dir / f"{name}_components.csv")
    assert list(frame.columns) == ["trend", "season", "residual"]
    assert len(frame) == len(y)
    np.testing.assert_allclose(frame.sum(axis=1).to_numpy(), y, atol=1e-14)
    with np.load(out_dir / f"{name}_components_3d.npz") as payload:
        assert payload.files == ["imfs"]
        np.testing.assert_array_equal(payload["imfs"], expected_imfs)
    meta = json.loads((out_dir / f"{name}_meta.json").read_text())
    assert meta["component_shapes"]["imfs"] == list(expected_imfs.shape)
    assert meta["component_layouts"]["imfs"] == "mode,time,channel"
    assert meta["saved_3d_components"]["imfs"] == {
        "path": f"{name}_components_3d.npz", "shape": list(expected_imfs.shape)
    }


def test_real_backend_matches_seeded_upstream_and_repeats(tmp_path):
    upstream = pytest.importorskip("PyEMD")
    t = np.arange(72, dtype=float)
    y = 0.02 * t + np.sin(2 * np.pi * t / 12) + 0.15 * np.sin(2 * np.pi * t / 5)
    config = DecompositionConfig(
        method="CEEMDAN",
        params={"trials": 4, "epsilon": 0.02, "primary_period": 12},
        seed=73,
        n_jobs=1,
        backend="python",
    )
    first = decompose(y, config)
    second = decompose(y, config)
    reference = upstream.CEEMDAN(trials=4, epsilon=0.02, parallel=False)
    reference.noise_seed(73)
    expected_imfs = reference(y)
    assert first.components["imfs"].shape == (*expected_imfs.shape, 1)
    np.testing.assert_array_equal(first.components["imfs"][:, :, 0], expected_imfs)
    np.testing.assert_array_equal(first.components["imfs"], second.components["imfs"])
    np.testing.assert_array_equal(first.trend, second.trend)
    np.testing.assert_array_equal(first.season, second.season)
    np.testing.assert_allclose(first.trend + first.season + first.residual, y, atol=1e-14)
    save_result(first, tmp_path, "real_ceemdan")
    _assert_full_export(tmp_path, "real_ceemdan", y, expected_imfs[:, :, np.newaxis])


def test_empty_imfs_keep_exportable_mode_time_channel_layout(recording_backend, monkeypatch, tmp_path):
    monkeypatch.setattr(ceemdan.CEEMDAN, "__call__", lambda self, y: np.empty(0))
    y = np.arange(48, dtype=float)
    result = decompose(y, DecompositionConfig(method="CEEMDAN"))
    assert result.components["imfs"].shape == (0, len(y), 1)
    np.testing.assert_array_equal(result.residual, y)
    save_result(result, tmp_path, "empty_ceemdan")
    _assert_full_export(tmp_path, "empty_ceemdan", y, np.empty((0, len(y), 1)))


def test_cli_default_full_output_exports_imfs(recording_backend, monkeypatch, tmp_path):
    from detime.cli import main

    t = np.arange(48, dtype=float)
    y = 0.02 * t + np.sin(2 * np.pi * t / 12)
    input_path = tmp_path / "series.csv"
    pd.DataFrame({"value": y}).to_csv(input_path, index=False)
    # Use the parsed input as the reference for exact backend-array equality.
    loaded_y = pd.read_csv(input_path)["value"].to_numpy()
    out_dir = tmp_path / "cli_output"
    monkeypatch.setattr(sys, "argv", [
        "detime", "run", "--method", "CEEMDAN", "--series", str(input_path),
        "--col", "value", "--param", "trials=2", "--param", "primary_period=12",
        "--out-dir", str(out_dir),
    ])
    main()
    expected_imfs = np.vstack([0.7 * loaded_y, 0.3 * loaded_y])[:, :, np.newaxis]
    _assert_full_export(out_dir, "series", loaded_y, expected_imfs)
