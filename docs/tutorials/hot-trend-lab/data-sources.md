# Hot Trend Lab Source Protocol

Every Hot Trend Lab chart starts with a source card. The card tells the reader
what the series measures, when it was collected, how much coverage it has, and
which claim it can support. This keeps the column readable without hiding the
measurement limits.

## Source card

Use this checklist before publishing a chart or table:

| Field | What to record | Pass condition |
|---|---|---|
| Source | API, endpoint, vendor, or cached public snapshot | the source can be named and re-fetched or inspected |
| Query | category, keyword, ticker basket, article title, or repo list | another reader can reproduce the selection |
| Timestamp | access date plus source time field | the collection date is visible in the table |
| Coverage | first timestamp, last timestamp, observation count, missing ratio | gaps are small enough for the intended chart |
| Refresh rule | per run, daily, weekly, or event-driven | cadence matches the claim being made |
| Interpretation | what the source measures and what it does not measure | the article sentence stays inside the evidence |

## Source registry

The registry is the live list of public feeds used by the notebooks. Each row
maps a source to its metric, notebook use, refresh rule, and interpretation
limit.

## Reliability matrix

| Source | Measures | Best use | Main limit | Publish threshold |
|---|---|---|---|---|
| arXiv API | public preprint counts and metadata | research-output trend, deadline pulses, topic watchlists | preprints are not peer-reviewed; cross-listing and query wording change counts | query and date window shown; spike explained against deadline context |
| Hugging Face Hub API | model metadata, downloads, likes | current open-model attention and repeated snapshot retention | one snapshot is cross-sectional; downloads do not measure quality | snapshot date shown; repeated snapshots required for momentum language |
| GitHub REST API | repo metadata and stargazer timestamps | developer attention and launch-week velocity | token limits, page limits, bots, and repo selection bias | covered page/window shown; stars described as attention |
| Wikimedia Analytics API | article pageviews | public attention and hype-decay curves | article naming and media events can dominate the series | project, article, date range, and access type shown |
| DeFiLlama stablecoin API | stablecoin supply and chain distribution | liquidity context around crypto events | endpoint schema can change; supply is not execution liquidity | schema inspected and top-chain context shown |
| CoinGecko API | crypto price and market data | price residual context for BTC/ETH examples | public API rate limits and vendor methodology | market structure language; no trade recommendation |
| Yahoo Finance through `yfinance` | public market prices | AI infrastructure price-proxy examples | unofficial public wrapper; not licensed point-in-time market data | basket definition shown; valuation claims excluded |

## API, cache, and timestamp rules

Public APIs change shape, paginate results, and rate-limit unauthenticated
requests. Each notebook records the endpoint or query context, then writes a
source audit table with first timestamp, last timestamp, observation count, and
missing ratio. Cached files are treated as dated public snapshots rather than
anonymous local data.

For snapshot sources, wording changes with depth:

| Snapshot depth | Allowed wording | Avoid |
|---|---|---|
| One dated snapshot | current public ranking or adoption proxy | momentum, acceleration, retention |
| Repeated snapshots | change in downloads, likes, stars, or attention over time | quality, production usage, valuation |
| Full source history or scheduled collection | trend, seasonality, residual events over the covered window | claims outside the source universe |

## Source snapshot rules

Cached source snapshots keep the same source-card fields as freshly fetched
data: source, query, access date, time range, coverage, and interpretation
scope. A cache can support a chart only when its date and query are visible.

## Replacement sources

A notebook may use a better licensed or institutional source, but the result
still needs the same source card. For production work, add vendor name, point-in
time policy, revision policy, calendar, and redistribution limits.
