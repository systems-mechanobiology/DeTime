---
title: "Time-Series Decomposition in 2026: Methods and Research Map"
description: "Compare classical decomposition, wavelet tokenization, neural decomposition blocks, new SSA and VMD research, and evaluation methods with verified references."
---

# Time-Series Decomposition in 2026: Algorithms, Tokens, and Losses

Decomposition now enters time-series systems at several stages: an explicit
signal transform, a forecasting block, a discrete tokenizer, a decoder, a
training objective, or a statistical diagnostic. These choices answer different
questions. A useful comparison starts by identifying the object each method
produces and the evidence needed to judge it.

This reading map covers **20 selected references**, with publication records
checked on **29 October 2026**. It connects classical methods to recent research
through 2026. The accompanying [CSV](decomposition-reading-list.csv) records
publication status, sources, method role, and relationship to DeTime; the
[BibTeX file](decomposition-reading-list.bib) contains normalized citations.
Scope is selective, with an emphasis on decomposition mechanisms and evaluation.

## Start with the object you need

| Object | Representative work | What to inspect |
|---|---|---|
| Components of an observed signal | STL, SSA, EMD, VMD | Component meaning, reconstruction, boundary behavior, and parameter sensitivity |
| A forecasting architecture | [Autoformer](https://proceedings.neurips.cc/paper_files/paper/2021/hash/bcc0d400288793e8bdcd7c19a8ac0c2b-Abstract.html), [TimeMixer](https://proceedings.iclr.cc/paper_files/paper/2024/hash/a7ac8a21e5a27e7ab31a5f42a0117bdb-Abstract-Conference.html) | Held-out forecast accuracy and an ablation isolating the decomposition block |
| Discrete tokens for a pretrained forecaster | [WaveToken](https://proceedings.mlr.press/v267/masserano25a.html) | Tokenization error, coefficient ordering, vocabulary, training data, and forecast quality |
| A loss applied during training | [DBLoss](https://proceedings.neurips.cc/paper_files/paper/2025/hash/2823c4f838727564c108c85d7e6e8507-Abstract-Conference.html) | The loss definition and performance with the same backbone and training budget |
| A structured forecast decoder | [Implicit Forecaster](https://papers.neurips.cc/paper_files/paper/2025/hash/0e82ef0c89df6a6eff8734ea7e27c42f-Abstract-Conference.html) | The parameterization of future waves and the decoder's incremental contribution |
| A rule for selecting signal components | [Confident grouping in SSA](https://link.springer.com/article/10.1007/s10463-026-00987-8) | Statistical assumptions, error control, and sensitivity to the grouping criterion |

The inspection criteria in the last column are editorial recommendations.
They are not a cross-paper performance ranking.

## Classical families remain useful because their assumptions differ

| Family | Mechanism | Useful starting question | Choices to record |
|---|---|---|---|
| [STL](https://www.scb.se/contentassets/ca21efb41fee47d293bbee5bf7be7fb3/stl-a-seasonal-trend-decomposition-procedure-based-on-loess.pdf), 1990 | Iterative LOESS smoothing separates trend, a seasonal component, and remainder. | Does a specified seasonal period provide a meaningful description? | Period, smoothing spans, robustness settings, and endpoint treatment |
| [MSTL](https://www.inderscience.com/info/e_inarticle.php?artid=143957), 2025 journal version | Extends STL to several seasonal periods. | Are multiple recurring periods relevant, such as daily and weekly cycles? | Every period, seasonal window, transformation, and iteration setting |
| [SSA](https://link.springer.com/book/10.1007/978-3-662-62436-4), 2020 reference monograph | Embeds a series in a trajectory matrix, decomposes it, groups components, and reconstructs time-domain signals. | Can a low-dimensional subspace capture the structure of interest? | Embedding window, retained rank, grouping rule, and reconstruction procedure |
| [EMD](https://doi.org/10.1098/rspa.1998.0193), 1998 | Uses data-dependent sifting to extract intrinsic mode functions. | Which oscillatory modes emerge without fixing a sinusoidal basis? | Extrema/envelope implementation, stopping criteria, mode count, and boundaries |
| [EEMD](https://doi.org/10.1142/S1793536909000047), 2009 | Averages decompositions of noise-perturbed copies of a signal. | How do ensemble settings affect extracted modes? | Noise scale, number of trials, seed, and mode-alignment behavior |
| [CEEMDAN](https://sinc.unl.edu.ar/sinc-publications/2011/TCSF11/), 2011 | Uses adaptive noise-assisted ensembles and a residual-based construction. | Does the chosen implementation provide the intended ensemble decomposition? | Exact algorithm variant, noise settings, trials, seed, and residual handling |
| [VMD](https://math.montana.edu/dzosso/code/), 2014 | Jointly estimates band-limited modes and their center frequencies through a variational objective. | Is a chosen number of narrow-band modes appropriate? | Mode count, bandwidth penalty, initialization, tolerance, and boundary extension |
| [Wavelet multiresolution analysis](https://doi.org/10.1109/34.192463), 1989 foundation | Represents a signal through approximation and detail coefficients across scales. | Which scales and localized changes are useful for the task? | Wavelet family, levels, extension mode, coefficient handling, and inverse transform |

The dates distinguish original work from later reference material. SSA predates
the 2020 monograph. MSTL's [preprint appeared in 2021](https://arxiv.org/abs/2107.13462),
while its journal version is *International Journal of Operational Research*
52(1), 79–98 (2025). The bibliography uses the published version.

The columns describing useful questions and recorded choices are practical
guidance. They do not establish that a family will outperform another on a new
dataset. A frequency band, an intrinsic mode function, and an SSA eigentriple
group also need explicit interpretation before being called a physical trend,
season, or noise source.

## Decomposition inside modern forecasting systems

### Architecture: a family of design choices

[Autoformer (NeurIPS 2021)](https://proceedings.neurips.cc/paper_files/paper/2021/hash/bcc0d400288793e8bdcd7c19a8ac0c2b-Abstract.html)
uses decomposition as an internal forecasting block, alongside its
Auto-Correlation mechanism.
[DLinear, introduced in AAAI 2023](https://ojs.aaai.org/index.php/AAAI/article/view/26317),
provides a simpler decomposition-based linear forecasting reference. Together,
they motivate a useful experimental control: compare the same data and split
with a simple decomposed model before attributing a gain to a more elaborate
architecture.

[TimeMixer (ICLR 2024)](https://proceedings.iclr.cc/paper_files/paper/2024/hash/a7ac8a21e5a27e7ab31a5f42a0117bdb-Abstract-Conference.html)
decomposes series at multiple sampling scales and mixes seasonal and trend
representations in different directions. Its contribution concerns the joint
architecture of decomposition, mixing, and prediction. Replacing one smoothing
operation alone does not reproduce that architecture.

[TimeMixer++ (ICLR 2025)](https://proceedings.iclr.cc/paper_files/paper/2025/hash/2b187165e28fdfdc0ffb34d1bfff2b0c-Abstract-Conference.html)
introduces time imaging, time-image decomposition with dual-axis attention,
and mixing across scales and resolutions. It extends the discussion to several
analysis tasks. Its latent representations need task-specific interpretation;
their names alone do not establish recovery of unique physical components.

### Tokenization: decomposition changes what a model predicts

[WaveToken (ICML 2025)](https://proceedings.mlr.press/v267/masserano25a.html)
scales a time series, applies wavelet decomposition, thresholds and quantizes
coefficients, and trains an autoregressive model to forecast coefficients.
The reconstructed forecast comes from the inverse tokenization process.

This is a useful reference when the research question concerns a representation
for a foundation model. A standalone wavelet transform exposes only part of
that system. A convincing tokenizer comparison should keep the training data,
backbone, evaluation split, and compute allocation controlled while examining
both representation error and downstream forecast quality. That is an
experimental recommendation; this article does not supply a new tokenizer
benchmark.

### Training and decoding: decomposition has additional entry points

| Work | Published venue | Role described by the paper | A useful comparison to run |
|---|---|---|---|
| [DBLoss](https://proceedings.neurips.cc/paper_files/paper/2025/hash/2823c4f838727564c108c85d7e6e8507-Abstract-Conference.html) | NeurIPS 2025 | Decomposes horizon sequences with exponential moving averages and weights losses for the resulting components. | Hold the forecaster fixed and compare objectives, including their effect on the original task metric. |
| [DecompNet](https://proceedings.nips.cc/paper_files/paper/2025/hash/2e56189f02f4b00de8bf6020455830e0-Abstract-Conference.html) | NeurIPS 2025 | Transfers decomposition-related knowledge into a model through an implicit-decomposition framework; the paper describes inference without explicit input decomposition. | Account for training cost as well as inference cost and compare the same backbone with and without the framework. |
| [Implicit Forecaster](https://papers.neurips.cc/paper_files/paper/2025/hash/0e82ef0c89df6a6eff8734ea7e27c42f-Abstract-Conference.html) | NeurIPS 2025 | Predicts constituent waves through frequency, amplitude, and phase in an added decoding module. | Compare decoder variants while holding the representation and forecasting protocol fixed. |

These papers enlarge the design space. They do not supply interchangeable
standalone decomposers. Their original experimental results remain tied to
their own datasets, implementations, and evaluation protocols.

## Three developments to read from 2026

### Short-time VMD: local frequency structure

[Short-time variational mode decomposition](https://www.sciencedirect.com/science/article/pii/S0165168425003172)
appears in *Signal Processing* 238, article 110203 (2026). It introduces
windowed variational decomposition using a short-time Fourier representation,
with dynamic and non-dynamic versions distinguished by whether center
frequencies can change over time. The paper links
[author-provided code](https://github.com/plustar/Short-Time-Variational-Mode-Decomposition).
The issue year is 2026; the [publisher version](https://upcommons.upc.edu/bitstreams/50ad1039-832e-47b9-9bfd-7b58bb25c1a7/download)
records online availability on 19 July 2025.

For a decomposition library, this suggests a concrete extension to investigate:
how local windows and time-varying frequencies change mode recovery. Window
length, overlap, edge behavior, and mode correspondence should be included in
any implementation comparison. This article records the method as literature;
it does not claim an STVMD implementation in DeTime.

### SSA grouping: a statistical decision

[Movahedifar, Preusse, Vesely, and Dickhaus](https://link.springer.com/article/10.1007/s10463-026-00987-8)
published *Confident grouping in singular spectrum analysis via multiple
testing* on 25 June 2026. Their procedure tests weighted-correlation-based
separability across candidate signal/noise groupings, using a wild bootstrap
and family-wise error control.

This addresses a practical part of SSA that a fast singular-value decomposition
alone leaves open: selecting components. Its statistical guarantees belong to
the paper's hypotheses and assumptions. They should not be interpreted as a
general certificate that an estimated component is a particular biological,
economic, or mechanical process. The grouping procedure is not implemented by
adding this reference to DeTime.

### TimeRecipe: test the contribution of a module

[TimeRecipe (ICLR 2026)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/f46ddea413df86832418c5e04e59644f-Abstract-Conference.html)
studies forecasting designs at the module level, including choices such as
decomposition and normalization. It offers a relevant evaluation perspective
for developers comparing alternative decomposition operators inside a model.

The practical implication is to preserve the rest of the pipeline while
changing the component under study. Changing the tokenizer, scaling, backbone,
and training budget together answers a different question: whether the whole
system performs better under that combined configuration.

## Evaluate the claim you want to make

Two evaluation questions deserve separate evidence. A forecasting experiment
asks whether a representation helps predict unseen observations. A component
recovery experiment asks whether estimated components match an explicit target.
The published
[standalone decomposition benchmark (ICML 2026)](https://proceedings.mlr.press/v306/wu26bh.html)
provides an example of the latter using controlled generating mechanisms and
complementary structural metrics. That paper and the DeTime software package
are distinct artifacts; their relationship is described in the repository's
[project note](https://github.com/systems-mechanobiology/DeTime/blob/main/RELATION_TO_ICML2026.md).

Reconstruction alone cannot determine the correct component allocation.
For an additive decomposition, `x[t] = T[t] + S[t] + R[t]`.
Replacing `T[t]` by `T[t] + a[t]` and `S[t]` by `S[t] - a[t]` preserves
the same reconstruction for any sequence `a[t]`. Additional assumptions or
reference information are therefore necessary to judge component meaning.

The following is a proposed validation checklist, rather than a new empirical
result:

| Intended claim | Evidence to collect | Common ambiguity to resolve |
|---|---|---|
| Faithful numerical reconstruction | Reconstruction error, shape checks, and missing-value policy | Components can sum correctly while carrying the wrong structure. |
| Useful component recovery | Known or defensible component targets, including shape, phase, and frequency behavior | A smooth-looking curve does not identify a generating mechanism. |
| Better forecasting | Chronological holdout, a frozen preprocessing policy, and rolling-origin evaluation where appropriate | Full-series preprocessing can expose future observations to an earlier prediction origin. |
| Stable decomposition | Repeated seeds for stochastic methods and perturbations of parameters, endpoints, and observations | A single favorable run hides variability. |
| More efficient software | Matched inputs, settings, precision, dependencies, and hardware | A faster configuration may be computing a different approximation. |
| Useful downstream features | Fixed feature definitions, training-only fitting, and held-out evaluation | Fitting the original series from its own reconstructing components is not evidence of predictive value. |

For forecasting, document the information available at each prediction origin.
Fit every data-dependent preprocessing step using that information. If a
decomposition revises old components when new samples arrive, measure those
revisions separately from the final offline fit. For offline signal analysis,
using the complete observed record can be appropriate; the intended use must
be stated.

## Where DeTime fits

DeTime supplies a shared configuration, result object, and execution surface for
decomposition workflows. Its
[method matrix](../method-matrix.md),
[method references](../method-references.md), and
[machine-facing interface](../machine-api.md)
describe the implementation boundaries.

The current documentation distinguishes maintained SSA/MSSA and STD/STDR paths,
upstream wrappers such as STL/MSTL, EMD-family methods, VMD and wavelets,
optional backends, and experimental operators. Several experimental names refer
to operators **inspired by** published forecasting models. An operator carrying
an architecture's name does not establish reproduction of that model's training
procedure, complete network, or paper results. Consult the method's actual
status and upstream reference before selecting an experimental baseline.

A useful first workflow is to choose two or three families with different
assumptions, fix their settings, inspect the output contract and diagnostics,
and evaluate the property needed downstream. Start with
[choosing a method](../choose-a-method.md) and the
[quickstart](../quickstart.md), then use the
[software comparison](../comparisons.md) for package-level trade-offs.

## Reference maintenance and scope

The CSV contains the exact publication titles and author lists, role labels,
primary URLs, verified identifiers, bibliographic provenance, and an access
date. Blank identifier fields mean that no identifier was included in this
verification pass. They do not assert that an identifier does not exist.

DBLP records were preferred for bibliographic corroboration where available;
publisher and official proceedings records determine publication status.
The BibTeX entries are normalized from those records, with stable local keys
and optional fields omitted when unnecessary or unverified. They are not
presented as unmodified downloads. MSTL cites its 2025 journal version, and
WaveToken cites its 2025 ICML proceedings entry rather than the earlier
preprint. The 2026 SSA grouping paper is recorded as a published online article
without inventing volume or page numbers.

This map does not claim exhaustive coverage of all decomposition applications,
all 2026 publications, or the latest revision of every linked implementation.
Source verification establishes what the papers describe; independent
reproduction of their experiments is a separate task. Additions should retain
that distinction and supply a primary source before changing implementation
or performance claims.
