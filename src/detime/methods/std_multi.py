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
    raise NotImplementedError(
        "STD_MULTI is an archived experimental prototype and is not part of "
        "the supported public method surface."
    )

def std_full_ablation_decompose(
    y: np.ndarray,
    params: Dict[str, Any],
) -> DecompResult:
    return std_multi_decompose(y, {**params, "mode": "STD_FULL_ABLATION"})
