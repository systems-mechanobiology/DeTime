---
title: Time-Series Decomposition Research and Practical Guides
description: Choose Python decomposition tools, explore recent algorithms and neural modules, and download a verified reading list with BibTeX references.
---

# Decomposition Research and Practical Guides

Use these guides to choose a method, understand its assumptions, and design a
comparison that answers your application question. The articles are written by
the DeTime maintainers and link to primary papers and official software sources.

| Start with your question | Guide |
|---|---|
| Which method and Python package fit my data? | [STL, SSA, Wavelets, EMD, or VMD? Choosing Python Decomposition Tools](python-decomposition-tools.md) |
| Where is decomposition used in recent research? | [Time-Series Decomposition in 2026: Algorithms, Tokens, and Losses](decomposition-landscape-2026.md) |
| How can components become forecasting features? | [History-only features and held-out evaluation](../ml-workflows.md) |
| Which methods does DeTime actually implement? | [Method matrix](../method-matrix.md) and [configuration reference](../config-reference.md) |

## Download the reading list

The initial selection contains **20 references**, with publication records
checked on **29 October 2026**. Eight cover classical methods and reference
material, eight cover neural architectures, tokenization, objectives and
decoders, and four cover methods or evaluation with 2026 publication records.

- [CSV: titles, authors, publication status, mechanisms, sources, and verification dates](decomposition-reading-list.csv)
- [BibTeX: normalized citations with bibliographic provenance](decomposition-reading-list.bib)

The map identifies literature candidates separately from implemented DeTime
features. It records publication status and the cited version rather than
assuming that a preprint date is the final publication date. The selection is
intended to support method choice and follow-up reading; it is not exhaustive.

## Use and share

The [quickstart](../quickstart.md) provides the first runnable decomposition.
The [English sharing kit](sharing-kit.md) contains a community post, short
post, thread, and newsletter blurb linked to the comparison guide. The drafts
disclose maintainer involvement and are ready to adapt to the destination's
format and community rules.

## Suggest an addition

Open a [repository issue](https://github.com/systems-mechanobiology/DeTime/issues/new)
with the publication title, primary-source URL, publication status, and a brief
explanation of the decomposition mechanism. For software comparisons, include
the upstream documentation and tested version when available. An implementation
or performance claim needs its own reproducible evidence.
