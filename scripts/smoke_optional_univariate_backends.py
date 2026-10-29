# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import numpy as np

from detime import DecompositionConfig, decompose


def _check(method: str, params: dict[str, object]) -> None:
    t = np.arange(48, dtype=float)
    series = 0.02 * t + np.sin(2.0 * np.pi * t / 12.0)
    result = decompose(series, DecompositionConfig(method=method, params=params))

    assert result.meta["method"] == method
    assert result.trend.shape == series.shape
    assert result.season.shape == series.shape
    assert result.residual.shape == series.shape
    np.testing.assert_allclose(result.trend + result.season + result.residual, series)


def main() -> None:
    _check("EMD", {"primary_period": 12, "n_imfs": 3})
    _check(
        "CEEMDAN",
        {"primary_period": 12, "trials": 2, "epsilon": 0.02},
    )
    print("optional EMD/CEEMDAN backends passed")


if __name__ == "__main__":
    main()
