from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Union
import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator

@dataclass
class DecompResult:
    """
    Unified container for time-series decomposition results.
    """
    trend: np.ndarray
    season: np.ndarray
    residual: np.ndarray
    components: Dict[str, np.ndarray] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.trend = np.asarray(self.trend, dtype=float)
        self.season = np.asarray(self.season, dtype=float)
        self.residual = np.asarray(self.residual, dtype=float)
        if not (self.trend.shape == self.season.shape == self.residual.shape):
            raise ValueError(
                "DecompResult trend, season, and residual must have identical shapes; "
                f"got {self.trend.shape}, {self.season.shape}, and {self.residual.shape}."
            )
        for name, value in (
            ("trend", self.trend),
            ("season", self.season),
            ("residual", self.residual),
        ):
            if not np.isfinite(value).all():
                raise ValueError(f"DecompResult {name} contains non-finite values.")
        self.components = {
            str(key): np.asarray(value)
            for key, value in dict(self.components or {}).items()
        }
        self.meta = dict(self.meta or {})

class DecompositionConfig(BaseModel):
    """
    Configuration for a decomposition method.
    """
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)
    return_components: Optional[List[str]] = None
    backend: Literal["auto", "native", "python"] = "auto"
    speed_mode: Literal["exact", "fast"] = "exact"
    profile: bool = False
    device: Optional[str] = "cpu"
    n_jobs: int = Field(default=1, ge=1)
    seed: Optional[int] = 42
    channel_names: Optional[List[str]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    @model_validator(mode="after")
    def _validate_method_params(self) -> "DecompositionConfig":
        try:
            from .registry import validate_method_params
        except Exception:
            return self
        validate_method_params(self.method, self.params)
        return self
