from collections.abc import Awaitable, Callable

from fastapi import FastAPI

from app.db import ping_db, ping_redis
from app.routers.completion import router as completion_router
from app.routers.history import router as history_router
from app.routers.me import router as me_router
from app.routers.quests import router as quests_router

app = FastAPI(title="Nexus")
app.include_router(quests_router)
app.include_router(me_router)
app.include_router(completion_router)
app.include_router(history_router)


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
