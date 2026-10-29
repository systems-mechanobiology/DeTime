---
title: Decomposition Guide — English Sharing Kit
description: English post drafts for sharing a practical comparison of Python time-series decomposition tools, with source links and a clear DeTime maintainer disclosure.
---

# Decomposition Guide: English Sharing Kit

*Prepared 29 October 2026. These are reusable drafts; their presence in this
repository does not indicate publication on an external platform.*

Each draft links to the [full comparison](python-decomposition-tools.md), which
contains the official sources and the scope of the comparison. Use the article
URL after the documentation deployment is live:

<https://systems-mechanobiology.github.io/DeTime/research/python-decomposition-tools/>

## LinkedIn or a research-community post

**STL, SSA, wavelets, EMD, or VMD: what are you actually choosing?**

A decomposition comparison needs more than a list of methods.

Which seasonal periods are supplied? How are modes grouped? Are outputs
coefficients or sample-aligned components? Does preprocessing use observations
that would be unavailable when the forecast is issued?

We put together a practical guide to statsmodels, PyWavelets, PyEMD, emd, pyts,
SSALib, sktime, PySDKit and DeTime. It covers the documented interfaces,
reproducibility choices and evaluation pitfalls, with links to the official
sources.

One useful check: if the residual is defined as input minus trend minus
seasonality, exact reconstruction is expected. Evidence that the estimated
components represent the process needs a separate test.

We maintain DeTime, a Python and CLI toolkit for running decomposition families
through a shared configuration and result interface. The guide also explains
when a specialist package is the more useful starting point.

Read the guide:
https://systems-mechanobiology.github.io/DeTime/research/python-decomposition-tools/

## Short post

STL, SSA, wavelets, EMD, or VMD? We compared Python decomposition tools by
assumptions, outputs, reproducibility and forecasting workflow. From the
DeTime maintainers:
https://systems-mechanobiology.github.io/DeTime/research/python-decomposition-tools/

## A five-post thread

### 1

STL, SSA, wavelets, EMD, or VMD? Start with the structure you want to estimate,
the observations available at prediction time, and the output your next step
needs. We maintain DeTime and wrote a practical comparison of the Python tools.

### 2

STL uses a seasonal period; MSTL supports several. Wavelets expose scale
coefficients; SSA needs a window and grouping rule; EMD-family methods and VMD
produce modes. Record the choices that turn these outputs into your features.

### 3

If residual = input - trend - season, reconstruction is exact by construction.
That checks arithmetic consistency. Testing component identification needs
known components, independent measurements, or another justified reference.

### 4

For a forecast at time t, decompose only the history available at t. Computing
components on the full record and slicing afterward can retain future
information. Reproduce the information available at deployment.

### 5

The guide covers statsmodels, PyWavelets, PyEMD, emd, pyts, SSALib, sktime,
PySDKit and DeTime, with official sources and the scope of each comparison:
https://systems-mechanobiology.github.io/DeTime/research/python-decomposition-tools/

## Newsletter blurb

**A practical map of Python decomposition tools.** This guide compares STL,
MSTL, SSA, wavelets, EMD-family methods and VMD by their assumptions, outputs
and reproducibility controls. It also explains why reconstruction error alone
cannot establish component recovery, and how to keep future observations out
of forecasting preprocessing. Written by the DeTime maintainers, with links to
official documentation and a distinction between implemented software,
proposed evaluations and measured evidence.

[Read the guide](https://systems-mechanobiology.github.io/DeTime/research/python-decomposition-tools/).

## Repository description for profiles

DeTime provides Python and CLI workflows for time-series decomposition, with a
shared configuration, trend/season/residual results, backend metadata and
machine-readable schemas. The project includes method references, tutorials
and a source-linked guide to choosing decomposition tools.

[Repository](https://github.com/systems-mechanobiology/DeTime) ·
[Quickstart](https://systems-mechanobiology.github.io/DeTime/quickstart/) ·
[Comparison guide](https://systems-mechanobiology.github.io/DeTime/research/python-decomposition-tools/)
