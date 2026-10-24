from datetime import datetime, timezone
from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="India-focused market intelligence, strategy research and paper-trading foundation.",
)


@app.get("/", tags=["system"])
def root() -> dict:
    return {
        "name": settings.app_name,
        "status": "running",
        "mode": "paper-only",
        "live_orders_enabled": settings.enable_live_orders,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health", tags=["system"])
def health() -> dict:
    return {"status": "ok", "timestamp_utc": datetime.now(timezone.utc).isoformat()}


@app.get("/api/v1/system/status", tags=["system"])
def system_status() -> dict:
    return {
        "environment": settings.app_env,
        "dhan_credentials_configured": bool(settings.dhan_access_token and settings.dhan_client_id),
        "live_orders_enabled": settings.enable_live_orders,
        "message": "Credentials are not tested by this endpoint. Live order execution is not implemented.",
    }


@app.get("/api/v1/strategies", tags=["strategies"])
def list_strategies() -> dict:
    return {
        "count": 0,
        "strategies": [],
        "message": "Plugin registry is the next implementation stage; no strategy is enabled yet.",
    }
