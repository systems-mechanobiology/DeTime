---
title: Decomposition Features for Time-Series Machine Learning
description: Build decomposition features from available history, compare them with raw lags on held-out forecast origins, and retain a clear information boundary.
---

# ML Workflows

DeTime provides a workflow layer around decomposition for machine-learning
pipelines. It wraps decomposition methods with a shared configuration contract,
result object, and CLI/Python surface.

## Where it fits in ML pipelines

Common machine-learning-facing uses include:

- denoising a series before feature engineering or model fitting,
- separating trend and seasonal structure before downstream regression or
  classification,
- generating components that can be summarized into tabular features,
- inspecting shared structure across channels before multivariate modeling.

These steps use one configuration contract, one result object, and one
CLI/Python surface. Whether decomposition improves an application depends on
the data, estimator and evaluation protocol.

<div class="pipeline-panel">
  <div class="pipeline-flow">
    <div class="pipeline-step">
      <strong>Raw series</strong>
      <span>sensor, experimental, or panel data</span>
    </div>
    <div class="pipeline-step">
      <strong>DeTime</strong>
      <span>trend / season / residual / components</span>
    </div>
    <div class="pipeline-step">
      <strong>Features</strong>
      <span>component summaries, residual diagnostics, channel structure</span>
    </div>
    <div class="pipeline-step">
      <strong>Model</strong>
      <span>regression, classification, clustering, or inspection</span>
    </div>
  </div>
</div>

## One-step forecasting with history-only features

The following executable example uses a **synthetic** series to demonstrate
the information boundary. Every decomposition receives a trailing history
window that ends before the forecast target. The forecasting model and its
feature scaler are fitted only on training targets.

Two Ridge models use the same fixed regularization: one receives raw lags;
the other receives those lags plus component summaries. Last-observation and
seasonal-naive predictions provide additional references. The parameters are
fixed in advance; this example does not tune them against the test interval.

```python
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from detime import DecompositionConfig, decompose

period = 12
window = 96
train_end = 240
rng = np.random.default_rng(42)
t = np.arange(360, dtype=float)
series = (
    0.02 * t
    + np.sin(2.0 * np.pi * t / period)
    + rng.normal(0.0, 0.15, t.size)
)
config = DecompositionConfig(
    method="STL", params={"period": period}, backend="python"
)

origins = np.arange(window, len(series))
raw_features, component_features = [], []
for origin in origins:
    # Predict series[origin] using observations up to origin - 1.
    history = series[origin - window : origin]
    result = decompose(history, config)
    raw_features.append(history[-period:].copy())
    component_features.append(
        [
            result.trend[-1],
            result.trend[-1] - result.trend[-period],
            result.season[-1],
            result.residual[-1],
            np.std(result.residual[-period:]),
        ]
    )

raw = np.asarray(raw_features)
augmented = np.column_stack([raw, np.asarray(component_features)])
targets = series[origins]
train = origins < train_end
test = ~train

for name, features in (("Raw lags", raw), ("Lags + components", augmented)):
    model = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    model.fit(features[train], targets[train])
    prediction = model.predict(features[test])
    mae = mean_absolute_error(targets[test], prediction)
    print(f"{name}: held-out one-step MAE = {mae:.4f}")

test_origins = origins[test]
for name, prediction in (
    ("Last observation", series[test_origins - 1]),
    ("Seasonal naive", series[test_origins - period]),
):
    mae = mean_absolute_error(targets[test], prediction)
    print(f"{name}: held-out one-step MAE = {mae:.4f}")
```

This is a rolling **one-step** evaluation. Once a test observation has
occurred, it becomes available in the history for the next forecast. The Ridge
models remain fixed after the training interval. This protocol differs from
issuing an entire future trajectory at one origin; that task would require a
separate multi-step prediction strategy.

The example runs on a CPU and uses no external data or GPU. Its errors are
illustrative results on one constructed series. Either feature set may win;
a general benefit from decomposition requires multiple datasets, training
seeds where applicable, and a declared tuning protocol. If selecting the
method, window or regularization from data, use validation origins before the
held-out test interval.

## Reconstruction and prediction answer different questions

For methods that define `residual = input - trend - season`, the identity
`input = trend + season + residual` is expected. Regressing the original
series on those same-time components and reporting training R² mostly checks
that identity. It does not measure future prediction or recovery of the true
generating components.

The forecasting example instead uses component summaries ending at the last
available observation to predict the next observation. The target is absent
from the decomposition input. Keep this distinction when replacing the
synthetic data with an application dataset.

## Other downstream tasks

For classification of fully observed windows, the complete input window may
be available at deployment. Compute its features under that contract, and
split participants, devices or time blocks as required by the scientific
question. Overlapping windows from one record need particular attention when
assigning train and test sets.

For anomaly detection, specify whether an alert is issued immediately or
after a permitted delay. A retrospective component estimate can use more
context than an immediate detector. For clustering, report the component
grouping, scaling, distance and clustering method together; a change in the
whole pipeline does not isolate the contribution of decomposition.

The [Python decomposition tools guide](research/python-decomposition-tools.md)
explains method assumptions, output differences and reproducibility controls.

## Project notes

Release checks, coverage boundaries, and validation evidence live in
[Reproducibility](reproducibility.md). This page stays focused on where the
package fits in downstream ML work.
