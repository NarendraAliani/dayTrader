# Dashboard Design Specification — v1

## Design rule
Treat the supplied dashboard video as the primary reference, not a rigid copy. Preserve its useful interaction patterns; add or omit fields based on Dhan data availability, the combined Day Trader Skill capabilities, and the Iceberg research module. Where requirements are ambiguous, ask Narendra a short Yes/No question.

## Primary navigation
1. Overview
2. Market Scanner
3. Multi-Timeframe RSI
4. Strategies
5. Options & OI Flow
6. Liquidity / Iceberg
7. Signals
8. Backtesting
9. Paper Trading
10. Risk & Journal
11. Alerts
12. Settings / Data Health

## Overview screen
- Market session and Dhan connection status; last update timestamp and stale-feed warning.
- Watchlist/segment selector: NSE equity, stock futures, index futures, options.
- KPI cards: active signals, high-score setups, paper positions, daily realised/unrealised P&L (paper only), risk-limit status.
- Market breadth and trend context.
- Recent signals table with symbol, segment, timeframe, strategy, direction, score, entry zone, stop, targets, risk/reward, timestamp, and invalidation reason.
- Strategy health and latest backtest summary.

## Reference-inspired scanner
- Multi-timeframe RSI heatmap (e.g. 5m, 15m, 1h, daily) with overbought/oversold thresholds configurable.
- Sortable/filterable screener with timeframe agreement and signal explanation.
- Tabs for Options, Radar, Liquidity, OI Flow, Strength, and Journal, implemented only when the underlying data is available and validated.
- Every table supports search, sorting, pagination, and CSV export.

## Strategy workspace
- Plugin-based strategy catalogue: enable/disable, configuration, supported segment/timeframes, data requirements, version, and test status.
- Initial strategy families: EMA/trend, Supertrend, RSI, MACD, ADX, VWAP/volume breakout, Donchian/range breakout, options OI/PCR/IV/Greeks (only where Dhan supplies reliable data), and Iceberg/absorption research.
- The discussed Day Trader Skill's 11 capabilities are to be mapped individually to concrete features before marking them implemented; a capability is not considered complete merely because a dashboard tab exists.
- Strategy comparison: trade count, win rate, net P&L after costs, profit factor, max drawdown, expectancy, average R, and out-of-sample results.
- Adaptive weights must use minimum sample thresholds and out-of-sample validation; expose why weights changed.

## Iceberg / liquidity screen
- Label observations as *possible absorption / replenishment*, never confirmed hidden orders.
- Display trade prints and available market-depth snapshots with exchange/broker timestamps, spread, traded volume, depth changes, and confidence/evidence.
- Track data gaps, reconnects, and snapshot freshness. Backtest with the same fields actually available historically; do not imply historical depth exists if it was not recorded.

## Signal detail panel
- BUY / SELL / EXIT / NO TRADE; strategy and timeframe; indicator values; evidence; score breakdown; entry/stop/targets; position-size suggestion; risk/reward; invalidation; data timestamp; and a link to the backtest results.
- A deterministic risk gate can reject a signal regardless of AI output. AI is advisory for news/context, not an authority to bypass risk controls.

## Backtesting and paper trading
- Configure symbol universe, date range, timeframe, strategy/version, capital, risk rules, brokerage/taxes, slippage, and execution assumptions.
- Report equity curve, drawdown, trades, win rate, profit factor, expectancy, average R, exposure, and segment-wise breakdown.
- Prevent look-ahead bias and duplicate candles/signals; keep strategy versions and test configurations reproducible.
- Paper trading only until data integrity and strategy validation pass. Live order execution remains disabled by default.

## Reliability and data health
- PostgreSQL migrations with versioning; foreign keys, unique constraints, indexes, transaction boundaries, and UTC timestamps plus exchange-local display.
- Idempotent candle/depth ingestion, duplicate protection, reconnect/backoff, rate-limit handling, and observable error logs.
- Backups and restore test documented; health screen shows Dhan API/WebSocket status, last message time, queue lag, and failed ingestion count.
- Secrets stay in local .env; never commit tokens.

## Visual style
- Modern dark trading workspace with restrained green/red signal colors, accessible contrast, clear density, compact data tables, responsive layout, and keyboard-friendly controls.
- Desktop-first for live monitoring; responsive layout for read-only mobile checks.
- All displayed prices/indicators must be labelled as live, delayed, historical, or simulated.

## Implementation order
1. Verify repository structure and requirements.
2. Build dashboard shell and navigation with clearly marked sample/demo data.
3. Connect API endpoints and database-backed data.
4. Implement scanner and strategy catalogue.
5. Integrate Dhan feed and data-quality indicators.
6. Add backtesting, performance reports, paper trading, and Iceberg research.
7. Run migrations, unit/integration tests, failure/reconnect tests, and backup/restore verification.
8. Provide a final report listing changed files, commits, test outcomes, known limitations, and Windows run instructions.

## Acceptance rule
Do not describe a module as complete until its implementation, tests, and data assumptions have been verified. The dashboard reference is a design guide; correct market data, transparent evidence, and risk controls take priority over visual similarity.
