from collections.abc import AsyncIterator

import redis.asyncio as aioredis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings

# One database engine for the whole app.
engine = create_async_engine(settings.database_url, pool_pre_ping=True)

# One session factory for the whole app; routers get a session via get_session().
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# One Redis client for the whole app.
redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)


async def ping_db() -> None:
    """Runs a trivial query. Raises if the DB is unreachable."""
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))


async def ping_redis() -> None:
    """Pings Redis. Raises if unreachable."""
    await redis_client.ping()


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency — yields a session, closed at the end of the request."""
    async with async_session_factory() as session:
        yield session
