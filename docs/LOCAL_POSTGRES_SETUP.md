# Local PostgreSQL setup (Windows)

This guide creates the local database for DayTrader. It does not enable live trading; keep `ENABLE_LIVE_ORDERS=false`.

## 1. Install PostgreSQL

Install a supported PostgreSQL release for Windows from the official PostgreSQL download page:
https://www.postgresql.org/download/windows/

During setup, remember the password you choose for the PostgreSQL administrator (`postgres`). Ensure the PostgreSQL service is running. Open a new PowerShell window and confirm `psql --version` works. If PowerShell cannot find `psql`, add PostgreSQL's `bin` folder to PATH or run it using its full path (usually under `C:\Program Files\PostgreSQL\<version>\bin\psql.exe`).

## 2. Create the app role and database

In PowerShell, connect as the PostgreSQL administrator (replace the version/path if needed):

```powershell
psql -U postgres -h localhost -d postgres
```

At the `postgres=#` prompt, run these commands. Choose a strong local password and replace `REPLACE_WITH_A_STRONG_PASSWORD` before running:

```sql
CREATE ROLE daytrader LOGIN PASSWORD 'REPLACE_WITH_A_STRONG_PASSWORD';
CREATE DATABASE daytrader OWNER daytrader;
\q
```

If the role or database already exists, do not blindly repeat the CREATE commands; inspect the existing setup first.

## 3. Configure the application

From the repository root in PowerShell:

```powershell
Copy-Item .env.example .env
notepad .env
```

Set `DATABASE_URL` to use the password chosen above, URL-encoding special characters in the password if needed. Example format:

```dotenv
DATABASE_URL=postgresql://daytrader:YOUR_PASSWORD@localhost:5432/daytrader
ENABLE_LIVE_ORDERS=false
```

Keep `.env` private and never commit it. Do not put Dhan tokens or database passwords in GitHub or chat.

## 4. Install Python dependencies and create tables

Activate your existing virtual environment if you have one, then run from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
psql -U daytrader -h localhost -d daytrader -f migrations/001_initial_schema.sql
```

When prompted, enter the app role password. The schema script uses a transaction and records migration version `001_initial_schema`.

Verify that the table exists:

```powershell
psql -U daytrader -h localhost -d daytrader -c "SELECT version FROM schema_migrations;"
psql -U daytrader -h localhost -d daytrader -c "SELECT COUNT(*) AS instruments_before FROM instruments;"
```

Expected before the import: `instruments_before = 0` for a brand-new database.

## 5. Preview the Dhan import before writing

Make sure the downloaded Dhan instrument-master CSV is the current official file. The import command downloads the current master itself; it does not read a local CSV path.

```powershell
python -m scripts.import_dhan_instruments
```

This is preview-only and must not change the database. Review the parsed total and segment counts. To actually upsert instruments, explicitly run:

```powershell
python -m scripts.import_dhan_instruments --apply
```

Do not use `--apply` until the preview looks reasonable and the database migration has succeeded.

## 6. Verify import results

```powershell
psql -U daytrader -h localhost -d daytrader -c "SELECT COUNT(*) AS instruments_total FROM instruments;"
psql -U daytrader -h localhost -d daytrader -c "SELECT exchange_segment, COUNT(*) FROM instruments WHERE provider='DHAN' GROUP BY exchange_segment ORDER BY exchange_segment;"
```

The importer reports rows attempted/upserted. The SQL queries above confirm what is actually present in PostgreSQL. Re-running the import updates matching `(provider, security_id, exchange_segment)` keys instead of adding duplicate rows.

## Troubleshooting

- `psql is not recognized`: use the full path to `psql.exe` or add PostgreSQL's `bin` folder to PATH, then reopen PowerShell.
- `connection refused`: confirm the PostgreSQL Windows service is running and listening on port 5432.
- `password authentication failed`: verify the role password and `.env` URL.
- `relation instruments does not exist`: rerun the schema command and inspect any SQL error.
- `python -m scripts.import_dhan_instruments` fails to connect: confirm `.env` exists at the repo root and its `DATABASE_URL` matches the local role/database.
