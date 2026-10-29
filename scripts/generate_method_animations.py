# SPDX-License-Identifier: BSD-3-Clause
"""Render, document, and audit the registry-complete method teaching GIFs.

Rendering uses small deterministic numerical traces. ``--check`` validates
committed artifacts without importing optional algorithm backends.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import html
import importlib
from importlib.metadata import PackageNotFoundError, version
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import textwrap
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _repo_source import prefer_repo_source

prefer_repo_source(ROOT)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
from PIL import Image, ImageChops

from detime import MethodRegistry
from method_animations.common import AnimationSpec, COLORS, Frame, Panel


ASSETS = ROOT / "docs/assets/generated/method-animations"
MANIFEST = ASSETS / "manifest.json"
START = "<!-- detime:method-animation:start -->"
END = "<!-- detime:method-animation:end -->"
INDEX_START = "<!-- detime:animation-index:start -->"
INDEX_END = "<!-- detime:animation-index:end -->"
WIDTH, HEIGHT = 1280, 820
GROUPS = {
    "classical": {"SSA", "MSSA", "STD", "STDR", "STL", "MSTL", "ROBUST_STL", "MA_BASELINE"},
    "adaptive": {"EMD", "CEEMDAN", "VMD", "WAVELET", "MVMD", "MEMD", "GABOR_CLUSTER"},
    "neural": {
        "AMD_BLOCK", "AUTOFORMER_BLOCK", "DELELSTM_BLOCK", "DLINEAR_BLOCK",
        "FREQMOE_BLOCK", "INPARFORMER_BLOCK", "LEDDAM_BLOCK",
        "MOVING_AVERAGE_DECOMPOSITION_BLOCK", "NBEATS_INTERPRETABLE",
        "PARSIMONY_BLOCK", "ST_MTM_BLOCK", "TIMEKAN_BLOCK", "TIMES2D_BLOCK",
        "WAVEFORM_BLOCK", "WAVELETMIXER_BLOCK", "XPATCH_BLOCK",
    },
}


def slug(method: str) -> str:
    return method.lower().replace("_", "-")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def color(value: str) -> str:
    return COLORS.get(value, value)


def render_provenance(spec: AnimationSpec) -> dict:
    """Capture the sources and environment that actually produced one trace."""
    group = next(name for name, methods in GROUPS.items() if spec.method in methods)
    sources = {
        Path(__file__), ROOT / "scripts/method_animations/common.py",
        ROOT / f"scripts/method_animations/{group}.py",
        ROOT / "src/detime/registry.py", ROOT / "src/detime/core.py",
        ROOT / "src/detime/backends.py",
        *(ROOT / source for source in spec.source_files),
    }
    dependencies = {}
    for distribution in ["numpy", "scipy", "statsmodels", "matplotlib", "Pillow",
                         "PyWavelets", "EMD-signal", "vmdpy", "PySDKit"]:
        try:
            dependencies[distribution] = version(distribution)
        except PackageNotFoundError:
            dependencies[distribution] = "not installed"
    return {
        "python_version": platform.python_version(), "dependencies": dependencies,
        "source_hashes": {p.relative_to(ROOT).as_posix(): sha256(p) for p in sorted(sources)},
    }


def verify_render_provenance(row: dict) -> list[str]:
    provenance = row.get("render_provenance", {})
    hashes = provenance.get("source_hashes", {})
    if not hashes or not provenance.get("dependencies") or not provenance.get("python_version"):
        return [f"{row['method']}: missing render provenance; regenerate this animation"]
    errors = []
    for source, digest in hashes.items():
        path = ROOT / source
        if not path.is_file() or sha256(path) != digest:
            errors.append(f"{row['method']}: source changed: {source}; regenerate this animation")
    return errors


def _plot_panel(ax, panel: Panel) -> None:
    ax.set_facecolor("#FFFFFF")
    ax.set_title(textwrap.fill(panel.title, 52), loc="left", fontsize=11, fontweight="bold", pad=11)
    ax.spines[["top", "right"]].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#CBD5E1")
    ax.tick_params(labelsize=9, colors="#536078", length=3)
    ax.grid(axis="y", color="#E7EBF2", linewidth=0.6, zorder=0)
    if panel.image is not None:
        arr = np.asarray(panel.image)
        if arr.ndim != 2 or not np.isfinite(arr).all():
            raise ValueError(f"invalid heatmap: {panel.title}")
        ax.imshow(arr, aspect="auto", origin="lower", cmap=panel.cmap,
                  vmin=panel.vmin, vmax=panel.vmax, extent=panel.extent, interpolation="nearest")
        ax.grid(False)
    if panel.bars is not None:
        values = np.asarray(panel.bars)
        if not np.isfinite(values).all():
            raise ValueError(f"invalid bars: {panel.title}")
        bar_colors = [color(c) for c in panel.bar_colors] if panel.bar_colors else COLORS["blue"]
        ax.bar(np.arange(len(values)), values, color=bar_colors, alpha=0.88, zorder=2)
        if panel.bar_labels:
            ax.set_xticks(np.arange(len(values)), panel.bar_labels,
                          rotation=25 if max(map(len, panel.bar_labels)) > 9 else 0,
                          fontsize=8)
    for line in panel.lines:
        y = np.asarray(line.y)
        x = np.arange(len(y)) if line.x is None else np.asarray(line.x)
        if x.shape != y.shape or not np.isfinite(x).all() or not np.isfinite(y).all():
            raise ValueError(f"invalid line: {panel.title}/{line.label}")
        ax.plot(x, y, label=line.label or None, color=color(line.color),
                linestyle=line.style, marker=line.marker, markersize=4,
                linewidth=line.linewidth, alpha=line.alpha, zorder=3)
    if panel.span is not None:
        ax.axvspan(*panel.span, color=COLORS["blue"], alpha=0.09, zorder=1)
    if panel.vline is not None:
        ax.axvline(panel.vline, color=COLORS["orange"], linestyle="--", linewidth=1.3, zorder=4)
    if panel.xlim is not None:
        ax.set_xlim(*panel.xlim)
    if panel.ylim is not None:
        ax.set_ylim(*panel.ylim)
    ax.set_xlabel(panel.xlabel, fontsize=9, labelpad=4)
    ax.set_ylabel(panel.ylabel, fontsize=9, labelpad=4)
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(handles, labels, loc="best", fontsize=8,
                  framealpha=0.92, facecolor="white", edgecolor="#E3E8F0",
                  ncols=2 if len(handles) > 3 else 1)
    if panel.annotation:
        ax.text(0.02, 0.97, textwrap.fill(panel.annotation, 58),
                transform=ax.transAxes, va="top", fontsize=8, color=COLORS["dark"],
                bbox={"facecolor": "white", "alpha": 0.92, "edgecolor": "#DDE4EF", "pad": 4},
                zorder=6)


def render_frame(spec: AnimationSpec, index: int, count: int) -> Image.Image:
    frame: Frame = spec.make_frame(index, count)
    if len(spec.steps) != 4 or len(frame.panels) != 4 or frame.stage not in range(4):
        raise ValueError(f"{spec.method}: four stages and four panels are required")
    with plt.rc_context({"font.family": "DejaVu Sans", "text.color": COLORS["dark"],
                         "axes.labelcolor": COLORS["dark"], "axes.titlecolor": COLORS["dark"]}):
        fig = plt.figure(figsize=(WIDTH / 100, HEIGHT / 100), dpi=100, facecolor="#F5F7FC")
        title = f"{spec.method}  |  {spec.title}"
        fig.text(0.045, 0.958, title, fontsize=18 if len(title) < 80 else 15,
                 fontweight="bold", ha="left", va="top")
        summary = textwrap.shorten(spec.summary, width=148, placeholder="…")
        fig.text(0.045, 0.914, summary, fontsize=10.5, color="#52617A", va="top")
        for stage, step in enumerate(spec.steps):
            x = 0.045 + stage * 0.238
            active = stage == frame.stage
            box = FancyBboxPatch((x, 0.848), 0.222, 0.039,
                                 boxstyle="round,pad=0.004,rounding_size=0.009",
                                 facecolor=COLORS["blue"] if active else "#E6ECF8",
                                 edgecolor="none", transform=fig.transFigure)
            fig.patches.append(box)
            label = f"{stage + 1:02d}  {step.title}"
            fig.text(x + 0.012, 0.867, textwrap.shorten(label, width=33, placeholder="…"),
                     fontsize=10, fontweight="bold", color="white" if active else "#516584",
                     va="center")
        positions = [(0.075, 0.555, 0.397, 0.231), (0.568, 0.555, 0.397, 0.231),
                     (0.075, 0.19, 0.397, 0.231), (0.568, 0.19, 0.397, 0.231)]
        for position, panel in zip(positions, frame.panels):
            _plot_panel(fig.add_axes(position), panel)
        caption = frame.caption or spec.steps[frame.stage].text
        fig.text(0.045, 0.092, textwrap.fill(caption, 143), fontsize=11,
                 va="top", linespacing=1.45, color=COLORS["dark"])
        footer = f"DETIME  /  Synthetic teaching input  /  {spec.trace_kind.replace('_', ' ')}"
        fig.text(0.045, 0.026, textwrap.shorten(footer, width=142, placeholder="…"),
                 fontsize=8, color="#718099", va="center")
        fig.text(0.96, 0.026, f"{index + 1:02d}/{count:02d}", fontsize=8,
                 color="#718099", ha="right", va="center")
        fig.patches.append(plt.Rectangle((0.045, 0.011), 0.92 * (index + 1) / count,
                                         0.003, transform=fig.transFigure,
                                         facecolor=COLORS["teal"], edgecolor="none"))
        fig.canvas.draw()
        image = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[..., :3].copy())
        plt.close(fig)
        return image


def render(spec: AnimationSpec, count: int, directory: Path) -> dict:
    start = time.perf_counter()
    provenance = render_provenance(spec)
    name = slug(spec.method)
    images = [render_frame(spec, i, count) for i in range(count)]
    # A single palette avoids per-frame color shifts in heatmaps and line art.
    palette_source = Image.new("RGB", (WIDTH, HEIGHT * 4))
    for k, i in enumerate([0, count // 3, 2 * count // 3, count - 1]):
        palette_source.paste(images[i], (0, k * HEIGHT))
    palette = palette_source.quantize(colors=128, method=Image.Quantize.MEDIANCUT,
                                     dither=Image.Dither.NONE)
    frames = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in images]
    durations = [250] * count
    for i in range(count):
        if i + 1 == count or spec.make_frame(i, count).stage != spec.make_frame(i + 1, count).stage:
            durations[i] = 1000
    durations[0] = 800
    durations[-1] = 1500
    gif = directory / f"{name}.gif"
    png = directory / f"{name}.png"
    data = directory / f"{name}.npz"
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=durations,
                   loop=0, optimize=True, disposal=1)
    poster_index = max(0, count // 2 - 1)
    images[poster_index].save(png, optimize=True)
    if not spec.data:
        raise ValueError(f"{spec.method}: source arrays must accompany the GIF")
    for key, value in spec.data.items():
        arr = np.asarray(value)
        if arr.dtype.hasobject or not np.isfinite(arr).all():
            raise ValueError(f"{spec.method}: invalid source array {key}")
    np.savez_compressed(data, **spec.data)
    with Image.open(gif) as encoded:
        actual_frames = encoded.n_frames
        if actual_frames != len(frames):
            raise ValueError(f"{spec.method}: GIF lost a planned frame")
        for index, expected in enumerate(frames):
            encoded.seek(index)
            if ImageChops.difference(encoded.convert("RGB"), expected.convert("RGB")).getbbox():
                raise ValueError(f"{spec.method}: GIF delta encoding changed frame {index}")
    metadata = {
        "method": spec.method, "slug": name, "title": spec.title,
        "summary": spec.summary, "steps": [asdict(s) for s in spec.steps],
        "parameters": [asdict(p) for p in spec.parameters],
        "cautions": spec.cautions, "references": [asdict(r) for r in spec.references],
        "trace_kind": spec.trace_kind, "trace_note": spec.trace_note,
        "input_note": spec.input_note, "example_config": spec.example_config,
        "checks": spec.checks, "source_files": spec.source_files,
        "frames": actual_frames, "duration_ms": sum(durations),
        "poster_frame": poster_index,
        "width": WIDTH, "height": HEIGHT,
        "artifacts": {kind: {"file": p.name, "bytes": p.stat().st_size, "sha256": sha256(p)}
                      for kind, p in [("gif", gif), ("poster", png), ("data", data)]},
        "source_arrays": {k: list(np.asarray(v).shape) for k, v in spec.data.items()},
        "render_provenance": provenance,
    }
    if render_provenance(spec) != provenance:
        raise RuntimeError(f"{spec.method}: sources changed during rendering; rerun on stable sources")
    (directory / f"{name}.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n")
    print(f"{spec.method}: {actual_frames} frames, {gif.stat().st_size / 1024:.0f} KiB, "
          f"{time.perf_counter() - start:.1f}s", flush=True)
    return metadata


def _replace_block(text: str, start: str, end: str, block: str, *, before: str | None = None) -> str:
    marked = f"{start}\n{block.strip()}\n{end}"
    if start in text:
        return re.sub(re.escape(start) + r".*?" + re.escape(end),
                      lambda _: marked, text, flags=re.S)
    if before and before in text:
        return text.replace(before, marked + "\n\n" + before, 1)
    return text.rstrip() + "\n\n" + marked + "\n"


def explanation(row: dict) -> str:
    name, method = row["slug"], row["method"]
    asset = "../assets/generated/method-animations/"
    alt = f"{method}: " + "; ".join(s["title"] for s in row["steps"])
    lines = [
        "## How it works", "", row["summary"], "",
        f"[![{alt}]({asset}{name}.png)]({asset}{name}.gif)", "",
        row["input_note"], "",
        f"[Open GIF]({asset}{name}.gif) · [Static PNG]({asset}{name}.png) · "
        f"[Source arrays (NPZ)]({asset}{name}.npz) · [Trace metadata]({asset}{name}.json)", "",
        "### Follow the four steps", "",
    ]
    for index, step in enumerate(row["steps"], 1):
        lines.extend([f"**{index}. {step['title']}**", "", step["text"], ""])
    lines += ["### Parameters that change the result", "",
              "| Parameter | Effect on the computation |", "|---|---|"]
    for param in row["parameters"]:
        effect = param["effect"].replace("|", "\\|")
        lines.append(f"| `{param['name']}` | {effect} |")
    lines += ["", "### What this animation computes", "", row["trace_note"], ""]
    if row["cautions"]:
        lines += ["### Interpretation", ""]
        lines += [f"- {note}" for note in row["cautions"]]
        lines += [""]
    if row["trace_kind"] == "basis_illustration_untrained":
        api_note = (
            "The configuration below runs the optional Torch-based fitting path. "
            "It is a separate experiment from this GIF, whose basis coefficients were chosen "
            "explicitly for teaching. Reproduce the pictured coefficients with the animation "
            "generator and inspect them in the source-array archive."
        )
    elif method == "GABOR_CLUSTER":
        api_note = (
            "The public method requires a GaborClusterModel object or a saved model_path. "
            "The animation generator constructs an explicitly fixed teaching codebook; "
            "the arrays are included in its source archive. Supply a model before calling "
            "decompose with the configuration below."
        )
    else:
        api_note = (
            "Use this configuration with DecompositionConfig and decompose. "
            "The animation generator supplies the teaching input and records intermediate arrays."
        )
    lines += ["### Try the method", "", api_note, "", "```json",
              json.dumps(row["example_config"], indent=2), "```", "",
              f"See [the configuration reference](../config-reference.md#{method.lower()}) "
              "for the full interface and optional dependencies.", "",
              "### Sources and reproduction", ""]
    for ref in row["references"]:
        lines.append(f"- [{ref['title']}]({ref['url']})")
    for source in row["source_files"]:
        lines.append(f"- [DeTime implementation: `{source}`](https://github.com/systems-mechanobiology/DeTime/blob/main/{source})")
    lines += ["", f"Regenerate this animation with `python scripts/generate_method_animations.py --methods {method}`.",
              "The [reproduction guide](../maintenance/method-animations.md) explains the environment,",
              "numerical checks, coverage manifest, and how to inspect the stored arrays.", ""]
    return "\n".join(lines)


def index_block(rows: list[dict]) -> str:
    catalog = {e["name"]: e for e in MethodRegistry.list_catalog()}
    lines = [
        "## Animated method explanations", "",
        f"Explore all **{len(rows)} registered method entries** through a four-step GIF,",
        "an English explanation, parameter guidance, and the numerical arrays behind the plots.",
        "Open a method and choose **Play animation**. Each page also provides a static image",
        "and direct GIF download. Examples use synthetic signals chosen to expose the mechanism.", "",
        "Aliases and experimental blocks are identified below. Their pages explain the operator",
        "implemented by DeTime and its relationship to the source architecture.", "",
    ]
    for group, title in [("classical", "Smoothing, seasonal structure, and subspaces"),
                         ("adaptive", "Adaptive modes, wavelets, and time-frequency structure"),
                         ("neural", "Experimental decomposition blocks")]:
        lines += [f"### {title}", "", "| Method | Mechanism to watch | Scope |", "|---|---|---|"]
        for row in rows:
            if row["method"] not in GROUPS[group]:
                continue
            entry = catalog[row["method"]]
            scope = f"Alias of `{entry['alias_of']}`" if entry.get("alias_of") else entry["maturity"]
            steps = " → ".join(s["title"] for s in row["steps"])
            lines.append(f"| [{row['method']}](gallery/{row['slug']}.md#how-it-works) | {steps} | {scope} |")
        lines += [""]
    lines += ["[Reproduce or audit the animations](maintenance/method-animations.md).", ""]
    return "\n".join(lines)


def write_docs(rows: list[dict]) -> None:
    catalog = {e["name"]: e for e in MethodRegistry.list_catalog()}
    for row in rows:
        path = ROOT / "docs/gallery" / f"{row['slug']}.md"
        if path.exists():
            text = path.read_text()
        else:
            entry = catalog[row["method"]]
            title = f"{row['method']}: {row['title']}"
            text = ("---\n" + f"title: {json.dumps(title)}\n"
                    + f"description: {json.dumps(row['method'] + ': ' + textwrap.shorten(row['summary'], width=145))}\n" + "---\n\n"
                    + f"# {row['title']}\n\n"
                    + "[Back to methods](../methods.md#animated-method-explanations)\n\n"
                    + f"**Method:** `{row['method']}`. **Status:** {entry['maturity']}. "
                    + f"**Implementation:** {entry['implementation']}.\n")
        block = explanation(row)
        path.write_text(_replace_block(text, START, END, block, before="## Code"), encoding="utf-8")
    methods = ROOT / "docs/methods.md"
    methods.write_text(_replace_block(methods.read_text(), INDEX_START, INDEX_END,
                                      index_block(rows), before="## More detail"), encoding="utf-8")


def assemble(directory: Path, *, write_pages: bool = True) -> dict:
    names = {e["name"] for e in MethodRegistry.list_catalog()}
    rows = [json.loads((directory / f"{slug(name)}.json").read_text()) for name in sorted(names)]
    errors = [error for row in rows for error in verify_render_provenance(row)]
    if errors:
        raise ValueError("Cannot assemble stale animation assets:\n" + "\n".join(errors))
    source_hashes = {}
    environments = {}
    for row in rows:
        provenance = row["render_provenance"]
        source_hashes.update(provenance["source_hashes"])
        environment = {key: provenance[key] for key in ("python_version", "dependencies")}
        environments[json.dumps(environment, sort_keys=True)] = environment
    manifest = {
        "schema_version": 2, "purpose": "numerical teaching animations; not benchmark evidence",
        "source_baseline": "c209d81fc9f9624fddf04c922c091bc86c820b60",
        "render_environments": list(environments.values()),
        "method_count": len(rows), "source_hashes": source_hashes,
        "methods": rows,
    }
    (directory / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    if write_pages:
        write_docs(rows)
    return manifest


def validate(directory: Path, *, check_docs: bool = True) -> list[str]:
    errors = []
    try:
        manifest = json.loads((directory / "manifest.json").read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return [f"manifest: {exc}"]
    expected = {e["name"] for e in MethodRegistry.list_catalog()}
    rows = manifest.get("methods", [])
    names = [r["method"] for r in rows]
    if set(names) != expected or len(names) != len(set(names)):
        errors.append("manifest does not cover the registered methods exactly once")
    for source, digest in manifest["source_hashes"].items():
        if not (ROOT / source).is_file() or sha256(ROOT / source) != digest:
            errors.append(f"source changed: {source}; regenerate affected traces and manifest")
    for row in rows:
        errors.extend(verify_render_provenance(row))
        metadata_path = directory / f"{row['slug']}.json"
        if not metadata_path.is_file() or json.loads(metadata_path.read_text()) != row:
            errors.append(f"{row['method']}: per-method metadata differs from manifest")
        for kind, artifact in row["artifacts"].items():
            path = directory / artifact["file"]
            if not path.is_file() or sha256(path) != artifact["sha256"]:
                errors.append(f"{row['method']}: missing or changed {kind}")
        try:
            with Image.open(directory / row["artifacts"]["gif"]["file"]) as im:
                if im.n_frames < 16 or im.size != (WIDTH, HEIGHT):
                    errors.append(f"{row['method']}: invalid animation dimensions or frame count")
                im.seek(im.n_frames - 1)
                im.load()
            with np.load(directory / row["artifacts"]["data"]["file"], allow_pickle=False) as arrays:
                if set(arrays.files) != set(row["source_arrays"]):
                    errors.append(f"{row['method']}: source array inventory differs")
                for key in arrays.files:
                    if list(arrays[key].shape) != row["source_arrays"][key] or not np.isfinite(arrays[key]).all():
                        errors.append(f"{row['method']}: invalid array {key}")
        except (OSError, ValueError, EOFError) as exc:
            errors.append(f"{row['method']}: unreadable artifact: {exc}")
        if row["artifacts"]["gif"]["bytes"] > 3 * 1024 * 1024:
            errors.append(f"{row['method']}: GIF exceeds 3 MiB budget")
        if check_docs:
            page = ROOT / "docs/gallery" / f"{row['slug']}.md"
            if not page.is_file() or explanation(row).strip() not in page.read_text():
                errors.append(f"{row['method']}: missing or stale English explanation")
    if check_docs and index_block(rows).strip() not in (ROOT / "docs/methods.md").read_text():
        errors.append("methods page animation index is stale")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--methods", nargs="+", help="Regenerate selected registered methods.")
    parser.add_argument("--group", choices=list(GROUPS))
    parser.add_argument("--frames", type=int, default=32)
    parser.add_argument("--output-dir", type=Path, default=ASSETS)
    parser.add_argument("--check", action="store_true", help="Audit committed assets without optional backends.")
    parser.add_argument("--assemble", action="store_true", help="Rebuild manifest and docs from existing per-method metadata.")
    parser.add_argument("--no-docs", action="store_true")
    args = parser.parse_args()
    if args.check:
        errors = validate(args.output_dir, check_docs=not args.no_docs)
        if errors:
            print("\n".join(f"ERROR: {e}" for e in errors))
            return 1
        print(f"Animation coverage, source hashes, GIFs, arrays and explanations passed for {len(MethodRegistry.list_catalog())} methods.")
        return 0
    if args.frames < 16:
        parser.error("at least 16 frames are required")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if not args.assemble:
        selected = set(args.methods or (GROUPS[args.group] if args.group else set().union(*GROUPS.values())))
        unknown = selected - set().union(*GROUPS.values())
        if unknown:
            parser.error(f"unknown methods: {sorted(unknown)}")
        for group, names in GROUPS.items():
            if not selected & names:
                continue
            module = importlib.import_module(f"method_animations.{group}")
            specs = module.build_specs()
            if {s.method for s in specs} != names:
                raise ValueError(f"{group}: trace specifications differ from declared coverage")
            for spec in specs:
                if spec.method in selected:
                    render(spec, args.frames, args.output_dir)
    names = [e["name"] for e in MethodRegistry.list_catalog()]
    if all((args.output_dir / f"{slug(name)}.json").is_file() for name in names):
        assemble(args.output_dir, write_pages=not args.no_docs)
    else:
        print("Partial render complete; assemble after every registered method has metadata.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
