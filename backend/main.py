"""CloudLaunch Phase 1 API and static dashboard server.

All measurements returned by this application describe the machine running
the process. They are local system metrics, not AWS CloudWatch metrics.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psutil
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
STARTED_AT = time.monotonic()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cloudlaunch")

app = FastAPI(
    title="CloudLaunch",
    description="Local machine monitoring API for CloudLaunch Phase 1.",
    version="0.1.0",
)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


def utc_timestamp() -> str:
    """Return an ISO-8601 UTC timestamp for API responses."""
    return datetime.now(timezone.utc).isoformat()


def collect_metrics() -> dict[str, Any]:
    """Read current CPU, memory, and system-drive usage with psutil."""
    disk_path = Path.cwd().anchor or str(Path.cwd())
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(disk_path)
    return {
        "source": "local machine",
        "timestamp": utc_timestamp(),
        "cpu": {"percent": psutil.cpu_percent(interval=None), "cores": psutil.cpu_count(logical=True)},
        "memory": {
            "percent": memory.percent,
            "used_bytes": memory.used,
            "total_bytes": memory.total,
            "available_bytes": memory.available,
        },
        "disk": {
            "percent": disk.percent,
            "used_bytes": disk.used,
            "total_bytes": disk.total,
            "free_bytes": disk.free,
            "path": disk_path,
        },
    }


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Log unexpected failures and return a safe, consistent error response."""
    logger.exception("Unhandled error while handling %s", request.url.path, exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "An unexpected server error occurred."})


@app.get("/", include_in_schema=False)
async def dashboard() -> FileResponse:
    """Serve the monitoring dashboard."""
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    """Lightweight liveness endpoint for the API process."""
    return {"status": "ok", "timestamp": utc_timestamp()}


@app.get("/api/status")
async def status() -> dict[str, Any]:
    """Return application state and process uptime."""
    return {
        "application": "CloudLaunch",
        "status": "running",
        "metrics_source": "local machine",
        "uptime_seconds": round(time.monotonic() - STARTED_AT, 2),
        "timestamp": utc_timestamp(),
    }


@app.get("/api/metrics")
async def metrics() -> dict[str, Any]:
    """Return local CPU, memory, and disk metrics."""
    try:
        return collect_metrics()
    except (OSError, psutil.Error, ValueError) as exc:
        logger.exception("Could not collect local system metrics")
        raise HTTPException(status_code=503, detail="Local system metrics are temporarily unavailable.") from exc
