# SPDX-License-Identifier: BSD-3-Clause
"""Small declarative contract for reproducible teaching animations.

These objects describe educational numerical traces, not benchmark results.
The renderer lives in ``scripts/generate_method_animations.py``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np


COLORS = {
    "blue": "#1F4FFF",
    "teal": "#008D8D",
    "orange": "#D77B11",
    "red": "#CC4B57",
    "purple": "#8058C6",
    "gray": "#8C98AD",
    "dark": "#24334D",
    "green": "#3B8A60",
}


@dataclass
class Line:
    y: np.ndarray
    label: str = ""
    x: np.ndarray | None = None
    color: str = "blue"
    style: str = "-"
    marker: str | None = None
    linewidth: float = 2.0
    alpha: float = 1.0


@dataclass
class Panel:
    title: str
    lines: list[Line] = field(default_factory=list)
    xlabel: str = "Sample"
    ylabel: str = "Value"
    image: np.ndarray | None = None
    cmap: str = "viridis"
    vmin: float | None = None
    vmax: float | None = None
    extent: tuple[float, float, float, float] | None = None
    bars: np.ndarray | None = None
    bar_labels: list[str] | None = None
    bar_colors: list[str] | None = None
    vline: float | None = None
    span: tuple[float, float] | None = None
    xlim: tuple[float, float] | None = None
    ylim: tuple[float, float] | None = None
    annotation: str = ""


@dataclass
class Step:
    title: str
    text: str


@dataclass
class Frame:
    stage: int
    panels: list[Panel]
    caption: str = ""


@dataclass
class Parameter:
    name: str
    effect: str


@dataclass
class Reference:
    title: str
    url: str


@dataclass
class AnimationSpec:
    method: str
    title: str
    summary: str
    steps: list[Step]
    make_frame: Callable[[int, int], Frame]
    parameters: list[Parameter]
    cautions: list[str]
    references: list[Reference]
    trace_kind: str
    trace_note: str
    example_config: dict
    checks: dict = field(default_factory=dict)
    data: dict[str, np.ndarray] = field(default_factory=dict)
    source_files: list[str] = field(default_factory=list)
    input_note: str = "Deterministic synthetic teaching signal; not a benchmark."


def phase(index: int, total: int, stages: int = 4) -> tuple[int, float]:
    """Return the current step and its local progress, including both endpoints."""
    lengths = np.array_split(np.arange(total), stages)
    for stage, indices in enumerate(lengths):
        if index in indices:
            return stage, float(index - indices[0]) / max(1, len(indices) - 1)
    raise ValueError(f"frame {index} outside [0, {total})")


def teaching_signal(n: int = 144, period: int = 24, seed: int = 42):
    rng = np.random.default_rng(seed)
    t = np.arange(n, dtype=float)
    trend = 0.012 * t + 0.18 * np.sin(2 * np.pi * t / (3 * n))
    season = (0.8 + 0.25 * t / n) * np.sin(2 * np.pi * t / period)
    season += 0.22 * np.cos(4 * np.pi * t / period)
    noise = 0.055 * rng.normal(size=n)
    return t, trend + season + noise, trend, season, noise
