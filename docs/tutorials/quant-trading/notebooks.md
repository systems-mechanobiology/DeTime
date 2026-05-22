# Quant Trading Notebook Series

The executable notebooks live with the De-Time examples at
`examples/notebooks/quant_trading/`. This page presents the notebook path as a
web tutorial first, so the research flow stays readable before a reader opens
Jupyter.

<div class="quant-notebook-browser">
  <div class="quant-browser-copy">
    <span class="section-kicker">Notebook browser</span>
    <h2>Follow the research column without leaving the docs surface.</h2>
    <p>Each notebook keeps one boundary visible: De-Time produces decomposition features; the data policy, signal recipe, backtest adapter, and audit protocol remain explicit.</p>
    <div class="quant-stage-metrics">
      <span><b>00</b> start</span>
      <span><b>07</b> strategy cases</span>
      <span><b>09</b> audit</span>
    </div>
  </div>
  <div class="quant-notebook-map" aria-label="Notebook sequence map">
    <span>Real market inputs</span>
    <span>Walk-forward features</span>
    <span>Signals and weights</span>
    <span>Backtest adapters</span>
    <span>Validation audit</span>
  </div>
</div>

<div class="quant-web-note">
  <strong>Research boundary</strong>
  <span>The notebooks download real market data at runtime and stop on vendor errors. They are educational examples, not live-trading claims.</span>
</div>

<div class="quant-notebook-stories">
  <section class="quant-notebook-story" id="column-overview">
    <header><span>00</span><div><h2>Column Overview</h2><p>Roadmap for traders using decomposition as a feature layer.</p></div></header>
    <div class="quant-story-grid">
      <div><small>Notebook focus</small><strong>Reading order and feature boundary</strong><p>Introduces the column, imports the data, feature, signal, and backtest helpers, then maps decomposition outputs to downstream research tasks.</p></div>
      <div><small>De-Time view</small><strong>Trend / season / residual</strong><p>The first stop is not a strategy promise. It is the contract that all later signal notebooks build on.</p></div>
      <div><small>Use next</small><strong>Start at real-data features</strong><p>Move to notebook 01 before timing, pairs, factors, or rotation so the input audit is visible.</p></div>
    </div>
  </section>

  <section class="quant-notebook-story" id="real-data-features">
    <header><span>01</span><div><h2>Real Data Features</h2><p>Market download, audit, one-asset decomposition, then walk-forward feature construction.</p></div></header>
    <div class="quant-story-grid">
      <div><small>Inputs</small><strong>US, Korea, and crypto symbols</strong><p>The data loader validates live close-price panels instead of creating artificial fallback prices.</p></div>
      <div><small>Feature factory</small><strong><code>walkforward_decompose</code></strong><p>Builds De-Time features only from the information window available at each research step.</p></div>
      <div class="quant-code-card"><small>Shape of the step</small><code>prices -> data_audit_report -> De-Time features</code></div>
    </div>
  </section>

  <section class="quant-notebook-story" id="single-asset-timing">
    <header><span>02</span><div><h2>Single Asset Timing</h2><p>Trend pullback and residual timing on SPY and QQQ research inputs.</p></div></header>
    <div class="quant-story-grid">
      <div><small>Signal recipe</small><strong>Positive trend, temporarily cheap residual</strong><p>Long timing entries use decomposition context instead of treating raw price deviation alone as the trigger.</p></div>
      <div><small>Backtest surface</small><strong>Pandas first, vectorbt after</strong><p>The notebook verifies entries, exits, fee basis points, and slippage before handing the same matrices to an optional adapter.</p></div>
      <div class="quant-code-card"><small>Feature gate</small><code>trend_slope + residual_z -> entries / exits</code></div>
    </div>
  </section>

  <section class="quant-notebook-story" id="turtle-trend-filter">
    <header><span>03</span><div><h2>Turtle Trend Filter</h2><p>Donchian breakout logic with a decomposition trend gate.</p></div></header>
    <div class="quant-story-grid">
      <div><small>Classical rule</small><strong>Breakout above prior highs</strong><p>The tutorial uses the familiar Turtle or Donchian setting so the added De-Time role stays inspectable.</p></div>
      <div><small>De-Time role</small><strong>Trend filter before entry</strong><p>Breakout entries are conditioned on the decomposition trend signal instead of routed blindly.</p></div>
      <div><small>Universe</small><strong>ETF examples</strong><p>SPY, QQQ, IWM, and DIA form the tutorial research panel.</p></div>
    </div>
  </section>

  <section class="quant-notebook-story" id="pairs-residual-cycle">
    <header><span>04</span><div><h2>Pairs Residual Cycle</h2><p>Spread residual and cycle checks for a pairs research path.</p></div></header>
    <div class="quant-story-grid">
      <div><small>Inputs</small><strong>KO and PEP spread example</strong><p>Pair weights are built from the spread research setup with explicit fee and slippage handling.</p></div>
      <div><small>Component cue</small><strong>Residual is not the whole spread</strong><p>The page calls out drift in spread trend before residual mean reversion is trusted.</p></div>
      <div class="quant-code-card"><small>Notebook path</small><code>spread -> residual cycle -> pair weights</code></div>
    </div>
  </section>

  <section class="quant-notebook-story" id="factor-selection">
    <header><span>05</span><div><h2>Factor Selection</h2><p>Cross-sectional De-Time alpha candidates for US stock research.</p></div></header>
    <div class="quant-story-grid">
      <div><small>Score ingredients</small><strong>Trend, pullback, cycle, noise penalty</strong><p>The notebook turns feature columns into a ranking surface, not into a hidden end-to-end strategy.</p></div>
      <div><small>Portfolio view</small><strong>Top-N weights</strong><p>Rotation weights make the ranking concrete while leaving data and execution assumptions reviewable.</p></div>
      <div><small>Audit need</small><strong>Cross-section timing</strong><p>Every feature row remains tied to the walk-forward recomputation schedule.</p></div>
    </div>
  </section>

  <section class="quant-notebook-story" id="etf-rotation">
    <header><span>06</span><div><h2>ETF Rotation</h2><p>Style and sector target weights with an optional <code>bt</code> adapter.</p></div></header>
    <div class="quant-story-grid">
      <div><small>Research shape</small><strong>Target-weight portfolio problem</strong><p>Style and sector ETFs show how decomposition scores can feed a rotation weight table.</p></div>
      <div><small>Adapter</small><strong><code>bt</code> after transparent weights</strong><p>The tutorial computes De-Time rotation weights before routing them into optional portfolio tooling.</p></div>
      <div class="quant-code-card"><small>Controls</small><code>top_n + vol_target + max_weight</code></div>
    </div>
  </section>

  <section class="quant-notebook-story" id="multi-market-regimes">
    <header><span>07</span><div><h2>Multi-Market Regimes</h2><p>Korea, US, and crypto decomposition examples in one research view.</p></div></header>
    <div class="quant-story-grid">
      <div><small>Coverage</small><strong>Korean equities, US ETFs, crypto pairs</strong><p>The notebook shows cross-market feature use without hiding symbol conventions or runtime data requests.</p></div>
      <div><small>Calendar boundary</small><strong>Equity hours differ from crypto</strong><p>24/7 crypto and exchange calendars must be treated separately in production research.</p></div>
      <div><small>Component cue</small><strong>Cycle and residual stress</strong><p>Regime ideas are framed as feature experiments rather than universal timing rules.</p></div>
    </div>
  </section>

  <section class="quant-notebook-story" id="framework-adapters">
    <header><span>08</span><div><h2>Framework Adapters</h2><p>Route visible De-Time signals into established research tooling.</p></div></header>
    <div class="quant-story-grid">
      <div><small>Baseline</small><strong>Transparent pandas backtester</strong><p>Alignment, costs, turnover, and equity construction are inspectable before optional frameworks enter.</p></div>
      <div><small>Adapters</small><strong>vectorbt, <code>bt</code>, reporting, templates</strong><p>Framework integration stays downstream of feature generation and signal review.</p></div>
      <div class="quant-code-card"><small>Surface</small><code>signals -> adapter -> report</code></div>
    </div>
  </section>

  <section class="quant-notebook-story" id="validation-audit">
    <header><span>09</span><div><h2>Validation Audit</h2><p>The final notebook keeps leakage and reporting failures visible.</p></div></header>
    <div class="quant-story-grid">
      <div><small>Checks</small><strong>Walk-forward, shift, costs</strong><p>It calls out full-sample decomposition, same-bar fills, and omitted costs as failure modes.</p></div>
      <div><small>Data checks</small><strong>Missing vendor runs stay visible</strong><p>Failed downloads and hidden data problems should not disappear from the research story.</p></div>
      <div><small>Exit point</small><strong>Return to validation guide</strong><p>The walk-forward page turns these audit ideas into the column protocol.</p></div>
    </div>
  </section>
</div>

## Continue

<div class="info-grid quant-continue-grid">
  <a class="info-card" href="../data/"><h3>Real Data</h3><p>Review universes and data replacement rules.</p></a>
  <a class="info-card" href="../strategy-map/"><h3>Strategy Map</h3><p>Compare trend, pair, factor, and risk use cases.</p></a>
  <a class="info-card" href="../backtesting-frameworks/"><h3>Backtesting Frameworks</h3><p>See how visible signals reach optional adapters.</p></a>
  <a class="info-card" href="../walkforward/"><h3>Validation</h3><p>Keep leakage, shift, and cost checks explicit.</p></a>
</div>
