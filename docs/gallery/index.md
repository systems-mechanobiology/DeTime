---
title: All 31 DeTime Method Animations
description: Explore all 31 DeTime method entries with four-step animations, parameter explanations, maturity labels, source arrays and references.
---

# All 31 Method Animations

Choose a method to see its calculation unfold in four steps. Each page includes
a **Play animation** control, a static diagram, parameter explanations, references,
and downloadable numerical arrays with source provenance. Playback starts only
when requested; the written steps remain available without JavaScript.

The gallery covers **31 registered entries**: 8 smoothing, seasonal and subspace
entries, 7 adaptive or time-frequency entries, and 16 experimental decomposition
blocks. Autoformer and DLinear are aliases of the moving-average block. The count
includes these aliases and does not imply 31 independent algorithms.

## Read the scope labels

| Label | Meaning in DeTime |
|---|---|
| `maintained` | A maintained core implementation with Python and native execution paths. |
| `stable` | A retained method or wrapper on the supported interface. |
| `optional-backend` | Requires an additional upstream package, such as PySDKit. |
| `experimental` | A research operator or illustration with the limits stated on its page. |

These labels describe the package support level. The synthetic teaching examples
show computations; they do not measure forecasting accuracy or establish clinical
or financial performance. Experimental architecture names refer to the implemented
decomposition blocks. **N-BEATS uses explicitly chosen, untrained coefficients in
its animation.** The Gabor example uses a fixed teaching codebook.

## Smoothing, seasonal structure and subspaces

| Method | Computation illustrated | Scope |
|---|---|---|
| [MA_BASELINE](ma-baseline.md#how-it-works) | Slide a uniform window → Subtract the smooth trend → Average seasonal phases → Center and form residual | stable |
| [MSSA](mssa.md#how-it-works) | Stack aligned windows → Compute shared singular modes → Reconstruct each channel → Group trend and season | maintained |
| [MSTL](mstl.md#how-it-works) | Specify the seasonal periods → Estimate seasonal terms → Add back and refine each term → Aggregate the common output | stable |
| [ROBUST_STL](robust-stl.md#how-it-works) | Fit initial smooths → Compute robustness weights → Refit and update the weights → Retain a residual | stable |
| [SSA](ssa.md#how-it-works) | Embed overlapping windows → Factor the trajectory matrix → Average each anti-diagonal → Group trend and season | maintained |
| [STD](std.md#how-it-works) | Partition and center cycles → Separate dispersion and shape → Restore each cycle's shape → Compute the common result | maintained |
| [STDR](stdr.md#how-it-works) | Partition and center cycles → Separate dispersion and shape → Average shapes across cycles → Compute the common result | maintained |
| [STL](stl.md#how-it-works) | Form seasonal-phase subseries → Use local polynomial smoothing → Alternate seasonal and trend → Form the additive result | stable |

## Adaptive modes, wavelets and time-frequency structure

| Method | Computation illustrated | Scope |
|---|---|---|
| [CEEMDAN](ceemdan.md#how-it-works) | Generate perturbations → Average first IMFs → Update adaptively → Retain the residue | stable |
| [EMD](emd.md#how-it-works) | Locate extrema → Build envelopes → Sift → Remove the IMF | stable |
| [GABOR_CLUSTER](gabor-cluster.md#how-it-works) | Window and transform → Build atom features → Assign the codebook → Mask and reconstruct | experimental |
| [MEMD](memd.md#how-it-works) | Project the data → Construct vector envelopes → Sift jointly → Extract aligned modes | optional-backend |
| [MVMD](mvmd.md#how-it-works) | Align the channels → Update channel spectra → Pool spectral energy → Recover mode stacks | optional-backend |
| [VMD](vmd.md#how-it-works) | Prepare the spectrum → Update a mode → Update its center → Reconstruct and group | stable |
| [WAVELET](wavelet.md#how-it-works) | Choose the filter bank → Build the pyramid → Select coefficient blocks → Assign outputs | stable |

## Experimental decomposition blocks

| Method | Computation illustrated | Scope |
|---|---|---|
| [AMD_BLOCK](amd-block.md#how-it-works) | Compute several smooth trends → Average equal seasonal phases → Repeat the phase template → Inspect the derived residual | experimental |
| [AUTOFORMER_BLOCK](autoformer-block.md#how-it-works) | Specify the filter → Move along the series → Subtract the trend → Inspect the output contract | experimental; alias of `MOVING_AVERAGE_DECOMPOSITION_BLOCK` |
| [DELELSTM_BLOCK](delelstm-block.md#how-it-works) | Update level and slope → Average equal seasonal phases → Repeat the phase template → Inspect the derived residual | experimental |
| [DLINEAR_BLOCK](dlinear-block.md#how-it-works) | Specify the filter → Move along the series → Subtract the trend → Inspect the output contract | experimental; alias of `MOVING_AVERAGE_DECOMPOSITION_BLOCK` |
| [FREQMOE_BLOCK](freqmoe-block.md#how-it-works) | Separate trend and selection input → Select discrete spectral peaks → Fit and average candidate seasons → Inspect actual output streams | experimental |
| [INPARFORMER_BLOCK](inparformer-block.md#how-it-works) | Smooth the prefix → Average equal seasonal phases → Repeat the phase template → Inspect the derived residual | experimental |
| [LEDDAM_BLOCK](leddam-block.md#how-it-works) | Specify the filter → Move along the series → Subtract the trend → Inspect the output contract | experimental |
| [MOVING_AVERAGE_DECOMPOSITION_BLOCK](moving-average-decomposition-block.md#how-it-works) | Specify the filter → Move along the series → Subtract the trend → Inspect the output contract | experimental |
| [NBEATS_INTERPRETABLE](nbeats-interpretable.md#how-it-works) | Construct fixed basis functions → Separate backcast and output weights → Pass a remainder to seasonal blocks → Distinguish the two residuals | experimental |
| [PARSIMONY_BLOCK](parsimony-block.md#how-it-works) | Remove a smoothed trend → Build the harmonic design → Add fitted basis terms → Inspect the decomposition | experimental |
| [ST_MTM_BLOCK](st-mtm-block.md#how-it-works) | Smooth the prefix → Average equal seasonal phases → Smooth the repeated template → Inspect the derived residual | experimental |
| [TIMEKAN_BLOCK](timekan-block.md#how-it-works) | Smooth and inspect prefix frequencies → Fit two kinds of seasonal estimate → Apply the implemented fixed blend → Inspect the checked output | experimental |
| [TIMES2D_BLOCK](times2d-block.md#how-it-works) | Separate trend and selection input → Select discrete spectral peaks → Fit and average candidate seasons → Inspect actual output streams | experimental |
| [WAVEFORM_BLOCK](waveform-block.md#how-it-works) | Analyze with fixed wavelet filters → Reconstruct the approximation → Reconstruct selected detail bands → Inspect the remaining detail | experimental |
| [WAVELETMIXER_BLOCK](waveletmixer-block.md#how-it-works) | Analyze with fixed wavelet filters → Reconstruct the approximation → Reconstruct selected detail bands → Inspect the remaining detail | experimental |
| [XPATCH_BLOCK](xpatch-block.md#how-it-works) | Mix observation and state → Advance the recurrence → Smooth the difference → Inspect all three streams | experimental |

## Data and reproduction

[Reproduction guide](../maintenance/method-animations.md) ·
[Complete numerical manifest](../assets/generated/method-animations/manifest.json) ·
[Parameter reference](../config-reference.md) ·
[Runnable notebook examples](../notebook-gallery.md)

Every animation records its synthetic input, computed intermediate arrays, checks,
dependency versions and source hashes. The per-method **What this animation
computes** section identifies whether the trace is a public-method run, an
instrumented solver, or a teaching illustration.
