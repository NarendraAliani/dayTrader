"""Download Dhan's current instrument master and optionally upsert it.

Preview only by default. Pass --apply to persist records to PostgreSQL.
"""
from __future__ import annotations

import argparse
import sys

import psycopg

from app.core.config import settings
from app.data.dhan_master_client import download_instrument_master
from app.data.instrument_repository import upsert_instruments


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compact", action="store_true", help="Use compact CSV.")
    parser.add_argument(
        "--apply", action="store_true",
        help="Write to PostgreSQL. Without this flag, only preview.",
    )
    args = parser.parse_args(argv)

    instruments = download_instrument_master(detailed=not args.compact)
    counts: dict[str, int] = {}
    for item in instruments:
        counts[item.exchange_segment] = counts.get(item.exchange_segment, 0) + 1

    print(f"Parsed {len(instruments):,} supported instrument rows.")
    for segment, count in sorted(counts.items()):
        print(f"  {segment}: {count:,}")

    if not args.apply:
        print("Preview only: database unchanged. Use --apply to import.")
        return 0
    if not instruments:
        print("No supported instruments parsed; refusing empty import.", file=sys.stderr)
        return 2

    try:
        with psycopg.connect(settings.database_url) as connection:
            attempted = upsert_instruments(connection, instruments)
    except Exception as exc:
        print(f"Database import failed ({type(exc).__name__}): {exc}", file=sys.stderr)
        return 1
    print(f"Successfully upserted {attempted:,} instruments.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
