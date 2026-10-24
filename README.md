# Market Intelligence & Signal Engine

India-focused market analysis and trading signal platform for NSE/BSE, designed around Dhan market data, indicator-based strategies, risk controls, backtesting, paper trading, dashboard reporting, and notifications.

## Project status

Initial project setup. No live order execution is enabled.

## Development principles

- Validate data quality before generating signals.
- Every signal must include its rationale, timestamp, strategy, entry/exit plan, and risk estimate.
- Backtests must account for transaction costs and avoid look-ahead bias.
- Paper trading and explicit risk checks precede any live execution.
- Never commit API keys, tokens, or other secrets.

## Planned modules

1. Market data and instrument master
2. Indicator engine
3. Strategy and signal generation
4. Signal scoring and explanation
5. Risk management and position sizing
6. Historical backtesting and reporting
7. Paper trading and signal tracking
8. Dashboard and notifications
9. Broker execution gateway (disabled by default)

## Status

Architecture and implementation plan are being established. Trading profitability is not assumed; strategies require independent validation.
