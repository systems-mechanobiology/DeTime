# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

from detime import DecompositionConfig, decompose
from detime.io import save_result


def _check(method: str, params: dict[str, object]) -> None:
    t = np.arange(48, dtype=float)
    series = 0.02 * t + np.sin(2.0 * np.pi * t / 12.0)
    result = decompose(series, DecompositionConfig(method=method, params=params))

    assert result.meta["method"] == method
    assert result.trend.shape == series.shape
    assert result.season.shape == series.shape
    assert result.residual.shape == series.shape
    np.testing.assert_allclose(result.trend + result.season + result.residual, series)

    # Exercise the artifact boundary too: optional arrays must not break the
    # default full-output path used by the CLI.
    with TemporaryDirectory(prefix="detime-backend-smoke-") as directory:
        output = Path(directory)
        save_result(result, output, "smoke")
        table = np.genfromtxt(output / "smoke_components.csv", delimiter=",", names=True)
        np.testing.assert_allclose(
            table["trend"] + table["season"] + table["residual"], series
        )
        if method == "CEEMDAN":
            with np.load(output / "smoke_components_3d.npz", allow_pickle=False) as archive:
                np.testing.assert_array_equal(archive["imfs"], result.components["imfs"])
                assert archive["imfs"].shape[1:] == (series.size, 1)


def main() -> None:
    _check("EMD", {"primary_period": 12, "n_imfs": 3})
    _check(
        "CEEMDAN",
        {"primary_period": 12, "trials": 2, "epsilon": 0.02},
    )
    print("optional EMD/CEEMDAN backends passed")


if __name__ == "__main__":
    main()
