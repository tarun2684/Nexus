from collections.abc import Awaitable, Callable

from fastapi import FastAPI

from app.db import ping_db, ping_redis

app = FastAPI(title="Nexus")


async def _check(check_fn: Callable[[], Awaitable[None]]) -> str:
    """Runs a ping function and reports 'ok' or the error name."""
    try:
        await check_fn()
        return "ok"
    except Exception as exc:  # noqa: BLE001 - we want any failure reported
        return f"error: {type(exc).__name__}"


@app.get("/")
async def root():
    return {"app": "Nexus", "message": "It lives."}


@app.get("/health")
async def health():
    db = await _check(ping_db)
    redis = await _check(ping_redis)
    status = "ok" if db == "ok" and redis == "ok" else "degraded"
    return {"status": status, "db": db, "redis": redis}
