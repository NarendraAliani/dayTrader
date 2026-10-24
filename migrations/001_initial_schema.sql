-- PostgreSQL initial schema. Apply once to a new database using psql.
-- Keep raw market events append-only; deduplicate using provider_event_key where available.

BEGIN;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(100) PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS instruments (
    id BIGSERIAL PRIMARY KEY,
    provider VARCHAR(30) NOT NULL DEFAULT 'DHAN',
    security_id VARCHAR(80) NOT NULL,
    exchange_segment VARCHAR(30) NOT NULL,
    trading_symbol VARCHAR(100) NOT NULL,
    instrument_type VARCHAR(30) NOT NULL,
    underlying_symbol VARCHAR(100),
    expiry_date DATE,
    strike_price NUMERIC(14,4),
    option_type VARCHAR(5),
    lot_size INTEGER,
    tick_size NUMERIC(12,6),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(provider, security_id, exchange_segment)
);
CREATE INDEX IF NOT EXISTS ix_instruments_symbol ON instruments(trading_symbol);
CREATE INDEX IF NOT EXISTS ix_instruments_underlying_expiry ON instruments(underlying_symbol, expiry_date);

CREATE TABLE IF NOT EXISTS candles (
    id BIGSERIAL PRIMARY KEY,
    instrument_id BIGINT NOT NULL REFERENCES instruments(id),
    timeframe VARCHAR(10) NOT NULL,
    candle_time TIMESTAMPTZ NOT NULL,
    open NUMERIC(18,6) NOT NULL,
    high NUMERIC(18,6) NOT NULL,
    low NUMERIC(18,6) NOT NULL,
    close NUMERIC(18,6) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0 CHECK (volume >= 0),
    open_interest BIGINT,
    source VARCHAR(30) NOT NULL DEFAULT 'DHAN',
    is_final BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(instrument_id, timeframe, candle_time),
    CHECK (high >= low),
    CHECK (high >= open AND high >= close),
    CHECK (low <= open AND low <= close)
);
CREATE INDEX IF NOT EXISTS ix_candles_instrument_time ON candles(instrument_id, timeframe, candle_time DESC);

CREATE TABLE IF NOT EXISTS market_events (
    id BIGSERIAL PRIMARY KEY,
    provider VARCHAR(30) NOT NULL,
    provider_event_key VARCHAR(200),
    instrument_id BIGINT REFERENCES instruments(id),
    event_time TIMESTAMPTZ NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    event_type VARCHAR(40) NOT NULL,
    payload JSONB NOT NULL,
    quality_flags JSONB NOT NULL DEFAULT '[]'::jsonb,
    UNIQUE(provider, provider_event_key)
);
CREATE INDEX IF NOT EXISTS ix_market_events_instrument_time ON market_events(instrument_id, event_time DESC);
CREATE INDEX IF NOT EXISTS ix_market_events_type_time ON market_events(event_type, event_time DESC);

CREATE TABLE IF NOT EXISTS strategy_definitions (
    strategy_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(160) NOT NULL,
    version VARCHAR(40) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS signals (
    id BIGSERIAL PRIMARY KEY,
    strategy_id VARCHAR(100) NOT NULL REFERENCES strategy_definitions(strategy_id),
    instrument_id BIGINT NOT NULL REFERENCES instruments(id),
    timeframe VARCHAR(10) NOT NULL,
    signal_time TIMESTAMPTZ NOT NULL,
    action VARCHAR(20) NOT NULL CHECK (action IN ('BUY','SELL','NO_TRADE','EXIT')),
    score NUMERIC(8,4) NOT NULL CHECK (score >= 0 AND score <= 100),
    reason TEXT NOT NULL,
    evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
    strategy_version VARCHAR(40) NOT NULL,
    data_quality JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(strategy_id, strategy_version, instrument_id, timeframe, signal_time)
);
CREATE INDEX IF NOT EXISTS ix_signals_instrument_time ON signals(instrument_id, signal_time DESC);
CREATE INDEX IF NOT EXISTS ix_signals_strategy_time ON signals(strategy_id, signal_time DESC);

CREATE TABLE IF NOT EXISTS backtest_runs (
    id BIGSERIAL PRIMARY KEY,
    strategy_id VARCHAR(100) NOT NULL REFERENCES strategy_definitions(strategy_id),
    strategy_version VARCHAR(40) NOT NULL,
    instrument_id BIGINT REFERENCES instruments(id),
    timeframe VARCHAR(10) NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    config JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(20) NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','running','completed','failed')),
    metrics JSONB NOT NULL DEFAULT '{}'::jsonb,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (end_time > start_time)
);
CREATE INDEX IF NOT EXISTS ix_backtest_runs_strategy_created ON backtest_runs(strategy_id, created_at DESC);

CREATE TABLE IF NOT EXISTS backtest_trades (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES backtest_runs(id) ON DELETE CASCADE,
    instrument_id BIGINT NOT NULL REFERENCES instruments(id),
    side VARCHAR(5) NOT NULL CHECK (side IN ('LONG','SHORT')),
    entry_time TIMESTAMPTZ NOT NULL,
    entry_price NUMERIC(18,6) NOT NULL,
    exit_time TIMESTAMPTZ,
    exit_price NUMERIC(18,6),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    gross_pnl NUMERIC(18,4),
    costs NUMERIC(18,4) NOT NULL DEFAULT 0,
    net_pnl NUMERIC(18,4),
    exit_reason VARCHAR(100),
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    CHECK (exit_time IS NULL OR exit_time >= entry_time)
);
CREATE INDEX IF NOT EXISTS ix_backtest_trades_run_entry ON backtest_trades(run_id, entry_time);

CREATE TABLE IF NOT EXISTS paper_trades (
    id BIGSERIAL PRIMARY KEY,
    signal_id BIGINT REFERENCES signals(id),
    instrument_id BIGINT NOT NULL REFERENCES instruments(id),
    strategy_id VARCHAR(100) NOT NULL REFERENCES strategy_definitions(strategy_id),
    side VARCHAR(5) NOT NULL CHECK (side IN ('LONG','SHORT')),
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN','CLOSED','CANCELLED')),
    entry_time TIMESTAMPTZ NOT NULL,
    entry_price NUMERIC(18,6) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    stop_price NUMERIC(18,6),
    target_price NUMERIC(18,6),
    exit_time TIMESTAMPTZ,
    exit_price NUMERIC(18,6),
    gross_pnl NUMERIC(18,4),
    costs NUMERIC(18,4) NOT NULL DEFAULT 0,
    net_pnl NUMERIC(18,4),
    notes JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (exit_time IS NULL OR exit_time >= entry_time)
);
CREATE INDEX IF NOT EXISTS ix_paper_trades_status_time ON paper_trades(status, entry_time DESC);
CREATE INDEX IF NOT EXISTS ix_paper_trades_strategy_time ON paper_trades(strategy_id, entry_time DESC);

CREATE TABLE IF NOT EXISTS strategy_metrics (
    id BIGSERIAL PRIMARY KEY,
    strategy_id VARCHAR(100) NOT NULL REFERENCES strategy_definitions(strategy_id),
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    sample_size INTEGER NOT NULL DEFAULT 0 CHECK (sample_size >= 0),
    win_rate NUMERIC(8,4),
    net_pnl NUMERIC(18,4),
    max_drawdown NUMERIC(12,4),
    profit_factor NUMERIC(12,4),
    risk_reward NUMERIC(12,4),
    metrics JSONB NOT NULL DEFAULT '{}'::jsonb,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (period_end > period_start)
);
CREATE INDEX IF NOT EXISTS ix_strategy_metrics_recent ON strategy_metrics(strategy_id, calculated_at DESC);

CREATE TABLE IF NOT EXISTS data_gap_logs (
    id BIGSERIAL PRIMARY KEY,
    provider VARCHAR(30) NOT NULL,
    instrument_id BIGINT REFERENCES instruments(id),
    detected_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    gap_start TIMESTAMPTZ,
    gap_end TIMESTAMPTZ,
    severity VARCHAR(20) NOT NULL DEFAULT 'warning',
    description TEXT NOT NULL,
    recovered_at TIMESTAMPTZ,
    details JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS ix_data_gap_logs_detected ON data_gap_logs(detected_at DESC);

INSERT INTO schema_migrations(version) VALUES ('001_initial_schema')
ON CONFLICT (version) DO NOTHING;

COMMIT;
