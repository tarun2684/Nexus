import asyncio
from collections.abc import AsyncGenerator, Iterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.main import app as nexus_app
import app.models  # noqa: F401 - populates SQLModel.metadata before create_all


async def _create_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@pytest.fixture
def test_engine() -> Iterator[AsyncEngine]:
    """A throwaway in-memory SQLite engine with every table created.

    Stands in for Postgres in tests that need a real (async) DB round-trip
    without Docker. `StaticPool` keeps the same in-memory connection alive
    for the fixture's lifetime instead of a fresh, empty DB per connection.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    asyncio.run(_create_tables(engine))
    yield engine
    asyncio.run(engine.dispose())


@pytest.fixture
async def client(test_engine: AsyncEngine) -> AsyncGenerator[AsyncClient, None]:
    """HTTP client bound to test DB session."""
    
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with AsyncSession(test_engine) as session:
            yield session
    
    # Override dependency
    nexus_app.dependency_overrides[get_session] = override_get_session
    
    async with AsyncClient(
        transport=ASGITransport(app=nexus_app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    # Clean up overrides
    nexus_app.dependency_overrides.clear()
