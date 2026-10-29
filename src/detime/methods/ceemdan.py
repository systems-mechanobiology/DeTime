# SPDX-License-Identifier: BSD-3-Clause
import numpy as np
import warnings
from typing import Dict, Any, Tuple, Optional
from ..backends import split_runtime_params
from ..core import DecompResult
from ..registry import MethodRegistry
from .utils import dominant_frequency

try:
    from PyEMD import CEEMDAN
    _HAS_CEEMDAN = True
    _CEEMDAN_IMPORT_ERROR = None
except Exception as exc:
    _HAS_CEEMDAN = False
    _CEEMDAN_IMPORT_ERROR = exc

def estimate_imf_dom_freqs(imfs: np.ndarray, fs: float) -> np.ndarray:
    freqs = []
    for imf in imfs:
        freqs.append(dominant_frequency(imf, fs))
    return np.array(freqs, dtype=float)

def assign_imfs_to_components(
    freqs: np.ndarray,
    primary_freq: Optional[float],
    config: Dict[str, Any],
) -> Tuple[np.ndarray, np.ndarray]:
    trend_threshold = float(config.get("trend_freq_max", 0.02))
    if primary_freq:
        trend_threshold = config.get("trend_freq_max", primary_freq / 8.0)

    season_band_factor = float(config.get("season_band_factor", 2.0))
    trend_mask = freqs <= max(trend_threshold, 1e-6)
    season_mask = np.zeros_like(freqs, dtype=bool)

    if primary_freq and primary_freq > 0:
        low = primary_freq / max(season_band_factor, 1.0)
        high = primary_freq * max(season_band_factor, 1.0)
        season_mask = (freqs >= low) & (freqs <= high)

    if not trend_mask.any():
        trend_mask[np.argmin(freqs)] = True
    # A mode contributes to at most one named component. In particular, a
    # single low-frequency mode must not be counted as both trend and season.
    season_mask &= ~trend_mask
    if not season_mask.any():
        candidates = np.flatnonzero(~trend_mask)
        if primary_freq and candidates.size:
            idx = candidates[np.argmin(np.abs(freqs[candidates] - primary_freq))]
            season_mask[idx] = True
        else:
            season_mask[~trend_mask] = True
    return trend_mask, season_mask

@MethodRegistry.register("CEEMDAN")
def ceemdan_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    if not _HAS_CEEMDAN:
        raise ImportError(
            "PyEMD>=1.0 is required for CEEMDAN decomposition. Install 'detime-toolkit[emd]' or 'EMD-signal'."
        ) from _CEEMDAN_IMPORT_ERROR

    cfg, runtime = split_runtime_params(params)
    if runtime.backend == "native":
        raise ValueError("CEEMDAN only provides a python backend.")
    if "epsilon" in cfg and "noise_width" in cfg:
        raise ValueError("CEEMDAN accepts either epsilon or legacy noise_width, not both.")
    if "noise_width" in cfg:
        warnings.warn(
            "CEEMDAN noise_width is deprecated; use epsilon. The legacy parameter "
            "previously had no effect and now controls the upstream epsilon value.",
            FutureWarning,
            stacklevel=2,
        )
    trials = int(cfg.get("trials", 100))
    epsilon = float(cfg.get("epsilon", cfg.get("noise_width", 0.005)))
    parallel = runtime.n_jobs > 1
    backend_options = {"trials": trials, "epsilon": epsilon, "parallel": parallel}
    if parallel:
        backend_options["processes"] = runtime.n_jobs
    ceemdan = CEEMDAN(**backend_options)
    if runtime.seed is not None:
        ceemdan.noise_seed(int(runtime.seed))

    runtime_meta = {
        "method": "CEEMDAN",
        "backend_used": "python",
        "trials": trials,
        "epsilon": epsilon,
        "seed": runtime.seed,
        "n_jobs": runtime.n_jobs,
        "parallel": parallel,
        "component_layouts": {"imfs": "mode,time,channel"},
    }

    imfs = ceemdan(y)
    imfs = np.asarray(imfs, dtype=float)
    if imfs.ndim == 1:
        imfs = imfs[np.newaxis, :]
    
    if imfs.size == 0:
        zeros = np.zeros_like(y)
        return DecompResult(
            trend=zeros,
            season=zeros,
            residual=y.copy(),
            components={"imfs": np.empty((0, len(y), 1), dtype=float)},
            meta={**runtime_meta, "imfs": []}
        )

    fs = float(cfg.get("fs", 1.0))
    freqs = estimate_imf_dom_freqs(imfs, fs)
    primary_period = cfg.get("primary_period")
    primary_freq = 1.0 / float(primary_period) if primary_period else None

    trend_mask, season_mask = assign_imfs_to_components(freqs, primary_freq, cfg)

    trend = imfs[trend_mask].sum(axis=0) if trend_mask.any() else np.zeros_like(y)
    season = imfs[season_mask].sum(axis=0) if season_mask.any() else np.zeros_like(y)
    residual = y - trend - season
    
    return DecompResult(
        trend=trend,
        season=season,
        residual=residual,
        # Retain a channel axis for mode collections so save_result uses its
        # established 3D NPZ layout, rather than interpreting modes as time.
        components={"imfs": imfs[:, :, np.newaxis]},
        meta={
            **runtime_meta,
            "dominant_frequencies": freqs.tolist(),
            "trend_mask": trend_mask.tolist(),
            "season_mask": season_mask.tolist(),
            "primary_period": primary_period,
        }
    )
