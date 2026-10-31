# SPDX-License-Identifier: BSD-3-Clause
"""Computed teaching traces for DeTime's classical decomposition paths.

The synthetic arrays explain operations; the equality checks only verify that
the trace reaches the configured implementation output. They are not accuracy
or runtime benchmarks. STL's local LOESS illustration is explicitly separated
from exact statsmodels iteration checkpoints.
"""
from __future__ import annotations

import numpy as np

from .common import (
    AnimationSpec, Frame, Line, Panel, Parameter, Reference, Step, phase,
    teaching_signal,
)


SSA_REFERENCE = Reference(
    "Golyandina and Zhigljavsky (2020), Singular Spectrum Analysis for Time Series",
    "https://link.springer.com/book/10.1007/978-3-662-62436-4",
)
STL_REFERENCE = Reference(
    "Cleveland et al. (1990), STL: A Seasonal-Trend Decomposition Procedure Based on Loess",
    "https://www.scb.se/contentassets/ca21efb41fee47d293bbee5bf7be7fb3/stl-a-seasonal-trend-decomposition-procedure-based-on-loess.pdf",
)
STD_REFERENCE = Reference(
    "Dudek (2022), STD: A Seasonal-Trend-Dispersion Decomposition of Time Series",
    "https://arxiv.org/abs/2204.10398",
)
STL_API = Reference(
    "statsmodels STL: parameters and implementation contract",
    "https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.STL.html",
)


def _result(method, y, params):
    from detime import DecompositionConfig, decompose

    return decompose(y, DecompositionConfig(
        method=method, backend="python", speed_mode="exact", params=params,
    ))


def _error(a, b):
    return float(np.max(np.abs(np.asarray(a) - np.asarray(b))))


def _line(y, label="", color="blue", x=None, **kwargs):
    return Line(np.asarray(y), label=label, color=color, x=x, **kwargs)


def _pick(progress, count):
    return min(count - 1, int(round(progress * (count - 1))))


def _sum_or_zero(modes, indices, shape):
    return np.sum(modes[indices], axis=0) if indices else np.zeros(shape)


def _ssa_spec(multivariate=False):
    from detime.methods.ssa import _basic_ssa, _diagonal_averaging
    from detime.methods.mssa import _build_mssa_trajectory, _reconstruct_mode
    from detime.methods.utils import dominant_frequency

    method = "MSSA" if multivariate else "SSA"
    t, base, _, _, _ = teaching_signal()
    window, rank, period = 36, 8, 24
    if multivariate:
        rng = np.random.default_rng(72)
        y = np.column_stack([
            base,
            0.7 * base + 0.23 * np.sin(2 * np.pi * t / period + 0.45),
            1.2 * base + 0.20 * np.cos(2 * np.pi * t / period + 0.20),
        ]) + 0.025 * rng.normal(size=(len(t), 3))
        trajectory = _build_mssa_trajectory(y, window)
        channels = y.shape[1]
    else:
        y = base
        trajectory = np.lib.stride_tricks.sliding_window_view(y, window).T.copy()
        channels = 1
    n, columns = len(t), trajectory.shape[1]
    u, singular, vt = np.linalg.svd(trajectory, full_matrices=False)
    matrices = np.asarray([np.outer(u[:, j], singular[j] * vt[j]) for j in range(rank)])
    if multivariate:
        modes = np.asarray([
            _reconstruct_mode(matrix, window, channels, n) for matrix in matrices
        ])
    else:
        modes = np.asarray([_diagonal_averaging(matrix) for matrix in matrices])
    params = {"window": window, "rank": rank, "primary_period": period}
    result = _result(method, y, params)
    trend_indices = list(result.meta["trend_components"])
    season_indices = list(result.meta["season_components"])
    freqs = np.array([
        dominant_frequency(np.mean(mode, axis=1) if multivariate else mode)
        for mode in modes
    ])
    group_colors = [
        "teal" if j in trend_indices else "orange" if j in season_indices else "gray"
        for j in range(rank)
    ]
    rr, cc = np.indices((window, columns))
    groups_text = "Trend: " + str(trend_indices) + "\nSeason: " + str(season_indices)
    if multivariate:
        equality = _error(modes, result.components["modes"])
    else:
        equality = _error(modes, np.asarray(_basic_ssa(y, window, rank)))
    checks = {
        "trace_modes_vs_implementation_max_abs_error": equality,
        "grouped_trend_max_abs_error": _error(_sum_or_zero(modes, trend_indices, y.shape), result.trend),
        "grouped_season_max_abs_error": _error(_sum_or_zero(modes, season_indices, y.shape), result.season),
        "additive_reconstruction_max_abs_error": _error(y, result.trend + result.season + result.residual),
        "full_svd_matrix_reconstruction_max_abs_error": _error(trajectory, (u * singular) @ vt),
    }

    def observed_panel(cursor=None, span=None):
        return Panel(
            "Aligned input channels" if multivariate else "Observed series and window",
            lines=[_line(y[:, j], f"Channel {j + 1}", c) for j, c in enumerate(["blue", "teal", "purple"])]
            if multivariate else [_line(y, "Observed")],
            vline=cursor, span=span,
        )

    def make_frame(index, total):
        stage, p = phase(index, total)
        cursor = _pick(p, n)
        if stage == 0:
            col = _pick(p, columns)
            shown = trajectory[:, :col + 1]
            counts = np.bincount((rr[:, :col + 1] + cc[:, :col + 1]).ravel(), minlength=n)
            segment = y[col:col + window]
            panels = [
                observed_panel(span=(col, col + window - 1)),
                Panel("Stacked trajectory matrix" if multivariate else "Hankel trajectory matrix",
                      image=shown, vmin=float(trajectory.min()), vmax=float(trajectory.max()),
                      extent=(-0.5, col + 0.5, -0.5, trajectory.shape[0] - 0.5),
                      xlim=(-0.5, columns - 0.5),
                      xlabel="Window start", ylabel="Channel blocks / lag" if multivariate else "Lag"),
                Panel("Values in the current window",
                      lines=[_line(segment[:, j], f"Channel {j + 1}", c)
                             for j, c in enumerate(["blue", "teal", "purple"])]
                      if multivariate else [_line(segment, "Window values")], xlabel="Lag"),
                Panel("Overlapping copies of each sample", lines=[_line(counts, "Copies per channel", "purple")],
                      ylabel="Count", annotation=f"Window {col + 1}/{columns}; L={window}"),
            ]
            caption = "Each channel uses the same window positions; its lag matrix occupies a separate row block." if multivariate else "Entry (lag, start) is the observed value at lag + start. Overlap creates repeated copies."
        elif stage == 1:
            k = 1 + _pick(p, rank)
            partial_matrix = matrices[:k].sum(axis=0)
            mode = modes[k - 1]
            partial = modes[:k].sum(axis=0)
            panels = [
                Panel("Singular values", bars=singular[:rank],
                      bar_labels=[str(j + 1) for j in range(rank)],
                      bar_colors=["blue" if j < k else "gray" for j in range(rank)],
                      xlabel="Mode (one-based)", ylabel="Singular value"),
                Panel(f"Matrix using the first {k} modes", image=partial_matrix,
                      xlabel="Window start", ylabel="Channel blocks / lag" if multivariate else "Lag"),
                Panel(f"Reconstructed mode {k}",
                      lines=[_line(mode[:, j], f"Channel {j + 1}", c)
                             for j, c in enumerate(["blue", "teal", "purple"])]
                      if multivariate else [_line(mode, f"Mode {k}", "purple")]),
                Panel("Cumulative reconstruction: channel 1" if multivariate else "Cumulative reconstruction",
                      lines=[_line(y[:, 0] if multivariate else y, "Observed", "gray"),
                             _line(partial[:, 0] if multivariate else partial, f"First {k} modes")]),
            ]
            caption = "SVD supplies a common set of matrix modes. More retained modes add structure, including possible noise."
        elif stage == 2:
            if multivariate:
                item = _pick(p, 3 * channels)
                mode_idx, channel = divmod(item, channels)
                matrix = matrices[mode_idx, channel * window:(channel + 1) * window]
                target = n // 2
                rc = modes[mode_idx, :, channel]
                title = f"Mode {mode_idx + 1}, channel {channel + 1}"
            else:
                mode_idx, channel = 1, 0
                matrix = matrices[mode_idx]
                target = cursor
                rc, title = modes[mode_idx], "Mode 2: anti-diagonal averaging"
            selected = rr + cc == target
            values = matrix[selected]
            panels = [
                Panel(title, image=matrix, xlabel="Window start", ylabel="Lag"),
                Panel(f"Entries representing sample {target}", image=selected.astype(float),
                      xlabel="Window start", ylabel="Lag", cmap="Blues", vmin=0.0, vmax=1.0,
                      annotation=f"Blue cells: lag + start = {target}"),
                Panel("Average the repeated estimates",
                      lines=[_line(values, "Matrix entries", "purple", marker="o"),
                             _line(np.full(len(values), np.mean(values)), "Their mean", "orange")],
                      xlabel="Copy index", annotation=f"Mean = {np.mean(values):.3f}"),
                Panel("Reconstructed time-domain mode",
                      lines=[_line(rc, "Reconstructed mode", "teal")], vline=target),
            ]
            caption = "MSSA applies anti-diagonal averaging inside each channel block; it does not average channels together." if multivariate else "All matrix entries on one anti-diagonal refer to the same time index; their mean gives one reconstructed value."
        else:
            k = 1 + _pick(p, rank)
            ti = [j for j in trend_indices if j < k]
            si = [j for j in season_indices if j < k]
            trend = _sum_or_zero(modes, ti, y.shape)
            season = _sum_or_zero(modes, si, y.shape)
            residual = y - trend - season
            if multivariate:
                panels = [
                    Panel("Grouped trends", lines=[_line(trend[:, j], f"Channel {j + 1}", c) for j, c in enumerate(["blue", "teal", "purple"])]),
                    Panel("Grouped seasonal modes", lines=[_line(season[:, j], f"Channel {j + 1}", c) for j, c in enumerate(["blue", "teal", "purple"])]),
                    Panel("Unassigned variation", lines=[_line(residual[:, j], f"Channel {j + 1}", c) for j, c in enumerate(["blue", "teal", "purple"])]),
                    Panel("Grouping uses each mode's channel mean", bars=freqs,
                          bar_labels=[str(j) for j in range(rank)], bar_colors=group_colors,
                          xlabel="Mode index (zero-based)", ylabel="Cycles / sample", annotation=groups_text),
                ]
            else:
                panels = [
                    Panel("Mode frequencies and assigned groups", bars=freqs,
                          bar_labels=[str(j) for j in range(rank)], bar_colors=group_colors,
                          xlabel="Mode index (zero-based)", ylabel="Cycles / sample", annotation=groups_text),
                    Panel("Grouped components", lines=[_line(trend, "Trend", "teal"), _line(season, "Season", "orange")]),
                    Panel("Unassigned variation", lines=[_line(residual, "Residual", "red")]),
                    Panel("Reconstruction", lines=[_line(y, "Observed", "gray"), _line(trend + season + residual, "Sum", "blue", style="--")]),
                ]
            caption = f"Assigning modes through index {k - 1}. The remaining variation stays in residual; the grouping rule is a heuristic."
        return Frame(stage, panels, caption)

    steps = [
        Step("Stack aligned windows" if multivariate else "Embed overlapping windows",
             "Use a common window length and start positions for all channels, then stack their trajectory matrices vertically. Columns describe simultaneous multichannel windows."
             if multivariate else
             "Slide an L-sample window across the series. Put each window in a column. Repeated observations lie on anti-diagonals, which is the Hankel structure used by SSA."),
        Step("Compute shared singular modes" if multivariate else "Factor the trajectory matrix",
             "Compute the exact NumPy SVD and retain the requested rank. Every matrix mode spans all channel blocks, so a mode can express related temporal structure across channels."
             if multivariate else
             "Compute X = U diag(s) V^T. Each singular triplet gives one rank-one matrix. Retaining only a chosen number of modes determines which matrix structure can enter subsequent grouping."),
        Step("Reconstruct each channel" if multivariate else "Average each anti-diagonal",
             "Split each rank-one matrix into its original channel blocks. Within each block, average entries representing the same time index to obtain one reconstructed series per channel."
             if multivariate else
             "A rank-one matrix need not itself be Hankel. Average its anti-diagonals to turn its repeated time-index estimates back into one time-domain reconstructed component."),
        Step("Group trend and season",
             "This example uses DeTime's primary-period frequency heuristic. Low-frequency modes are assigned to trend and modes near 1/period to season, with documented fallbacks if a group is empty. Residual is the observed input minus those two groups. "
             + ("For MSSA, the grouping frequency comes from the mean across channels of each reconstructed mode." if multivariate else
                "Explicit component-index lists can replace this automatic grouping.")),
    ]
    cautions = [
        "The labels trend and season come from a grouping rule; singular-value order alone does not establish physical meaning.",
        "Changing window, rank, or grouping can change components even when additive reconstruction remains exact.",
        "The animation uses backend='python', speed_mode='exact'. Native or randomized fast paths are separate numerical execution choices.",
        "This is an offline decomposition. Forecasting features must be recomputed using only observations available at each forecast origin.",
    ]
    if multivariate:
        cautions += [
            "Channel magnitudes affect the stacked SVD. Scale channels deliberately when units or amplitudes differ.",
            "The current automatic grouping uses the mean across channels; opposing phases can cancel in that mean.",
        ]
    return AnimationSpec(
        method=method,
        title="Extract shared modes across channels" if multivariate else "Turn overlapping windows into modes",
        summary="A joint trajectory-matrix SVD produces modes that are reconstructed separately for each channel."
        if multivariate else "SSA decomposes a lag matrix and maps its grouped modes back to time-domain components.",
        steps=steps, make_frame=make_frame,
        parameters=[
            Parameter("window", "Embedding length L; changes the temporal scale and matrix dimensions."),
            Parameter("rank", "Number of singular modes available for grouping; more modes can retain both signal structure and noise."),
            Parameter("primary_period", "Target period for the frequency-based seasonal grouping heuristic."),
            Parameter("trend_components / season_components", "Optional zero-based mode indices that explicitly define the groups."),
            Parameter("season_freq_tol_ratio / trend_freq_threshold", "Control the frequency bands used by automatic grouping."),
        ], cautions=cautions, references=[SSA_REFERENCE],
        trace_kind="computed operator trace",
        trace_note="The trajectory matrix, exact SVD, reconstructed modes, and grouped outputs are computed from the source algorithm. Checks compare trace modes and final groups with the configured Python implementation. The animation explains construction order, not solver wall-clock execution.",
        example_config={"method": method, "backend": "python", "speed_mode": "exact", "params": params},
        checks=checks,
        data={"t": t, "observed": y, "trajectory": trajectory, "singular_values": singular,
              "rank_one_matrices": matrices, "reconstructed_modes": modes, "dominant_frequencies": freqs,
              "trend_indices": np.asarray(trend_indices, dtype=int), "season_indices": np.asarray(season_indices, dtype=int),
              "trend": result.trend, "season": result.season, "residual": result.residual},
        source_files=[f"src/detime/methods/{method.lower()}.py", f"native/src/{method.lower()}.cpp", "src/detime/methods/utils.py"],
    )


def _std_spec(shared_shape=False):
    from detime.methods.std import compute_std_components

    method = "STDR" if shared_shape else "STD"
    period, n = 24, 139
    t, y, _, _, _ = teaching_signal(n=n, period=period, seed=29)
    # Vary the cycle scale and shape to make the retained/averaged-shape choice visible.
    y = y + (0.10 + 0.08 * (t // period)) * np.cos(4 * np.pi * t / period + 0.2 * (t // period))
    block_ranges = [(start, min(start + period, n)) for start in range(0, n, period)]
    means, scales, shapes = [], [], []
    padded_shapes = np.zeros((len(block_ranges), period))
    availability = np.zeros_like(padded_shapes, dtype=int)
    for j, (start, stop) in enumerate(block_ranges):
        block = y[start:stop]
        mean = float(np.mean(block))
        centered = block - mean
        scale = float(np.linalg.norm(centered))
        if scale > 1e-12:
            shape = centered / scale
        else:
            shape = np.zeros_like(centered)
            scale = 0.0
        means.append(mean)
        scales.append(scale)
        shapes.append(shape)
        padded_shapes[j, :len(shape)] = shape
        availability[j, :len(shape)] = 1
    means, scales = np.asarray(means), np.asarray(scales)
    running_counts = np.cumsum(availability, axis=0)
    running_shapes = np.cumsum(padded_shapes, axis=0) / np.maximum(1, running_counts)
    traced_trend = np.concatenate([np.full(stop - start, means[j])
                                  for j, (start, stop) in enumerate(block_ranges)])
    traced_dispersion = np.concatenate([np.full(stop - start, scales[j])
                                       for j, (start, stop) in enumerate(block_ranges)])
    traced_shape = np.concatenate([running_shapes[-1, :stop - start]
                                  for start, stop in block_ranges]) if shared_shape else np.concatenate(shapes)
    traced_season = traced_dispersion * traced_shape
    raw = compute_std_components(y, period=period, variant=method)
    result = _result(method, y, {"period": period})

    def make_frame(index, total):
        stage, p = phase(index, total)
        b = _pick(p, len(block_ranges))
        start, stop = block_ranges[b]
        block, shape = y[start:stop], shapes[b]
        if stage == 0:
            panels = [
                Panel("Partition the input into cycles", lines=[_line(y, "Observed")], span=(start, stop - 1)),
                Panel(f"Cycle {b + 1}: subtract its mean", lines=[_line(block, "Cycle values"), _line(np.full(len(block), means[b]), "Cycle mean", "teal")], xlabel="Phase"),
                Panel("Level of each cycle", bars=means, bar_labels=[str(j + 1) for j in range(len(means))],
                      bar_colors=["teal" if j == b else "gray" for j in range(len(means))], xlabel="Cycle", ylabel="Mean"),
                Panel("Centered cycle", lines=[_line(block - means[b], "Value - mean", "purple")], xlabel="Phase", annotation=f"Cycle length: {len(block)}\nSpecified period: {period}"),
            ]
            caption = "Trend is constant within each block. The final incomplete cycle is processed using its available samples."
        elif stage == 1:
            centered = block - means[b]
            panels = [
                Panel("Centered cycle", lines=[_line(centered, "Centered values", "purple")], xlabel="Phase"),
                Panel("Squared deviations", bars=centered ** 2, xlabel="Phase", ylabel="Squared value",
                      annotation=f"Sum = {np.sum(centered ** 2):.3f}\nSquare root = {scales[b]:.3f}"),
                Panel("Unit-length cycle shape", lines=[_line(shape, "Centered / L2 norm", "orange")], xlabel="Phase",
                      annotation=f"Shape norm = {np.linalg.norm(shape):.3f}"),
                Panel("Dispersion by cycle", bars=scales, bar_labels=[str(j + 1) for j in range(len(scales))],
                      bar_colors=["purple" if j == b else "gray" for j in range(len(scales))], xlabel="Cycle", ylabel="L2 norm"),
            ]
            caption = "Dispersion is the Euclidean norm of centered values, not a standard deviation; shape is the normalized vector."
        elif stage == 2 and shared_shape:
            average = running_shapes[b]
            partial_season = np.concatenate([scales[j] * average[:right - left]
                                             for j, (left, right) in enumerate(block_ranges)])
            overlays = [_line(shapes[j], f"Cycle {j + 1}", "gray", alpha=0.35, linewidth=1) for j in range(b + 1)]
            panels = [
                Panel("Normalized cycles seen so far", lines=overlays, xlabel="Phase"),
                Panel("Average shape at matching phases", lines=[_line(average, "Phase-wise average", "orange")], xlabel="Phase"),
                Panel("Available cycles at each phase", bars=running_counts[b], xlabel="Phase", ylabel="Count",
                      annotation="Partial cycles contribute\nonly where observed."),
                Panel("Rescale that shared shape", lines=[_line(partial_season, "Cycle scale x average shape", "orange")]),
            ]
            caption = f"STDR averages normalized shapes through cycle {b + 1}; each phase uses its own count. The average is not renormalized."
        elif stage == 2:
            panels = [
                Panel("Retain this cycle's own shape", lines=[_line(shape, "Unit shape", "orange")], xlabel="Phase"),
                Panel("Multiply by this cycle's scale", lines=[_line(scales[b] * shape, "Scale x shape", "purple"),
                                                            _line(block - means[b], "Centered input", "gray", style="--")], xlabel="Phase"),
                Panel("Add the cycle mean", lines=[_line(block, "Observed", "gray"),
                                                   _line(means[b] + scales[b] * shape, "Mean + scale x shape", "blue", style="--")], xlabel="Phase"),
                Panel("Within-cycle residual", lines=[_line(block - means[b] - scales[b] * shape, "Residual", "red")], xlabel="Phase",
                      ylim=(-0.05, 0.05), annotation="Near-zero residual is\nexpected by construction."),
            ]
            caption = "STD retains every normalized cycle shape, including its irregular fluctuations. Reconstruction follows directly from normalization."
        else:
            panels = [
                Panel("Block levels", lines=[_line(y, "Observed", "gray"), _line(result.trend, "Trend", "teal")], span=(start, stop - 1)),
                Panel("Scaled seasonal component", lines=[_line(result.season, "Season", "orange")], span=(start, stop - 1)),
                Panel("Remainder after reconstruction", lines=[_line(result.residual, "Residual", "red")], span=(start, stop - 1),
                      ylim=None if shared_shape else (-0.05, 0.05)),
                Panel(f"Cycle {b + 1}: component sum", lines=[_line(block, "Observed", "gray"),
                      _line((result.trend + result.season)[start:stop], "Trend + season", "blue"),
                      _line((result.trend + result.season + result.residual)[start:stop], "Plus residual", "teal", style="--")], xlabel="Phase"),
            ]
            caption = "STDR's residual records deviations from the shared average shape; ordinary averaging is not robust outlier weighting." if shared_shape else "A small STD residual confirms the algebraic split; it does not demonstrate denoising or forecasting accuracy."
        return Frame(stage, panels, caption)

    return AnimationSpec(
        method=method,
        title="Average normalized cycle shapes" if shared_shape else "Separate cycle level, scale, and shape",
        summary="STDR uses a phase-wise average of normalized cycle shapes, then restores each cycle's dispersion and keeps a remainder."
        if shared_shape else "STD represents each cycle using its mean, an L2 dispersion, and its own normalized shape.",
        steps=[
            Step("Partition and center cycles", "Split at the configured period, compute each block's arithmetic mean, and subtract it. DeTime assigns that mean to every sample of the block, producing a piecewise-constant trend. A final partial block uses the samples that exist."),
            Step("Separate dispersion and shape", "Compute the Euclidean norm of each centered block as its dispersion. Divide by that norm to obtain a unit-length seasonal shape. A block whose norm is below eps receives zero dispersion and a zero shape."),
            Step("Average shapes across cycles" if shared_shape else "Restore each cycle's shape",
                 "Average normalized shape entries at the same phase across cycles. For a partial cycle, increment counts only for available phases. Multiply this shared average by each cycle's own dispersion; the average shape is not normalized again."
                 if shared_shape else
                 "Multiply every cycle's own normalized shape by its own dispersion. This recovers the centered block, including irregular fluctuations. Add the block mean to reconstruct the observed values."),
            Step("Compute the common result", "Return trend, the scaled seasonal term, and residual = observed - trend - season, plus dispersion and seasonal-shape arrays. "
                 + ("Deviations from the common cycle shape remain in the residual. In the cited formulation, R denotes a remainder; the code does not perform robust reweighting."
                    if shared_shape else "Residual is approximately zero by construction for nondegenerate blocks; this behavior is part of the representation and is not a denoising result.")),
        ], make_frame=make_frame,
        parameters=[
            Parameter("period", "Block length and seasonal phase convention; a wrong period changes levels, scales, and shape alignment."),
            Parameter("eps", "Threshold below which a centered block is treated as having zero dispersion."),
            Parameter("max_period_search", "Upper bound on the FFT-based period heuristic used only when period is omitted; this animation supplies the period explicitly."),
        ],
        cautions=[
            "DeTime's STD/STDR use block means and L2 norms. Dispersion is not the sample standard deviation.",
            "STDR uses ordinary phase-wise means of normalized shapes. No robust loss, trimming, or outlier weights are used in this implementation.",
            "A partial cycle has its own mean and norm and contributes only available phases; its scale is not directly comparable to a full cycle without accounting for length.",
            "STD retains within-cycle irregular variation in its shape. STDR assigns deviations from a shared shape to the remainder.",
            "The supplied period and the starting phase define block boundaries; shifting the start changes the decomposition.",
        ], references=[STD_REFERENCE], trace_kind="computed operator trace",
        trace_note="Every stage follows compute_std_components and the corresponding native kernel: block means, Euclidean norms, phase counts, and scaling. Both direct-source and public Python outputs are compared. The final short block is intentional.",
        example_config={"method": method, "backend": "python", "params": {"period": period}},
        checks={
            "traced_block_levels_max_abs_error": _error(traced_trend, raw["trend"]),
            "traced_dispersion_max_abs_error": _error(traced_dispersion, raw["dispersion"]),
            "traced_shape_max_abs_error": _error(traced_shape, raw["seasonal_shape"]),
            "traced_season_max_abs_error": _error(traced_season, raw["season"]),
            "source_trend_max_abs_error": _error(raw["trend"], result.trend),
            "source_season_max_abs_error": _error(raw["season"], result.season),
            "source_residual_max_abs_error": _error(raw["residual"], result.residual),
            "additive_reconstruction_max_abs_error": _error(y, result.trend + result.season + result.residual),
            "phase_average_trace_max_abs_error": _error(running_shapes[-1], raw["average_seasonal_shape"]) if shared_shape else 0.0,
        },
        data={"t": t, "observed": y, "block_means": means, "block_dispersion": scales,
              "normalized_shapes_zero_padded": padded_shapes, "phase_available_mask": availability,
              "running_phase_counts": running_counts, "running_average_shapes": running_shapes,
              "sample_dispersion": traced_dispersion, "returned_seasonal_shape": traced_shape,
              "trend": result.trend, "season": result.season, "residual": result.residual},
        source_files=["src/detime/methods/std.py", "native/src/std.cpp"],
    )


def _ma_spec():
    from detime.methods.ma_baseline import _moving_average, _estimate_seasonal_indices

    t, y, _, _, _ = teaching_signal()
    n, window, period = len(y), 25, 24
    half = window // 2
    trend = _moving_average(y, window)
    detrended = y - trend
    phase_means = np.asarray([np.mean(detrended[j::period]) for j in range(period)])
    uncentered = phase_means[np.arange(n) % period]
    season = _estimate_seasonal_indices(detrended, period)
    result = _result("MA_BASELINE", y, {"trend_window": window, "season_period": period})
    padded = np.pad(y, (half, half))

    def make_frame(index, total):
        stage, p = phase(index, total)
        cursor = _pick(p, n)
        values = padded[cursor:cursor + window]
        if stage == 0:
            panels = [
                Panel("Slide a centered window", lines=[_line(y, "Observed")], span=(cursor - half, cursor + half)),
                Panel("Values used in this average", lines=[_line(values, "Window values", "purple", x=np.arange(-half, half + 1), marker="o"),
                      _line(np.full(window, values.mean()), "Mean", "teal", x=np.arange(-half, half + 1))], xlabel="Offset from center"),
                Panel("Uniform weights, including edge zeros", bars=np.full(window, 1.0 / window), xlabel="Window position", ylabel="Weight",
                      annotation=f"Sum / {window}\nOutside the record: zero"),
                Panel("Computed moving-average trend", lines=[_line(y, "Observed", "gray"), _line(trend, "Trend", "teal")], vline=cursor),
            ]
            caption = "The Python convolution uses mode='same': values outside the record are zero, and the divisor stays equal to the full window length."
        elif stage == 1:
            panels = [
                Panel("Observed and smooth level", lines=[_line(y, "Observed", "blue"), _line(trend, "Trend", "teal")], vline=cursor),
                Panel("Subtract the level", lines=[_line(detrended, "Observed - trend", "purple")], vline=cursor),
                Panel("Cycle alignment", image=detrended.reshape(-1, period), xlabel="Phase", ylabel="Cycle", cmap="coolwarm"),
                Panel("Values at the selected sample", bars=np.array([y[cursor], trend[cursor], detrended[cursor]]),
                      bar_labels=["Observed", "Trend", "Difference"], bar_colors=["blue", "teal", "purple"], xlabel="Term"),
            ]
            caption = "The detrended array is the input to the phase-average calculation; smoothing alone has not identified a seasonal pattern."
        elif stage == 2:
            q = _pick(p, period)
            ix = np.arange(q, n, period)
            partial = phase_means.copy()
            partial[q + 1:] = 0.0
            panels = [
                Panel(f"Collect phase {q}", lines=[_line(detrended, "Detrended", "gray"), _line(detrended[ix], "Matching phases", "orange", x=ix, marker="o", style="")]),
                Panel("Average across cycles", lines=[_line(detrended[ix], "Phase values", "purple", marker="o"),
                      _line(np.full(len(ix), phase_means[q]), "Phase mean", "orange")], xlabel="Cycle"),
                Panel("Estimated phase means", bars=partial, xlabel="Phase", ylabel="Mean", annotation="Unprocessed phases are zero."),
                Panel("Repeat the current phase template", lines=[_line(partial[np.arange(n) % period], "Uncentered seasonal template", "orange")]),
            ]
            caption = f"All detrended samples with index modulo {period} equal to {q} contribute to this phase mean."
        else:
            panels = [
                Panel("Center the repeated template", lines=[_line(uncentered[:period], "Before centering", "gray"), _line(season[:period], "After centering", "orange")], xlabel="Phase"),
                Panel("Trend and seasonal component", lines=[_line(trend, "Trend", "teal"), _line(season, "Season", "orange")], vline=cursor),
                Panel("Remaining variation", lines=[_line(result.residual, "Residual", "red")], vline=cursor),
                Panel("Check the additive identity", lines=[_line(y, "Observed", "gray"),
                      _line(result.trend + result.season + result.residual, "Component sum", "blue", style="--")], vline=cursor),
            ]
            caption = "DeTime subtracts the mean of the repeated seasonal array, then defines residual as the difference from trend + season."
        return Frame(stage, panels, caption)

    return AnimationSpec(
        method="MA_BASELINE", title="Smooth, fold, and average",
        summary="A centered uniform moving average supplies the trend; equal-phase means of the detrended series supply one repeated seasonal template.",
        steps=[
            Step("Slide a uniform window", "Use uniform weights over an odd-length window. DeTime increments an even requested window by one. Its NumPy mode='same' convolution uses zero extension at both ends, so the divisor remains the full window length even near an edge."),
            Step("Subtract the smooth trend", "Compute detrended = observed - trend. Folding this array into cycle rows shows the values that share each seasonal phase."),
            Step("Average seasonal phases", "For each phase offset, average the detrended values separated by season_period samples. Repeat those means along the record. If season_period is omitted, the seasonal component is identically zero."),
            Step("Center and form residual", "Subtract the mean of the complete repeated seasonal array, then return residual = observed - trend - season. This guarantees an additive identity without establishing that each assigned component is physically correct."),
        ], make_frame=make_frame,
        parameters=[
            Parameter("trend_window", "Smoothing width; even requests are advanced to the next odd integer. The animation uses 25."),
            Parameter("season_period", "Spacing between observations assigned to the same seasonal phase; omitted means no seasonal estimate."),
        ],
        cautions=[
            "This is an in-package baseline, not a reproduction of a separately published forecasting model.",
            "Zero extension pulls endpoint moving averages toward zero. Inspect boundary behavior before using the resulting components.",
            "One repeated phase template cannot express arbitrary cycle-to-cycle shape changes.",
            "Centered smoothing and full-record phase averaging use future observations relative to earlier time points; causal forecasting requires an origin-specific pipeline.",
        ], references=[Reference("DeTime moving-average baseline implementation", "https://github.com/systems-mechanobiology/DeTime/blob/main/src/detime/methods/ma_baseline.py")],
        trace_kind="computed operator trace",
        trace_note="Window values, zero extension, uniform weights, phase averages, and centering follow the Python source. Final arrays are checked against the public Python execution path.",
        example_config={"method": "MA_BASELINE", "backend": "python", "params": {"trend_window": window, "season_period": period}},
        checks={"trend_max_abs_error": _error(trend, result.trend), "season_max_abs_error": _error(season, result.season),
                "additive_reconstruction_max_abs_error": _error(y, result.trend + result.season + result.residual)},
        data={"t": t, "observed": y, "zero_padded_input": padded, "trend": trend, "detrended": detrended,
              "phase_means": phase_means, "uncentered_season": uncentered, "season": season, "residual": result.residual},
        source_files=["src/detime/methods/ma_baseline.py", "native/src/ma_baseline.cpp"],
    )


def _local_linear(values, center, neighbors=7):
    """Numerical LOESS illustration; not a replacement for statsmodels STL."""
    x = np.arange(len(values), dtype=float)
    distance = np.abs(x - center)
    bandwidth = np.sort(distance)[min(neighbors, len(x)) - 1]
    bandwidth = max(float(bandwidth), 1e-12) * (1 + 1e-12)
    weights = np.maximum(0, 1 - (distance / bandwidth) ** 3) ** 3
    design = np.column_stack([np.ones(len(x)), x - center])
    coef = np.linalg.lstsq(design * np.sqrt(weights)[:, None], values * np.sqrt(weights), rcond=None)[0]
    return weights, design @ coef


def _stl_spec(robust=False):
    from statsmodels.tsa.seasonal import STL

    method = "ROBUST_STL" if robust else "STL"
    period = 12
    t, y, _, _, _ = teaching_signal(n=144, period=period, seed=31)
    if robust:
        y[[49, 95]] += [3.8, -3.2]
    params = {"period": period, "seasonal": 7, "trend": 23, "low_pass": 13, "robust": robust}
    budgets = [0, 1, 2, 3, 5, 8, 12, 15] if robust else [1, 2, 3, 4, 5]
    fits = [STL(y, **params).fit(inner_iter=2, outer_iter=b) for b in budgets] if robust else [
        STL(y, **params).fit(inner_iter=b, outer_iter=0) for b in budgets
    ]
    result = _result(method, y, params)
    initial, final = fits[0], fits[-1]
    detrended = y - initial.trend
    initial_abs = np.abs(initial.resid)
    h = 6 * float(np.median(initial_abs))
    first_weights = np.where(initial_abs < h, (1 - (initial_abs / h) ** 2) ** 2, 0.0) if h > 0 else np.ones(len(y))
    curve_x = np.linspace(0, 1.25 * h, 100)
    curve_w = np.where(curve_x < h, (1 - (curve_x / h) ** 2) ** 2, 0.0) if h > 0 else np.ones_like(curve_x)
    phase_values = detrended[3::period]
    local_weights, local_fits = zip(*[
        _local_linear(phase_values, center, neighbors=7) for center in range(len(phase_values))
    ])
    local_weights, local_fits = np.asarray(local_weights), np.asarray(local_fits)

    def fit_panels(fit, cursor, label):
        return [
            Panel("Observed and fitted structure", lines=[_line(y, "Observed", "gray"), _line(fit.trend + fit.seasonal, label)], vline=cursor),
            Panel("Trend from the deseasonalized input", lines=[_line(y - fit.seasonal, "Observed - season", "gray"), _line(fit.trend, "Trend", "teal")], vline=cursor),
            Panel("Seasonal component", lines=[_line(fit.seasonal, "Season", "orange")], vline=cursor),
            Panel("Robustness weights" if robust else "Residual", lines=[_line(fit.weights if robust else fit.resid, "Weight" if robust else "Residual", "purple" if robust else "red")],
                  vline=cursor, ylim=(-0.05, 1.05) if robust else None),
        ]

    def make_frame(index, total):
        stage, p = phase(index, total)
        cursor = _pick(p, len(y))
        if stage == 0 and robust:
            panels = fit_panels(initial, cursor, "Initial unweighted fit")
            panels[3] = Panel("Residuals reveal unusual observations", lines=[_line(initial.resid, "Initial residual", "red")], vline=cursor)
            caption = "Start with two inner iterations and no robustness updates. The isolated spikes can affect the initial smooths."
        elif stage == 0:
            q = _pick(p, period)
            ix = np.arange(q, len(y), period)
            panels = [
                Panel("Collect equal seasonal phases", lines=[_line(y, "Observed", "gray"), _line(y[ix], "Selected phase", "orange", x=ix, marker="o", style="")]),
                Panel("One detrended phase subseries", lines=[_line(detrended[ix], "Phase values", "purple", marker="o")], xlabel="Cycle"),
                Panel("All detrended phase subseries", image=detrended.reshape(-1, period), xlabel="Phase", ylabel="Cycle", cmap="coolwarm"),
                Panel("Trend used in this illustration", lines=[_line(initial.trend, "First inner-fit trend", "teal")]),
            ]
            caption = "Seasonal smoothing works along equal-phase observations across cycles. This illustration uses the first exact checkpoint's detrended data."
        elif stage == 1 and robust:
            panels = [
                Panel("Absolute initial residuals", lines=[_line(initial_abs, "Absolute residual", "red"), _line(np.full(len(y), h), "6 x median absolute residual", "gray", style="--")], vline=cursor),
                Panel("Bisquare weight function", lines=[_line(curve_w, "Weight curve", "purple", x=curve_x),
                      _line(first_weights, "Observation weights", "orange", x=initial_abs, marker="o", style="", alpha=0.5)], xlabel="Absolute residual", ylabel="Weight", ylim=(-0.05, 1.05)),
                Panel("Weights at observation times", lines=[_line(first_weights, "First outer-update weights", "purple")], vline=cursor, ylim=(-0.05, 1.05)),
                Panel("Selected observation", bars=np.array([initial_abs[cursor], first_weights[cursor]]), bar_labels=["Abs residual", "Weight"],
                      bar_colors=["red", "purple"], xlabel="Different units", annotation=f"Sample {cursor}\nCutoff h={h:.3f}"),
            ]
            caption = "Large residuals receive small robustness weights in later smooths. The first computed weights match statsmodels' first outer update."
        elif stage == 1:
            values = phase_values
            center = _pick(p, len(values))
            weights, local_fit = local_weights[center], local_fits[center]
            panels = [
                Panel("A local linear fit in one phase", lines=[_line(values, "Phase observations", "gray", marker="o"), _line(local_fit, "Local fitted line", "teal")],
                      xlabel="Cycle", vline=center, annotation="LOESS mechanism illustration"),
                Panel("Nearby cycles receive more weight", bars=weights, xlabel="Cycle", ylabel="Tricube weight"),
                Panel("The target is the fitted center", lines=[_line(local_fit, "Local fit", "teal"),
                      _line(np.asarray([local_fit[center]]), "Center estimate", "orange", x=np.asarray([center]), marker="o", style="")], xlabel="Cycle", vline=center),
                Panel("Exact STL seasonal checkpoint", lines=[_line(initial.seasonal, "After one inner iteration", "orange")]),
            ]
            caption = "The local regression is computed for illustration. Full STL additionally applies low-pass filtering, boundary extension, and its own smoothing schedule."
        elif stage == 2:
            k = _pick(p, len(fits))
            panels = fit_panels(fits[k], cursor, f"Outer {budgets[k]}" if robust else f"Inner {budgets[k]}")
            caption = f"Exact statsmodels checkpoint: {budgets[k]} outer robustness iterations with 2 inner iterations per cycle." if robust else f"Exact statsmodels checkpoint: {budgets[k]} inner iterations, with robustness disabled."
        else:
            panels = [
                Panel("Final trend and seasonal structure", lines=[_line(result.trend, "Trend", "teal"), _line(result.season, "Season", "orange")], vline=cursor),
                Panel("Final remainder", lines=[_line(result.residual, "Residual", "red")], vline=cursor),
                Panel("Final robustness weights" if robust else "Deseasonalized observations", lines=[_line(final.weights if robust else y - result.season,
                      "Weight" if robust else "Observed - season", "purple")], vline=cursor, ylim=(-0.05, 1.05) if robust else None),
                Panel("Original signal is still reconstructed", lines=[_line(y, "Observed", "gray"),
                      _line(result.trend + result.season + result.residual, "Component sum", "blue", style="--")], vline=cursor),
            ]
            caption = "Downweighted spikes remain visible in the residual. Robust smoothing does not delete observations." if robust else "The final checkpoint uses the wrapper's default five inner iterations and no robust outer loop."
        return Frame(stage, panels, caption)

    if robust:
        steps = [
            Step("Fit initial smooths", "DeTime's ROBUST_STL selects statsmodels STL with robust=True by default. The initial inner loop estimates seasonal and trend structure before robustness weights are updated."),
            Step("Compute robustness weights", "The first outer update uses absolute residuals from the initial fit. With h equal to six times their median, the bisquare rule assigns (1 - (abs(residual)/h)^2)^2 below h and zero above h. This example computes those weights and checks them against statsmodels."),
            Step("Refit and update the weights", "Repeated outer iterations recalculate robustness weights and refit seasonal and trend smooths. Each shown checkpoint is a fresh deterministic statsmodels fit with the indicated iteration budget; it reaches the same state for that budget."),
            Step("Retain a residual", "The wrapper returns the final trend, seasonal component, and residual. Downweighted observations remain in the input, so their unexplained values appear in the residual. The animation also displays upstream weights, which the current DeTime wrapper does not export as a result component."),
        ]
    else:
        steps = [
            Step("Form seasonal-phase subseries", "After removing the current trend, collect values at the same phase in successive cycles. STL smooths along each of these subseries, allowing the seasonal pattern to vary through the record."),
            Step("Use local polynomial smoothing", "The illustrative panel computes a tricube-weighted local linear fit for one phase. Full STL also extends boundaries, applies low-pass filtering, and combines the smoothed subseries; the illustration is not a replacement implementation of those internals."),
            Step("Alternate seasonal and trend", "The seasonal estimate is subtracted to form a deseasonalized series, which is smoothed for trend. The numerical checkpoints come from exact statsmodels fits with one through five inner iterations and no outer robustness loop."),
            Step("Form the additive result", "The final five-iteration checkpoint matches the configured DeTime STL wrapper. Residual is the input minus the returned trend and seasonal component. Reconstruction consistency does not validate a unique physical interpretation."),
        ]
    checks = {
        "checkpoint_trend_max_abs_error": _error(final.trend, result.trend),
        "checkpoint_season_max_abs_error": _error(final.seasonal, result.season),
        "checkpoint_residual_max_abs_error": _error(final.resid, result.residual),
        "additive_reconstruction_max_abs_error": _error(y, result.trend + result.season + result.residual),
    }
    if robust:
        checks["first_bisquare_weights_max_abs_error"] = _error(first_weights, fits[1].weights)
    return AnimationSpec(
        method=method,
        title="Reweight observations and refit" if robust else "Smooth seasonal phases and trend",
        summary="Residual-based robustness weights limit how strongly unusual observations influence subsequent STL smooths."
        if robust else "STL alternates local seasonal and trend smoothing while retaining a residual component.",
        steps=steps, make_frame=make_frame,
        parameters=[
            Parameter("period", "Specified number of samples in a seasonal cycle; this example uses 12."),
            Parameter("seasonal", "Odd LOESS span across cycles for the seasonal subseries; smaller spans allow faster seasonal change."),
            Parameter("trend / low_pass", "Odd smoothing spans controlling trend and low-pass behavior; this example uses 23 and 13."),
            Parameter("robust", "Controls the outer reweighting loop. ROBUST_STL defaults to True; setting it False disables robustness."),
        ],
        cautions=[
            "ROBUST_STL is the registry name for statsmodels STL with its robust option. This name does not establish implementation of other published algorithms also called RobustSTL.",
            "Smoothing spans, seasonal period, endpoint handling, and outliers influence the estimated components.",
            "The animation uses statsmodels' actual checkpoints. Internal fits are restarted for each budget; frame count is not an execution-time measure.",
            "STL is an offline smoother. Use only available history when constructing forecasting features.",
        ], references=[STL_REFERENCE, STL_API],
        trace_kind="computed iteration trace" if robust else "illustrative internals + actual output",
        trace_note="All robustness weights and iteration checkpoints are computed from statsmodels; the first bisquare update is independently calculated and compared. Final arrays match DeTime's Python wrapper."
        if robust else "The local weighted regression illustrates LOESS numerically and omits STL's full low-pass and boundary machinery. Exact statsmodels inner-iteration checkpoints and final DeTime output are shown separately and compared.",
        example_config={"method": method, "backend": "python", "params": params}, checks=checks,
        data={"t": t, "observed": y, "iteration_budgets": np.asarray(budgets),
              "checkpoint_trend": np.asarray([fit.trend for fit in fits]),
              "checkpoint_season": np.asarray([fit.seasonal for fit in fits]),
              "checkpoint_residual": np.asarray([fit.resid for fit in fits]),
              "checkpoint_weights": np.asarray([fit.weights for fit in fits]),
              "first_bisquare_weights": first_weights, "bisquare_curve_residuals": curve_x,
              "bisquare_curve_weights": curve_w, "loess_phase_values": phase_values,
              "loess_local_weights": local_weights, "loess_local_fits": local_fits,
              "trend": result.trend, "season": result.season, "residual": result.residual},
        source_files=["src/detime/methods/stl.py"],
    )


def _mstl_spec():
    from statsmodels.tsa.seasonal import MSTL, STL

    n, periods, windows, iterations = 144, [12, 36], [11, 15], 2
    t = np.arange(n, dtype=float)
    y = 0.012 * t + 0.9 * np.sin(2 * np.pi * t / periods[0])
    y += 0.55 * np.cos(2 * np.pi * t / periods[1]) + 0.045 * np.random.default_rng(14).normal(size=n)
    seasonal = np.zeros((len(periods), n))
    deseas = y.copy()
    snapshots = []
    for iteration in range(iterations):
        for j, (period, window) in enumerate(zip(periods, windows)):
            old = seasonal[j].copy()
            fit_input = deseas + old
            fit = STL(fit_input, period=period, seasonal=window).fit()
            seasonal[j] = fit.seasonal
            deseas = fit_input - seasonal[j]
            snapshots.append({"pass": iteration + 1, "period": period, "input": fit_input.copy(),
                              "previous": old, "new": seasonal[j].copy(), "all": seasonal.copy(),
                              "adjusted": deseas.copy(), "trend": fit.trend.copy()})
    upstream = MSTL(y, periods=periods, windows=windows, iterate=iterations).fit()
    params = {"periods": periods, "windows": windows, "iterate": iterations, "lmbda": None}
    result = _result("MSTL", y, params)
    frequencies = np.fft.rfftfreq(n)
    spectrum = np.abs(np.fft.rfft(y - y.mean()))

    def make_frame(index, total):
        stage, p = phase(index, total)
        cursor = _pick(p, n)
        if stage == 0:
            panels = [
                Panel("One signal, two supplied periods", lines=[_line(y, "Observed")], vline=cursor),
                Panel("Spectrum of the teaching signal", lines=[_line(spectrum, "FFT magnitude", "purple", x=frequencies)], xlabel="Cycles / sample", ylabel="Magnitude", xlim=(0, 0.15), annotation="Chosen periods: 12 and 36\nThe wrapper does not infer them."),
                Panel("Fold by 12 samples", image=y.reshape(-1, periods[0]), xlabel="Phase", ylabel="Cycle"),
                Panel("Fold by 36 samples", image=y.reshape(-1, periods[1]), xlabel="Phase", ylabel="Cycle"),
            ]
            caption = "Different periods expose different repeating structures. Both seasonal periods are supplied explicitly to MSTL."
        elif stage in (1, 2):
            snap = snapshots[(stage - 1) * 2 + _pick(p, 2)]
            panels = [
                Panel(f"STL input for period {snap['period']}", lines=[_line(snap["input"], "Adjusted input")], vline=cursor),
                Panel("Replace this seasonal estimate", lines=[_line(snap["previous"], "Previous estimate", "gray"), _line(snap["new"], "Updated estimate", "orange")], vline=cursor),
                Panel("Current separate seasonal estimates", lines=[_line(snap["all"][0], "Period 12", "orange"), _line(snap["all"][1], "Period 36", "purple")], vline=cursor),
                Panel("Remove updated seasonality", lines=[_line(snap["adjusted"], "Deseasonalized so far", "gray"), _line(snap["trend"], "Current STL trend", "teal")], vline=cursor),
            ]
            caption = f"Pass {snap['pass']}: add back the old period-{snap['period']} estimate, fit its replacement, then subtract the new estimate."
        else:
            panels = [
                Panel("Upstream seasonal columns", lines=[_line(seasonal[0], "Period 12", "orange"), _line(seasonal[1], "Period 36", "purple")], vline=cursor),
                Panel("DeTime aggregates the seasons", lines=[_line(result.season, "Combined season", "orange"), _line(result.trend, "Trend", "teal")], vline=cursor),
                Panel("Residual after the last trend fit", lines=[_line(result.residual, "Residual", "red")], vline=cursor),
                Panel("Additive result in the input scale", lines=[_line(y, "Observed", "gray"), _line(result.trend + result.season + result.residual, "Component sum", "blue", style="--")], vline=cursor),
            ]
            caption = "This example uses no Box-Cox transform. The final trend comes from the last STL fit; DeTime sums upstream seasonal columns."
        return Frame(stage, panels, caption)

    return AnimationSpec(
        method="MSTL", title="Alternate between seasonal periods",
        summary="MSTL repeatedly estimates one seasonal period while removing the current estimates of the others, then returns a trend and remainder.",
        steps=[
            Step("Specify the seasonal periods", "Supply the periods and their seasonal smoothing windows. This synthetic signal contains periods 12 and 36, and both are specified explicitly. The FFT panel describes the input; it is not an automatic period-selection stage in the wrapper."),
            Step("Estimate seasonal terms", "Initialize seasonal arrays at zero. For each period in the upstream processing order, fit STL to the currently adjusted series and subtract the estimated seasonal term before processing the next period."),
            Step("Add back and refine each term", "On each later pass, add back the previous estimate for the period being updated, refit that seasonal term, and subtract its replacement. This preserves the other current seasonal estimates while refining one term at a time."),
            Step("Aggregate the common output", "Use the trend from the last STL fit and subtract it from the deseasonalized series to obtain residual. DeTime sums separate upstream seasonal columns into result.season. This animation uses lmbda=None; transformed fits require the wrapper's documented original-scale allocation."),
        ], make_frame=make_frame,
        parameters=[
            Parameter("periods", "One or more integer cycle lengths. Upstream MSTL sorts them and filters periods that are too long for the record."),
            Parameter("windows", "Odd seasonal-smoothing spans paired with the periods; this example uses 11 and 15."),
            Parameter("iterate", "Number of passes over the seasonal terms; this example uses two."),
            Parameter("lmbda", "Optional Box-Cox transform. None keeps the additive trace in the original scale; transformed components cannot be inverted independently and then simply added."),
            Parameter("stl_kwargs", "Options forwarded to each STL fit, including its robustness setting."),
        ],
        cautions=[
            "Choose periods with enough observed repetitions. The example is illustrative and does not identify periods from data.",
            "Closely related periods and smoothing choices can change how variation is allocated between seasonal terms.",
            "DeTime's common season field is the sum of upstream seasonal columns; individual periods in this animation are instrumented from the upstream procedure.",
            "For Box-Cox fits, DeTime uses inverse(T) for trend and inverse(T+S)-inverse(T) for combined season, with the remaining difference in residual. This no-transform trace does not animate that nonlinear allocation.",
        ], references=[
            Reference("Bandara, Hyndman, and Bergmeir (2025), MSTL", "https://www.inderscience.com/info/e_inarticle.php?artid=143957"),
            Reference("statsmodels MSTL implementation contract", "https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.MSTL.html"),
            STL_REFERENCE,
        ], trace_kind="computed upstream procedure trace",
        trace_note="The alternating STL loop follows the installed statsmodels MSTL.fit procedure with an explicit two-period, no-transform setup. Its separate seasonal estimates, final trend, and public DeTime output are checked numerically.",
        example_config={"method": "MSTL", "backend": "python", "params": params},
        checks={
            "separate_seasons_vs_upstream_max_abs_error": _error(seasonal.T, upstream.seasonal),
            "trace_trend_vs_upstream_max_abs_error": _error(snapshots[-1]["trend"], upstream.trend),
            "aggregate_season_max_abs_error": _error(seasonal.sum(axis=0), result.season),
            "trend_max_abs_error": _error(upstream.trend, result.trend),
            "residual_max_abs_error": _error(deseas - snapshots[-1]["trend"], result.residual),
            "additive_reconstruction_max_abs_error": _error(y, result.trend + result.season + result.residual),
        },
        data={"t": t, "observed": y, "periods": np.asarray(periods), "windows": np.asarray(windows),
              "snapshot_inputs": np.asarray([snap["input"] for snap in snapshots]),
              "snapshot_old_seasons": np.asarray([snap["previous"] for snap in snapshots]),
              "snapshot_new_seasons": np.asarray([snap["new"] for snap in snapshots]),
              "snapshot_all_seasons": np.asarray([snap["all"] for snap in snapshots]),
              "snapshot_adjusted": np.asarray([snap["adjusted"] for snap in snapshots]),
              "upstream_seasonal_columns": seasonal.T, "trend": result.trend,
              "season": result.season, "residual": result.residual},
        source_files=["src/detime/methods/stl.py"],
    )


def build_specs() -> list[AnimationSpec]:
    """Build the eight classical traces once, ready for the shared renderer."""
    return [
        _ssa_spec(), _ssa_spec(multivariate=True), _std_spec(),
        _std_spec(shared_shape=True), _stl_spec(), _mstl_spec(),
        _stl_spec(robust=True), _ma_spec(),
    ]
