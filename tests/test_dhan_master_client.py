import httpx
import pytest

from app.data.dhan_master_client import (
    COMPACT_MASTER_URL,
    DETAILED_MASTER_URL,
    download_instrument_master,
)


CSV = (
    "SEM_EXM_EXCH_ID,SEM_SEGMENT,SEM_SMST_SECURITY_ID,"
    "SEM_INSTRUMENT_NAME,SEM_TRADING_SYMBOL\n"
    "NSE,E,1333,EQUITY,HDFCBANK\n"
)


def client_for(response_status=200, body=CSV, headers=None):
    def handler(request):
        return httpx.Response(
            response_status,
            content=body.encode("utf-8"),
            headers=headers or {"content-type": "text/csv"},
            request=request,
        )
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_downloads_detailed_master_by_default_and_parses_rows():
    with client_for() as client:
        rows = download_instrument_master(client=client)
    assert len(rows) == 1
    assert rows[0].security_id == "1333"


def test_compact_url_selected_when_requested():
    requested = []

    def handler(request):
        requested.append(str(request.url))
        return httpx.Response(200, text=CSV, request=request)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        download_instrument_master(detailed=False, client=client)
    assert requested == [COMPACT_MASTER_URL]
    assert requested[0] != DETAILED_MASTER_URL


def test_http_error_is_not_silently_ignored():
    with client_for(response_status=503) as client:
        with pytest.raises(httpx.HTTPStatusError):
            download_instrument_master(client=client)


def test_rejects_declared_oversize_download():
    with client_for(headers={"content-length": str(50 * 1024 * 1024)}) as client:
        with pytest.raises(ValueError, match="40 MiB"):
            download_instrument_master(client=client)


def test_rejects_non_csv_payload():
    with client_for(body="") as client:
        with pytest.raises(ValueError, match="no header"):
            download_instrument_master(client=client)
