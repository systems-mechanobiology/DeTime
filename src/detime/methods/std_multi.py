import numpy as np
from typing import Dict, Any
from dataclasses import dataclass
from ..core import DecompResult

"""
Archived experimental prototypes.

These helpers are intentionally not registered in the public MethodRegistry and
are not part of the supported public method surface.
"""

@dataclass
class STDBasisCache:
    """
    Cache for STD bases.
    """
    bases: Dict[str, np.ndarray] # key -> basis matrix (L, K) or similar

    def fit(self, X_windows: np.ndarray):
        # Placeholder: fit bases from windows
        pass

    def project(self, window: np.ndarray) -> np.ndarray:
        # Placeholder: project window onto basis
        return window

    def save(self, path: str):
        np.savez(path, **self.bases)

    @staticmethod
    def load(path: str) -> "STDBasisCache":
        data = np.load(path)
        return STDBasisCache(bases={k: data[k] for k in data.files})

def std_multi_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    """
    Multi-scale STD decomposition with caching.
    """
    # Check for faststd/fasttimes
    try:
        import fasttimes
        _HAS_FASTTIMES = True
    except ImportError:
        _HAS_FASTTIMES = False

    cfg = params.copy()
    mode = cfg.get("mode", "STD_MULTI") # or STD_FULL_ABLATION
    
    if not _HAS_FASTTIMES:
        raise NotImplementedError(
            "STD_MULTI is an archived experimental prototype and is not part of "
            "the supported public method surface. Install a compatible fasttimes "
            "implementation and register a maintained backend before using it."
        )

    # Real implementation would go here using fasttimes
    # ...
    
    return DecompResult(
        trend=np.zeros_like(y),
        season=np.zeros_like(y),
        residual=y,
        meta={"method": mode, "params": cfg, "note": "Archived experimental prototype"}
    )

def std_full_ablation_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    return std_multi_decompose(y, {**params, "mode": "STD_FULL_ABLATION"})
