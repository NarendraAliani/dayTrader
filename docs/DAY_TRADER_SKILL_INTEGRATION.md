# Day Trader Skill + Iceberg Integration Plan

Reference project: https://github.com/Jakeschincariol/day-trader-skill

## Integration decision
Use the reference repository's 11 workflow capabilities as design inputs, and combine them with the separate NIFTY Futures Iceberg Detection module. Do not blindly transplant US-market assumptions, data providers, symbols, or broker execution. Adapt the workflows for India, Dhan API, NSE instruments, and the local PostgreSQL-backed application.

## The 11 workflow capabilities
1. Scanner — find candidate setups; adapt universe and setups to NSE instruments.
2. News monitor — track relevant market/company news with source and timestamp.
3. Entry timer — confirm setup state on completed bars/events; prevent premature triggers.
4. Exit planner — define stop, target, expiry/session exit and rationale before entry.
5. Time Machine — historical replay and Monte Carlo-style scenario simulation; clearly label assumptions and uncertainty.
6. Risk manager — block signals/orders that violate configured limits.
7. Budget manager — calculate quantity from account equity, max risk, lot size and stop distance.
8. Broker workflow — initially paper-only; future live execution must require explicit separate enablement and approval.
9. Alerts — price, signal, stop/target, data-quality and session alerts.
10. Analyst — summarize earnings/fundamental releases when relevant to the instrument.
11. Public-disclosure tracker — optional India-specific module only after identifying a reliable, lawful, authoritative public source; do not assume US Congress/Pelosi data maps to India.

## Iceberg module
Keep Iceberg Detection as an additional strategy/plugin, not a replacement for the eleven capabilities. Initial target is NIFTY Futures. It will use timestamped Dhan WebSocket trade updates and available 20-level depth snapshots to estimate replenishment/absorption patterns. Hidden reserve quantity cannot be directly confirmed from ordinary displayed depth; output must be a scored hypothesis with evidence, data-quality flags and confidence, not a fact.

## Integration pipeline
Market data -> normalization and quality checks -> scanner/candidate setup -> news/context -> entry confirmation -> exit plan -> Time Machine/backtest evidence -> budget sizing -> risk veto/pass -> signal coordinator -> dashboard/alerts -> paper-trade ledger.

Iceberg evidence enters the same candidate-signal and risk pipeline. The coordinator must preserve each strategy's independent signal, version, timestamp, score, explanation and later performance.

## India/Dhan adaptation requirements
- Validate actual Dhan API subscription, authentication, rate limits, instrument master, WebSocket payloads, supported depth levels, reconnect behavior and historical data availability against official docs and the user's account.
- Replace US-specific market data, Nasdaq universe, Alpaca broker assumptions, SEC/House Clerk sources, US session times and US ticker conventions.
- Use NSE instrument IDs and expiry/lot metadata from a versioned instrument master; do not hard-code changing contract identifiers.
- Options analytics and any option strategy are enabled only when the required source fields are available and validated.

## Verification gates before live use
- Unit tests for each strategy and all risk/budget calculations.
- Replay tests using captured or validated historical data, including reconnects and missing/stale/out-of-order events.
- Backtests include brokerage, taxes/fees where modeled, slippage, realistic fills, expiry/session rules and no look-ahead leakage.
- Database migration, transaction, uniqueness/deduplication, restart recovery, backup and restore tests.
- Integration tests in the target Windows environment; paper trading and operational monitoring before any live-order feature is separately considered.

## Status
This is an integration design and initial Iceberg scoring scaffold, not a completed live implementation. The reference capabilities still need to be implemented, adapted, tested and exposed through the dashboard.