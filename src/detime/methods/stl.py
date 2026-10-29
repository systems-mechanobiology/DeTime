# SPDX-License-Identifier: BSD-3-Clause
import numpy as np
from typing import Dict, Any
from ..backends import finalize_result, split_runtime_params
from ..core import DecompResult
from ..registry import MethodRegistry

@MethodRegistry.register("STL")
def stl_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    """
    STL decomposition: y = trend + seasonal + resid.
    """
    try:
        from statsmodels.tsa.seasonal import STL
    except ImportError as exc:
        raise ImportError("statsmodels is required for STL decomposition.") from exc

    cfg, runtime = split_runtime_params(params)
    if runtime.backend in {"native", "gpu"}:
        raise ValueError("STL only provides a python backend.")
    period = cfg.pop("period", None)
    if period is None:
        raise ValueError("STL requires 'period' in params.")
    period = int(period)

    stl = STL(y, period=period, **cfg)
    res = stl.fit()

    trend = np.asarray(res.trend)
    seasonal = np.asarray(res.seasonal)
    residual = np.asarray(res.resid)
    
    result = DecompResult(
        trend=trend,
        season=seasonal,
        residual=residual,
        meta={"method": "STL", "params": {"period": period, **cfg}},
    )
    return finalize_result(result, method="STL", runtime=runtime, backend_used="python")

@MethodRegistry.register("MSTL")
def mstl_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    """Return MSTL components in the input scale, including after Box-Cox.

    For a transformed trend T and combined seasonal term S, the original-scale
    allocation is trend = inverse(T), season = inverse(T + S) - inverse(T), and
    residual = y - inverse(T + S). Nonlinear inverse transforms do not preserve
    additivity when applied to each component independently.
    """
    try:
        from statsmodels.tsa.seasonal import MSTL
    except ImportError as exc:
        raise ImportError("statsmodels>=0.14 is required for MSTL decomposition.") from exc

    cfg, runtime = split_runtime_params(params)
    if runtime.backend in {"native", "gpu"}:
        raise ValueError("MSTL only provides a python backend.")
    raw_periods = cfg.pop("periods", None)
    if raw_periods is None:
        raise ValueError("MSTL requires 'periods' in params.")
    if isinstance(raw_periods, (int, np.integer)) and not isinstance(
        raw_periods, (bool, np.bool_)
    ):
        period_values = [raw_periods]
    else:
        try:
            period_values = list(raw_periods)
        except TypeError as exc:
            raise ValueError("MSTL 'periods' must be an integer or an integer sequence.") from exc
    if not period_values or any(
        isinstance(period, (bool, np.bool_))
        or not isinstance(period, (int, np.integer))
        or period < 2
        for period in period_values
    ):
        raise ValueError("MSTL 'periods' must contain integer values >= 2.")
    periods = [int(period) for period in period_values]

    requested_lmbda = cfg.get("lmbda")
    upstream_cfg = dict(cfg)
    if isinstance(upstream_cfg.get("stl_kwargs"), dict):
        # MSTL removes fit-only options from this nested dictionary in-place.
        upstream_cfg["stl_kwargs"] = dict(upstream_cfg["stl_kwargs"])
    fit_y = y
    if requested_lmbda == 0:
        # statsmodels 0.14/0.15 use a truthiness check for fixed lambda, which
        # skips lambda=0. Apply its log transform explicitly and fit once.
        fit_y = np.asarray(y, dtype=float)
        if np.any(fit_y <= 0):
            raise ValueError("MSTL with lmbda=0 requires strictly positive input.")
        fit_y = np.log(fit_y)
        upstream_cfg["lmbda"] = None
    mstl = MSTL(fit_y, periods=periods, **upstream_cfg)
    res = mstl.fit()

    seasonal = np.asarray(res.seasonal, dtype=float)
    if seasonal.ndim == 2:
        season = seasonal.sum(axis=1)
    else:
        season = seasonal

    trend = np.asarray(res.trend, dtype=float)
    residual = np.asarray(res.resid, dtype=float)
    effective_lmbda = None
    if requested_lmbda == "auto":
        effective_lmbda = getattr(mstl, "est_lmbda", None)
        if effective_lmbda is None or not np.isfinite(effective_lmbda):
            raise ValueError("MSTL did not return a finite estimated Box-Cox lambda.")
    elif requested_lmbda is not None:
        # In statsmodels 0.15 est_lmbda exists but stays None for fixed lambda.
        effective_lmbda = float(requested_lmbda)
    if effective_lmbda is not None:
        from scipy.special import inv_boxcox

        fitted = inv_boxcox(trend + season, effective_lmbda)
        original_trend = inv_boxcox(trend, effective_lmbda)
        if not np.isfinite(fitted).all() or not np.isfinite(original_trend).all():
            raise ValueError("MSTL Box-Cox components could not be mapped to the original scale.")
        trend = original_trend
        season = fitted - original_trend
        residual = np.asarray(y, dtype=float) - fitted

    result = DecompResult(
        trend=trend,
        season=season,
        residual=residual,
        meta={
            "method": "MSTL",
            "params": {"periods": periods, **cfg},
            "output_scale": "original",
            "boxcox_lambda": (
                float(effective_lmbda) if effective_lmbda is not None else None
            ),
        },
    )
    return finalize_result(result, method="MSTL", runtime=runtime, backend_used="python")

@MethodRegistry.register("ROBUST_STL")
def robuststl_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    try:
        from statsmodels.tsa.seasonal import STL
    except ImportError as exc:
        raise ImportError("statsmodels is required for RobustSTL.") from exc

    cfg, runtime = split_runtime_params(params)
    if runtime.backend in {"native", "gpu"}:
        raise ValueError("ROBUST_STL only provides a python backend.")
    period = cfg.pop("period", None)
    if period is None:
        raise ValueError("RobustSTL requires 'period' in params.")
    period = int(period)

    # RobustSTL is just STL with robust=True by default and maybe some specific tuning
    robust = cfg.pop("robust", True)
    
    stl = STL(y, period=period, robust=robust, **cfg)
    res = stl.fit()

    result = DecompResult(
        trend=res.trend,
        season=res.seasonal,
        residual=res.resid,
        meta={"method": "ROBUST_STL", "params": {"period": period, "robust": robust, **cfg}}
    )
    return finalize_result(result, method="ROBUST_STL", runtime=runtime, backend_used="python")
