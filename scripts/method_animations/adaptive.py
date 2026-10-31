# SPDX-License-Identifier: BSD-3-Clause
"""Computed teaching stages for adaptive, spectral and multichannel methods.

The plots use tiny synthetic records. Upstream routines are observed without
changing their numerical updates; they are not replacements for the production
implementations. Each specification identifies exactly which computation was
recorded, including deliberately small demonstration settings.
"""
from __future__ import annotations

import importlib
from importlib.metadata import version
import sys

import numpy as np

from .common import (
    AnimationSpec, Frame, Line, Panel, Parameter, Reference, Step, phase,
    teaching_signal,
)


_MODE_COLORS = ("blue", "orange", "teal", "purple", "red", "green")


def _at(progress: float, count: int) -> int:
    return min(count - 1, int(progress * count))


def _err(left, right) -> float:
    return float(np.max(np.abs(np.asarray(left) - np.asarray(right))))


def _series(title, arrays, labels, *, x=None, xlabel="Sample", annotation=""):
    return Panel(
        title, [Line(np.asarray(a), label, x=x, color=_MODE_COLORS[j % 6])
                for j, (a, label) in enumerate(zip(arrays, labels))],
        xlabel=xlabel, annotation=annotation,
    )


def _panel_signal(n=144):
    t = np.arange(n, dtype=float)
    slow = np.sin(2 * np.pi * t / 24)
    fast = np.sin(2 * np.pi * t / 7)
    panel = np.column_stack([
        0.006 * t + 0.9 * slow + 0.27 * fast,
        -0.003 * t + 0.65 * np.sin(2 * np.pi * t / 24 + 0.45)
        + 0.35 * np.sin(2 * np.pi * t / 7 + 0.25),
        0.004 * t + 0.75 * np.sin(2 * np.pi * t / 24 - 0.3)
        + 0.2 * np.sin(2 * np.pi * t / 7 - 0.4),
    ])
    return t, panel


def _capture_return(function, args, kwargs, names):
    """Read numerical state at a selected upstream function's return event."""
    code = getattr(function, "__func__", function).__code__
    captured = {}
    previous = sys.gettrace()

    def trace(frame, event, arg):
        if frame.f_code is not code:
            return None
        if event == "return":
            for name in names:
                value = frame.f_locals.get(name)
                captured[name] = value.copy() if isinstance(value, np.ndarray) else value
        return trace

    sys.settrace(trace)
    try:
        result = function(*args, **kwargs)
    finally:
        sys.settrace(previous)
    if any(captured.get(name) is None for name in names):
        raise RuntimeError("Upstream trace fields changed; review the animation recorder.")
    return result, captured


def _inverse_positive_spectrum(spectrum):
    """Apply the upstream VMD conjugate completion and mirror crop.

    Input has frequency first and optionally a final channel axis. The helper
    only reconstructs captured iterates; it does not implement VMD updates.
    """
    size = spectrum.shape[0]
    complete = np.zeros_like(spectrum, dtype=complex)
    complete[size // 2:] = spectrum[size // 2:]
    complete[np.arange(size // 2, 0, -1)] = np.conj(spectrum[size // 2:])
    complete[0] = np.conj(complete[-1])
    time = np.fft.ifft(np.fft.ifftshift(complete, axes=0), axis=0).real
    return np.moveaxis(time[size // 4: 3 * size // 4], 1, 0)


def _emd():
    from PyEMD import EMD

    t, y, _, _, _ = teaching_signal(192, 24)

    class RecordedEMD(EMD):
        def __init__(self):
            super().__init__()
            self.sifts = []

        def extract_max_min_spline(self, time, signal):
            result = super().extract_max_min_spline(time, signal)
            if isinstance(result, tuple) and len(result) == 4:
                upper, lower, _, _ = result
                if np.ndim(upper) == 1:
                    self.sifts.append((signal.copy(), upper.copy(), lower.copy()))
            return result

    model = RecordedEMD()
    modes = model.emd(y, max_imf=1)
    if not model.sifts:
        raise RuntimeError("The EMD teaching signal did not produce a recorded sift.")
    sifts = np.asarray(model.sifts)
    updated_candidates = sifts[:, 0] - (sifts[:, 1] + sifts[:, 2]) / 2
    maxima, max_values, minima, min_values, _ = model.find_extrema(t, y)
    first_imf = modes[0]
    remainder = y - first_imf

    def frame(index, total):
        stage, progress = phase(index, total)
        sift = _at(progress, len(sifts)) if stage == 2 else 0
        candidate, upper, lower = sifts[sift]
        local_mean = (upper + lower) / 2
        after = candidate - local_mean
        scan = max(1, int(progress * (len(t) - 1))) if stage == 0 else len(t) - 1
        p0 = _series("Find extrema of the candidate", [candidate], ["Candidate"], x=t)
        p0.lines += [
            Line(max_values[maxima <= scan], "Maxima", maxima[maxima <= scan],
                 "red", "", "o", 1.0),
            Line(min_values[minima <= scan], "Minima", minima[minima <= scan],
                 "teal", "", "o", 1.0),
        ] if stage == 0 else []
        p0.vline = float(scan) if stage == 0 else None
        p1 = _series("Interpolate upper and lower envelopes", [candidate, upper, lower],
                     ["Candidate", "Upper spline", "Lower spline"], x=t)
        p2 = _series("Subtract the local envelope mean", [candidate, local_mean, after],
                     ["Before", "Envelope mean", "After one sift"], x=t)
        p3 = _series("Extract a mode, retain the remainder", [y, first_imf, remainder],
                     ["Input", "First IMF", "Input minus IMF"], x=t)
        caption = (
            f"Observed first-IMF sift {sift + 1}/{len(sifts)}. "
            "The spline mean changes when the candidate changes."
            if stage == 2 else
            "Actual PyEMD envelope calculations; the first IMF may contain fine-scale noise."
        )
        return Frame(stage, [p0, p1, p2, p3], caption)

    return AnimationSpec(
        "EMD", "EMD: estimate envelopes, subtract their mean, and sift",
        "EMD adapts its oscillatory modes to the extrema of the current signal. "
        "DeTime then groups upstream modes into its trend/season/residual result.",
        [Step("Locate extrema", "Local maxima and minima anchor the envelope construction."),
         Step("Build envelopes", "PyEMD interpolates upper and lower envelopes with its boundary treatment."),
         Step("Sift", "Subtract their pointwise mean, recompute extrema, and apply the stopping criteria."),
         Step("Remove the IMF", "Subtract the accepted mode from the signal and continue on the remainder.")],
        frame,
        [Parameter("n_imfs", "Limits extracted modes in DeTime's PyEMD call; a final residue can also be returned."),
         Parameter("primary_period / explicit IMF groups", "Controls DeTime's subsequent grouping; it does not determine the sifting envelopes."),
         Parameter("PyEMD stopping criteria", "This trace uses the upstream defaults; DeTime's wrapper exposes a narrower parameter surface.")],
        ["EMD modes are not uniquely identified physical sources; the first mode is not automatically the desired season.",
         "Spline boundary choices and added observations can change previously estimated components.",
         "The animation records the first IMF; it does not imply the algorithm stops after one mode."],
        [Reference("PyEMD EMD algorithm and envelope API", "https://pyemd.readthedocs.io/en/latest/emd.html"),
         Reference("Huang et al. (1998)", "https://doi.org/10.1098/rspa.1998.0193")],
        "upstream execution trace",
        f"Envelope calls recorded from EMD-signal {version('EMD-signal')} with default sifting settings and max_imf=1. "
        "All curves are computed; no intermediate curve is interpolated between final results.",
        {"method": "EMD", "params": {"n_imfs": 3, "primary_period": 24}},
        {"recorded_sifts": len(sifts), "imf_plus_remainder_max_abs_error": _err(first_imf + remainder, y),
         "sequential_sift_update_error": _err(updated_candidates[:-1], sifts[1:, 0]) if len(sifts) > 1 else 0.0,
         "final_sift_matches_first_imf": _err(updated_candidates[-1], first_imf),
         "finite_sifts": bool(np.isfinite(sifts).all())},
        {"time": t, "input": y, "sift_candidate_upper_lower": sifts, "first_imf": first_imf,
         "remainder": remainder, "maxima": maxima, "minima": minima},
        ["src/detime/methods/emd.py"],
    )


def _ceemdan():
    from PyEMD import CEEMDAN

    t, y, _, _, _ = teaching_signal(144, 24)
    trials, epsilon, seed = 8, 0.04, 42
    scale = float(np.std(y))

    class RecordedCEEMDAN(CEEMDAN):
        def __init__(self):
            super().__init__(trials=trials, epsilon=epsilon, parallel=False)
            self.first_trials = []
            self.adaptive_trials = []

        def _trial_update(self, trial):
            values = super()._trial_update(trial)
            perturbed = self._S + self.epsilon * self.all_noise_EMD[trial][0]
            self.first_trials.append((perturbed.copy(), values[0].copy()))
            return values

        def emd(self, signal, time=None, max_imf=-1):
            values = super().emd(signal, time, max_imf=max_imf)
            caller = sys._getframe(1)
            if caller.f_code is CEEMDAN.ceemdan.__code__ and "imfNo" in caller.f_locals:
                self.adaptive_trials.append((int(caller.f_locals["imfNo"]),
                                             signal.copy(), values[-1].copy()))
            return values

    model = RecordedCEEMDAN()
    model.noise_seed(seed)
    modes = model.ceemdan(y, max_imf=3)
    first = np.asarray(model.first_trials) * scale
    adaptive = np.asarray([entry[1:] for entry in model.adaptive_trials if entry[0] == 1]) * scale
    if len(first) != trials or len(adaptive) != trials:
        raise RuntimeError("CEEMDAN did not produce the expected first two ensemble stages.")
    first_means = np.cumsum(first[:, 1], axis=0) / np.arange(1, trials + 1)[:, None]
    local_means = np.cumsum(adaptive[:, 1], axis=0) / np.arange(1, trials + 1)[:, None]
    previous_residual = y - modes[0]

    def frame(index, total):
        stage, progress = phase(index, total)
        j = _at(progress, trials)
        if stage < 2:
            p0 = _series("Add a seeded noise-mode perturbation", [y, first[j, 0]],
                         ["Input", f"Perturbed trial {j + 1}"], x=t)
            p1 = _series("Extract the first IMF in each trial", [first[j, 0], first[j, 1]],
                         ["Perturbed input", "Trial first IMF"], x=t)
            p2 = _series("Average trial IMFs", [first[j, 1], first_means[j], modes[0]],
                         ["Current trial", f"Mean of {j + 1}", "Full ensemble mean"], x=t)
            p3 = _series("The first ensemble component", [y, modes[0], previous_residual],
                         ["Input", "First cIMF", "Remaining signal"], x=t)
        else:
            p0 = _series("Perturb the current residual", [previous_residual, adaptive[j, 0]],
                         ["Residual before stage 2", f"Adaptive trial {j + 1}"], x=t)
            p1 = _series("Estimate a local mean in each trial", [adaptive[j, 0], adaptive[j, 1]],
                         ["Perturbed residual", "Trial local mean"], x=t)
            p2 = _series("Subtract the averaged local mean", [previous_residual, local_means[j],
                                                                   previous_residual - local_means[j]],
                         ["Previous residual", f"Mean of {j + 1} trials", "Next cIMF estimate"], x=t)
            p3 = _series("Keep the complete additive accounting", [y, modes.sum(axis=0), modes[-1]],
                         ["Input", "Sum of returned slices", "Final remaining slice"], x=t)
        return Frame(stage, [p0, p1, p2, p3],
                     f"Actual serial upstream run: seed={seed}, trials={trials}, epsilon={epsilon}. "
                     "Larger noise is chosen here for visibility, not as a performance recommendation.")

    return AnimationSpec(
        "CEEMDAN", "CEEMDAN: ensemble averaging with adaptive noise",
        "CEEMDAN repeatedly estimates components from perturbed signals and updates a shared residual. "
        "The noise modes and ensemble averages are algorithmic inputs, not decorative uncertainty bands.",
        [Step("Generate perturbations", "Normalize the input, draw seeded noise, and decompose the noise realizations."),
         Step("Average first IMFs", "Apply EMD to each perturbed input and average its first IMF."),
         Step("Update adaptively", "Perturb the current residual with the next noise mode, average local means, and extract the next cIMF."),
         Step("Retain the residue", "Continue until the stopping criterion, then retain the remaining signal for additive reconstruction.")],
        frame,
        [Parameter("trials", "Number of ensemble members; this small animation uses 8, while DeTime's default is 100."),
         Parameter("epsilon", "Controls the perturbation scale; this visibility-oriented trace uses 0.04, not the default 0.005."),
         Parameter("seed and n_jobs", "The trace uses seed 42 and serial execution. Preserve both for reproducibility."),
         Parameter("primary_period", "Affects DeTime's grouping after the upstream component extraction.")],
        ["Different CEEMDAN variants exist; PyEMD includes the later improved formulation documented by its authors.",
         "An ensemble average does not establish that an IMF is a unique physical component.",
         "Raw DeTime IMF arrays use (mode, time, channel), including a singleton channel for one series."],
        [Reference("PyEMD CEEMDAN implementation and reproducibility", "https://pyemd.readthedocs.io/en/latest/ceemdan.html"),
         Reference("Torres et al. (2011)", "https://doi.org/10.1109/ICASSP.2011.5947265"),
         Reference("Colominas et al. (2014)", "https://doi.org/10.1016/j.bspc.2014.06.009")],
        "upstream execution trace",
        f"Trial inputs, first IMFs, and adaptive local means recorded from EMD-signal {version('EMD-signal')}; "
        "max_imf=3 bounds this upstream teaching run. DeTime's example below exposes the public controls and does not set this internal trace cap.",
        {"method": "CEEMDAN", "params": {"trials": trials, "epsilon": epsilon, "primary_period": 24},
         "seed": seed, "n_jobs": 1, "backend": "python"},
        {"first_ensemble_mean_error": _err(first_means[-1], modes[0]),
         "second_local_mean_error": _err(local_means[-1], y - modes[0] - modes[1]),
         "sum_of_returned_slices_error": _err(modes.sum(axis=0), y)},
        {"time": t, "input": y, "first_trial_input_and_imf": first,
         "adaptive_trial_input_and_local_mean": adaptive, "first_running_means": first_means,
         "adaptive_running_means": local_means, "returned_slices": modes},
        ["src/detime/methods/ceemdan.py"],
    )


def _vmd():
    from vmdpy import VMD

    t = np.arange(192, dtype=float)
    y = 0.7 * np.cos(2 * np.pi * t / 80) + np.sin(2 * np.pi * t / 24)
    y += 0.3 * np.sin(2 * np.pi * t / 7)
    (modes, _, omega), state = _capture_return(
        VMD, (y, 1500.0, 0.0, 3, 0, 1, 1e-7), {},
        ("u_hat_plus", "omega_plus", "freqs", "f_hat_plus", "fMirr", "n"),
    )
    last = len(omega) - 1  # the exact iterate returned by vmdpy
    sample_ids = np.unique(np.rint(np.linspace(1, max(1, last), 8)).astype(int))
    spectra = state["u_hat_plus"][sample_ids]
    centers = state["omega_plus"][sample_ids]
    mode_trace = np.asarray([_inverse_positive_spectrum(s) for s in spectra])
    freqs = state["freqs"]
    positive = freqs >= 0
    full_centers = state["omega_plus"][:last + 1]

    def frame(index, total):
        stage, progress = phase(index, total)
        j = _at(progress, len(sample_ids)) if stage in (1, 2) else (0 if stage == 0 else -1)
        iteration = int(sample_ids[j])
        k = _at(progress, 3) if stage == 1 else 1
        p0 = _series("Mirror the record before the FFT", [state["fMirr"]], ["Mirrored input"])
        p0.span = (len(y) / 2, 3 * len(y) / 2)
        p1 = _series(f"Narrow-band spectral update: mode {k + 1}",
                     [np.abs(state["f_hat_plus"][positive]), np.abs(spectra[j, positive, k])],
                     ["Input positive spectrum", "Current mode spectrum"], x=freqs[positive],
                     xlabel="Frequency (cycles/sample)")
        p1.vline = float(centers[j, k])
        p2 = _series("Energy-weighted center frequencies", full_centers[:iteration + 1].T,
                     [f"Center {c + 1}" for c in range(3)],
                     x=np.arange(iteration + 1), xlabel="Solver iteration")
        p2.ylim = (0, 0.4)
        p3 = _series(f"Modes reconstructed from iterate {iteration}", mode_trace[j],
                     [f"Mode {c + 1}" for c in range(3)], x=t)
        return Frame(stage, [p0, p1, p2, p3],
                     "Every spectrum and center shown is a captured solver iterate. "
                     "tau=0 permits reconstruction slack; sum-of-modes fit is not forced to be exact.")

    return AnimationSpec(
        "VMD", "VMD: update narrow-band modes and their center frequencies",
        "VMD alternates between frequency-domain mode updates and spectral-energy centers. "
        "DeTime's grouping into trend and season is a separate step after this optimization.",
        [Step("Prepare the spectrum", "Mirror the signal, compute its FFT, and retain the positive-frequency representation."),
         Step("Update a mode", "Fit the remaining spectrum with a bandwidth penalty around the current center frequency."),
         Step("Update its center", "Use the mode's positive-frequency energy to update its center, then repeat across modes."),
         Step("Reconstruct and group", "Complete the conjugate spectrum, invert the FFT, crop the mirrored margins, and group modes.")],
        frame,
        [Parameter("K", "Number of modes; the demonstration uses 3."),
         Parameter("alpha", "Penalizes spectral spread around each center; the demonstration uses 1500."),
         Parameter("tau", "Dual-update step; zero permits noise slack and does not enforce an exact sum of modes."),
         Parameter("init / tol", "Initialization and convergence tolerance affect the computed solution.")],
        ["The animation captures the optional vmdpy path; the native path has its own implementation and iteration control.",
         "Center frequencies shown here are raw solver frequencies in cycles/sample, not DeTime's converted metadata field.",
         "VMD modes need a grouping rule before being named trend or season; frequency ordering is not a physical-source guarantee."],
        [Reference("Original VMD paper", "https://doi.org/10.1109/TSP.2013.2288675"),
         Reference("vmdpy reference implementation", "https://github.com/vrcarva/vmdpy"),
         Reference("Maintained sktime continuation", "https://www.sktime.net/docs/api-reference/sktimetransformationsvmdvmdtransformer/")],
        "upstream execution trace",
        f"Captured vmdpy {version('vmdpy')} loop arrays without changing solver updates; "
        "intermediate time-domain modes use its conjugate-completion and mirror-cropping convention.",
        {"method": "VMD", "params": {"K": 3, "alpha": 1500.0, "tau": 0.0,
                                       "init": 1, "tol": 1e-7, "primary_period": 24}, "backend": "python"},
        {"recorded_final_iterate": int(last), "trace_matches_upstream_modes": _err(mode_trace[-1], modes),
         "mode_sum_rmse": float(np.sqrt(np.mean((modes.sum(axis=0) - y) ** 2)))},
        {"time": t, "input": y, "mirrored_input": state["fMirr"], "frequency_grid": freqs,
         "iteration_ids": sample_ids, "mode_spectra": spectra, "center_frequency_trace": full_centers,
         "mode_trace": mode_trace, "returned_modes": modes},
        ["src/detime/methods/vmd.py", "native/src/vmd.cpp"],
    )


def _wavelet():
    import pywt
    from detime.methods.wavelet import _reconstruct_from_levels

    t, y, _, _, _ = teaching_signal(192, 24)
    wavelet = pywt.Wavelet("db4")
    approximations, details = [y], []
    for _ in range(3):
        approximation, detail = pywt.dwt(approximations[-1], wavelet, mode="symmetric")
        approximations.append(approximation)
        details.append(detail)
    coeffs = pywt.wavedec(y, wavelet, level=3, mode="symmetric")
    bands = np.asarray([_reconstruct_from_levels(coeffs, [j], "db4", len(y))
                        for j in range(len(coeffs))])
    labels = ["A3", "D3", "D2", "D1"]

    def frame(index, total):
        stage, progress = phase(index, total)
        level = _at(progress, 3) + 1 if stage == 1 else 1
        band = _at(progress, 4) if stage == 2 else 0
        p0 = _series("Analysis low-pass and high-pass filters", [wavelet.dec_lo, wavelet.dec_hi],
                     ["Low-pass taps", "High-pass taps"], xlabel="Filter tap")
        p1 = _series(f"Level {level}: filter, then downsample by 2",
                     [approximations[level], details[level - 1]], [f"A{level} coefficients", f"D{level} coefficients"],
                     xlabel="Downsampled coefficient index",
                     annotation=f"Input length {len(approximations[level - 1])}; coefficient length {len(approximations[level])}")
        p2 = _series(f"Synthesize selected coefficient block {labels[band]}",
                     [y, bands[band]], ["Input", f"Reconstructed {labels[band]}"], x=t)
        p3 = _series("Group sample-aligned reconstructed bands", [bands[0], bands[1] + bands[2], bands[3]],
                     ["Trend: A3", "Season: D3 + D2", "Remaining D1"], x=t)
        if stage == 0:
            p2 = _series("Input to the first filter bank", [y], ["Synthetic input"], x=t)
            p2.span = (progress * (len(y) - 8), progress * (len(y) - 8) + 8)
            p2.annotation = "Moving span illustrates local filter support, not a separate fit."
        return Frame(stage, [p0, p1, p2, p3],
                     "Actual PyWavelets filter-bank outputs and inverse reconstructions. "
                     "Coefficient lengths include the symmetric boundary-extension convention.")

    return AnimationSpec(
        "WAVELET", "Wavelets: filter, downsample, and reconstruct selected scales",
        "A discrete wavelet transform separates scales through paired low-pass and high-pass filters. "
        "DeTime reconstructs selected coefficient blocks onto the original sample grid.",
        [Step("Choose the filter bank", "The wavelet fixes the analysis and synthesis filters; this trace uses db4."),
         Step("Build the pyramid", "Low-pass and high-pass filtering are followed by decimation; repeat on the approximation."),
         Step("Select coefficient blocks", "Retain a block, zero the others, and apply the inverse transform to obtain a sample-aligned contribution."),
         Step("Assign outputs", "This example assigns A3 to trend and D3+D2 to season; the remainder is input minus those outputs.")],
        frame,
        [Parameter("wavelet", "Controls filters and their support; db4 has eight analysis taps."),
         Parameter("level", "Controls pyramid depth; the example uses three levels."),
         Parameter("trend_levels / season_levels", "Indexes the wavedec list [A3,D3,D2,D1] here, not ascending physical scales."),
         Parameter("Boundary convention", "The current wrapper uses PyWavelets' default symmetric mode.")],
        ["Wavelet detail coefficients are decimated and should not be mistaken for sample-aligned output curves.",
         "Assigning scales to trend or season is an application choice; the transform does not identify physical mechanisms.",
         "The animation uses a safe fixed depth; excessive levels make boundary effects dominate."],
        [Reference("PyWavelets discrete transform", "https://pywavelets.readthedocs.io/en/stable/ref/dwt-discrete-wavelet-transform.html"),
         Reference("Inverse transform and partial reconstruction", "https://pywavelets.readthedocs.io/en/stable/ref/idwt-inverse-discrete-wavelet-transform.html"),
         Reference("Signal-extension modes", "https://pywavelets.readthedocs.io/en/stable/ref/signal-extension-modes.html")],
        "upstream numerical stages",
        f"Computed with PyWavelets {version('PyWavelets')}; inverse band reconstructions call the current DeTime helper. "
        "Moving filter support is a labeled illustration; coefficient values are actual library outputs.",
        {"method": "WAVELET", "params": {"wavelet": "db4", "level": 3,
                                           "trend_levels": [0], "season_levels": [1, 2]}},
        {"all_band_reconstruction_max_abs_error": _err(bands.sum(axis=0), y),
         "pyramid_matches_wavedec": max(_err(approximations[-1], coeffs[0]),
                                         *[_err(a, b) for a, b in zip(details[::-1], coeffs[1:])])},
        {"time": t, "input": y, "analysis_lowpass": np.asarray(wavelet.dec_lo),
         "analysis_highpass": np.asarray(wavelet.dec_hi), "reconstructed_bands": bands,
         **{f"approximation_{j}": a for j, a in enumerate(approximations)},
         **{f"detail_{j+1}": d for j, d in enumerate(details)}},
        ["src/detime/methods/wavelet.py"],
    )


def _mvmd():
    from pysdkit import MVMD

    t, y = _panel_signal()
    model = MVMD(alpha=1500.0, K=3, tau=0.0, init="uniform", max_iter=60)
    (returned_modes, _, omega), state = _capture_return(
        model.fit_transform, (y.T,), {"return_all": True},
        ("u_hat_plus", "omega_plus", "freqs", "f_hat_plus", "n"),
    )
    last = len(omega) - 1
    sample_ids = np.unique(np.rint(np.linspace(1, last, 8)).astype(int))
    internal_spectra = state["u_hat_plus"][sample_ids]
    # Base.fftshift shifts both frequency and channel axes on the input FFT.
    # The final channel ifftshift compensates this. Apply that same permutation
    # to every displayed iterate so labels retain the original input identity.
    spectra = np.fft.ifftshift(internal_spectra, axes=-1)
    centers = state["omega_plus"][:last + 1].real
    mode_trace = np.asarray([_inverse_positive_spectrum(s) for s in spectra])
    freqs = state["freqs"]
    positive = freqs >= 0
    internal_order = np.fft.fftshift(np.arange(y.shape[1]))
    output_permutation = np.fft.ifftshift(np.arange(y.shape[1]))

    def frame(index, total):
        stage, progress = phase(index, total)
        j = _at(progress, len(sample_ids)) if stage in (1, 2) else (0 if stage == 0 else -1)
        iteration = int(sample_ids[j])
        k = _at(progress, 3) if stage == 1 else 1
        p0 = _series("Aligned multichannel observations", y.T, ["Channel 1", "Channel 2", "Channel 3"], x=t)
        p1 = _series(f"Mode {k+1}: channel spectra share a center",
                     np.abs(spectra[j, positive, k, :]).T,
                     ["Channel 1", "Channel 2", "Channel 3"], x=freqs[positive],
                     xlabel="Frequency (cycles/sample)")
        p1.vline = float(centers[iteration, k])
        p2 = _series("Centers use energy across all channels", centers[:iteration+1].T,
                     [f"Shared center {c+1}" for c in range(3)],
                     x=np.arange(iteration+1), xlabel="Solver iteration")
        p2.ylim = (0, 0.4)
        p3 = _series(f"Mode {k+1} in original input-channel order", mode_trace[j, k].T,
                     ["Input channel 1", "Input channel 2", "Input channel 3"], x=t)
        return Frame(stage, [p0, p1, p2, p3],
                     "Captured joint spectral updates. Shared center frequency does not force equal channel amplitudes or phases. "
                     "The upstream output permutation preserves the input labels shown here.")

    return AnimationSpec(
        "MVMD", "MVMD: share mode frequencies across multiple channels",
        "MVMD couples channel-specific mode spectra through shared center frequencies. "
        "The modes can have different amplitudes and phases in each channel.",
        [Step("Align the channels", "Supply measurements on a common time grid and prepare their mirrored spectra."),
         Step("Update channel spectra", "Each channel fits a mode around the current shared center."),
         Step("Pool spectral energy", "Update each center using the spectral energy from all channels, then repeat."),
         Step("Recover mode stacks", "Invert the spectra and retain the (mode,time,channel) organization before application-specific grouping.")],
        frame,
        [Parameter("K and alpha", "The teaching run uses three modes and bandwidth penalty 1500."),
         Parameter("Upstream trace settings", "Uniform initialization, tau=0, and max_iter=60 bound this PySDKit demonstration; not all are public DeTime parameters."),
         Parameter("primary_period / mode groups", "Controls DeTime's assignment of the returned modes to output components.")],
        ["The optional backend requires aligned multichannel input and an explicitly checked axis convention.",
         "PySDKit's all-axis FFT shift changes the internal channel order; its final inverse shift restores input order. The animation applies that same restoration to every displayed iterate.",
         "A shared mode center does not identify a shared causal source, and tau=0 can leave reconstruction error."],
        [Reference("PySDKit MVMD interface and implementation", "https://pysdkit.readthedocs.io/en/stable/API/pysdkit._vmd.html"),
         Reference("Multivariate variational mode decomposition", "https://doi.org/10.1109/TSP.2019.2951223")],
        "upstream execution trace",
        f"Captured PySDKit {version('PySDKit')} joint solver arrays on input shaped (channel,time). "
        f"Internal channels correspond to input indexes {internal_order.tolist()} (zero-based); applying indexes "
        f"{output_permutation.tolist()} restores original order in every displayed spectrum and mode. "
        "The final trace is checked against the upstream returned modes.",
        {"method": "MVMD", "params": {"K": 3, "alpha": 1500.0, "primary_period": 24}, "backend": "python"},
        {"captured_final_iteration": int(last), "trace_matches_upstream_modes": _err(mode_trace[-1], returned_modes),
         "mode_sum_rmse": float(np.sqrt(np.mean((mode_trace[-1].sum(axis=0)-y)**2))),
         "backend_version": version("PySDKit"), "internal_channel_input_indexes": internal_order.tolist(),
         "output_channel_permutation": output_permutation.tolist(),
         "finite_trace": bool(np.isfinite(mode_trace).all())},
        {"time": t, "input_channels": y, "frequency_grid": freqs, "iteration_ids": sample_ids,
         "mode_spectra": spectra, "internal_mode_spectra": internal_spectra,
         "shared_centers": centers, "input_order_mode_trace": mode_trace,
         "internal_channel_input_indexes": internal_order, "output_channel_permutation": output_permutation,
         "upstream_returned_modes": returned_modes},
        ["src/detime/methods/mvmd.py"],
    )


def _memd():
    from pysdkit import MEMD
    from scipy.interpolate import CubicSpline

    upstream = importlib.import_module("pysdkit._emd.memd")
    t, y = _panel_signal()
    clock = t + 1

    class RecordedMEMD(MEMD):
        def __init__(self):
            super().__init__(n_dir=16, max_iter=50)
            self.first_sifts = []
            self.first_done = False

        def stop(self, signal, time, seq, seq_len, n_dim):
            stop, mean = super().stop(signal, time, seq, seq_len, n_dim)
            if not self.first_done:
                self.first_sifts.append((signal.copy(), mean.copy()))
                self.first_done = bool(stop)
            return stop, mean

    model = RecordedMEMD()
    directions = model.direction_vectors(3)
    sequence = model.init_hammersley(3)
    projections = y @ directions.T
    envelopes, selected_ids, minima, maxima = [], [], [], []
    for j in range(len(directions)):
        low, high = upstream.local_peaks(projections[:, j])
        tmin, tmax, zmin, zmax, valid = upstream.boundary_conditions(
            low, high, clock, projections[:, j], y, 2
        )
        if valid:
            envelopes.append((CubicSpline(tmin, zmin, bc_type="not-a-knot")(clock),
                              CubicSpline(tmax, zmax, bc_type="not-a-knot")(clock)))
            selected_ids.append(j)
            minima.append(np.asarray(low))
            maxima.append(np.asarray(high))
    envelopes = np.asarray(envelopes)
    if not len(envelopes):
        raise RuntimeError("MEMD teaching projections produced no valid vector envelopes.")
    direction_means = envelopes.mean(axis=1)
    running_means = np.cumsum(direction_means, axis=0) / np.arange(1, len(envelopes)+1)[:, None, None]
    reference_mean = upstream.envelope_mean(y, clock, sequence, 16, len(t), 3)[0]
    imfs = model.fit_transform(y.T)
    sifts = np.asarray(model.first_sifts)

    def frame(index, total):
        stage, progress = phase(index, total)
        j = _at(progress, len(envelopes)) if stage in (0, 1) else len(envelopes)-1
        direction = selected_ids[j]
        sift = _at(progress, len(sifts)) if stage == 2 else 0
        p0 = Panel("Project the vector signal along directions", [
            Line(directions[:, 1], "Direction vectors", directions[:, 0], "gray", "", "o"),
            Line(np.array([0, directions[direction, 1]]), "Selected direction",
                 np.array([0, directions[direction, 0]]), "blue", "-", "o"),
        ], xlabel="Direction coordinate 1", ylabel="Direction coordinate 2",
            xlim=(-1.1, 1.1), ylim=(-1.1, 1.1),
            annotation="2D view of 3D unit directions")
        p1 = _series(f"Scalar projection {direction+1}: extrema times", [projections[:, direction]], ["Projection"], x=t)
        p1.lines += [
            Line(projections[maxima[j], direction], "Maxima", t[maxima[j]], "orange", "", "o", 1),
            Line(projections[minima[j], direction], "Minima", t[minima[j]], "teal", "", "o", 1),
        ]
        p2 = _series("Interpolate vector samples at those times", [y[:, 0], envelopes[j, 0, :, 0], envelopes[j, 1, :, 0]],
                     ["Input channel 1", "Lower vector envelope", "Upper vector envelope"], x=t)
        if stage < 2:
            p3 = _series("Average envelope means across directions", [y[:, 0], running_means[j, :, 0], reference_mean[:, 0]],
                         ["Input channel 1", f"Mean of {j+1} directions", "All valid directions"], x=t)
        elif stage == 2:
            candidate, mean = sifts[sift]
            p3 = _series(f"Joint sift {sift+1}: subtract a vector mean", [candidate[:, 0], mean[:, 0], candidate[:, 0]-mean[:, 0]],
                         ["Candidate channel 1", "Direction-averaged mean", "Updated channel 1"], x=t)
        else:
            p3 = _series("First aligned IMF across channels", imfs[0].T,
                         ["Channel 1", "Channel 2", "Channel 3"], x=t)
        return Frame(stage, [p0, p1, p2, p3],
                     "Extrema come from scalar projections, but envelopes interpolate the multichannel vectors. "
                     "The same vector mean is subtracted jointly, channel by channel.")

    return AnimationSpec(
        "MEMD", "MEMD: project multichannel data to estimate a joint envelope mean",
        "MEMD uses many projection directions to construct a multivariate local mean. "
        "Its sifting preserves aligned mode slices across the input channels.",
        [Step("Project the data", "Use Hammersley-based unit directions and locate extrema of each scalar projection."),
         Step("Construct vector envelopes", "At the projection extrema times, interpolate the original vector samples and average valid envelopes."),
         Step("Sift jointly", "Subtract the direction-averaged vector mean and repeat the multivariate stopping test."),
         Step("Extract aligned modes", "Remove the accepted multichannel IMF, continue on the vector residue, and keep the final residue.")],
        frame,
        [Parameter("n_dir (upstream trace)", "This bounded PySDKit demonstration uses 16 projection directions; the DeTime wrapper does not expose this as a documented public control."),
         Parameter("Stopping rule (upstream trace)", "Uses PySDKit's default Rilling-style test with a safety cap of 50 sifts."),
         Parameter("primary_period / explicit mode groups", "Used by DeTime after upstream extraction, independently of the projection directions.")],
        ["This PySDKit backend requires at least three channels for MEMD; the example uses three aligned channels.",
         "Projection count, envelope boundaries, and stopping rules affect the result.",
         "Aligned IMF indexes do not establish physiological or other physical source identity."],
        [Reference("PySDKit MEMD API and implementation", "https://pysdkit.readthedocs.io/en/stable/API/pysdkit._emd.html"),
         Reference("Rehman and Mandic: Multivariate empirical mode decomposition", "https://doi.org/10.1098/rspa.2009.0502")],
        "upstream numerical stages and execution trace",
        f"Computed with PySDKit {version('PySDKit')}: its direction, extrema, and boundary helpers supply the vector envelopes; "
        "actual first-IMF sifting calls are recorded. The reduced direction count is a teaching setting, not a benchmark setting.",
        {"method": "MEMD", "params": {"primary_period": 24}, "backend": "python"},
        {"unit_direction_error": _err(np.linalg.norm(directions, axis=1), np.ones(len(directions))),
         "mean_matches_upstream_helper": _err(running_means[-1], reference_mean),
         "first_recorded_mean_error": _err(sifts[0, 1], reference_mean),
         "sum_of_returned_slices_error": _err(imfs.sum(axis=0), y), "recorded_first_imf_sifts": len(sifts)},
        {"time": t, "input_channels": y, "directions": directions, "projections": projections,
         "valid_direction_ids": np.asarray(selected_ids), "vector_envelopes": envelopes,
         "running_vector_means": running_means, "first_imf_sifts": sifts, "returned_imfs": imfs},
        ["src/detime/methods/memd.py", "src/detime/methods/mvmd.py"],
    )


def _gabor():
    from detime.methods import gabor_cluster as gabor
    from detime._native import has_native_method, invoke_native

    t, y, _, _, _ = teaching_signal(192, 24)
    cfg = gabor.GaborClusterConfig(win_len=48, hop=12, n_fft=64, n_clusters=4)
    window = gabor._make_window(48, "gaussian", None)
    features, z = gabor._extract_gabor_features(y, cfg, window)
    mu = features.mean(axis=0).astype(np.float32)
    sigma = features.std(axis=0).astype(np.float32)
    sigma[sigma < 1e-6] = 1.0
    # A deliberately specified demonstration codebook, not a learned model.
    raw_centers = np.asarray([
        [0.25, 0.04, 0.9], [0.7, 0.12, 0.65],
        [0.25, 0.55, 0.08], [0.8, 0.8, 0.05],
    ], dtype=np.float32)
    centers = (raw_centers - mu) / sigma
    standardized = (features - mu) / sigma
    distances = np.sum((standardized[:, None, :] - centers[None, :, :])**2, axis=2)
    labels = np.argmin(distances, axis=1).reshape(z.shape)
    components = np.asarray([
        gabor._istft_rfft(z * (labels == k), 48, 12, 64, window, len(y))
        for k in range(4)
    ])
    summed = components.sum(axis=0)
    residual = y - summed
    checks = {"mask_partition_error": int(np.max(np.abs(sum((labels == k).astype(int) for k in range(4))-1))),
              "overlap_add_reconstruction_error": _err(summed, y),
              "component_plus_residual_error": _err(summed + residual, y)}
    if has_native_method("gabor_cluster_decompose"):
        native = invoke_native(
            "gabor_cluster_decompose", y, centers, mu, sigma, win_len=48, hop=12,
            n_fft=64, window=window, use_log_amp=True, max_clusters=-1, trend_freq_thr=0.08,
        )
        native_components = native["components"]
        checks["native_cluster_component_max_abs_difference"] = max(
            _err(components[k], native_components.get(f"Cluster_{k}", np.zeros_like(y)))
            for k in range(4)
        )
    else:
        checks["native_comparison"] = "not executed: native Gabor method unavailable"
    frequencies = np.fft.rfftfreq(64)
    selected_points = np.linspace(0, len(features)-1, min(300, len(features))).astype(int)
    # The first four tab10 entries, shared by the categorical map and points.
    cluster_colors = ("#1f77b4", "#ff7f0e", "#2ca02c", "#d62728")

    def frame(index, total):
        stage, progress = phase(index, total)
        m = _at(progress, len(z))
        k = _at(progress, 4)
        start = m * 12
        p0 = _series("Slide a Gaussian analysis window", [y], ["Input"], x=t)
        p0.span = (start, start + 48)
        if stage == 0:
            p1 = _series("Window the selected segment", [y[start:start+48], y[start:start+48]*window],
                         ["Segment", "Windowed segment"], xlabel="Local sample")
            p2 = _series("Compute the windowed Fourier spectrum", [np.abs(z[m])],
                         [f"Frame {m+1} magnitude"], x=frequencies, xlabel="Frequency (cycles/sample)")
        else:
            p1 = Panel("STFT log magnitudes" if stage == 1 else "Assigned cluster labels",
                       image=(np.log1p(np.abs(z)).T if stage == 1 else labels.T),
                       cmap="viridis" if stage == 1 else "tab10",
                       vmin=None if stage == 1 else 0, vmax=None if stage == 1 else 9,
                       extent=(0, len(z)-1, 0, 0.5), xlabel="Window index", ylabel="Frequency (cycles/sample)")
            p2 = Panel("Feature-space nearest-centroid assignment", xlabel="Normalized frequency [0,1]", ylabel="log(1 + magnitude)",
                       annotation="2D projection; distances also include normalized time.")
            for c in range(4):
                ids = selected_points[labels.ravel()[selected_points] == c]
                p2.lines.append(Line(features[ids, 2], f"Cluster {c+1}", features[ids, 1],
                                     cluster_colors[c], "", "o", 1.0, 0.65))
                p2.lines.append(Line(np.array([raw_centers[c, 2]]), "", np.array([raw_centers[c, 1]]),
                                     cluster_colors[c], "", "X", 2.0))
        p3 = _series(f"Mask cluster {k+1}, inverse FFT, overlap-add", [y, components[k], residual],
                     ["Input", f"Cluster {k+1} contribution", "Unreconstructed residual"], x=t)
        p3.lines[0].color = "gray"
        p3.lines[1].color = cluster_colors[k]
        if stage == 3:
            p1 = Panel(f"Complex STFT mask for cluster {k+1}", image=(labels == k).T.astype(float),
                       cmap="Blues", vmin=0, vmax=1, extent=(0, len(z)-1, 0, .5),
                       xlabel="Window index", ylabel="Frequency (cycles/sample)")
            p2 = _series("All masked reconstructions add together", [y, summed],
                         ["Input", "Sum of cluster contributions"], x=t)
        return Frame(stage, [p0, p1, p2, p3],
                     "Experimental DeTime operator; centroids are an explicitly fixed teaching codebook. "
                     "No model is trained and no canonical Gabor-decomposition paper is reproduced.")

    return AnimationSpec(
        "GABOR_CLUSTER", "Gabor clustering: assign time-frequency atoms and reconstruct masks",
        "DeTime's experimental operator builds windowed Fourier atoms, assigns their features to a supplied codebook, "
        "and reconstructs cluster-specific contributions with overlap-add.",
        [Step("Window and transform", "Slide the normalized Gaussian window and compute real FFT coefficients."),
         Step("Build atom features", "Represent each time-frequency bin by normalized time, normalized frequency, and log amplitude."),
         Step("Assign the codebook", "Standardize features with the stored mean/scale and select the nearest supplied centroid."),
         Step("Mask and reconstruct", "Retain each cluster's complex coefficients, apply inverse FFT and normalized overlap-add, then group contributions heuristically.")],
        frame,
        [Parameter("model / model_path", "A supplied GaborClusterModel is required; the decomposition function does not train a codebook."),
         Parameter("win_len / hop / n_fft", "Stored in the model; the example uses 48/12/64 and a Gaussian window."),
         Parameter("max_clusters", "Optionally retains the highest-energy clusters before reconstruction."),
         Parameter("trend_freq_thr", "Heuristic threshold on the de-standardized centroid frequency, normalized from zero to Nyquist.")],
        ["This is an experimental, repository-specific operator, not a claimed reproduction of a canonical forecasting or decomposition architecture.",
         "The fixed four-centroid teaching codebook is neither trained nor evidence of a useful scientific clustering.",
         "The current frame grid can leave an uncovered tail when the record length is not aligned with the hop; the residual retains that difference.",
         "Cluster labels are codebook labels; assigning low-frequency clusters to trend is a heuristic."],
        [Reference("DeTime Gabor operator source", "https://github.com/systems-mechanobiology/DeTime/blob/main/src/detime/methods/gabor_cluster.py"),
         Reference("DeTime native Gabor kernels", "https://github.com/systems-mechanobiology/DeTime/blob/main/native/src/gabor.cpp")],
        "repository numerical stages with illustrative fixed codebook",
        "Uses the current repository's window, STFT, feature extraction and inverse-overlap-add functions. "
        "Squared Euclidean assignment matches the supplied-centroid operation; native cluster reconstructions are independently compared when available. "
        "Model normalization, fixed teaching centroids, and numeric window settings are saved with the trace. "
        "The public call requires a GaborClusterModel or a model archive created with its save() method; the generic config is incomplete until that model is supplied.",
        {"method": "GABOR_CLUSTER", "params": {"trend_freq_thr": 0.08}},
        checks,
        {"time": t, "input": y, "window": window, "stft": z, "raw_features": features,
         "feature_mean": mu, "feature_scale": sigma, "raw_demo_centroids": raw_centers,
         "standardized_demo_centroids": centers, "squared_centroid_distances": distances,
         "cluster_labels": labels, "cluster_components": components, "residual": residual,
         "config_win_len": np.asarray(48), "config_hop": np.asarray(12),
         "config_n_fft": np.asarray(64), "config_use_log_amp": np.asarray(True)},
        ["src/detime/methods/gabor_cluster.py", "native/src/gabor.cpp"],
    )


def build_specs() -> list[AnimationSpec]:
    """Build the seven declared traces; missing backends fail explicitly."""
    return [_emd(), _ceemdan(), _vmd(), _wavelet(), _mvmd(), _memd(), _gabor()]
