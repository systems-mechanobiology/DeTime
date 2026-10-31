---
title: Time-Series Decomposition Methods
description: Choose a DeTime decomposition method for univariate or multichannel time series. Compare SSA, MSSA, STL, VMD, EMD, wavelets and optional backends.
---

# Time-Series Decomposition Methods in DeTime

Start with the four core maintained paths. Move to wrappers only when the
data or comparison need points there.

<div class="method-signature-banner">
  <span>Observed</span>
  <span>Trend</span>
  <span>Seasonal</span>
  <span>Residual</span>
</div>

## Core method cards

<div class="method-use-grid">
  <div class="method-use-card">
    <h3><code>SSA</code></h3>
    <p><strong>Use when:</strong> one series needs interpretable subspace components.</p>
    <p><strong>Avoid when:</strong> the series is too short for a meaningful window.</p>
    <p><strong>Key params:</strong> <code>window</code>, <code>rank</code>, <code>primary_period</code>.</p>
  </div>
  <div class="method-use-card">
    <h3><code>STD</code></h3>
    <p><strong>Use when:</strong> a known seasonal period should split trend, season, and dispersion quickly.</p>
    <p><strong>Avoid when:</strong> the main period is unknown or unstable.</p>
    <p><strong>Key params:</strong> <code>period</code>.</p>
  </div>
  <div class="method-use-card">
    <h3><code>STDR</code></h3>
    <p><strong>Use when:</strong> cycles share a normalized seasonal shape while their levels and dispersions vary.</p>
    <p><strong>Avoid when:</strong> structural breaks dominate the seasonal pattern.</p>
    <p><strong>Key params:</strong> <code>period</code>.</p>
  </div>
  <div class="method-use-card">
    <h3><code>MSSA</code></h3>
    <p><strong>Use when:</strong> aligned channels share trend or oscillatory structure.</p>
    <p><strong>Avoid when:</strong> channels are unrelated or one univariate method is enough.</p>
    <p><strong>Key params:</strong> <code>window</code>, <code>rank</code>, <code>primary_period</code>.</p>
  </div>
</div>

## Decision flow

<div class="pipeline-panel">
  <div class="pipeline-flow">
    <div class="pipeline-step">
      <strong>One regular seasonal series?</strong>
      <span>Use <code>STD</code> for each cycle's own shape, or <code>STDR</code> for a shared shape and remainder. For outlier reweighting, compare <code>ROBUST_STL</code>.</span>
    </div>
    <div class="pipeline-step">
      <strong>One series, unknown components?</strong>
      <span>Start with <code>SSA</code>, then compare against <code>STD</code> or <code>STL</code>.</span>
    </div>
    <div class="pipeline-step">
      <strong>Aligned channels?</strong>
      <span>Use <code>MSSA</code> for shared structure; use <code>STD</code> channelwise for a fast baseline.</span>
    </div>
    <div class="pipeline-step">
      <strong>Need a specialist family?</strong>
      <span>Move to <code>EMD</code>, <code>CEEMDAN</code>, <code>VMD</code>, <code>WAVELET</code>, <code>MVMD</code>, or <code>MEMD</code>.</span>
    </div>
  </div>
</div>

## Wrapper use cases

| Method | Typical scenario | First parameter to check |
|---|---|---|
| `STL` | classical seasonal-trend baseline for one known period | `period` |
| `MSTL` | one series with multiple seasonal periods | `periods` |
| `ROBUST_STL` | STL-style baseline with outliers | `period` |
| `EMD` | adaptive IMF inspection for nonlinear signals | `n_imfs` |
| `CEEMDAN` | noise-assisted EMD when mode stability matters | `trials` |
| `VMD` | band-limited modes with a chosen mode count | `K`, `alpha` |
| `WAVELET` | multiscale signal inspection | `wavelet`, `level` |
| `MVMD` | optional multivariate VMD through PySDKit | `K`, `alpha` |
| `MEMD` | optional multivariate EMD through PySDKit | `primary_period` |

<!-- detime:animation-index:start -->
## Animated method explanations

Explore all **31 registered method entries** through a four-step GIF,
an English explanation, parameter guidance, and the numerical arrays behind the plots.
Open a method and choose **Play animation**. Each page also provides a static image
and direct GIF download. Examples use synthetic signals chosen to expose the mechanism.

Aliases and experimental blocks are identified below. Their pages explain the operator
implemented by DeTime and its relationship to the source architecture.

### Smoothing, seasonal structure, and subspaces

| Method | Mechanism to watch | Scope |
|---|---|---|
| [MA_BASELINE](gallery/ma-baseline.md#how-it-works) | Slide a uniform window → Subtract the smooth trend → Average seasonal phases → Center and form residual | stable |
| [MSSA](gallery/mssa.md#how-it-works) | Stack aligned windows → Compute shared singular modes → Reconstruct each channel → Group trend and season | maintained |
| [MSTL](gallery/mstl.md#how-it-works) | Specify the seasonal periods → Estimate seasonal terms → Add back and refine each term → Aggregate the common output | stable |
| [ROBUST_STL](gallery/robust-stl.md#how-it-works) | Fit initial smooths → Compute robustness weights → Refit and update the weights → Retain a residual | stable |
| [SSA](gallery/ssa.md#how-it-works) | Embed overlapping windows → Factor the trajectory matrix → Average each anti-diagonal → Group trend and season | maintained |
| [STD](gallery/std.md#how-it-works) | Partition and center cycles → Separate dispersion and shape → Restore each cycle's shape → Compute the common result | maintained |
| [STDR](gallery/stdr.md#how-it-works) | Partition and center cycles → Separate dispersion and shape → Average shapes across cycles → Compute the common result | maintained |
| [STL](gallery/stl.md#how-it-works) | Form seasonal-phase subseries → Use local polynomial smoothing → Alternate seasonal and trend → Form the additive result | stable |

### Adaptive modes, wavelets, and time-frequency structure

| Method | Mechanism to watch | Scope |
|---|---|---|
| [CEEMDAN](gallery/ceemdan.md#how-it-works) | Generate perturbations → Average first IMFs → Update adaptively → Retain the residue | stable |
| [EMD](gallery/emd.md#how-it-works) | Locate extrema → Build envelopes → Sift → Remove the IMF | stable |
| [GABOR_CLUSTER](gallery/gabor-cluster.md#how-it-works) | Window and transform → Build atom features → Assign the codebook → Mask and reconstruct | experimental |
| [MEMD](gallery/memd.md#how-it-works) | Project the data → Construct vector envelopes → Sift jointly → Extract aligned modes | optional-backend |
| [MVMD](gallery/mvmd.md#how-it-works) | Align the channels → Update channel spectra → Pool spectral energy → Recover mode stacks | optional-backend |
| [VMD](gallery/vmd.md#how-it-works) | Prepare the spectrum → Update a mode → Update its center → Reconstruct and group | stable |
| [WAVELET](gallery/wavelet.md#how-it-works) | Choose the filter bank → Build the pyramid → Select coefficient blocks → Assign outputs | stable |

### Experimental decomposition blocks

| Method | Mechanism to watch | Scope |
|---|---|---|
| [AMD_BLOCK](gallery/amd-block.md#how-it-works) | Compute several smooth trends → Average equal seasonal phases → Repeat the phase template → Inspect the derived residual | experimental |
| [AUTOFORMER_BLOCK](gallery/autoformer-block.md#how-it-works) | Specify the filter → Move along the series → Subtract the trend → Inspect the output contract | Alias of `MOVING_AVERAGE_DECOMPOSITION_BLOCK` |
| [DELELSTM_BLOCK](gallery/delelstm-block.md#how-it-works) | Update level and slope → Average equal seasonal phases → Repeat the phase template → Inspect the derived residual | experimental |
| [DLINEAR_BLOCK](gallery/dlinear-block.md#how-it-works) | Specify the filter → Move along the series → Subtract the trend → Inspect the output contract | Alias of `MOVING_AVERAGE_DECOMPOSITION_BLOCK` |
| [FREQMOE_BLOCK](gallery/freqmoe-block.md#how-it-works) | Separate trend and selection input → Select discrete spectral peaks → Fit and average candidate seasons → Inspect actual output streams | experimental |
| [INPARFORMER_BLOCK](gallery/inparformer-block.md#how-it-works) | Smooth the prefix → Average equal seasonal phases → Repeat the phase template → Inspect the derived residual | experimental |
| [LEDDAM_BLOCK](gallery/leddam-block.md#how-it-works) | Specify the filter → Move along the series → Subtract the trend → Inspect the output contract | experimental |
| [MOVING_AVERAGE_DECOMPOSITION_BLOCK](gallery/moving-average-decomposition-block.md#how-it-works) | Specify the filter → Move along the series → Subtract the trend → Inspect the output contract | experimental |
| [NBEATS_INTERPRETABLE](gallery/nbeats-interpretable.md#how-it-works) | Construct fixed basis functions → Separate backcast and output weights → Pass a remainder to seasonal blocks → Distinguish the two residuals | experimental |
| [PARSIMONY_BLOCK](gallery/parsimony-block.md#how-it-works) | Remove a smoothed trend → Build the harmonic design → Add fitted basis terms → Inspect the decomposition | experimental |
| [ST_MTM_BLOCK](gallery/st-mtm-block.md#how-it-works) | Smooth the prefix → Average equal seasonal phases → Smooth the repeated template → Inspect the derived residual | experimental |
| [TIMEKAN_BLOCK](gallery/timekan-block.md#how-it-works) | Smooth and inspect prefix frequencies → Fit two kinds of seasonal estimate → Apply the implemented fixed blend → Inspect the checked output | experimental |
| [TIMES2D_BLOCK](gallery/times2d-block.md#how-it-works) | Separate trend and selection input → Select discrete spectral peaks → Fit and average candidate seasons → Inspect actual output streams | experimental |
| [WAVEFORM_BLOCK](gallery/waveform-block.md#how-it-works) | Analyze with fixed wavelet filters → Reconstruct the approximation → Reconstruct selected detail bands → Inspect the remaining detail | experimental |
| [WAVELETMIXER_BLOCK](gallery/waveletmixer-block.md#how-it-works) | Analyze with fixed wavelet filters → Reconstruct the approximation → Reconstruct selected detail bands → Inspect the remaining detail | experimental |
| [XPATCH_BLOCK](gallery/xpatch-block.md#how-it-works) | Mix observation and state → Advance the recurrence → Smooth the difference → Inspect all three streams | experimental |

[Reproduce or audit the animations](maintenance/method-animations.md).
<!-- detime:animation-index:end -->

## More detail

- [Method Matrix](method-matrix.md) gives a compact table across input mode,
  maturity, dependencies, parameters, outputs, and recommended use.
- [Config Reference](config-reference.md) documents exact
  `DecompositionConfig` fields and method-specific parameters.
- [Method References](method-references.md) collects primary literature and
  official package links.
- [Notebook Gallery](notebook-gallery.md) shows runnable plots for the retained
  method surface.
