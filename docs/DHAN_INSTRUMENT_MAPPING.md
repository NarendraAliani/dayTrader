# Dhan instrument master mapping

## Official source

DhanHQ documents two CSV security-master files:

- Compact: https://images.dhan.co/api-data/api-scrip-master.csv
- Detailed: https://images.dhan.co/api-data/api-scrip-master-detailed.csv

The parser in `app/data/dhan_instruments.py` accepts compact and detailed column aliases. It normalizes rows to `InstrumentIdentity` and skips unsupported segments. A malformed row in a supported segment raises a line-numbered error; duplicate provider/security-ID/segment identities in one CSV are ignored.

## Segment mapping currently supported

| Dhan exchange + segment code | Internal exchange segment |
| --- | --- |
| NSE + E | NSE_EQ |
| NSE + D | NSE_FNO |
| BSE + E | BSE_EQ |
| BSE + D | BSE_FNO |
| MCX + M | MCX_COMM |
| IDX/NSE + I | IDX_I |

The last mapping is a defensive alias for index-feed records; verify actual row values against the downloaded master before relying on it.

## Field aliases

- Security ID: `SECURITY_ID` or `SEM_SMST_SECURITY_ID`
- Exchange/segment: `EXCH_ID` + `SEGMENT`, or `SEM_EXM_EXCH_ID` + `SEM_SEGMENT`
- Instrument type: `INSTRUMENT` or `SEM_INSTRUMENT_NAME`
- Symbol: `SEM_TRADING_SYMBOL`, `TRADING_SYMBOL`, `DISPLAY_NAME`, `SEM_CUSTOM_SYMBOL`, or symbol-name aliases
- Expiry, strike, option type, lot size, tick size: detailed/compact aliases in the parser

## PostgreSQL persistence

`app/data/instrument_repository.py` provides `upsert_instruments(connection, instruments)`. It uses the migration's unique key `(provider, security_id, exchange_segment)`, refreshes the current contract fields, and commits a batch once. On failure it rolls the batch back and re-raises the error. Apply `migrations/001_initial_schema.sql` before calling it. The function accepts an already-open psycopg-compatible connection; connection lifecycle and downloading/scheduling the CSV remain separate tasks.

Do not hardcode derivative security IDs or lot sizes. Refresh the master regularly and resolve contracts using the current master. A live Dhan CSV download and real PostgreSQL integration test have not yet been completed.

## Local verification

After pulling the branch and installing `requirements.txt`, run:

```powershell
python -m pytest -q
```

The GitHub Actions workflow runs the same test command on pushes and pull requests. A successful commit alone is not evidence that the tests passed; check the workflow result.
