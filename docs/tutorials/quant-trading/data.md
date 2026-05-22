# Quant Trading Data Due Diligence

The quant trading column starts with a data decision. A strategy result is not
publishable until the source, universe, calendar, adjustment policy, cache date,
and missing-data profile are visible.

## Default source

The default notebook source is Yahoo Finance through `yfinance`:

```python
from examples.quant_trading.data import fetch_yahoo_prices

prices = fetch_yahoo_prices(
    ["AAPL", "MSFT", "NVDA", "005930.KS", "000660.KS", "BTC-USD", "ETH-USD"],
    start="2018-01-01",
    interval="1d",
    cache_dir="examples/quant_trading/data/cache",
)
```

The loader validates that the returned panel is non-empty, contains requested
tickers, has enough observations, and does not consist of all-missing columns.
Those checks are the first gate, not a complete data-vendor audit.

## Example universes

| Universe | Examples | Use |
|---|---|---|
| US large cap | `AAPL`, `MSFT`, `NVDA`, `AMZN`, `META` | stock timing and cross-sectional ranking |
| US style ETFs | `SPY`, `QQQ`, `IWM`, `MTUM`, `QUAL`, `VLUE` | style rotation |
| US sector ETFs | `XLK`, `XLF`, `XLE`, `XLV`, `XLY` | sector rotation |
| Korea equities | `005930.KS`, `000660.KS`, `035420.KS` | Korea market examples |
| Crypto pairs | `BTC-USD`, `ETH-USD`, `SOL-USD` | 24/7 regime examples |

## Pass/fail gate

| Check | Pass | Fail action |
|---|---|---|
| Source identity | vendor or API wrapper is named, with cache path or access date | do not compare strategy results |
| Date coverage | every ticker has enough observations for the train window and test period | shrink universe or change window |
| Missing ratio | missing ratio is below the notebook threshold, usually 5% | inspect ticker, calendar, or cache |
| Adjusted price policy | adjusted/unadjusted field is known | do not interpret corporate-action periods |
| Calendar | timezone and trading calendar are compatible across assets | split the universe or align explicitly |
| Universe membership | ticker list is documented before results are known | avoid cross-sectional claims |
| Survivorship | current-universe bias is named or removed | use point-in-time membership for claims |
| Stale or delisted tickers | flat, missing, or terminated series are flagged | remove with a documented rule |

## Data audit

```python
from examples.quant_trading.data import data_audit_report

audit = data_audit_report(prices)
print(audit)
```

The audit report records the first and last timestamps, observation count,
missing ratio, and price range for each asset. Use the audit as a pass/fail
gate before feature construction.

Rendered notebook transcript with code and output:
[01 real market data and De-Time features](notebooks/01_real_market_data_and_detime_features.md)

## yfinance boundaries

`yfinance` is an unofficial public wrapper, not licensed point-in-time market
data. Treat it as a convenient source for reproducible tutorials and smoke
tests. It can carry current-universe survivorship bias, delisting gaps,
corporate-action ambiguity, cache/date drift, timezone differences, and calendar
mismatch between equities and crypto.

## Replacement source

For production research, replace the public wrapper with a licensed data vendor
and document:

- adjusted versus unadjusted prices;
- split and dividend policy;
- point-in-time symbol membership;
- trading calendar and timezone;
- delisting handling;
- FX conversion;
- borrow, funding, and execution assumptions.
