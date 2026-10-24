# Hybrid Market Intelligence & Signal Engine Architecture

## Confirmed initial scope
- Primary market-data provider: Dhan API.
- Initial live strategy target: NIFTY futures.
- Iceberg Detection Engine: monitor live trade updates and 20-level market-depth snapshots with timestamps; persist raw observations continuously for analysis and replay.
- No automatic order placement. Signals and paper-trading only until separately reviewed and explicitly approved.
- Later extensions: Equity, Stock Futures, other Index Futures and Options, each with instrument-specific validation.

## Core architecture
Use deterministic Python components for market calculations and risk controls, optional AI agents for unstructured analysis, and a central coordinator for signal assembly.

## Components
- Market Data: Dhan API adapter for live WebSocket trade/depth updates and supported historical data. Check actual subscription entitlements, message fields, limits, and historical availability before relying on them.
- Data Capture: append-only, timestamped market events; source timestamp and local receive timestamp; sequence/ordering checks where available; reconnect and gap markers.
- Instrument Master: versioned instrument identifiers and expiry metadata; never assume symbols or expiries stay constant.
- Storage: normalized relational tables for instruments, sessions, events, signals, strategy versions, backtests, trades and performance; indexed timestamps/instrument IDs; migrations and backup/restore tests.
- Indicator Engine: deterministic RSI, MACD, ADX, VWAP, EMA and Supertrend calculations.
- Strategy Engine: plugin interface; each strategy returns structured candidate signals and evidence.
- Iceberg Detection Engine: estimate possible replenishment/absorption from repeated displayed quantity at a price, executed trades, subsequent depth changes, traded volume and price response. This detects patterns consistent with iceberg activity; hidden reserve quantity cannot be directly confirmed from ordinary displayed depth.
- Options Analytics: OI, IV, PCR and Greeks only when valid source data is available.
- Signal Coordinator: validates data freshness/quality, combines evidence, rejects stale/conflicting inputs, emits BUY/SELL/EXIT/NO TRADE with rationale.
- Risk Engine: position sizing, stop-loss and exposure checks; may veto any signal.
- Backtesting: historical simulation with fees/slippage and anti-look-ahead safeguards. For order-book strategies, OHLCV-only backtests are insufficient; use captured event/depth data where available and report data gaps.
- Paper Trading: tracks hypothetical fills and outcomes.
- Dashboard/Notifications: live status, order-book evidence, signal history, entry/stop/target, strategy performance and alerts.
- Execution Gateway: disabled by default; no live orders in the initial scope.

## Database and production-readiness requirements
- Use PostgreSQL for the intended application database; SQLite is for local smoke tests only.
- Version-controlled migrations; unique constraints and indexes for instrument/time/event identity; idempotent ingestion.
- Transactions for related writes, bounded queues/backpressure, retry with deduplication, explicit data-gap monitoring.
- Automated unit/integration tests, schema migration tests, reconnect tests, and backup/restore verification.
- Do not describe the system as live-ready until tests run in the target Windows environment and data capture has been validated against the Dhan account.

## Local development
- Windows 10/11
- Python virtual environment (venv)
- FastAPI backend
- HTML/CSS/JavaScript with Bootstrap 5 frontend
- No Docker requirement

## Safety and reliability
- Never commit API keys, broker tokens, passwords, or .env files.
- AI-derived claims must be labeled and linked to sources when applicable.
- AI output is advisory; deterministic validation and risk controls are authoritative.
- No profitability claims without reproducible out-of-sample testing.
- Begin with signal generation and paper trading; live execution is out of scope until explicitly approved.

## Implementation order
1. Local project skeleton and configuration
2. Database migrations, schema, health checks
3. Dhan adapter and instrument handling
4. Timestamped live data capture and replay
5. Indicator and plugin strategy modules
6. Iceberg detection scoring and signal/risk schema
7. Backtesting and paper-trading records
8. Modern Bootstrap dashboard and notifications
9. Optional AI analysis adapter
10. Integration tests, migration/restore checks and Windows run documentation
