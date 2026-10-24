# Hybrid Market Intelligence & Signal Engine Architecture

## Decision
Use a hybrid architecture: deterministic Python components for market calculations and controls, optional AI agents for unstructured analysis, and a central coordinator for signal assembly.

## Components
- Market Data: Dhan API adapter (credentials configured locally via environment variables); historical data interface.
- Indicator Engine: deterministic RSI, MACD, ADX, VWAP, EMA and Supertrend calculations.
- Strategy Engine: rule-based strategy evaluation; emits structured candidate signals.
- Options Analytics: OI, IV, PCR and Greeks only when valid source data is available.
- News Analyst (optional AI): summarizes sourced news and labels uncertainty; never invents prices or overrides risk controls.
- Signal Coordinator: validates timestamps/data quality, combines evidence, rejects stale/conflicting inputs, emits BUY/SELL/EXIT/NO TRADE with rationale.
- Risk Engine: position sizing, stop-loss and exposure checks; may veto any signal.
- Backtesting: historical simulation with fees/slippage and anti-look-ahead safeguards.
- Paper Trading: tracks hypothetical fills and outcomes.
- Dashboard/Notifications: signal history and alerts.
- Execution Gateway: disabled by default; live orders require separate explicit configuration and safeguards.

## Local development
- Windows 10/11
- Python virtual environment (venv)
- PostgreSQL
- FastAPI backend
- HTML/CSS/JavaScript with Bootstrap 5 frontend
- No Docker requirement

## Safety and reliability
- Do not commit API keys, broker tokens, passwords, or .env files.
- All AI-derived claims must be labeled and linked to their source when applicable.
- AI output is advisory; deterministic validation and risk controls are authoritative.
- No claim of profitability without reproducible out-of-sample testing.
- Start with paper trading; live execution is out of scope until explicitly approved.

## Implementation order
1. Local project skeleton and configuration
2. Database migrations and health endpoint
3. Market-data adapter and instrument handling
4. Indicator and strategy modules
5. Signal schema, coordinator and risk checks
6. Backtesting and paper-trading records
7. Dashboard and notifications
8. Optional AI analysis adapter
9. Integration tests and local run documentation
