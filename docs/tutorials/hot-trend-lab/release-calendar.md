# Hot Trend Lab Publishing Protocol

A column works when it can be refreshed without reinventing the analysis each
week. This protocol turns the notebooks into a weekly editorial loop.

## Weekly loop

| Day | Action | Output |
|---|---|---|
| Monday scan | refresh source cards and run the low-cost notebooks | candidate table with coverage and residual ranks |
| Midweek verify | inspect query wording, API limits, cache dates, and suspicious spikes | short list of publishable charts |
| Friday publish | write the article around one source card and one clear judgment | source table, figure, boundary paragraph, notebook link |

## Residual trigger rules

Use residuals as prompts for closer reading, not as final conclusions.

| Trigger | What to check before writing | Likely article form |
|---|---|---|
| Category residual spike | conference deadline, query drift, duplicate cross-listing | arXiv research pulse |
| Hugging Face snapshot jump | launch date, model family, benchmark context, repeated snapshots | open-model pulse |
| GitHub star velocity burst | pagination coverage, token limit, media or demo event | developer attention pulse |
| Wikimedia attention spike | article title, news event, source project, decay speed | public-attention note |
| Crypto residual event | BTC/ETH move, stablecoin context, venue or macro event | market-structure note |
| AI infrastructure basket move | basket definition, sector or market benchmark, earnings calendar | market-proxy note |

## Publish/no-publish thresholds

| Gate | Publish when | Do not publish when |
|---|---|---|
| Minimum observations | the chart has enough points for the selected method and period | warm-up or cool-down dominates the event table |
| Freshness | access date matches the article date or stated cache date | cache date is unclear |
| Residual threshold | residual event is large enough to survive chart inspection and source context | the event is a first/last-window artifact |
| Source failure | failure is visible and the article can be framed as a source limitation | missing source is silently replaced |
| Artifact checklist | source card, figure, summary table, boundary paragraph, and notebook link are present | any artifact is missing |

## Article contract

Every article includes:

1. a source card with query, access date, coverage, and limits;
2. one decomposition summary table or figure;
3. a residual event table when the story is event-driven;
4. two or three sentences explaining the chart axes and signal;
5. a boundary sentence naming what the chart does not measure;
6. a rendered notebook transcript link.

## Cadence map

| Cadence | Article | Notebook | Publish when |
|---|---|---|---|
| Weekly | arXiv AI category pulse | [01 arXiv category pulse](notebooks/01_arxiv_category_pulse.md) | source coverage is complete and deadline context is checked |
| Weekly | AI agent / coding-agent research pulse | [02 arXiv agent research pulse](notebooks/02_arxiv_agent_research_pulse.md) | query terms are stable and a residual event has a clear topic |
| Weekly | Hugging Face open-model pulse | [03 Hugging Face open-model pulse](notebooks/03_huggingface_open_model_pulse.md) | snapshot date and ranking scope are explicit |
| Weekly | GitHub AI-agent star velocity | [04 GitHub AI-agent star velocity](notebooks/04_github_ai_agent_star_velocity.md) | coverage window and pagination limits are shown |
| Monthly | Wikimedia attention and hype decay | [05 Wikipedia attention hype decay](notebooks/05_wikipedia_attention_hype_decay.md) | article set and date window are stable |
| Event-driven | crypto and stablecoin liquidity pulse | [06 crypto stablecoin liquidity pulse](notebooks/06_crypto_stablecoin_liquidity_pulse.md) | a residual event has market-structure context |
| Earnings / macro weeks | AI infrastructure market pulse | [07 AI infrastructure market pulse](notebooks/07_ai_infrastructure_market_pulse.md) | basket definition and benchmark comparison are included |
