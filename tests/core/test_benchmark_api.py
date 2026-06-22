from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

import detime.benchmark as benchmark


def test_download_tsdecompose_benchmark_fetches_code_prefix(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        benchmark,
        "_read_json_url",
        lambda url: [
            {"type": "directory", "path": "code/TSDecompose"},
            {"type": "file", "path": "code/TSDecompose/scripts/run_paper_benchmark.py"},
            {"type": "file", "path": "code/TSDecompose/src/tsdecomp/__init__.py"},
            {"type": "file", "path": "README.md"},
        ],
    )

    downloaded: list[Path] = []

    def fake_download(url: str, target: Path) -> None:
        downloaded.append(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# file\n", encoding="utf-8")

    monkeypatch.setattr(benchmark, "_download_file", fake_download)

    source_dir = benchmark.download_tsdecompose_benchmark(cache_dir=tmp_path)

    assert (source_dir / "scripts" / "run_paper_benchmark.py").exists()
    assert (source_dir / "src" / "tsdecomp" / "__init__.py").exists()
    assert len(downloaded) == 2
    assert (source_dir / ".detime_benchmark_source.json").exists()


def test_benchmark_helpers_cover_env_headers_tree_and_cache(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DETIME_BENCHMARK_CACHE", str(tmp_path / "cache-root"))
    assert benchmark.default_benchmark_cache_dir() == tmp_path / "cache-root"

    monkeypatch.setenv("HF_TOKEN", "secret")
    headers = benchmark._request_headers()
    assert headers["User-Agent"] == "de-time-benchmark-runner"
    assert headers["Authorization"] == "Bearer secret"

    siblings = benchmark._tree_entries({"siblings": [{"type": "file", "path": "a.py"}, "bad"]})
    value = benchmark._tree_entries({"value": [{"type": "file", "path": "b.py"}]})
    files = benchmark._tree_entries({"files": [{"type": "file", "path": "c.py"}]})
    assert [item["path"] for item in siblings + value + files] == ["a.py", "b.py", "c.py"]
    with pytest.raises(benchmark.BenchmarkSourceError, match="Unexpected"):
        benchmark._tree_entries({"unexpected": []})

    cache_hit = tmp_path / benchmark._cache_subdir(
        benchmark.TSDECOMPOSE_BENCHMARK_DATASET,
        benchmark.TSDECOMPOSE_BENCHMARK_REVISION,
        "cached",
    )
    runner = cache_hit / "scripts" / "run_paper_benchmark.py"
    runner.parent.mkdir(parents=True)
    runner.write_text("# runner\n", encoding="utf-8")

    assert benchmark.download_tsdecompose_benchmark(cache_dir=tmp_path, code_prefix="cached") == cache_hit


def test_download_tsdecompose_benchmark_error_paths(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(benchmark, "_read_json_url", lambda url: [])
    with pytest.raises(benchmark.BenchmarkSourceError, match="No files found"):
        benchmark.download_tsdecompose_benchmark(cache_dir=tmp_path)

    monkeypatch.setattr(
        benchmark,
        "_read_json_url",
        lambda url: [{"type": "file", "path": "code/TSDecompose/README.md"}],
    )
    monkeypatch.setattr(
        benchmark,
        "_download_file",
        lambda url, target: target.parent.mkdir(parents=True, exist_ok=True)
        or target.write_text("# file\n", encoding="utf-8"),
    )

    with pytest.raises(benchmark.BenchmarkSourceError, match="missing runner"):
        benchmark.download_tsdecompose_benchmark(cache_dir=tmp_path, force=True)


def test_ensure_tsdecompose_benchmark_accepts_local_source(tmp_path) -> None:
    source_dir = tmp_path / "code" / "TSDecompose"
    runner = source_dir / "scripts" / "run_paper_benchmark.py"
    runner.parent.mkdir(parents=True)
    runner.write_text("# runner\n", encoding="utf-8")

    assert benchmark.ensure_tsdecompose_benchmark(source_dir) == source_dir


def test_ensure_tsdecompose_benchmark_downloads_when_no_local_source(monkeypatch, tmp_path) -> None:
    target = tmp_path / "downloaded"
    monkeypatch.setattr(benchmark, "download_tsdecompose_benchmark", lambda **kwargs: target)

    assert benchmark.ensure_tsdecompose_benchmark(cache_dir=tmp_path, force_download=True) == target


def test_ensure_tsdecompose_benchmark_rejects_missing_runner(tmp_path) -> None:
    with pytest.raises(benchmark.BenchmarkSourceError, match="Cannot find benchmark runner"):
        benchmark.ensure_tsdecompose_benchmark(tmp_path)


def test_run_tsdecompose_benchmark_builds_smoke_command(monkeypatch, tmp_path) -> None:
    source_dir = tmp_path / "code" / "TSDecompose"
    runner = source_dir / "scripts" / "run_paper_benchmark.py"
    runner.parent.mkdir(parents=True)
    runner.write_text("# runner\n", encoding="utf-8")
    out_dir = tmp_path / "out"
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return SimpleNamespace(returncode=0, stdout="ok\n", stderr="")

    monkeypatch.setattr(benchmark.subprocess, "run", fake_run)

    result = benchmark.run_tsdecompose_benchmark(
        benchmark_dir=source_dir,
        out_dir=out_dir,
        methods="stl",
        n_samples=1,
        no_aggregate=True,
    )

    command = captured["command"]
    assert str(runner) in command
    assert "--smoke" in command
    assert command[command.index("--methods") + 1] == "stl"
    assert command[command.index("--n-samples") + 1] == "1"
    assert "--no-aggregate" in command
    assert captured["kwargs"]["cwd"] == source_dir
    assert result.stdout == "ok\n"
    assert result.leaderboard_path == out_dir / "leaderboard.csv"


def test_run_tsdecompose_benchmark_covers_full_command_without_check(monkeypatch, tmp_path) -> None:
    source_dir = tmp_path / "code" / "TSDecompose"
    runner = source_dir / "scripts" / "run_paper_benchmark.py"
    runner.parent.mkdir(parents=True)
    runner.write_text("# runner\n", encoding="utf-8")
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["env"] = kwargs["env"]
        return SimpleNamespace(returncode=3, stdout="out", stderr="err")

    monkeypatch.setattr(benchmark.subprocess, "run", fake_run)

    result = benchmark.run_tsdecompose_benchmark(
        benchmark_dir=source_dir,
        smoke=False,
        methods=None,
        seeds="",
        plots=True,
        env={"DETIME_TEST_ENV": "1"},
        check=False,
    )

    assert result.ok is False
    assert "--smoke" not in captured["command"]
    assert "--plots" in captured["command"]
    assert captured["env"]["DETIME_TEST_ENV"] == "1"


def test_run_tsdecompose_benchmark_raises_on_failure(monkeypatch, tmp_path) -> None:
    source_dir = tmp_path / "code" / "TSDecompose"
    runner = source_dir / "scripts" / "run_paper_benchmark.py"
    runner.parent.mkdir(parents=True)
    runner.write_text("# runner\n", encoding="utf-8")

    monkeypatch.setattr(
        benchmark.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=2, stdout="", stderr="failed"),
    )

    with pytest.raises(benchmark.BenchmarkRunError) as excinfo:
        benchmark.run_tsdecompose_benchmark(benchmark_dir=source_dir)

    assert excinfo.value.result.returncode == 2
    assert excinfo.value.result.stderr == "failed"
