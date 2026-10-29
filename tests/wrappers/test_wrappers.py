# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from types import ModuleType, SimpleNamespace

import numpy as np
import pytest

from detime import DecompResult, DecompositionConfig, decompose
from detime.methods import ceemdan, emd, ma_baseline, memd, mvmd, stl, vmd, wavelet
import detime.methods.gabor_cluster as gabor_mod


def test_ma_baseline_decompose() -> None:
    y = np.arange(20, dtype=float)
    result = ma_baseline.ma_decompose(y, {"trend_window": 5, "season_period": 4})
    assert result.trend.shape == y.shape
    assert result.season.shape == y.shape
    np.testing.assert_allclose(result.trend + result.season + result.residual, y)


def test_stl_family_with_fake_statsmodels(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeSTL:
        calls = []

        def __init__(self, y, period, **kwargs):
            self.y = np.asarray(y, dtype=float)
            self.period = period
            self.kwargs = kwargs
            self.calls.append((period, kwargs))

        def fit(self):
            return SimpleNamespace(
                trend=np.full_like(self.y, 1.0),
                seasonal=np.full_like(self.y, 2.0),
                resid=self.y - 3.0,
            )

    class FakeMSTL:
        calls = []

        def __init__(self, y, periods, **kwargs):
            self.y = np.asarray(y, dtype=float)
            self.periods = periods
            self.kwargs = kwargs
            self.calls.append((periods, kwargs))

        def fit(self):
            seasonals = np.column_stack(
                [
                    np.full_like(self.y, 0.5),
                    np.full_like(self.y, 1.5),
                ]
            )
            self.est_lmbda = 0.5
            observed = 2.0 * (np.sqrt(self.y) - 1.0)
            return SimpleNamespace(
                observed=observed,
                trend=np.full_like(self.y, 1.0),
                seasonal=seasonals,
                resid=observed - 3.0,
            )

    seasonal = ModuleType("statsmodels.tsa.seasonal")
    seasonal.STL = FakeSTL
    seasonal.MSTL = FakeMSTL
    monkeypatch.setitem(__import__("sys").modules, "statsmodels", ModuleType("statsmodels"))
    monkeypatch.setitem(__import__("sys").modules, "statsmodels.tsa", ModuleType("statsmodels.tsa"))
    monkeypatch.setitem(__import__("sys").modules, "statsmodels.tsa.seasonal", seasonal)

    y = np.arange(1, 13, dtype=float)
    stl_result = stl.stl_decompose(
        y,
        {
            "period": 4,
            "seasonal": 7,
            "trend": 9,
            "low_pass": 5,
            "seasonal_deg": 1,
            "trend_deg": 0,
            "low_pass_deg": 1,
            "robust": False,
            "seasonal_jump": 2,
            "trend_jump": 2,
            "low_pass_jump": 2,
        },
    )
    robust_result = stl.robuststl_decompose(y, {"period": 4})
    mstl_result = stl.mstl_decompose(
        y,
        {
            "periods": 4,
            "windows": 7,
            "lmbda": "auto",
            "iterate": 3,
            "stl_kwargs": {"robust": True},
        },
    )

    assert stl_result.meta["method"] == "STL"
    assert robust_result.meta["method"] == "ROBUST_STL"
    assert mstl_result.meta["method"] == "MSTL"
    assert FakeSTL.calls[0][1]["low_pass"] == 5
    assert FakeSTL.calls[0][1]["trend_deg"] == 0
    assert FakeSTL.calls[1][1]["robust"] is True
    assert FakeMSTL.calls == [
        (
            [4],
            {
                "windows": 7,
                "lmbda": "auto",
                "iterate": 3,
                "stl_kwargs": {"robust": True},
            },
        )
    ]
    np.testing.assert_allclose(mstl_result.trend + mstl_result.season + mstl_result.residual, y)


def test_mstl_boxcox_output_preserves_original_scale_contract() -> None:
    t = np.arange(240, dtype=float)
    y = 10.0 + 0.01 * t
    y += np.sin(2 * np.pi * t / 12) + 0.5 * np.sin(2 * np.pi * t / 24)

    result = decompose(
        y,
        DecompositionConfig(
            method="MSTL",
            params={
                "periods": (12, 24),
                "windows": (7, 11),
                "lmbda": 0.5,
                "iterate": 2,
            },
        ),
    )

    np.testing.assert_allclose(result.trend + result.season + result.residual, y)
    assert result.meta["output_scale"] == "original"
    assert result.meta["boxcox_lambda"] == pytest.approx(0.5)


@pytest.mark.parametrize("lmbda", [None, 0.0, 0.5, 1.0, -0.5, "auto"])
@pytest.mark.parametrize("periods", [(12,), (12, 24)])
def test_mstl_components_match_explicit_transformed_fit(lmbda, periods) -> None:
    from scipy.special import inv_boxcox
    from scipy.stats import boxcox
    from statsmodels.tsa.seasonal import MSTL

    t = np.arange(240, dtype=float)
    y = 10.0 + 0.01 * t + np.sin(2 * np.pi * t / 12)
    y += 0.5 * np.sin(2 * np.pi * t / 24) + 0.1 * np.cos(2 * np.pi * t / 7)
    windows = (7, 11)[:len(periods)]
    if lmbda == "auto":
        transformed, expected_lmbda = boxcox(y)
    elif lmbda is not None:
        expected_lmbda = lmbda
        transformed = boxcox(y, lmbda=lmbda)
    else:
        expected_lmbda = None
        transformed = y
    reference = MSTL(transformed, periods=periods, windows=windows).fit()
    reference_season = np.asarray(reference.seasonal)
    if reference_season.ndim == 2:
        reference_season = reference_season.sum(axis=1)
    if expected_lmbda is None:
        expected_trend = reference.trend
        expected_season = reference_season
        expected_residual = reference.resid
    else:
        expected_trend = inv_boxcox(reference.trend, expected_lmbda)
        expected_fit = inv_boxcox(reference.trend + reference_season, expected_lmbda)
        expected_season = expected_fit - expected_trend
        expected_residual = y - expected_fit

    result = decompose(
        y,
        DecompositionConfig(
            method="MSTL",
            params={"periods": periods, "windows": windows, "lmbda": lmbda},
        ),
    )

    np.testing.assert_allclose(result.trend, expected_trend, rtol=1e-11, atol=1e-11)
    np.testing.assert_allclose(result.season, expected_season, rtol=1e-11, atol=1e-11)
    np.testing.assert_allclose(result.residual, expected_residual, rtol=1e-11, atol=1e-11)
    np.testing.assert_allclose(result.trend + result.season + result.residual, y)
    assert result.meta["output_scale"] == "original"
    if expected_lmbda is None:
        assert result.meta["boxcox_lambda"] is None
    else:
        assert result.meta["boxcox_lambda"] == pytest.approx(expected_lmbda)
    assert result.meta["params"]["lmbda"] == lmbda


def test_mstl_transform_is_not_detected_by_float_closeness() -> None:
    from statsmodels.tsa.seasonal import MSTL

    t = np.arange(120, dtype=float)
    y = 1e6 + 0.1 * t + np.sin(2 * np.pi * t / 12)
    assert np.allclose(y - 1.0, y)
    reference = MSTL(y - 1.0, periods=(12,)).fit()
    result = decompose(
        y, DecompositionConfig(method="MSTL", params={"periods": (12,), "lmbda": 1.0})
    )
    np.testing.assert_allclose(result.trend, reference.trend + 1.0, rtol=0, atol=1e-7)
    assert result.meta["boxcox_lambda"] == 1.0


@pytest.mark.parametrize("invalid_value", [0.0, -1.0])
def test_mstl_log_transform_rejects_nonpositive_input(invalid_value) -> None:
    y = np.ones(120)
    y[10] = invalid_value
    with pytest.raises(ValueError, match="strictly positive"):
        decompose(
            y, DecompositionConfig(method="MSTL", params={"periods": (12,), "lmbda": 0.0})
        )


def test_mstl_preserves_nested_stl_options() -> None:
    t = np.arange(120, dtype=float)
    y = 10.0 + np.sin(2 * np.pi * t / 12)
    options = {"robust": True, "inner_iter": 2, "outer_iter": 1}
    config = DecompositionConfig(
        method="MSTL", params={"periods": (12,), "stl_kwargs": options.copy()}
    )
    result = decompose(y, config)
    assert config.params["stl_kwargs"] == options
    assert result.meta["params"]["stl_kwargs"] == options


def test_wavelet_decompose_with_fake_pywt(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeWavelet:
        def __init__(self, name: str):
            self.name = name
            self.dec_len = 4

    fake_pywt = SimpleNamespace(
        Wavelet=FakeWavelet,
        dwt_max_level=lambda length, dec_len: 3,
        wavedec=lambda y, wavelet, level: [
            np.full(8, 0.5),
            np.full(8, 0.25),
            np.full(8, 0.1),
        ],
        waverec=lambda coeffs, wavelet: np.sum(np.asarray(coeffs), axis=0),
    )
    monkeypatch.setattr(wavelet, "_HAS_PYWT", True)
    monkeypatch.setattr(wavelet, "pywt", fake_pywt)

    y = np.linspace(0, 1, 8)
    result = wavelet.wavelet_decompose(y, {"wavelet": "db4", "level": 2})
    assert result.meta["method"] == "WAVELET"
    assert result.trend.shape == y.shape


def test_emd_ceemdan_and_vmd_with_fake_backends(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeEMD:
        def emd(self, y, max_imf=None):
            arr = np.asarray(y, dtype=float)
            return np.vstack([0.6 * arr, 0.3 * arr, 0.1 * arr])

    class FakeCEEMDAN:
        def __init__(self, **kwargs):
            for name, value in kwargs.items():
                setattr(self, name, value)

        def noise_seed(self, seed):
            self.seed = seed

        def __call__(self, y):
            arr = np.asarray(y, dtype=float)
            return np.vstack([0.5 * arr, 0.25 * arr, 0.25 * arr])

    def fake_vmd(y, alpha, tau, K, DC, init, tol):
        arr = np.asarray(y, dtype=float)
        modes = np.vstack([0.5 * arr, 0.3 * arr, 0.2 * arr])
        omega = np.array([[0.01, 0.2, 0.4]])
        return modes, None, omega

    monkeypatch.setattr(emd, "_HAS_PYEMD", True)
    monkeypatch.setattr(emd, "EMD", FakeEMD, raising=False)
    monkeypatch.setattr(ceemdan, "_HAS_CEEMDAN", True)
    monkeypatch.setattr(ceemdan, "CEEMDAN", FakeCEEMDAN, raising=False)
    monkeypatch.setattr(vmd, "_HAS_VMD", True)
    monkeypatch.setattr(vmd, "VMD", fake_vmd, raising=False)

    y = np.sin(np.linspace(0, 2 * np.pi, 24))
    emd_result = emd.emd_decompose(y, {"primary_period": 12, "n_imfs": 3})
    ceemdan_result = ceemdan.ceemdan_decompose(y, {"primary_period": 12})
    vmd_result = vmd.vmd_decompose(y, {"primary_period": 12, "K": 3})

    assert emd_result.meta["method"] == "EMD"
    assert ceemdan_result.meta["method"] == "CEEMDAN"
    assert vmd_result.meta["method"] == "VMD"


def test_mvmd_and_memd_success_paths(monkeypatch) -> None:
    class FakeMVMD:
        def fit_transform(self, x):
            arr = np.asarray(x, dtype=float)
            return np.stack([0.5 * arr, 0.5 * arr], axis=0)

    class FakeMEMD:
        def fit_transform(self, x):
            arr = np.asarray(x, dtype=float)
            return {"imfs": np.stack([0.6 * arr, 0.4 * arr], axis=0)}

    def fake_import(name: str):
        module = ModuleType(name)
        if "MEMD" in name or name.endswith("memd"):
            module.MEMD = FakeMEMD
        if "MVMD" in name or name.endswith("mvmd"):
            module.MVMD = FakeMVMD
        if name in {"pysdkit", "PySDKit"}:
            module.MVMD = FakeMVMD
            module.MEMD = FakeMEMD
        return module

    monkeypatch.setattr(mvmd, "import_module", fake_import)

    t = np.arange(48, dtype=float)
    y = np.column_stack(
        [
            np.sin(2.0 * np.pi * t / 12.0) + 0.05 * t,
            0.8 * np.sin(2.0 * np.pi * t / 12.0 + 0.2) + 0.03 * t,
        ]
    )

    mvmd_result = mvmd.mvmd_decompose(y, {"primary_period": 12})
    memd_result = memd.memd_decompose(y, {"primary_period": 12})

    assert mvmd_result.trend.shape == y.shape
    assert mvmd_result.components["modes"].ndim == 3
    assert memd_result.components["imfs"].ndim == 3


def test_gabor_cluster_python_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gabor_mod, "_HAS_FAISS", True)
    monkeypatch.setattr(
        gabor_mod,
        "_assign_clusters_faiss",
        lambda feats, model: np.array([0, 0, 1, 1, 0, 1, 0, 1, 1], dtype=int),
    )

    cfg = gabor_mod.GaborClusterConfig(
        win_len=4,
        hop=2,
        n_fft=4,
        n_clusters=2,
    )
    model = gabor_mod.GaborClusterModel(
        centroids=np.array([[0.0, 0.0, 0.1], [0.0, 0.8, 0.2]], dtype=np.float32),
        mu=np.zeros(3, dtype=np.float32),
        sigma=np.ones(3, dtype=np.float32),
        cfg=cfg,
    )
    y = np.linspace(0.0, 1.0, 8)
    result = gabor_mod.gabor_cluster_decompose(
        y,
        {
            "__detime_runtime__": {"backend": "python"},
            "model": model,
            "max_clusters": 2,
        },
    )
    assert result.meta["method"] == "GABOR_CLUSTER"
    assert result.meta["backend_used"] == "python"
    assert result.trend.shape == y.shape


def test_wavelet_decompose_with_required_backend() -> None:
    y = np.sin(np.linspace(0.0, 4.0 * np.pi, 64)) + np.linspace(0.0, 1.0, 64)
    result = wavelet.wavelet_decompose(y, {"wavelet": "db4", "level": 2})

    assert result.meta["method"] == "WAVELET"
    np.testing.assert_allclose(result.trend + result.season + result.residual, y)


def test_gabor_centroid_frequency_is_unstandardized() -> None:
    cfg = gabor_mod.GaborClusterConfig()
    model = gabor_mod.GaborClusterModel(
        centroids=np.array([[0.0, 0.5, 0.0]], dtype=np.float32),
        mu=np.array([0.0, 0.1, 0.0], dtype=np.float32),
        sigma=np.array([1.0, 0.2, 1.0], dtype=np.float32),
        cfg=cfg,
    )

    assert gabor_mod._centroid_frequency(model, 0) == pytest.approx(0.2)


def test_gabor_model_roundtrip_uses_safe_npz_json(tmp_path) -> None:
    cfg = gabor_mod.GaborClusterConfig(win_len=8, hop=4, n_fft=8, n_clusters=2)
    model = gabor_mod.GaborClusterModel(
        centroids=np.array([[0.0, 0.1, 0.2], [0.0, 0.8, 0.4]], dtype=np.float32),
        mu=np.array([0.0, 0.2, 0.1], dtype=np.float32),
        sigma=np.array([1.0, 0.5, 0.25], dtype=np.float32),
        cfg=cfg,
    )
    path = tmp_path / "gabor-model.npz"

    model.save(str(path))
    loaded = gabor_mod.GaborClusterModel.load(str(path))

    np.testing.assert_allclose(loaded.centroids, model.centroids)
    np.testing.assert_allclose(loaded.mu, model.mu)
    np.testing.assert_allclose(loaded.sigma, model.sigma)
    assert loaded.cfg == cfg
    with np.load(path, allow_pickle=False) as archive:
        assert "cfg_json" in archive.files

    legacy_path = tmp_path / "legacy-pickle-model.npz"
    np.savez_compressed(
        legacy_path,
        centroids=model.centroids,
        mu=model.mu,
        sigma=model.sigma,
        cfg=np.array([cfg], dtype=object),
    )
    with pytest.raises(ValueError, match=r"safe NPZ\+JSON format"):
        gabor_mod.GaborClusterModel.load(str(legacy_path))
