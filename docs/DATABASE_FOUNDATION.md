# Database foundation (PostgreSQL)

The first migration is `migrations/001_initial_schema.sql`. It defines normalized tables for the instrument master, deduplicated candles and market events, strategy definitions and signals, backtest runs/trades, paper trades, strategy metrics, and data-gap monitoring.

## Apply on Windows

1. Install PostgreSQL and create a database and role for this application.
2. Open PowerShell or SQL Shell (`psql`) with the database credentials.
3. From the repository root, run:

```powershell
psql "postgresql://daytrader:YOUR_PASSWORD@localhost:5432/daytrader" -v ON_ERROR_STOP=1 -f migrations/001_initial_schema.sql
```

Replace the placeholder password locally; do not put real credentials in Git or chat. The SQL migration is transactional and records its version in `schema_migrations`. It is intended for a new/empty application database; review before applying to any database that already contains application tables.

## Important limits

This migration is a storage foundation only. It does not yet create the runtime repository/data-access layer, ingest Dhan events, or prove that the schema works against the user's PostgreSQL installation. The unique keys are designed to support idempotent upserts, but ingestion code must actually use them. Keep live order execution disabled.
