import asyncio
from collections.abc import Iterator

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

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
