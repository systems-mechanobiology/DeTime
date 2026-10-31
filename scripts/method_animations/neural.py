# SPDX-License-Identifier: BSD-3-Clause
"""Code-faithful teaching traces for DeTime's experimental neural-block surface.

Fifteen entries execute the actual nonlearned operators and verify their
outputs. N-BEATS is a separately labelled basis illustration with fixed teaching
coefficients; it never substitutes a NumPy fit for neural training.
"""
from __future__ import annotations

from typing import Callable

import numpy as np

from detime import DecompositionConfig, decompose
from detime.methods.neural_blocks import forecasting_blocks as moving
from detime.methods.neural_blocks import leddam_block as leddam
from detime.methods.neural_blocks import neural_block_portfolio as portfolio
from detime.methods.neural_blocks import xpatch_block as xpatch
from detime.registry import METHOD_REFERENCE_LINKS

from .common import (
    AnimationSpec, Frame, Line, Panel, Parameter, Reference, Step,
    phase, teaching_signal,
)


_ROOT = "src/detime/methods/neural_blocks/"
_PALETTE = ("blue", "orange", "purple", "teal", "red", "green")


def _line(y, label="", color="blue", *, x=None, style="-", alpha=1.0):
    return Line(np.asarray(y), label, x=x, color=color, style=style, alpha=alpha)


def _revealed(y: np.ndarray, progress: float) -> np.ndarray:
    count = max(1, min(len(y), 1 + int(round(progress * (len(y) - 1)))))
    return np.asarray(y[:count], dtype=float).copy()


def _series(title: str, y, *lines: Line, boundary=None, annotation=""):
    return Panel(
        title, [_line(y, "Observed", "gray", alpha=0.65), *lines],
        vline=boundary, annotation=annotation,
    )


def _final_panels(y, trend, season, residual, *, annotation=""):
    return [
        _series("Reconstruct the observed series", y,
                _line(trend + season + residual, "Sum", "blue", style="--"),
                annotation=annotation),
        Panel("Trend stream", [_line(trend, "Trend", "teal")]),
        Panel("Season / nontrend stream", [_line(season, "Season", "orange")]),
        Panel("Derived residual", [_line(residual, "Residual", "red")]),
    ]


def _refs(method: str, source: str) -> list[Reference]:
    refs = [Reference(
        "Implemented DeTime operator",
        "https://github.com/systems-mechanobiology/DeTime/blob/main/" + source,
    )]
    refs.extend(Reference(item["title"], item["url"])
                for item in METHOD_REFERENCE_LINKS.get(method, []))
    return refs


def _stable_sample_axes(frame: Frame, length: int) -> Frame:
    """Keep progressive time traces on the full-record horizontal scale."""
    for panel in frame.panels:
        if panel.bars is not None and panel.bar_labels and panel.xlabel == "Sample":
            panel.xlabel = "Component"
        if panel.xlabel == "Sample" and panel.lines and panel.xlim is None:
            if all(line.x is None for line in panel.lines):
                panel.xlim = (0, length - 1)
    return frame


def _checked(
    method: str, y: np.ndarray, params: dict,
    trend: np.ndarray, season: np.ndarray,
) -> tuple[np.ndarray, dict]:
    config = DecompositionConfig(method=method, params=params, backend="python")
    actual = decompose(y, config)
    residual = y - trend - season
    errors = {}
    for name, expected in (("trend", trend), ("season", season), ("residual", residual)):
        returned = getattr(actual, name)
        np.testing.assert_allclose(returned, expected, rtol=1e-10, atol=1e-11)
        errors[name] = float(np.max(np.abs(returned - expected)))
    return residual, {
        "public_method_executed": True,
        "method_output_max_abs_errors": errors,
        "reconstruction_max_abs_error": float(np.max(np.abs(trend + season + residual - y))),
        "validation_scope": "One deterministic teaching input; no benchmark claim.",
    }


def _spec(
    method: str, title: str, summary: str, steps: list[Step],
    make_frame: Callable[[int, int], Frame], params: dict,
    parameters: list[Parameter], cautions: list[str], source: str,
    data: dict, checks: dict,
) -> AnimationSpec:
    def stable_frame(index: int, total: int) -> Frame:
        return _stable_sample_axes(make_frame(index, total), len(data["observed"]))

    return AnimationSpec(
        method=method, title=title, summary=summary, steps=steps,
        make_frame=stable_frame, parameters=parameters, cautions=cautions,
        references=_refs(method, source), trace_kind="computed_operator_trace",
        trace_note=(
            "Intermediate arrays are computed with the implemented operator helpers. "
            "The final trend, season and residual are checked against public decompose(). "
            "The animation explains this standalone experimental block; its source "
            "architecture is cited for provenance."
        ),
        example_config={"method": method, "params": params, "backend": "python"},
        checks=checks, data=data, source_files=[source],
    )


def _filter_spec(method: str, y: np.ndarray) -> AnimationSpec:
    gaussian = method == "LEDDAM_BLOCK"
    if gaussian:
        params = {"kernel_size": 25, "sigma": 4.0}
        kernel = leddam._gaussian_kernel(25, 4.0)
        trend = leddam._replicate_pad_smooth(y, kernel)
        source = _ROOT + "leddam_block.py"
        title = "LEDDAM block: fixed Gaussian smoothing"
        summary = (
            "This standalone implementation evaluates a fixed Gaussian-weighted "
            "convolution. Its kernel is normalized to sum to one, the edge samples "
            "are replicated, and the filtered signal becomes the trend stream. "
            "Subtracting that stream from the input creates the second stream. "
            "The animation displays actual weights and local products before "
            "assembling the output. The kernel is not trained in this operator."
        )
        parameters = [
            Parameter("kernel_size", "Sets the odd filter support; even requests are rounded to an odd size and clipped to input length."),
            Parameter("sigma", "Controls the Gaussian weight spread in sample units. The example uses 4.0; the implementation default is 1.0."),
        ]
        cautions = [
            "The package computes a fixed Gaussian kernel. Its LEDDAM-inspired name does not imply trained convolution weights or the complete dual-attention architecture.",
            "Centered windows use samples on both sides of an interior point. Use only the history available at each forecast origin for forecasting features.",
            "The second stream contains everything removed by smoothing; its name does not establish periodicity. The derived residual is zero by construction.",
        ]
    else:
        params = {"moving_avg": 25}
        kernel = np.ones(25) / 25.0
        trend = moving._moving_average_block(y, 25)
        source = _ROOT + "forecasting_blocks.py"
        label = {
            "AUTOFORMER_BLOCK": "Autoformer",
            "DLINEAR_BLOCK": "DLinear",
            "MOVING_AVERAGE_DECOMPOSITION_BLOCK": "Moving-average",
        }[method]
        title = f"{label} block: moving-average split"
        summary = (
            "The implemented operator replaces each sample with a centered local "
            "mean and assigns the input minus that mean to a second stream. Edge "
            "replication maintains the original length. AUTOFORMER_BLOCK, "
            "DLINEAR_BLOCK and MOVING_AVERAGE_DECOMPOSITION_BLOCK call the same "
            "numeric implementation at equal settings; their method identifiers "
            "record provenance. The animation therefore shows the same numerical "
            "mechanism for all three, with a separate named asset for each entry."
        )
        parameters = [
            Parameter("moving_avg", "Sets the smoothing window. Larger windows average more samples; even requests become odd windows."),
            Parameter("window", "Acts as an alias after moving_avg. If neither is supplied, period hints are checked before the default window of 25."),
            Parameter("primary_period", "Can supply a window hint; this operator does not fit a periodic template."),
        ]
        cautions = [
            "The three registered moving-average block names are numerical aliases at equal configuration.",
            "This is the decomposition head. It does not execute Autoformer attention or DLinear's fitted forecasting projections.",
            "The nontrend stream can contain noise and transients. Here season = input - trend, so the derived residual is zero by construction.",
            "The centered filter uses future neighbours relative to an interior sample in a full-record analysis.",
        ]
    season = y - trend
    residual, checks = _checked(method, y, params, trend, season)
    checks["kernel_sum"] = float(kernel.sum())
    if not gaussian:
        checks["shared_operator_identifiers"] = [
            "AUTOFORMER_BLOCK", "DLINEAR_BLOCK", "MOVING_AVERAGE_DECOMPOSITION_BLOCK"
        ]
    half = len(kernel) // 2
    padded = np.pad(y, (half, half), mode="edge")
    steps = [
        Step("Specify the filter", "Inspect the normalized filter weights and the replicated-edge input window used for a local mean."),
        Step("Move along the series", "At each sample, multiply the local values by the same fixed kernel and sum them to form the trend."),
        Step("Subtract the trend", "Compute the nontrend stream as the input minus the smoothed trend, sample by sample."),
        Step("Inspect the output contract", "The two streams already reconstruct the input, leaving a derived residual of zero up to arithmetic precision."),
    ]

    def make_frame(index: int, total: int) -> Frame:
        stage, p = phase(index, total)
        center = min(len(y) - 1, int(round(p * (len(y) - 1))))
        window = padded[center:center + len(kernel)]
        if stage < 2:
            cursor = center if stage else len(y) // 3
            window = padded[cursor:cursor + len(kernel)]
            products = window * kernel
            return Frame(stage, [
                Panel("Select a local input window", [_line(y, "Observed", "gray")],
                      span=(max(0, cursor - half), min(len(y) - 1, cursor + half)),
                      vline=cursor),
                Panel("Normalized filter weights", bars=kernel, xlabel="Kernel position", ylabel="Weight",
                      annotation=f"sum(weights) = {kernel.sum():.3f}"),
                Panel("Weighted local sample values", bars=products, xlabel="Kernel position",
                      annotation=f"sum = {products.sum():.3f}"),
                _series("Assemble the smoothed trend", y,
                        _line(_revealed(trend, p if stage else 0.0), "Trend", "teal"),
                        Line(np.array([trend[cursor]]), "Local mean", x=np.array([cursor]),
                             color="orange", marker="o")),
            ], f"Sample {cursor}: the displayed weighted sum equals the implemented trend value.")
        if stage == 2:
            return Frame(stage, [
                _series("Input and smoothed trend", y, _line(trend, "Trend", "teal")),
                Panel("Subtract at the current sample", bars=np.array([y[center], trend[center], season[center]]),
                      bar_labels=["Input", "Trend", "Difference"],
                      bar_colors=["gray", "teal", "orange"]),
                Panel("Reveal the nontrend stream", [_line(_revealed(season, p), "Input - trend", "orange")]),
                Panel("Residual after both streams", [_line(residual, "Residual", "red")],
                      annotation="Defined by subtraction; approximately zero."),
            ], "Subtracting the filter output produces the second stream; no predictor is trained here.")
        return Frame(stage, _final_panels(y, trend, season, residual),
                     "A decomposition-head trace: filtering, subtraction and exact arithmetic reconstruction.")

    return _spec(method, title, summary, steps, make_frame, params, parameters,
                 cautions, source, {"observed": y, "kernel": kernel, "trend": trend,
                                   "season": season, "residual": residual}, checks)


def _xpatch_spec(y: np.ndarray) -> AnimationSpec:
    method = "XPATCH_BLOCK"
    params = {"ma_type": "ema", "alpha": 0.25, "season_smooth": 5}
    trend, season, _, _ = xpatch._xpatch_decompose(y, params)
    raw_difference = y - trend
    alternative = xpatch._ema(y, 0.65)
    residual, checks = _checked(method, y, params, trend, season)
    steps = [
        Step("Mix observation and state", "Initialize the level with the first sample, then update it as alpha times the observation plus one minus alpha times the previous level."),
        Step("Advance the recurrence", "Continue the EMA update through the record. A second, explicitly labelled alpha illustrates a parameter change."),
        Step("Smooth the difference", "This example smooths input minus trend with the requested five-sample centered mean; the remaining difference becomes residual."),
        Step("Inspect all three streams", "The final display matches the public xPatch-inspired operator at the stated configuration."),
    ]

    def make_frame(index: int, total: int) -> Frame:
        stage, p = phase(index, total)
        cursor = max(1, min(len(y) - 1, 1 + int(p * (len(y) - 2))))
        if stage < 2:
            return Frame(stage, [
                _series("EMA level follows observations", y,
                        _line(_revealed(trend, p), "EMA alpha = 0.25", "teal")),
                Panel("Two weighted update terms", bars=np.array([0.25 * y[cursor], 0.75 * trend[cursor - 1]]),
                      bar_labels=["New observation", "Previous level"],
                      annotation=f"New level = {trend[cursor]:.3f}"),
                Panel("Parameter comparison: same input", [
                    _line(trend, "alpha = 0.25", "teal"),
                    _line(alternative, "alpha = 0.65", "orange")], vline=cursor),
                Panel("Raw input minus EMA", [_line(_revealed(raw_difference, p), "Difference", "purple")]),
            ], f"EMA update at sample {cursor}; a larger alpha increases the new observation's weight.")
        if stage == 2:
            return Frame(stage, [
                Panel("Difference before smoothing", [_line(raw_difference, "Input - trend", "gray")]),
                Panel("Five equal smoothing weights", bars=np.ones(5) / 5, xlabel="Kernel position", ylabel="Weight"),
                Panel("Smooth the nontrend stream", [
                    _line(raw_difference, "Before", "gray"),
                    _line(_revealed(season, p), "After", "orange")]),
                Panel("Difference left as residual", [_line(_revealed(residual, p), "Residual", "red")]),
            ], "The optional seasonal smoother is centered; the complete configuration is not an online predictor.")
        return Frame(stage, _final_panels(y, trend, season, residual),
                     "Actual EMA plus five-sample seasonal smoothing; no dual-stream forecasting network is run.")

    return _spec(
        method, "xPatch block: exponential level updates",
        "The implemented xPatch-inspired block offers EMA and a Holt-style level/slope option named dema. "
        "This animation uses EMA with alpha = 0.25, followed by the optional five-sample smoother of the "
        "nontrend stream. It shows the exact two-term update and the effect of a second alpha. The "
        "raw EMA is one-sided; the selected centered seasonal smoother changes that information boundary.",
        steps, make_frame, params,
        [Parameter("alpha", "Weights the newest observation in the EMA level update; the other weight is 1 - alpha."),
         Parameter("ma_type", "Selects ema or the implemented Holt-style level/slope recurrence called dema."),
         Parameter("season_smooth", "Optionally smooths the nontrend stream with an odd centered mean; omission leaves a zero derived residual."),
         Parameter("beta", "Controls the slope update when ma_type='dema'; it does not affect the EMA path shown.")],
        ["This operator does not run the complete xPatch forecasting architecture.",
         "The source's dema option is a level/slope recurrence; interpret it from the code rather than assuming every library uses the same DEMA definition.",
         "With season_smooth enabled, the seasonal stream uses centered smoothing even though EMA itself is one-sided.",
         "When alpha is omitted, trend_window can derive it. Explicit alpha takes precedence."],
        _ROOT + "xpatch_block.py",
        {"observed": y, "trend": trend, "raw_difference": raw_difference,
         "season": season, "residual": residual, "alpha_065_trend": alternative}, checks,
    )


def _template_spec(method: str, y: np.ndarray) -> AnimationSpec:
    period, fraction = 24, 2 / 3
    params = {"primary_period": period, "fit_scope": "prefix", "train_fraction": fraction}
    fit_end = portfolio._fit_window(len(y), "prefix", fraction)
    slopes = np.zeros(len(y))
    if method == "AMD_BLOCK":
        windows = [13, 25, 49]
        params["multiscale_windows"] = windows
        candidates = np.array([portfolio._moving_average_trend(y, w, fit_scope="prefix", train_fraction=fraction) for w in windows])
        trend = candidates.mean(axis=0)
        title = "AMD block: average smoothing scales"
        first = "Compute several smooth trends"
        mechanism = "Several fixed moving-average windows are evaluated on the prefix, then averaged with equal weights."
        parameter = Parameter("multiscale_windows", "Sets the windows whose trends are equally averaged; this standalone operator does not learn scale weights.")
    elif method == "DELELSTM_BLOCK":
        params.update({"alpha": 0.4, "beta": 0.2})
        trend = portfolio._holt_trend(y, 0.4, 0.2, fit_scope="prefix", train_fraction=fraction)
        candidates = trend[None, :]
        level, slope = y[0], y[1] - y[0]
        slopes[0] = slope
        for i in range(1, fit_end):
            updated = 0.4 * y[i] + 0.6 * (level + slope)
            slope = 0.2 * (updated - level) + 0.8 * slope
            level = updated
            slopes[i] = slope
        slopes[fit_end:] = slope
        title = "DeLELSTM block: level, slope and phase"
        first = "Update level and slope"
        mechanism = "A Holt-style recurrence updates a level and slope on the prefix; its last slope extrapolates the trend afterward."
        parameter = Parameter("alpha / beta", "Control level and slope updates in the implemented Holt recurrence; no LSTM cell is evaluated.")
    else:
        windows = [49]
        params["trend_window"] = 49
        trend = portfolio._moving_average_trend(y, 49, fit_scope="prefix", train_fraction=fraction)
        candidates = trend[None, :]
        title = ("ST-MTM block: smooth a phase template" if method == "ST_MTM_BLOCK"
                 else "InParformer block: smooth, group, repeat")
        first = "Smooth the prefix"
        mechanism = "A centered moving average estimates the prefix trend and the final trend level is held constant afterward."
        parameter = Parameter("trend_window", "Sets the centered moving-average support on the prefix; its endpoint is extended as a constant.")
    detrended = y - trend
    raw_season = portfolio._seasonal_template(detrended, period, fit_scope="prefix", train_fraction=fraction)
    if method == "ST_MTM_BLOCK":
        params["season_smooth_window"] = 13
        season = portfolio._moving_average(raw_season, 13)
    else:
        season = raw_season
    cycles = detrended[:fit_end].reshape(-1, period)
    residual, checks = _checked(method, y, params, trend, season)
    checks["fit_end"] = fit_end
    step2 = ("Smooth the repeated template" if method == "ST_MTM_BLOCK" else "Repeat the phase template")
    steps = [
        Step(first, mechanism),
        Step("Average equal seasonal phases", "Subtract the trend on the fitting prefix. Group samples by index modulo the specified period and average each phase bucket."),
        Step(step2, "Tile the fitted phase means over the record. The ST-MTM variant additionally smooths that repeated curve with a centered mean." if method == "ST_MTM_BLOCK" else "Tile the fitted phase means over the record. The suffix does not update the template in this prefix configuration."),
        Step("Inspect the derived residual", "Compute input minus the implemented trend and seasonal estimate. This residual is part of a retrospective decomposition, not a forecast score."),
    ]

    def make_frame(index: int, total: int) -> Frame:
        stage, p = phase(index, total)
        cycle_count = max(1, min(len(cycles), int(np.ceil(p * len(cycles)))))
        bucket_mean = cycles[:cycle_count].mean(axis=0)
        if stage == 0:
            details = (
                Panel("Holt slope state", [_line(slopes, "Slope", "purple")], vline=fit_end - 0.5)
                if method == "DELELSTM_BLOCK" else
                Panel("Fixed smoothing weights", bars=np.ones(len(candidates)) / len(candidates),
                      bar_labels=[str(w) for w in windows], xlabel="Window length", ylabel="Weight")
            )
            return Frame(stage, [
                _series("Prefix used to fit the trend", y, boundary=fit_end - 0.5,
                        annotation=f"First {fit_end} samples; period = {period}"),
                Panel("Candidate trend estimates", [
                    _line(_revealed(c, p), f"Trend {i + 1}", _PALETTE[i])
                    for i, c in enumerate(candidates)], vline=fit_end - 0.5),
                details,
                Panel("Chosen trend and remaining signal", [
                    _line(trend, "Trend", "teal"), _line(detrended, "Input - trend", "gray")],
                    vline=fit_end - 0.5),
            ], "The vertical line separates the fitting prefix from the suffix; extension follows the source code.")
        if stage == 1:
            return Frame(stage, [
                Panel("Arrange prefix samples by phase", image=cycles, cmap="coolwarm",
                      xlabel="Phase within period", ylabel="Cycle"),
                Panel("Average matching phase positions", bars=bucket_mean,
                      xlabel="Phase within period", annotation=f"{cycle_count} of {len(cycles)} prefix cycles accumulated"),
                Panel("Repeat the current phase means", [
                    _line(np.tile(bucket_mean, len(y) // period), "Current template", "orange")],
                    vline=fit_end - 0.5),
                Panel("Final fitted phase template", [_line(raw_season, "Final repeated template", "purple")],
                      vline=fit_end - 0.5),
            ], "Phase averaging is shown as cumulative bucket sums; the final buckets match the implemented template.")
        if stage == 2:
            return Frame(stage, [
                Panel("Input after removing the trend", [_line(detrended, "Input - trend", "gray")], vline=fit_end - 0.5),
                Panel("Repeated phase means", [_line(raw_season, "Template", "purple")], vline=fit_end - 0.5),
                Panel("Seasonal output", [_line(_revealed(season, p), "Season", "orange")], vline=fit_end - 0.5),
                Panel("Remainder after both estimates", [_line(_revealed(residual, p), "Residual", "red")], vline=fit_end - 0.5),
            ], "Template smoothing is applied." if method == "ST_MTM_BLOCK" else "The same fitted phase values repeat across the suffix.")
        return Frame(stage, _final_panels(y, trend, season, residual),
                     "Actual standalone prefix operator; the plot does not represent a trained forecasting architecture.")

    extra = {
        "AMD_BLOCK": "The source architecture's adaptive weighting is represented here by a nonlearned, equal-weight average of fixed smoothers.",
        "DELELSTM_BLOCK": "The implemented trend is a level/slope recurrence with a phase template. No LSTM cell is trained or evaluated.",
        "INPARFORMER_BLOCK": "The computation shown contains smoothing and phase averaging. It does not execute evolutionary search or interactive parallel attention.",
        "ST_MTM_BLOCK": "The computation shown has a smoothed template. It does not perform masked-time-series pretraining.",
    }[method]
    parameters = [parameter,
                  Parameter("primary_period", "Defines phase buckets in samples; the fitting prefix must contain enough cycles for an interpretable average."),
                  Parameter("fit_scope / train_fraction", "Explicitly selects a two-thirds prefix in this example; it does not create a rolling forecasting evaluation.")]
    if method == "ST_MTM_BLOCK":
        parameters.append(Parameter("season_smooth_window", "Smooths the tiled phase estimate. It changes amplitudes and edge values after bucket averaging."))
    return _spec(
        method, title, mechanism + " The next step uses phase-wise means of the detrended prefix. "
        "The frames expose those buckets, their cumulative averages and the repeated seasonal output. " + extra,
        steps, make_frame, params, parameters,
        [extra,
         "Prefix fitting is a fixed fitting convention. It does not certify rolling causality or an out-of-sample prediction experiment.",
         "A repeated phase template assumes that the fitted seasonal shape remains useful over the displayed suffix.",
         "The residual is derived by subtraction; exact reconstruction does not validate the scientific interpretation of either component."],
        _ROOT + "neural_block_portfolio.py",
        {"observed": y, "trend_candidates": candidates, "trend": trend,
         "detrended": detrended, "prefix_phase_matrix": cycles, "raw_template": raw_season,
         "season": season, "residual": residual, "fit_end": np.array(fit_end)}, checks,
    )


def _harmonic_spec(y: np.ndarray) -> AnimationSpec:
    method = "PARSIMONY_BLOCK"
    params = {"primary_period": 24, "trend_window": 25, "num_harmonics": 2, "fit_scope": "full"}
    trend = portfolio._moving_average_trend(y, 25, fit_scope="full")
    detrended = y - trend
    design = portfolio._harmonic_design(len(y), 24, 2)
    coefficient = np.linalg.lstsq(design, detrended, rcond=None)[0]
    terms = (design * coefficient).T
    season = design @ coefficient
    residual, checks = _checked(method, y, params, trend, season)
    steps = [
        Step("Remove a smoothed trend", "Estimate the trend with a 25-sample centered mean, then form the signal to project onto harmonic basis functions."),
        Step("Build the harmonic design", "Create cosine and sine columns at the requested period and its harmonics, and solve their coefficients by ordinary least squares."),
        Step("Add fitted basis terms", "The animation adds the already fitted weighted basis terms. This is an algebraic construction, not an optimization trajectory."),
        Step("Inspect the decomposition", "The trend, harmonic projection and remaining residual match the registered standalone operator."),
    ]

    def make_frame(index: int, total: int) -> Frame:
        stage, p = phase(index, total)
        if stage == 0:
            return Frame(stage, [
                _series("Observed record", y),
                _series("Centered mean estimates trend", y, _line(_revealed(trend, p), "Trend", "teal")),
                Panel("Signal passed to harmonic fitting", [_line(detrended, "Input - trend", "gray")]),
                Panel("Chosen seasonal basis", [_line(design[:, i], f"Basis {i + 1}", _PALETTE[i]) for i in range(4)]),
            ], "Full-record fitting is explicit in this example configuration.")
        if stage == 1:
            return Frame(stage, [
                Panel("Harmonic design matrix", image=design.T, cmap="coolwarm", xlabel="Sample", ylabel="Basis column"),
                Panel("Least-squares coefficients", bars=coefficient, bar_labels=["cos 1", "sin 1", "cos 2", "sin 2"]),
                Panel("Weighted basis contributions", [_line(terms[i], f"Term {i + 1}", _PALETTE[i]) for i in range(4)]),
                Panel("Projection against its input", [_line(detrended, "Input - trend", "gray"), _line(season, "Projection", "orange")]),
            ], "Coefficients minimize squared error for the fixed harmonic design; no neural backbone is fitted.")
        if stage == 2:
            count = max(1, min(len(terms), int(np.ceil(p * len(terms)))))
            partial = terms[:count].sum(axis=0)
            return Frame(stage, [
                Panel("Weighted terms already fitted", [_line(terms[i], f"Term {i + 1}", _PALETTE[i]) for i in range(count)]),
                Panel("Add the displayed terms", [_line(partial, "Partial sum", "orange"), _line(season, "Full projection", "gray", style="--")]),
                Panel("Difference from projection input", [_line(detrended - partial, "Difference", "red")]),
                Panel("Basis contribution coefficients", bars=coefficient, bar_labels=["cos 1", "sin 1", "cos 2", "sin 2"]),
            ], f"Display {count} of {len(terms)} fixed weighted basis terms; the final sum is the seasonal projection.")
        return Frame(stage, _final_panels(y, trend, season, residual),
                     "Actual moving-average trend plus least-squares harmonic seasonality.")

    return _spec(
        method, "Parsimony block: a compact harmonic fit",
        "This implementation first smooths the observed series, then projects the remaining signal "
        "onto cosine and sine columns at a supplied period. It is a fixed-basis least-squares operator. "
        "The trace makes the design matrix, fitted coefficients and additive contributions visible; "
        "it does not reproduce a complete forecasting architecture from the cited paper.",
        steps, make_frame, params,
        [Parameter("trend_window", "Controls which structure remains after centered trend smoothing."),
         Parameter("primary_period", "Sets the base harmonic period in sample units."),
         Parameter("num_harmonics", "Adds paired cosine/sine columns. More terms increase representational capacity without guaranteeing better identification."),
         Parameter("fit_scope", "The example uses the complete record. Prefix fitting estimates coefficients on the chosen prefix and evaluates the basis over the record.")],
        ["The harmonic coefficients are fitted numerically, but this standalone operator has no trained neural backbone.",
         "Changing the supplied period changes the basis. The algorithm does not establish that the period is physically correct.",
         "The visual addition of basis terms is not the temporal sequence of a training algorithm.",
         "Full-record smoothing and fitting require an appropriate information boundary before downstream forecasting."],
        _ROOT + "neural_block_portfolio.py",
        {"observed": y, "trend": trend, "detrended": detrended, "harmonic_design": design,
         "coefficients": coefficient, "weighted_terms": terms, "season": season, "residual": residual}, checks,
    )


def _spectral_spec(method: str, y: np.ndarray) -> AnimationSpec:
    mixture = method == "FREQMOE_BLOCK"
    params = {"primary_period": 24, "trend_window": 49, "fit_scope": "full"}
    if mixture:
        params.update({"num_bands": 3, "expert_width": 128})
        count, harmonics = 3, 2
    else:
        params.update({"top_k_periods": 2, "num_harmonics": 1})
        count, harmonics = 2, 1
    trend = portfolio._moving_average_trend(y, 49, fit_scope="full")
    detrended = y - trend
    selection_input = detrended if mixture else y
    periods = portfolio._dominant_periods_from_fft(selection_input, 24, count, fit_scope="full")
    spectrum = np.abs(np.fft.rfft(selection_input - selection_input.mean()))
    spectrum[0] = 0
    frequency = np.fft.rfftfreq(len(y))
    pieces = np.array([portfolio._fourier_season(detrended, period, harmonics, fit_scope="full") for period in periods])
    season = pieces.mean(axis=0)
    residual, checks = _checked(method, y, params, trend, season)
    checks["selected_periods"] = periods
    first_design = portfolio._harmonic_design(len(y), periods[0], harmonics)
    steps = [
        Step("Separate trend and selection input", "Compute the moving-average trend. FreqMoE selects frequencies from the detrended signal; Times2D selects them from the original signal after mean removal."),
        Step("Select discrete spectral peaks", "Rank FFT magnitudes, convert bin positions into rounded integer periods, and retain distinct periods as implemented."),
        Step("Fit and average candidate seasons", "Fit a harmonic projection of the detrended signal for each selected period, then take the arithmetic mean of these projections."),
        Step("Inspect actual output streams", "The final trend, averaged projection and derived residual are checked against the public registered operator."),
    ]

    def make_frame(index: int, total: int) -> Frame:
        stage, p = phase(index, total)
        if stage == 0:
            return Frame(stage, [
                _series("Input and smoothed trend", y, _line(_revealed(trend, p), "Trend", "teal")),
                Panel("Detrended projection target", [_line(detrended, "Input - trend", "gray")]),
                Panel("Signal used to select periods", [_line(selection_input - selection_input.mean(), "Selection input", "purple")]),
                Panel("FFT magnitude", [_line(spectrum, "Magnitude", "blue", x=frequency)], xlabel="Cycles per sample"),
            ], "Frequency selection input is the detrended signal." if mixture else "Times2D's source selects periods from the original signal after removing its mean.")
        if stage == 1:
            selected = max(1, min(len(periods), int(np.ceil(p * len(periods)))))
            return Frame(stage, [
                Panel("Rank the FFT magnitudes", [_line(spectrum, "Magnitude", "blue", x=frequency)], xlabel="Cycles per sample"),
                Panel("Retained integer periods", bars=np.asarray(periods[:selected]),
                      bar_labels=[f"P{i + 1}" for i in range(selected)], ylabel="Samples per cycle"),
                Panel("First selected harmonic design", image=first_design.T, cmap="coolwarm", xlabel="Sample", ylabel="Basis column"),
                Panel("Independent seasonal projections", [_line(pieces[i], f"Period {periods[i]}", _PALETTE[i]) for i in range(selected)]),
            ], "Integer rounding and deduplication are part of this implementation's period-selection rule.")
        if stage == 2:
            selected = max(1, min(len(pieces), int(np.ceil(p * len(pieces)))))
            partial_mean = pieces[:selected].mean(axis=0)
            return Frame(stage, [
                Panel("Fitted seasonal candidates", [_line(pieces[i], f"Period {periods[i]}", _PALETTE[i]) for i in range(selected)]),
                Panel("Equal weights for selected fits", bars=np.ones(selected) / selected,
                      bar_labels=[f"P{i + 1}" for i in range(selected)], ylabel="Weight"),
                Panel("Average the projections", [_line(partial_mean, "Current mean", "orange"), _line(season, "Final mean", "gray", style="--")]),
                Panel("Difference after current mean", [_line(detrended - partial_mean, "Remainder", "red")]),
            ], "Independent harmonic fits are averaged; this standalone code has no learned routing weights.")
        return Frame(stage, _final_panels(y, trend, season, residual),
                     "Actual spectral-selection and harmonic-averaging operator; complete forecasting model not executed.")

    extra = ("The parameter expert_width determines the harmonic count by rounding expert_width / 64. "
             "It does not size a fitted mixture-of-experts network here." if mixture else
             "The operator uses rounded FFT periods and harmonic projections. It does not implement a two-dimensional derivative-mapping forecasting backbone.")
    return _spec(
        method, "FreqMoE block: average frequency fits" if mixture else "Times2D block: selected-period projections",
        "This standalone operator obtains candidate periods from an FFT magnitude ranking and fits "
        "a separate harmonic projection for each one. The selected seasonal estimate is their equal-weight "
        "average. The frames expose the selection signal, rounded periods, candidate curves and averaging "
        "operation. " + extra,
        steps, make_frame, params,
        [Parameter("trend_window", "Sets the centered moving-average trend."),
         Parameter("num_bands" if mixture else "top_k_periods", "Controls how many distinct rounded FFT periods are retained."),
         Parameter("expert_width" if mixture else "num_harmonics", "Sets harmonic capacity through round(expert_width / 64)." if mixture else "Sets the number of cosine/sine pairs in each candidate projection."),
         Parameter("fit_scope", "Explicitly full in this animation; prefix settings restrict the fitting interval.")],
        [extra,
         "A large FFT bin need not correspond to a stable physical oscillation. Trends, finite windows and rounding affect the selected periods.",
         "The independent candidate projections are averaged, rather than jointly fitted as one combined design.",
         "All coefficients use the selected fitting interval; no held-out forecast accuracy is shown."],
        _ROOT + "neural_block_portfolio.py",
        {"observed": y, "trend": trend, "detrended": detrended, "selection_input": selection_input,
         "spectrum": spectrum, "fft_frequencies": frequency, "selected_periods": np.array(periods),
         "candidate_seasons": pieces, "season": season, "residual": residual}, checks,
    )


def _timekan_spec(y: np.ndarray) -> AnimationSpec:
    method = "TIMEKAN_BLOCK"
    params = {"primary_period": 24, "trend_window": 25, "num_bands": 2,
              "kan_width": 64, "fit_scope": "prefix", "train_fraction": 2 / 3}
    fit_end = portfolio._fit_window(len(y), "prefix", 2 / 3)
    trend = portfolio._moving_average_trend(y, 25, fit_scope="prefix", train_fraction=2 / 3)
    detrended = y - trend
    periods = portfolio._dominant_periods_from_fft(detrended, 24, 2, fit_scope="prefix", train_fraction=2 / 3)
    templates = np.array([portfolio._seasonal_template(detrended, period, fit_scope="prefix", train_fraction=2 / 3) for period in periods])
    template_mean = templates.mean(axis=0)
    harmonic = portfolio._fourier_season(detrended, 24, 2, fit_scope="prefix", train_fraction=2 / 3)
    blend = float(np.clip(0.35 + 0.1 * 2, 0.25, 0.75))
    season = blend * template_mean + (1 - blend) * harmonic
    residual, checks = _checked(method, y, params, trend, season)
    checks.update({"selected_periods": periods, "template_blend_weight": blend})
    fit_values = detrended[:fit_end] - detrended[:fit_end].mean()
    spectrum = np.abs(np.fft.rfft(fit_values))
    spectrum[0] = 0
    steps = [
        Step("Smooth and inspect prefix frequencies", "Estimate the trend from the selected prefix and use the detrended prefix FFT to obtain candidate periods."),
        Step("Fit two kinds of seasonal estimate", "Average phase templates at selected periods and separately fit a harmonic projection at primary_period."),
        Step("Apply the implemented fixed blend", "Combine the template average and harmonic projection using a weight determined by num_bands. No KAN is optimized in this operator."),
        Step("Inspect the checked output", "Return the smoothed trend, blended seasonal estimate and input-minus-components residual."),
    ]

    def make_frame(index: int, total: int) -> Frame:
        stage, p = phase(index, total)
        if stage == 0:
            return Frame(stage, [
                _series("Trend fitted on a prefix", y, _line(trend, "Trend", "teal"), boundary=fit_end - 0.5),
                Panel("Detrended prefix", [_line(fit_values, "Selection input", "gray")]),
                Panel("Prefix FFT magnitude", [_line(spectrum, "Magnitude", "blue", x=np.fft.rfftfreq(fit_end))], xlabel="Cycles per sample"),
                Panel("Selected integer periods", bars=np.array(periods), bar_labels=[f"P{i + 1}" for i in range(len(periods))], ylabel="Samples per cycle"),
            ], "The prefix is explicit; a fixed suffix extension is separate from a rolling forecast experiment.")
        if stage == 1:
            return Frame(stage, [
                Panel("Templates at selected periods", [_line(c, f"Period {periods[i]}", _PALETTE[i]) for i, c in enumerate(templates)], vline=fit_end - 0.5),
                Panel("Average the templates", [_line(_revealed(template_mean, p), "Template average", "purple")], vline=fit_end - 0.5),
                Panel("Harmonic fit at primary period", [_line(_revealed(harmonic, p), "Harmonic fit", "orange")], vline=fit_end - 0.5),
                Panel("Target for both seasonal estimates", [_line(detrended, "Input - trend", "gray")], vline=fit_end - 0.5),
            ], "kan_width = 64 selects two harmonics in this code; it is not a fitted KAN layer width.")
        if stage == 2:
            return Frame(stage, [
                Panel("Fixed blend weights", bars=np.array([blend, 1 - blend]), bar_labels=["Templates", "Harmonics"], ylabel="Weight"),
                Panel("Weighted template contribution", [_line(blend * template_mean, "Template part", "purple")]),
                Panel("Weighted harmonic contribution", [_line((1 - blend) * harmonic, "Harmonic part", "orange")]),
                Panel("Sum the two contributions", [_line(_revealed(season, p), "Season", "teal")]),
            ], f"Fixed source rule: season = {blend:.2f} × template mean + {1 - blend:.2f} × harmonic fit.")
        return Frame(stage, _final_panels(y, trend, season, residual),
                     "Actual template-and-harmonic blending; no neural KAN training is represented.")

    return _spec(
        method, "TimeKAN block: template–harmonic blending",
        "The current standalone TimeKAN-inspired operator combines familiar numerical estimates. "
        "It smooths a trend, selects periods from a prefix FFT, averages phase templates, and "
        "fits a harmonic projection at the supplied primary period. A fixed rule blends the "
        "two seasonal estimates. The animation shows that rule directly; it does not portray "
        "the complete frequency-decomposition KAN architecture from the cited paper.",
        steps, make_frame, params,
        [Parameter("num_bands", "Controls the selected template periods and the fixed blend weight 0.35 + 0.1 × min(num_bands, 4), clipped by the implementation."),
         Parameter("kan_width", "Maps to max(1, kan_width // 32) harmonics in this operator."),
         Parameter("primary_period", "Sets the harmonic projection's period; FFT-selected periods define the separate templates."),
         Parameter("fit_scope / train_fraction", "The animation explicitly fits on the first two thirds of the record.")],
        ["No KAN coefficients or neural network are fitted by this standalone implementation.",
         "Template and harmonic components can overlap spectrally; the displayed blend is an explicit heuristic.",
         "Prefix fitting and suffix extension do not establish forecast accuracy or causal identification.",
         "The residual is defined from the observed series after forming both named components."],
        _ROOT + "neural_block_portfolio.py",
        {"observed": y, "trend": trend, "detrended": detrended, "templates": templates,
         "selected_periods": np.array(periods), "template_mean": template_mean,
         "harmonic_fit": harmonic, "blend_weights": np.array([blend, 1 - blend]),
         "season": season, "residual": residual}, checks,
    )


def _wavelet_spec(method: str, y: np.ndarray) -> AnimationSpec:
    import pywt

    mixer = method == "WAVELETMIXER_BLOCK"
    params = {"wavelet": "sym4" if mixer else "db4", "level": 4 if mixer else 3,
              "season_levels": [1, 2, 3] if mixer else [1, 2]}
    wavelet = pywt.Wavelet(params["wavelet"])
    level = max(1, min(params["level"], pywt.dwt_max_level(len(y), wavelet.dec_len)))
    coeffs = pywt.wavedec(y, wavelet, level=level)
    reconstructions = []
    for keep in range(len(coeffs)):
        selected = [c.copy() if i == keep else np.zeros_like(c) for i, c in enumerate(coeffs)]
        reconstructions.append(pywt.waverec(selected, params["wavelet"])[:len(y)])
    bands = np.asarray(reconstructions)
    trend, season = portfolio._wavelet_trend_season(y, wavelet_name=params["wavelet"],
                                                  level=params["level"], season_levels=params["season_levels"])
    residual, checks = _checked(method, y, params, trend, season)
    checks["all_bands_reconstruction_max_abs_error"] = float(np.max(np.abs(bands.sum(axis=0) - y)))
    checks["effective_level"] = level
    coefficient_image = np.zeros((len(coeffs), max(map(len, coeffs))))
    for i, coefficient in enumerate(coeffs):
        coefficient_image[i, :len(coefficient)] = coefficient
    band_labels = [f"cA{level}", *[f"cD{i}" for i in range(level, 0, -1)]]
    selected_details = [i for i in params["season_levels"] if 0 < i < len(coeffs)]
    steps = [
        Step("Analyze with fixed wavelet filters", "PyWavelets applies the selected analysis filters to produce approximation and detail coefficients at several resolutions."),
        Step("Reconstruct the approximation", "Keep only the coarsest approximation coefficients, zero the other coefficient arrays and apply inverse reconstruction to obtain the trend."),
        Step("Reconstruct selected detail bands", "Keep the explicitly selected coefficient-list positions and reconstruct their combined sample-aligned contribution as season."),
        Step("Inspect the remaining detail", "The residual is the observed input minus the approximation and selected details. All displayed components match the public operator."),
    ]

    def make_frame(index: int, total: int) -> Frame:
        stage, p = phase(index, total)
        if stage == 0:
            return Frame(stage, [
                _series("Observed teaching signal", y),
                Panel("Wavelet analysis filter taps", [_line(wavelet.dec_lo, "Low pass", "teal"), _line(wavelet.dec_hi, "High pass", "orange")], xlabel="Filter tap"),
                Panel("Coefficient arrays by resolution", image=coefficient_image, cmap="coolwarm", xlabel="Coefficient index", ylabel="Coefficient row",
                      annotation="Rows: " + ", ".join(band_labels) + "; zero-padded for display"),
                Panel("Inverse-reconstructed bands", [_line(bands[i], band_labels[i], _PALETTE[i]) for i in range(len(bands))]),
            ], "Coefficient arrays have different lengths; inverse reconstruction puts their contributions on the sample grid.")
        if stage == 1:
            selected = np.zeros_like(coefficient_image)
            selected[0] = coefficient_image[0]
            return Frame(stage, [
                Panel("Keep the approximation row", image=selected, cmap="coolwarm", xlabel="Coefficient index", ylabel="Coefficient row"),
                Panel("Approximation coefficients", [_line(coeffs[0], band_labels[0], "teal")], xlabel="Coefficient index"),
                _series("Inverse reconstruct the trend", y, _line(_revealed(trend, p), "Trend", "teal")),
                Panel("All details together", [_line(y - trend, "Input - approximation", "gray")]),
            ], "Unselected coefficients are zeroed; the inverse transform yields the full-length approximation.")
        if stage == 2:
            count = max(1, min(len(selected_details), int(np.ceil(p * len(selected_details)))))
            shown = selected_details[:count]
            current = bands[shown].sum(axis=0)
            selected = np.zeros_like(coefficient_image)
            selected[shown] = coefficient_image[shown]
            return Frame(stage, [
                Panel("Keep selected detail rows", image=selected, cmap="coolwarm", xlabel="Coefficient index", ylabel="Coefficient row"),
                Panel("Selected reconstructed detail bands", [_line(bands[i], band_labels[i], _PALETTE[i]) for i in shown]),
                Panel("Add the selected details", [_line(current, "Current sum", "orange"), _line(season, "Final season", "gray", style="--")]),
                Panel("Details left outside this sum", [_line(y - trend - current, "Remainder", "red")]),
            ], "season_levels indexes the coefficient list [cA_L, cD_L, …, cD_1], not the level number itself.")
        return Frame(stage, _final_panels(y, trend, season, residual),
                     "Actual fixed-wavelet decomposition head; no graph network or neural mixer is evaluated.")

    return _spec(
        method, "WaveletMixer block: combine detail bands" if mixer else "WaveForM block: reconstruct wavelet bands",
        "The implemented operator delegates the transform to PyWavelets. It reconstructs the coarsest "
        "approximation as trend and selected detail arrays as season, then derives the residual by "
        "subtraction. The animation exposes the analysis filter taps, coefficient arrays and inverse "
        "reconstructions. The WaveForM and WaveletMixer identifiers have different default wavelets "
        "and selected bands; neither operator runs the cited complete forecasting backbone.",
        steps, make_frame, params,
        [Parameter("wavelet", "Selects the fixed analysis/synthesis wavelet family; db4 and sym4 are used by these two examples."),
         Parameter("level", "Requests decomposition depth, limited by the implementation using the input length and filter length."),
         Parameter("season_levels", "Contains coefficient-list positions: 1 denotes cD_L, 2 denotes cD_(L-1), and so on; position 0 is the trend approximation.")],
        ["WaveForM's graph enhancement and WaveletMixer's trained mixing layers are outside these standalone operators.",
         "The source uses PyWavelets' default symmetric boundary extension; boundary values depend on that convention.",
         "A selected frequency-scale band is called season by the common result contract; periodic interpretation requires separate evidence.",
         "The coefficient heatmap pads unequal-length arrays with zeros for display only. Computation uses their original lengths."],
        _ROOT + "neural_block_portfolio.py",
        {"observed": y, "coefficient_display": coefficient_image, "reconstructed_bands": bands,
         "trend": trend, "season": season, "residual": residual,
         **{f"coefficient_{i}": c for i, c in enumerate(coeffs)}}, checks,
    )


def _nbeats_basis_spec(y: np.ndarray) -> AnimationSpec:
    method = "NBEATS_INTERPRETABLE"
    n, degree, harmonics = len(y), 2, 6
    normalized_time = np.linspace(0, 1, n, dtype=np.float32)
    polynomial = np.stack([normalized_time ** power for power in range(degree + 1)])
    frequencies = np.arange(1, harmonics + 1, dtype=np.float32)[:, None]
    angles = 2 * np.pi * frequencies * normalized_time[None, :]
    cosine, sine = np.cos(angles), np.sin(angles)
    mean, scale = float(y.mean()), float(y.std())
    normalized = (y - mean) / scale
    # Explicit teaching coefficients: no fitting, checkpoint or optimizer run.
    trend_back_coeff = np.array([-0.75, 1.25, 0.10])
    trend_fore_coeff = np.array([-0.85, 1.50, 0.15])
    season_back_cos = np.array([0.04, 0, 0, 0, 0, 0.04])
    season_back_sin = np.array([0, 0, 0, 0, 0, 0.75])
    season_fore_cos = np.array([0.06, 0, 0, 0, 0, 0.08])
    season_fore_sin = np.array([0, 0, 0, 0, 0, 0.95])
    trend_back = trend_back_coeff @ polynomial
    trend_fore = trend_fore_coeff @ polynomial
    season_back = season_back_cos @ cosine + season_back_sin @ sine
    season_fore = season_fore_cos @ cosine + season_fore_sin @ sine
    stack_residual = normalized - trend_back - season_back
    trend = trend_fore * scale + mean
    season = season_fore * scale
    residual = y - trend - season
    steps = [
        Step("Construct fixed basis functions", "The source creates polynomial trend bases and integer Fourier harmonics on a normalized grid from zero to one."),
        Step("Separate backcast and output weights", "An actual trained block predicts separate coefficients for backcast subtraction and output accumulation. Here both coefficient vectors are explicitly chosen teaching values."),
        Step("Pass a remainder to seasonal blocks", "Subtract the backcast contribution, then illustrate a seasonal block's separate backcast and output branches using the Fourier bases."),
        Step("Distinguish the two residuals", "The internal remainder subtracts backcasts. The public wrapper instead derives its residual from the observed input minus the accumulated trend and seasonal outputs."),
    ]

    def make_frame(index: int, total: int) -> Frame:
        stage, p = phase(index, total)
        if stage == 0:
            return Frame(stage, [
                Panel("Standardized teaching input", [_line(normalized, "Input z", "gray")], ylabel="Standardized value"),
                Panel("Polynomial trend bases", [_line(b, f"u^{i}", _PALETTE[i], x=normalized_time) for i, b in enumerate(polynomial)], xlabel="Normalized time u"),
                Panel("Selected Fourier basis functions", [
                    _line(cosine[0], "cos h=1", "blue", x=normalized_time),
                    _line(sine[0], "sin h=1", "orange", x=normalized_time),
                    _line(sine[-1], "sin h=6", "purple", x=normalized_time)], xlabel="Normalized time u"),
                Panel("Polynomial coefficient examples", [
                    _line(trend_back_coeff, "Backcast theta", "purple"),
                    _line(trend_fore_coeff, "Output theta", "teal")], xlabel="Polynomial power",
                    annotation="Chosen teaching values; no trained network."),
            ], "UNTRAINED BASIS ILLUSTRATION: the coefficients shown are selected constants, not model estimates.")
        if stage == 1:
            return Frame(stage, [
                Panel("Trend backcast from chosen weights", [_line(_revealed(trend_back, p), "Backcast", "purple")], ylabel="Standardized value"),
                Panel("Subtract backcast before next block", [_line(normalized - trend_back, "z - trend backcast", "red")], ylabel="Standardized value"),
                Panel("Separate accumulated trend output", [_line(_revealed(trend_fore, p), "Output contribution", "teal")], ylabel="Standardized value"),
                Panel("Two coefficient vectors", [
                    _line(trend_back_coeff, "Backcast theta", "purple"),
                    _line(trend_fore_coeff, "Output theta", "teal")], xlabel="Polynomial power"),
            ], "The source uses different coefficient slices for backcast subtraction and output accumulation.")
        if stage == 2:
            return Frame(stage, [
                Panel("Input to the seasonal block", [_line(normalized - trend_back, "Incoming remainder", "gray")], ylabel="Standardized value"),
                Panel("Seasonal backcast contribution", [_line(_revealed(season_back, p), "Backcast", "purple")], ylabel="Standardized value"),
                Panel("Separate seasonal output", [_line(_revealed(season_fore, p), "Output", "orange")], ylabel="Standardized value"),
                Panel("Remainder after both backcasts", [_line(stack_residual, "Internal remainder", "red")], ylabel="Standardized value"),
            ], "Fixed harmonic combinations illustrate the two branches; no fitting or checkpoint loading was performed.")
        return Frame(stage, [
            _series("Illustrative output reconstruction", y,
                    _line(trend + season + residual, "Trend + season + residual", "blue", style="--"),
                    annotation="Chosen coefficients; not a fitted result."),
            Panel("Illustrative named output streams", [_line(trend, "Trend", "teal"), _line(season, "Season", "orange")]),
            Panel("Public residual: input minus outputs", [_line(residual, "Derived residual", "red")]),
            Panel("Internal normalized remainder", [_line(stack_residual, "After backcasts", "purple")], ylabel="Standardized value"),
        ], "Public residual and internal backcast remainder are different objects in this source implementation.")

    source = _ROOT + "learned_priors.py"
    return AnimationSpec(
        method=method, title="N-BEATS: untrained basis illustration",
        summary=(
            "This teaching illustration follows the source's polynomial and Fourier basis formulas "
            "and its separate backcast/output branches. All coefficients are explicitly chosen "
            "constants. The actual NBEATS_INTERPRETABLE method trains an MLP for each decomposition "
            "call using Torch, but that optional backend is not executed for this asset. The "
            "animation explains the basis mechanism and residual bookkeeping without presenting "
            "an untrained curve as a learned decomposition."
        ),
        steps=steps, make_frame=lambda index, total: _stable_sample_axes(make_frame(index, total), n),
        parameters=[
            Parameter("degree_of_polynomial", "Sets the degree of the trend basis on the normalized full-record grid."),
            Parameter("num_harmonics", "Sets integer Fourier harmonics on normalized time; primary_period does not set these frequencies."),
            Parameter("trend_blocks / seasonality_blocks", "Set the numbers of residual-processing MLP blocks in an actual Torch execution."),
            Parameter("n_epochs / restarts / seed", "Control actual optimization when the optional method is run; they do not generate the fixed coefficients in this animation."),
        ],
        cautions=[
            "This is an untrained basis illustration. No neural checkpoint, optimization trace or public-method output is claimed for this asset.",
            "The example configuration below would train the optional method and will not reproduce the illustration's chosen coefficients.",
            "The current source standardizes using the full record before applying a prefix loss mask. fit_scope='prefix' therefore must not be described as leakage-free forecasting.",
            "The source fits a decomposition to one supplied series. Its same-length outputs do not establish generalization to unseen future observations.",
            "The public residual is recomputed from the named outputs and differs from the internal remainder produced by subtracting backcasts.",
        ],
        references=_refs(method, source), trace_kind="basis_illustration_untrained",
        trace_note=(
            "NumPy evaluates the polynomial/Fourier basis formulas with recorded, fixed teaching "
            "coefficients. Torch is not required, the public method is not run, and equality to "
            "a trained model is not asserted."
        ),
        example_config={"method": method, "backend": "python", "params": {
            "degree_of_polynomial": degree, "num_harmonics": harmonics,
            "trend_blocks": 1, "seasonality_blocks": 1, "layers": 1, "layer_size": 16,
            "fit_scope": "full", "n_epochs": 30, "restarts": 1, "device": "cpu", "seed": 42,
        }},
        checks={"public_method_executed": False, "trained_checkpoint_used": False,
                "coefficient_provenance": "Explicit fixed teaching constants in neural.py",
                "basis_formula_source_inspected": True,
                "illustrative_reconstruction_max_abs_error": float(np.max(np.abs(trend + season + residual - y)))},
        data={"observed": y, "normalized_input": normalized, "normalized_time": normalized_time,
              "polynomial_basis": polynomial, "cosine_basis": cosine, "sine_basis": sine,
              "trend_backcast_coefficients": trend_back_coeff, "trend_output_coefficients": trend_fore_coeff,
              "season_backcast_cos_coefficients": season_back_cos, "season_backcast_sin_coefficients": season_back_sin,
              "season_output_cos_coefficients": season_fore_cos, "season_output_sin_coefficients": season_fore_sin,
              "trend_backcast": trend_back, "season_backcast": season_back, "internal_remainder": stack_residual,
              "illustrative_trend_output": trend, "illustrative_season_output": season,
              "illustrative_public_residual": residual},
        source_files=[source],
    )


def build_specs() -> list[AnimationSpec]:
    """Build one independently named teaching animation per NeuralBlock entry."""
    _, y, _, _, _ = teaching_signal(n=144, period=24, seed=42)
    specs = [
        _filter_spec("AUTOFORMER_BLOCK", y),
        _filter_spec("DLINEAR_BLOCK", y),
        _filter_spec("MOVING_AVERAGE_DECOMPOSITION_BLOCK", y),
        _filter_spec("LEDDAM_BLOCK", y),
        _xpatch_spec(y),
        *[_template_spec(method, y) for method in
          ("AMD_BLOCK", "DELELSTM_BLOCK", "INPARFORMER_BLOCK", "ST_MTM_BLOCK")],
        _harmonic_spec(y),
        _spectral_spec("TIMES2D_BLOCK", y),
        _spectral_spec("FREQMOE_BLOCK", y),
        _timekan_spec(y),
        _wavelet_spec("WAVEFORM_BLOCK", y),
        _wavelet_spec("WAVELETMIXER_BLOCK", y),
        _nbeats_basis_spec(y),
    ]
    assert len(specs) == 16
    return sorted(specs, key=lambda spec: spec.method)
