"""Download the official Dhan instrument master with bounded HTTP behavior."""
from __future__ import annotations

import httpx

from app.data.dhan_instruments import parse_instrument_master

COMPACT_MASTER_URL = "https://images.dhan.co/api-data/api-scrip-master.csv"
DETAILED_MASTER_URL = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
DEFAULT_TIMEOUT_SECONDS = 30.0
MAX_MASTER_BYTES = 40 * 1024 * 1024


def download_instrument_master(
    *,
    detailed: bool = True,
    client: httpx.Client | None = None,
) -> list:
    """Download and parse Dhan's published CSV; caller owns injected clients."""
    url = DETAILED_MASTER_URL if detailed else COMPACT_MASTER_URL
    owns_client = client is None
    http_client = client or httpx.Client(
        timeout=httpx.Timeout(DEFAULT_TIMEOUT_SECONDS),
        follow_redirects=True,
        headers={"User-Agent": "DayTrader-Market-Intelligence/0.1"},
    )
    try:
        with http_client.stream("GET", url) as response:
            response.raise_for_status()
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > MAX_MASTER_BYTES:
                raise ValueError("Dhan instrument master exceeds 40 MiB safety limit")
            chunks: list[bytes] = []
            total = 0
            for chunk in response.iter_bytes():
                total += len(chunk)
                if total > MAX_MASTER_BYTES:
                    raise ValueError("Dhan instrument master exceeds 40 MiB safety limit")
                chunks.append(chunk)
        payload = b"".join(chunks)
        try:
            text = payload.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("Dhan instrument master is not valid UTF-8 CSV") from exc
        return parse_instrument_master(text)
    finally:
        if owns_client:
            http_client.close()
