# Backtesting Frameworks for the Quant Trading Column

The notebooks start with a small pandas backtester so readers can inspect
signal alignment, position shifting, transaction costs, turnover, and equity
construction. The same signals can then be routed to established Python
backtesting and reporting packages once the adapter preserves those fields.

| Framework | Column use | Adapter |
|---|---|---|
| pandas vectorized baseline | transparent close-to-close research checks | `examples/quant_trading/backtest.py` |
| vectorbt | multi-asset signal matrices and parameter grids | `run_vectorbt_from_signals` |
| backtesting.py | single-asset strategy class tutorials | `run_backtestingpy_signal` |
| bt | target-weight ETF and portfolio rotation | `run_bt_target_weights` |
| Backtrader | event-driven data feeds and order logic | template writer |
| Zipline-Reloaded | calendar-safe factor research skeleton | template writer |
| QuantStats | HTML reports and performance tear sheets | `quantstats_html_report` |

## Adapter contract

An adapter is acceptable only if it preserves:

| Field | Requirement |
|---|---|
| Feature timestamp | the feature row is known before the signal date |
| Signal date | the target weight or entry flag is created before execution |
| Execution date | fills are shifted at least one bar from the signal |
| Costs | fee, slippage, borrow, FX, and turnover assumptions are explicit |
| Baseline | the same date range and cost model are available for comparison |
| Metrics | equity, returns, turnover, costs, drawdown, and parameters are exported |

## vectorbt

```python
from examples.quant_trading.frameworks import run_vectorbt_from_signals

portfolio = run_vectorbt_from_signals(prices, entries, exits)
print(portfolio.total_return())
```

Parameter grids should be selected inside training folds only. Report the tried
configuration grid, do not use the final test window for parameter choice, and
keep failed or dominated configurations in the experiment log.

## backtesting.py

```python
from examples.quant_trading.data import fetch_yahoo_ohlcv
from examples.quant_trading.frameworks import run_backtestingpy_signal

ohlcv = fetch_yahoo_ohlcv("SPY", start="2018-01-01")
stats = run_backtestingpy_signal(ohlcv, signal)
```

## bt

```python
from examples.quant_trading.frameworks import run_bt_target_weights

result = run_bt_target_weights(prices, target_weights)
```

## Backtrader and Zipline-Reloaded

The column provides template files for these framework-specific workflows:

```python
from examples.quant_trading.frameworks import write_framework_templates

write_framework_templates("examples/quant_trading/templates")
```

These event-driven frameworks require explicit trading calendars, data bundles,
adjusted-price policy, order timing, commission model, slippage model, and
delisting treatment. Keep De-Time feature generation outside the event loop
unless the experiment includes online recomputation latency and cost.

Rendered notebook transcript with code and output:
[08 backtesting framework adapters](notebooks/08_backtesting_framework_adapters.md)
