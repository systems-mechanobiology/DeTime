# Method Cards

This page is generated from `MethodRegistry.list_catalog()` so the human-facing
method cards stay aligned with the machine-facing catalog contract.

Current package version target: `0.1.3`.

Source citations and official upstream package links are collected in
[Method References](method-references.md).

This page intentionally keeps cards compact. Use
[Method Matrix](method-matrix.md) for table comparison and
[Config Reference](config-reference.md) for full parameter semantics.

The `tsdecomp` top-level alias remains compatibility-only through `0.1.x` and is
not the canonical surface for any method listed below.

## Core maintained methods

### `MSSA`

- Summary: Multivariate SSA for shared-structure decomposition across channels.
- Use when: multivariate component recovery; shared seasonal structure across channels
- Avoid when: single-series workflows where a univariate core method is sufficient; very short series that cannot support a sensible window length
- Key params: `window` (derived; see description), `rank` (derived; see description), `primary_period` (None)
- Input/backend: `multivariate` input, `native-backed` implementation, maturity `maintained`
- Claim scope: `maintained`
- Alias of: none
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.elementary`
- References: [Method References](method-references.md#mssa)
- Learn the mechanism: [Animated explanation](gallery/mssa.md#how-it-works)

See [Config Reference](config-reference.md#mssa) for the full parameter table.

### `SSA`

- Summary: Singular spectrum analysis for structured univariate decomposition.
- Use when: accuracy-first univariate decomposition; component recovery
- Avoid when: shared-model multivariate decomposition problems; very short series that cannot support a sensible window length
- Key params: `window` (derived; see description), `rank` (10), `primary_period` (None)
- Input/backend: `univariate` input, `native-backed` implementation, maturity `maintained`
- Claim scope: `maintained`
- Alias of: none
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.elementary`
- References: [Method References](method-references.md#ssa)
- Learn the mechanism: [Animated explanation](gallery/ssa.md#how-it-works)

See [Config Reference](config-reference.md#ssa) for the full parameter table.

### `STD`

- Summary: Fast seasonal-trend decomposition with dispersion-aware diagnostics.
- Use when: fast seasonal-trend baselines; channelwise multivariate workflows
- Avoid when: problems that require one shared latent model across channels; series where the dominant period is unknown and cannot be inferred reliably
- Key params: `period` (None)
- Input/backend: `channelwise` input, `native-backed` implementation, maturity `maintained`
- Claim scope: `maintained`
- Alias of: none
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.dispersion`, `components.seasonal_shape`
- References: [Method References](method-references.md#std)
- Learn the mechanism: [Animated explanation](gallery/std.md#how-it-works)

See [Config Reference](config-reference.md#std) for the full parameter table.

### `STDR`

- Summary: Seasonal-trend-dispersion decomposition with an averaged cycle shape and a remainder.
- Use when: shared normalized seasonal shapes with cycle-dependent dispersion; channelwise multivariate workflows
- Avoid when: problems that require one shared latent model across channels; series where the dominant period is unknown and cannot be inferred reliably
- Key params: `period` (None)
- Input/backend: `channelwise` input, `native-backed` implementation, maturity `maintained`
- Claim scope: `maintained`
- Alias of: none
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.dispersion`, `components.seasonal_shape`
- References: [Method References](method-references.md#stdr)
- Learn the mechanism: [Animated explanation](gallery/stdr.md#how-it-works)

See [Config Reference](config-reference.md#stdr) for the full parameter table.

## Stable wrappers and retained methods

### `CEEMDAN`

- Summary: Noise-assisted EMD wrapper with IMFs in (mode, time, channel) layout.
- Use when: noise-assisted EMD workflows; adaptive decomposition with improved IMF stability
- Avoid when: shared-model multivariate decomposition problems
- Key params: `trials` (100), `epsilon` (0.005), `primary_period` (None)
- Input/backend: `univariate` input, `wrapper` implementation, maturity `stable`
- Claim scope: `integration`
- Alias of: none
- Optional dependencies: PyEMD
- Output components: `trend`, `season`, `residual`, `components.imfs`
- References: [Method References](method-references.md#ceemdan)
- Learn the mechanism: [Animated explanation](gallery/ceemdan.md#how-it-works)

See [Config Reference](config-reference.md#ceemdan) for the full parameter table.

### `EMD`

- Summary: Empirical mode decomposition under the DeTime result contract.
- Use when: adaptive decomposition of nonlinear signals; IMF-oriented exploratory analysis
- Avoid when: shared-model multivariate decomposition problems
- Key params: `n_imfs` (None), `primary_period` (None)
- Input/backend: `univariate` input, `wrapper` implementation, maturity `stable`
- Claim scope: `integration`
- Alias of: none
- Optional dependencies: PyEMD
- Output components: `trend`, `season`, `residual`, `components.imfs`
- References: [Method References](method-references.md#emd)
- Learn the mechanism: [Animated explanation](gallery/emd.md#how-it-works)

See [Config Reference](config-reference.md#emd) for the full parameter table.

### `MA_BASELINE`

- Summary: Simple moving-average baseline for smoke tests and lightweight workflows.
- Use when: sanity checks; lightweight baseline decomposition
- Avoid when: shared-model multivariate decomposition problems
- Key params: `trend_window` (derived; see description), `season_period` (None)
- Input/backend: `univariate` input, `native-backed` implementation, maturity `stable`
- Claim scope: `maintained`
- Alias of: none
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`
- References: [Method References](method-references.md#ma_baseline)
- Learn the mechanism: [Animated explanation](gallery/ma-baseline.md#how-it-works)

See [Config Reference](config-reference.md#ma_baseline) for the full parameter table.

### `MSTL`

- Summary: Statsmodels MSTL wrapped into the DeTime workflow surface.
- Use when: multiple seasonalities in univariate data; classical decomposition baselines
- Avoid when: shared-model multivariate decomposition problems; series where the dominant period is unknown and cannot be inferred reliably
- Key params: `periods` (required)
- Input/backend: `univariate` input, `wrapper` implementation, maturity `stable`
- Claim scope: `integration`
- Alias of: none
- Optional dependencies: statsmodels
- Output components: `trend`, `season`, `residual`
- References: [Method References](method-references.md#mstl)
- Learn the mechanism: [Animated explanation](gallery/mstl.md#how-it-works)

See [Config Reference](config-reference.md#mstl) for the full parameter table.

### `ROBUST_STL`

- Summary: Robust STL-style decomposition wrapped for reproducible workflows.
- Use when: outlier-prone seasonal-trend baselines; classical robust decomposition
- Avoid when: shared-model multivariate decomposition problems; series where the dominant period is unknown and cannot be inferred reliably
- Key params: `period` (required)
- Input/backend: `univariate` input, `wrapper` implementation, maturity `stable`
- Claim scope: `integration`
- Alias of: none
- Optional dependencies: statsmodels
- Output components: `trend`, `season`, `residual`
- References: [Method References](method-references.md#robust_stl)
- Learn the mechanism: [Animated explanation](gallery/robust-stl.md#how-it-works)

See [Config Reference](config-reference.md#robust_stl) for the full parameter table.

### `STL`

- Summary: Classical STL wrapped into the DeTime workflow contract.
- Use when: classical seasonal-trend baselines; statsmodels-compatible workflows
- Avoid when: shared-model multivariate decomposition problems; series where the dominant period is unknown and cannot be inferred reliably
- Key params: `period` (required)
- Input/backend: `univariate` input, `wrapper` implementation, maturity `stable`
- Claim scope: `integration`
- Alias of: none
- Optional dependencies: statsmodels
- Output components: `trend`, `season`, `residual`
- References: [Method References](method-references.md#stl)
- Learn the mechanism: [Animated explanation](gallery/stl.md#how-it-works)

See [Config Reference](config-reference.md#stl) for the full parameter table.

### `VMD`

- Summary: Variational mode decomposition integrated into the common workflow layer.
- Use when: band-limited mode separation; frequency-structured univariate workflows
- Avoid when: shared-model multivariate decomposition problems
- Key params: `K` (derived; see description), `alpha` (300.0), `primary_period` (None)
- Input/backend: `univariate` input, `native-backed` implementation, maturity `stable`
- Claim scope: `maintained`
- Alias of: none
- Optional dependencies: vmdpy
- Output components: `trend`, `season`, `residual`, `components.modes`
- References: [Method References](method-references.md#vmd)
- Learn the mechanism: [Animated explanation](gallery/vmd.md#how-it-works)

See [Config Reference](config-reference.md#vmd) for the full parameter table.

### `WAVELET`

- Summary: Wavelet-based decomposition exposed through the common output contract.
- Use when: multiscale exploratory analysis; wavelet-style trend and detail separation
- Avoid when: shared-model multivariate decomposition problems
- Key params: `wavelet` ("db4"), `level` (None)
- Input/backend: `univariate` input, `wrapper` implementation, maturity `stable`
- Claim scope: `integration`
- Alias of: none
- Optional dependencies: PyWavelets
- Output components: `trend`, `season`, `residual`, `components.coefficients`
- References: [Method References](method-references.md#wavelet)
- Learn the mechanism: [Animated explanation](gallery/wavelet.md#how-it-works)

See [Config Reference](config-reference.md#wavelet) for the full parameter table.

## Optional backend methods

### `MEMD`

- Summary: Optional multivariate EMD backend for shared oscillatory structure.
- Use when: multivariate adaptive decomposition; shared oscillatory modes across channels
- Avoid when: single-series workflows where a univariate core method is sufficient; environments where optional backend dependencies cannot be installed
- Key params: `primary_period` (None)
- Input/backend: `multivariate` input, `optional-backend` implementation, maturity `optional-backend`
- Claim scope: `integration`
- Alias of: none
- Optional dependencies: PySDKit
- Output components: `trend`, `season`, `residual`, `components.imfs`
- References: [Method References](method-references.md#memd)
- Learn the mechanism: [Animated explanation](gallery/memd.md#how-it-works)

See [Config Reference](config-reference.md#memd) for the full parameter table.

### `MVMD`

- Summary: Optional multivariate VMD backend for shared frequency structure.
- Use when: multivariate variational decomposition; shared frequency structure across channels
- Avoid when: single-series workflows where a univariate core method is sufficient; environments where optional backend dependencies cannot be installed
- Key params: `K` (3), `alpha` (2000.0), `primary_period` (None)
- Input/backend: `multivariate` input, `optional-backend` implementation, maturity `optional-backend`
- Claim scope: `integration`
- Alias of: none
- Optional dependencies: PySDKit
- Output components: `trend`, `season`, `residual`, `components.modes`
- References: [Method References](method-references.md#mvmd)
- Learn the mechanism: [Animated explanation](gallery/mvmd.md#how-it-works)

See [Config Reference](config-reference.md#mvmd) for the full parameter table.

## Experimental methods

### `AMD_BLOCK`

- Summary: AMD-inspired multiscale smoothing head with periodic-template seasonal reconstruction.
- Use when: multiscale neural decomposition comparisons; seasonal signals where multiple smoothing scales are informative
- Avoid when: shared-model multivariate decomposition problems; first-pass baselines or high-trust production workflows
- Key params: `primary_period` (None), `fit_scope` ("prefix"), `multiscale_windows` (None)
- Input/backend: `univariate` input, `python` implementation, maturity `experimental`
- Claim scope: `experimental-operator`
- Alias of: none
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`
- References: [Method References](method-references.md#amd_block)
- Learn the mechanism: [Animated explanation](gallery/amd-block.md#how-it-works)

See [Config Reference](config-reference.md#amd_block) for the full parameter table.

### `AUTOFORMER_BLOCK`

- Summary: Compatibility alias for the generic experimental moving-average operator, inspired by Autoformer.
- Use when: neural-architecture-inspired seasonal-trend baselines; Autoformer-style decomposition ablations
- Avoid when: shared-model multivariate decomposition problems; first-pass baselines or high-trust production workflows
- Key params: `moving_avg` (None), `primary_period` (None)
- Input/backend: `univariate` input, `python` implementation, maturity `experimental`
- Claim scope: `experimental-operator`
- Alias of: `MOVING_AVERAGE_DECOMPOSITION_BLOCK`
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.moving_mean`
- References: [Method References](method-references.md#autoformer_block)
- Learn the mechanism: [Animated explanation](gallery/autoformer-block.md#how-it-works)

See [Config Reference](config-reference.md#autoformer_block) for the full parameter table.

### `DELELSTM_BLOCK`

- Summary: DeLELSTM-inspired Holt trend plus periodic-template seasonal decomposition head.
- Use when: LSTM decomposition-head ablations; signals with smooth level and slope structure
- Avoid when: shared-model multivariate decomposition problems; first-pass baselines or high-trust production workflows
- Key params: `primary_period` (None), `fit_scope` ("prefix"), `alpha` (0.4), `beta` (0.2)
- Input/backend: `univariate` input, `python` implementation, maturity `experimental`
- Claim scope: `experimental-operator`
- Alias of: none
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`
- References: [Method References](method-references.md#delelstm_block)
- Learn the mechanism: [Animated explanation](gallery/delelstm-block.md#how-it-works)

See [Config Reference](config-reference.md#delelstm_block) for the full parameter table.

### `DLINEAR_BLOCK`

- Summary: Compatibility alias for the generic experimental moving-average operator, inspired by DLinear.
- Use when: DLinear-style trend/season split baselines; fast neural decomposition head comparisons
- Avoid when: shared-model multivariate decomposition problems; first-pass baselines or high-trust production workflows
- Key params: `moving_avg` (None), `primary_period` (None)
- Input/backend: `univariate` input, `python` implementation, maturity `experimental`
- Claim scope: `experimental-operator`
- Alias of: `MOVING_AVERAGE_DECOMPOSITION_BLOCK`
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.moving_mean`
- References: [Method References](method-references.md#dlinear_block)
- Learn the mechanism: [Animated explanation](gallery/dlinear-block.md#how-it-works)

See [Config Reference](config-reference.md#dlinear_block) for the full parameter table.

### `FREQMOE_BLOCK`

- Summary: FreqMoE-inspired frequency mixture head for trend plus multi-band seasonal reconstruction.
- Use when: frequency-mixture neural head ablations; multi-band seasonal decomposition experiments
- Avoid when: shared-model multivariate decomposition problems; first-pass baselines or high-trust production workflows
- Key params: `primary_period` (None), `fit_scope` ("full"), `trend_window` (None), `num_bands` (4)
- Input/backend: `univariate` input, `python` implementation, maturity `experimental`
- Claim scope: `experimental-operator`
- Alias of: none
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`
- References: [Method References](method-references.md#freqmoe_block)
- Learn the mechanism: [Animated explanation](gallery/freqmoe-block.md#how-it-works)

See [Config Reference](config-reference.md#freqmoe_block) for the full parameter table.

### `GABOR_CLUSTER`

- Summary: Experimental trained-model clustering operator with optional native acceleration.
- Use when: research prototypes; exploratory clustering-style decomposition
- Avoid when: shared-model multivariate decomposition problems; first-pass baselines or high-trust production workflows
- Key params: `model` (None), `model_path` (None)
- Input/backend: `univariate` input, `native-backed` implementation, maturity `experimental`
- Claim scope: `experimental-operator`
- Alias of: none
- Optional dependencies: faiss
- Output components: `trend`, `season`, `residual`, `components.Cluster_*`
- References: [Method References](method-references.md#gabor_cluster)
- Learn the mechanism: [Animated explanation](gallery/gabor-cluster.md#how-it-works)

See [Config Reference](config-reference.md#gabor_cluster) for the full parameter table.

### `INPARFORMER_BLOCK`

- Summary: InParformer-inspired moving-average trend plus periodic-template seasonal decomposition head.
- Use when: periodic-template neural decomposition baselines; prefix/full-scope ablation experiments
- Avoid when: shared-model multivariate decomposition problems; first-pass baselines or high-trust production workflows
- Key params: `primary_period` (None), `fit_scope` ("prefix"), `trend_window` (None)
- Input/backend: `univariate` input, `python` implementation, maturity `experimental`
- Claim scope: `experimental-operator`
- Alias of: none
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`
- References: [Method References](method-references.md#inparformer_block)
- Learn the mechanism: [Animated explanation](gallery/inparformer-block.md#how-it-works)

See [Config Reference](config-reference.md#inparformer_block) for the full parameter table.

### `LEDDAM_BLOCK`

- Summary: LEDDAM LD smoothing block exposed as a Gaussian-kernel decomposition operator.
- Use when: LEDDAM-style decomposition ablations; kernel smoothing neural head comparisons
- Avoid when: shared-model multivariate decomposition problems; first-pass baselines or high-trust production workflows
- Key params: `kernel_size` (25), `sigma` (1.0)
- Input/backend: `univariate` input, `python` implementation, maturity `experimental`
- Claim scope: `experimental-operator`
- Alias of: none
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.ld_trend`, `components.kernel`
- References: [Method References](method-references.md#leddam_block)
- Learn the mechanism: [Animated explanation](gallery/leddam-block.md#how-it-works)

See [Config Reference](config-reference.md#leddam_block) for the full parameter table.

### `MOVING_AVERAGE_DECOMPOSITION_BLOCK`

- Summary: Generic experimental moving-average operator; not a forecasting-architecture implementation.
- Use when: generic decomposition-block smoke tests; fast moving-average neural head baselines
- Avoid when: shared-model multivariate decomposition problems; first-pass baselines or high-trust production workflows
- Key params: `moving_avg` (None), `primary_period` (None)
- Input/backend: `univariate` input, `python` implementation, maturity `experimental`
- Claim scope: `experimental-operator`
- Alias of: none
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.moving_mean`
- References: [Method References](method-references.md#moving_average_decomposition_block)
- Learn the mechanism: [Animated explanation](gallery/moving-average-decomposition-block.md#how-it-works)

See [Config Reference](config-reference.md#moving_average_decomposition_block) for the full parameter table.

### `NBEATS_INTERPRETABLE`

- Summary: Torch-backed interpretable N-BEATS trend and seasonality stacks used as a learned decomposition prior.
- Use when: learned-basis decomposition experiments; N-BEATS interpretable-stack ablations
- Avoid when: shared-model multivariate decomposition problems; first-pass baselines or high-trust production workflows
- Key params: `degree_of_polynomial` (2), `num_harmonics` (8), `fit_scope` ("full"), `n_epochs` (200)
- Input/backend: `univariate` input, `python` implementation, maturity `experimental`
- Claim scope: `experimental-operator`
- Alias of: none
- Optional dependencies: torch
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`
- References: [Method References](method-references.md#nbeats_interpretable)
- Learn the mechanism: [Animated explanation](gallery/nbeats-interpretable.md#how-it-works)

See [Config Reference](config-reference.md#nbeats_interpretable) for the full parameter table.

### `PARSIMONY_BLOCK`

- Summary: Parsimony-inspired trend head with compact harmonic seasonal projection.
- Use when: compact harmonic decomposition baselines; low-parameter neural head comparisons
- Avoid when: shared-model multivariate decomposition problems; first-pass baselines or high-trust production workflows
- Key params: `primary_period` (None), `fit_scope` ("full"), `trend_window` (None), `num_harmonics` (2)
- Input/backend: `univariate` input, `python` implementation, maturity `experimental`
- Claim scope: `experimental-operator`
- Alias of: none
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`
- References: [Method References](method-references.md#parsimony_block)
- Learn the mechanism: [Animated explanation](gallery/parsimony-block.md#how-it-works)

See [Config Reference](config-reference.md#parsimony_block) for the full parameter table.

### `ST_MTM_BLOCK`

- Summary: ST-MTM-inspired smoothing head combining trend smoothing and smoothed periodic seasonality.
- Use when: seasonal-trend pretraining block ablations; smooth periodic decomposition baselines
- Avoid when: shared-model multivariate decomposition problems; first-pass baselines or high-trust production workflows
- Key params: `primary_period` (None), `fit_scope` ("prefix"), `trend_window` (None), `season_smooth_window` (None)
- Input/backend: `univariate` input, `python` implementation, maturity `experimental`
- Claim scope: `experimental-operator`
- Alias of: none
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`
- References: [Method References](method-references.md#st_mtm_block)
- Learn the mechanism: [Animated explanation](gallery/st-mtm-block.md#how-it-works)

See [Config Reference](config-reference.md#st_mtm_block) for the full parameter table.

### `TIMEKAN_BLOCK`

- Summary: TimeKAN-inspired decomposition head blending template and harmonic seasonal estimates.
- Use when: KAN-inspired neural decomposition ablations; frequency-template hybrid seasonal baselines
- Avoid when: shared-model multivariate decomposition problems; first-pass baselines or high-trust production workflows
- Key params: `primary_period` (None), `fit_scope` ("prefix"), `trend_window` (None), `num_bands` (2)
- Input/backend: `univariate` input, `python` implementation, maturity `experimental`
- Claim scope: `experimental-operator`
- Alias of: none
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`
- References: [Method References](method-references.md#timekan_block)
- Learn the mechanism: [Animated explanation](gallery/timekan-block.md#how-it-works)

See [Config Reference](config-reference.md#timekan_block) for the full parameter table.

### `TIMES2D_BLOCK`

- Summary: Times2D-inspired multi-period harmonic decomposition head.
- Use when: multi-period neural decomposition baselines; FFT-selected seasonal period comparisons
- Avoid when: shared-model multivariate decomposition problems; first-pass baselines or high-trust production workflows
- Key params: `primary_period` (None), `fit_scope` ("full"), `top_k_periods` (2), `num_harmonics` (1), `trend_window` (None)
- Input/backend: `univariate` input, `python` implementation, maturity `experimental`
- Claim scope: `experimental-operator`
- Alias of: none
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`
- References: [Method References](method-references.md#times2d_block)
- Learn the mechanism: [Animated explanation](gallery/times2d-block.md#how-it-works)

See [Config Reference](config-reference.md#times2d_block) for the full parameter table.

### `WAVEFORM_BLOCK`

- Summary: WaveForM-inspired wavelet multiresolution decomposition head.
- Use when: wavelet neural-head ablations; multiresolution trend/detail comparisons
- Avoid when: shared-model multivariate decomposition problems; first-pass baselines or high-trust production workflows
- Key params: `wavelet` ("db4"), `level` (3), `season_levels` ([1, 2])
- Input/backend: `univariate` input, `python` implementation, maturity `experimental`
- Claim scope: `experimental-operator`
- Alias of: none
- Optional dependencies: PyWavelets
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`
- References: [Method References](method-references.md#waveform_block)
- Learn the mechanism: [Animated explanation](gallery/waveform-block.md#how-it-works)

See [Config Reference](config-reference.md#waveform_block) for the full parameter table.

### `WAVELETMIXER_BLOCK`

- Summary: WaveletMixer-inspired multiresolution decomposition head using mixed wavelet detail levels.
- Use when: wavelet-mixer neural decomposition baselines; multi-level detail seasonal reconstruction
- Avoid when: shared-model multivariate decomposition problems; first-pass baselines or high-trust production workflows
- Key params: `wavelet` ("sym4"), `level` (4), `season_levels` ([1, 2, 3])
- Input/backend: `univariate` input, `python` implementation, maturity `experimental`
- Claim scope: `experimental-operator`
- Alias of: none
- Optional dependencies: PyWavelets
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`
- References: [Method References](method-references.md#waveletmixer_block)
- Learn the mechanism: [Animated explanation](gallery/waveletmixer-block.md#how-it-works)

See [Config Reference](config-reference.md#waveletmixer_block) for the full parameter table.

### `XPATCH_BLOCK`

- Summary: xPatch-inspired exponential smoothing head for standalone trend and local-season decomposition.
- Use when: exponential smoothing neural head comparisons; fast local seasonal-trend decomposition
- Avoid when: shared-model multivariate decomposition problems; first-pass baselines or high-trust production workflows
- Key params: `ma_type` ("ema"), `trend_window` (None), `season_smooth` (None)
- Input/backend: `univariate` input, `python` implementation, maturity `experimental`
- Claim scope: `experimental-operator`
- Alias of: none
- Optional dependencies: none
- Output components: `trend`, `season`, `residual`, `components.trend`, `components.season`
- References: [Method References](method-references.md#xpatch_block)
- Learn the mechanism: [Animated explanation](gallery/xpatch-block.md#how-it-works)

See [Config Reference](config-reference.md#xpatch_block) for the full parameter table.
