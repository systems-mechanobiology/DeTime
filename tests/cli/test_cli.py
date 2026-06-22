from __future__ import annotations

from argparse import Namespace
import os
import runpy

import numpy as np
import pytest

import detime.cli as cli
from detime.benchmark import BenchmarkRunResult
from detime.core import DecompResult


class FakeConfig:
    model_fields = {
        "method": object(),
        "params": object(),
        "backend": object(),
        "speed_mode": object(),
        "n_jobs": object(),
        "profile": object(),
        "device": object(),
    }

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def test_backend_selection_passes_flags(monkeypatch, tmp_path):
    captured = {}

    def fake_read_series(series, col=None, cols=None):
        captured["read_cols"] = cols
        return np.asarray([1.0, 2.0, 3.0], dtype=float)

    def fake_decompose(series, cfg):
        captured["cfg"] = cfg
        return DecompResult(
            trend=series,
            season=np.zeros_like(series),
            residual=np.zeros_like(series),
            meta={"backend_used": getattr(cfg, "backend", None)},
        )

    monkeypatch.setattr(cli, "DecompositionConfig", FakeConfig)
    monkeypatch.setattr(cli, "read_series", fake_read_series)
    monkeypatch.setattr(cli, "decompose", fake_decompose)
    monkeypatch.setattr(cli, "save_result", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli, "plot_components", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli, "plot_error", lambda *args, **kwargs: None)

    args = Namespace(
        method="SSA",
        series="input.csv",
        col=None,
        cols=None,
        param=["window=8"],
        backend="native",
        speed_mode="fast",
        n_jobs=4,
        profile=True,
        device="cpu",
        out_dir=str(tmp_path / "out"),
        plot=False,
    )

    cli.cmd_run(args)

    cfg = captured["cfg"]
    assert cfg.backend == "native"
    assert cfg.speed_mode == "fast"
    assert cfg.n_jobs == 4
    assert cfg.profile is True
    assert cfg.method == "SSA"
    assert cfg.params == {"window": 8}
    assert captured["read_cols"] is None


def test_parse_params_and_module_entrypoint(monkeypatch):
    params = cli.parse_params(["window=12", "robust=true", "name=SSA", "bad"])
    assert params == {"window": 12, "robust": True, "name": "SSA"}
    assert cli.parse_params([]) == {}

    called = {}
    monkeypatch.delenv("DETIME_CLI_BRAND", raising=False)
    monkeypatch.setattr(cli, "main", lambda: called.setdefault("main", True))

    runpy.run_module("detime.__main__", run_name="__main__")

    assert os.environ["DETIME_CLI_BRAND"] == "detime"
    assert called["main"] is True


def test_profile_command_writes_report(monkeypatch, tmp_path, capsys):
    report_path = tmp_path / "profile.json"
    monkeypatch.setattr(
        cli,
        "run_profile",
        lambda **kwargs: {
            "method": kwargs["method"],
            "backend_requested": kwargs["backend"],
            "backend_used": kwargs["backend"],
            "speed_mode": kwargs["speed_mode"],
            "repeat": kwargs["repeat"],
            "warmup": kwargs["warmup"],
            "samples_ms": [1.0, 2.0],
            "summary": {
                "min_ms": 1.0,
                "mean_ms": 1.5,
                "median_ms": 1.5,
                "p95_ms": 2.0,
                "stdev_ms": 0.5,
            },
        },
    )

    import sys

    old_argv = sys.argv
    sys.argv = [
        "detime",
        "profile",
        "--method",
        "SSA",
        "--series",
        "input.csv",
        "--backend",
        "native",
        "--speed-mode",
        "fast",
        "--repeat",
        "2",
        "--warmup",
        "1",
        "--output",
        str(report_path),
    ]
    try:
        cli.main()
    finally:
        sys.argv = old_argv

    captured = capsys.readouterr()
    assert "Profile report written" in captured.out
    assert report_path.exists()


def test_profile_command_prints_text_stdout(monkeypatch, capsys):
    monkeypatch.setattr(
        cli,
        "run_profile",
        lambda **kwargs: {
            "method": kwargs["method"],
            "backend_requested": kwargs["backend"],
            "backend_used": kwargs["backend"],
            "speed_mode": kwargs["speed_mode"],
            "repeat": kwargs["repeat"],
            "warmup": kwargs["warmup"],
            "samples_ms": [1.0, 2.0],
            "summary": {
                "min_ms": 1.0,
                "mean_ms": 1.5,
                "median_ms": 1.5,
                "p95_ms": 2.0,
                "stdev_ms": 0.5,
            },
        },
    )

    import sys

    old_argv = sys.argv
    sys.argv = [
        "detime",
        "profile",
        "--method",
        "SSA",
        "--series",
        "input.csv",
        "--backend",
        "native",
        "--speed-mode",
        "fast",
        "--repeat",
        "2",
        "--warmup",
        "1",
        "--format",
        "text",
    ]
    try:
        cli.main()
    finally:
        sys.argv = old_argv

    captured = capsys.readouterr()
    assert "method=SSA" in captured.out
    assert '"method"' not in captured.out


def test_profile_command_prints_json_stdout(monkeypatch, capsys):
    monkeypatch.setattr(
        cli,
        "run_profile",
        lambda **kwargs: {
            "method": kwargs["method"],
            "backend_requested": kwargs["backend"],
            "backend_used": kwargs["backend"],
            "speed_mode": kwargs["speed_mode"],
            "repeat": kwargs["repeat"],
            "warmup": kwargs["warmup"],
            "samples_ms": [1.0, 2.0],
            "summary": {
                "min_ms": 1.0,
                "mean_ms": 1.5,
                "median_ms": 1.5,
                "p95_ms": 2.0,
                "stdev_ms": 0.5,
            },
        },
    )

    import sys

    old_argv = sys.argv
    sys.argv = [
        "detime",
        "profile",
        "--method",
        "SSA",
        "--series",
        "input.csv",
        "--backend",
        "native",
        "--speed-mode",
        "fast",
        "--repeat",
        "2",
        "--warmup",
        "1",
        "--format",
        "json",
    ]
    try:
        cli.main()
    finally:
        sys.argv = old_argv

    captured = capsys.readouterr()
    assert '"method": "SSA"' in captured.out
    assert "method=SSA" not in captured.out


def test_run_command_accepts_multivariate_cols(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "DecompositionConfig", FakeConfig)
    captured = {}

    def fake_read_series(series, col=None, cols=None):
        captured["col"] = col
        captured["cols"] = cols
        return np.column_stack(
            [
                np.asarray([1.0, 2.0, 3.0], dtype=float),
                np.asarray([4.0, 5.0, 6.0], dtype=float),
            ]
        )

    monkeypatch.setattr(cli, "read_series", fake_read_series)
    monkeypatch.setattr(
        cli,
        "decompose",
        lambda series, cfg: DecompResult(
            trend=series,
            season=np.zeros_like(series),
            residual=np.zeros_like(series),
            meta={"backend_used": getattr(cfg, "backend", "auto"), "n_channels": series.shape[1]},
        ),
    )
    monkeypatch.setattr(cli, "save_result", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli, "plot_components", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli, "plot_error", lambda *args, **kwargs: None)

    args = Namespace(
        method="MSSA",
        series="input.csv",
        col=None,
        cols="a,b",
        param=["window=8"],
        backend="python",
        speed_mode="exact",
        n_jobs=1,
        profile=False,
        device="cpu",
        out_dir=str(tmp_path / "out"),
        plot=False,
    )

    cli.cmd_run(args)

    assert captured["col"] is None
    assert captured["cols"] == ["a", "b"]


def test_run_command_rejects_multivariate_plotting(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "DecompositionConfig", FakeConfig)
    monkeypatch.setattr(
        cli,
        "read_series",
        lambda series, col=None, cols=None: np.column_stack(
            [
                np.asarray([1.0, 2.0, 3.0], dtype=float),
                np.asarray([4.0, 5.0, 6.0], dtype=float),
            ]
        ),
    )
    monkeypatch.setattr(
        cli,
        "decompose",
        lambda series, cfg: DecompResult(
            trend=series,
            season=np.zeros_like(series),
            residual=np.zeros_like(series),
            meta={"backend_used": getattr(cfg, "backend", "auto"), "result_layout": "multivariate"},
        ),
    )
    monkeypatch.setattr(cli, "save_result", lambda *args, **kwargs: None)

    args = Namespace(
        method="MSSA",
        series="input.csv",
        col=None,
        cols="a,b",
        param=["window=8"],
        backend="python",
        speed_mode="exact",
        n_jobs=1,
        profile=False,
        device="cpu",
        out_dir=str(tmp_path / "out"),
        plot=True,
    )

    with pytest.raises((ValueError, NotImplementedError), match="plot|multivariate|2D"):
        cli.cmd_run(args)


def test_run_command_passes_output_mode_and_fields(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "DecompositionConfig", FakeConfig)
    monkeypatch.setattr(
        cli,
        "read_series",
        lambda series, col=None, cols=None: np.asarray([1.0, 2.0, 3.0], dtype=float),
    )
    monkeypatch.setattr(
        cli,
        "decompose",
        lambda series, cfg: DecompResult(
            trend=series,
            season=np.zeros_like(series),
            residual=np.zeros_like(series),
            meta={"backend_used": "python"},
        ),
    )
    captured = {}
    monkeypatch.setattr(
        cli,
        "save_result",
        lambda result, out_dir, name, **kwargs: captured.update(
            {"out_dir": out_dir, "name": name, **kwargs}
        ),
    )

    args = Namespace(
        method="SSA",
        series="input.csv",
        col=None,
        cols=None,
        param=[],
        backend="python",
        speed_mode="exact",
        n_jobs=1,
        profile=False,
        device="cpu",
        out_dir=str(tmp_path / "out"),
        output_mode="summary",
        fields="meta,diagnostics",
        plot=False,
    )

    cli.cmd_run(args)

    assert captured["output_mode"] == "summary"
    assert captured["fields"] == ["meta", "diagnostics"]


def test_batch_command_covers_empty_success_and_error_paths(monkeypatch, tmp_path, capsys):
    args = Namespace(
        method="SSA",
        glob=str(tmp_path / "none" / "*.csv"),
        col=None,
        cols=None,
        param=["window=8"],
        backend="python",
        speed_mode="exact",
        n_jobs=1,
        profile=True,
        device="cpu",
        out_dir=str(tmp_path / "batch"),
        output_mode="meta",
        fields="meta",
        plot=True,
    )

    cli.cmd_batch(args)
    assert "No files found" in capsys.readouterr().out

    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    first.write_text("value\n1\n2\n3\n", encoding="utf-8")
    second.write_text("value\n4\n5\n6\n", encoding="utf-8")
    args.glob = str(tmp_path / "*.csv")

    saved = []
    plotted = []

    def fake_read_series(path, col=None, cols=None, method=None, return_info=False):
        if str(path).endswith("second.csv"):
            raise RuntimeError("bad input")
        series = np.asarray([1.0, 2.0, 3.0])
        info = {"channel_names": ["value"], "multivariate": False}
        return (series, info) if return_info else series

    def fake_decompose(series, cfg):
        return DecompResult(
            trend=series,
            season=np.zeros_like(series),
            residual=np.zeros_like(series),
            meta={"backend_used": "python"},
        )

    monkeypatch.setattr(cli, "read_series", fake_read_series)
    monkeypatch.setattr(cli, "decompose", fake_decompose)
    monkeypatch.setattr(
        cli,
        "save_result",
        lambda result, out_dir, name, **kwargs: saved.append((name, kwargs)),
    )
    monkeypatch.setattr(
        cli,
        "plot_components",
        lambda result, series, save_path: plotted.append(save_path),
    )

    cli.cmd_batch(args)
    output = capsys.readouterr().out

    assert "Found 2 files" in output
    assert "Error processing" in output
    assert saved[0][0] == "first"
    assert saved[0][1]["output_mode"] == "meta"
    assert plotted


def test_schema_command_prints_json(capsys):
    import sys

    old_argv = sys.argv
    sys.argv = ["detime", "schema", "--name", "config"]
    try:
        cli.main()
    finally:
        sys.argv = old_argv

    captured = capsys.readouterr()
    assert '"title"' in captured.out
    assert "DecompositionConfig" in captured.out


def test_version_schema_output_and_text_recommend(monkeypatch, tmp_path, capsys):
    import sys

    old_argv = sys.argv
    try:
        sys.argv = ["detime", "version"]
        cli.main()
        assert cli.PACKAGE_VERSION in capsys.readouterr().out

        schema_path = tmp_path / "schema.json"
        sys.argv = ["detime", "schema", "--name", "meta", "--output", str(schema_path)]
        cli.main()
        assert schema_path.exists()
        assert "Schema written" in capsys.readouterr().out

        sys.argv = [
            "detime",
            "recommend",
            "--length",
            "128",
            "--channels",
            "1",
            "--format",
            "text",
        ]
        cli.main()
        text = capsys.readouterr().out
        assert "reasons:" in text
    finally:
        sys.argv = old_argv


def test_recommend_requires_series_or_length():
    with pytest.raises(ValueError, match="either --series or --length"):
        cli.cmd_recommend(
            Namespace(
                series=None,
                col=None,
                cols=None,
                length=None,
                channels=1,
                prefer="balanced",
                allow_optional_backends=False,
                require_native=False,
                top_k=5,
                format="json",
            )
        )


def test_schema_command_prints_method_registry_contract_version(capsys):
    import sys

    old_argv = sys.argv
    sys.argv = ["detime", "schema", "--name", "method-registry"]
    try:
        cli.main()
    finally:
        sys.argv = old_argv

    captured = capsys.readouterr()
    assert '"contract_version"' in captured.out
    assert '"MethodRegistryPayloadModel"' in captured.out


def test_recommend_command_outputs_json(capsys):
    import sys

    old_argv = sys.argv
    sys.argv = [
        "detime",
        "recommend",
        "--length",
        "128",
        "--channels",
        "2",
        "--prefer",
        "accuracy",
    ]
    try:
        cli.main()
    finally:
        sys.argv = old_argv

    captured = capsys.readouterr()
    assert '"recommendations"' in captured.out
    assert "MSSA" in captured.out


def test_benchmark_command_outputs_json(monkeypatch, tmp_path, capsys):
    def fake_run_tsdecompose_benchmark(**kwargs):
        assert kwargs["smoke"] is True
        assert kwargs["methods"] == "stl"
        assert kwargs["out_dir"] == str(tmp_path / "bench")
        return BenchmarkRunResult(
            benchmark_dir=tmp_path / "source",
            output_dir=tmp_path / "bench",
            command=("python", "runner.py", "--smoke"),
            returncode=0,
            stdout="ok\n",
            stderr="",
            leaderboard_path=tmp_path / "bench" / "leaderboard.csv",
            summary_dir=tmp_path / "bench" / "summary",
        )

    monkeypatch.setattr(cli, "run_tsdecompose_benchmark", fake_run_tsdecompose_benchmark)

    import sys

    old_argv = sys.argv
    sys.argv = [
        "detime",
        "benchmark",
        "--methods",
        "stl",
        "--out-dir",
        str(tmp_path / "bench"),
        "--format",
        "json",
    ]
    try:
        cli.main()
    finally:
        sys.argv = old_argv

    captured = capsys.readouterr()
    assert '"returncode": 0' in captured.out
    assert "leaderboard.csv" in captured.out
