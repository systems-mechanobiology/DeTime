# Strategy Selection and Falsification Map

De-Time is a feature layer, not a strategy claim by itself. Each strategy starts
with a hypothesis, a baseline, and a failure mode that would make the result
unusable.

| Strategy family | Hypothesis | Minimum baseline | Failure mode | Tutorial |
|---|---|---|---|---|
| Single-asset timing | trend plus residual timing improves entry quality | buy-and-hold and moving-average timing | underperforms after costs or trades too often | [02 single-asset timing](notebooks/02_single_asset_timing_vectorbt.md) |
| Turtle / Donchian | De-Time trend filter removes weak breakouts | unfiltered Donchian breakout | filter removes winners or adds parameter fragility | [03 Turtle Donchian trend filter](notebooks/03_turtle_donchian_trend_filter.md) |
| Residual mean reversion | modeled residual is cleaner than price z-score | price z-score mean reversion | residual remains directional or cost-sensitive | [02 single-asset timing](notebooks/02_single_asset_timing_vectorbt.md) |
| Pairs trading | spread residual helps avoid trend drift | classical spread z-score pair trade | spread trend persists or hedge ratio is unstable | [04 pairs trading residual cycle](notebooks/04_pairs_trading_residual_cycle.md) |
| Cross-sectional factors | decomposition factor candidates rank assets better than simple momentum | equal-weight, benchmark ETF, momentum-only top-N, random top-N | result depends on mega-cap sample or one regime | [05 cross-sectional factor selection](notebooks/05_cross_sectional_factor_selection.md) |
| Style / sector rotation | decomposition score improves ETF rotation timing | equal-weight sector basket and momentum rotation | turnover or one sector explains the result | [06 style and sector rotation](notebooks/06_style_sector_asset_rotation_bt.md) |
| Crypto regime | 24/7 trend and residual stress identify regime changes | buy-and-hold and volatility filter | calendar mismatch or fees erase the signal | [07 Korea, US, and crypto](notebooks/07_korea_us_crypto_multimarket.md) |
| Risk overlay | residual stress identifies unreliable periods | same strategy without overlay | cuts exposure after losses rather than before them | all strategy notebooks |

## Signal principles

1. Trend sets direction.
2. Cycle sets timing.
3. Residual measures deviation from the modeled structure.
4. Residual spikes and reconstruction error are reliability warnings.
5. Every signal is computed walk-forward before it is backtested.
6. A strategy is rejected when it fails its baseline or data gate.

## Component-to-rule checks

| Component | Before using it | After using it |
|---|---|---|
| Trend | plot price against walk-forward trend and inspect `trend_slope` | check whether it accepts good trades earlier than a price-only baseline |
| Cycle | inspect `season_z` or `season_slope` around entries | keep it diagnostic unless it improves a baseline out of sample |
| Residual | plot residual bands and mark entries/exits | verify that residual deviations mean-revert after costs |
| Residual stress | compare stress spikes with drawdowns and calendar gaps | use it to shrink exposure or reject periods, not to explain losses after the fact |
| Reconstruction error | inspect noisy assets before ranking them | penalize unreliable decompositions instead of treating every component as alpha |

## Example: trend pullback

```python
features = walkforward_decompose(prices, method="ROBUST_STL", period=63)
entries, exits = trend_pullback_signals(
    prices,
    features,
    residual_entry_z=-1.0,
    residual_exit_z=0.25,
    min_trend_slope=0.0,
)
```

In the notebooks this call is routed through `ROBUST_STL`, which is the default
for market-price examples. Use plain `STL` or faster baselines for sensitivity
checks, not as the headline decomposition.

## Example: pair spread residual

```python
spread = np.log(prices["KO"]) - np.log(prices["PEP"])
spread_panel = pd.DataFrame({"KO_PEP_spread": spread.add(100.0)})
spread_features = walkforward_decompose(
    spread_panel,
    method="ROBUST_STL",
    period=63,
    use_log_price=False,
)

weights = pair_trading_weights(
    prices["KO"],
    prices["PEP"],
    lookback=120,
    entry_z=1.5,
    exit_z=0.25,
    spread_residual_z=spread_features["residual_z"]["KO_PEP_spread"],
)
```

Compare this residual version with the classical spread z-score baseline over
the same dates and costs. A persistent spread trend is a failure warning even if
individual residual entries look attractive.
