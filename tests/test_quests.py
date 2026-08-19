import asyncio

from fastapi.testclient import TestClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.main import app
from app.models import Quest
from scripts.seed import load_quests, seed_quests

VALID_CATEGORIES = {"main", "side", "health", "leisure", "penalty"}


def test_quests_yaml_is_well_formed():
    """Catches typos/duplicates in quests.yaml before they hit the DB."""
    quests = load_quests()
    assert len(quests) > 0

    seen_ids = set()
    for q in quests:
        assert q["id"] not in seen_ids, f"duplicate quest id: {q['id']}"
        seen_ids.add(q["id"])
        category = q["category"]
        assert category in VALID_CATEGORIES, f"unknown category on {q['id']!r}: {category!r}"
        assert isinstance(q["xp"], int)
        assert isinstance(q["coins"], int)


def test_seed_is_idempotent(test_engine):
    """Sprint exit test: run seed twice, no duplicates."""
    quests = load_quests()

    first_count = asyncio.run(seed_quests(test_engine, quests))
    second_count = asyncio.run(seed_quests(test_engine, quests))
    assert first_count == second_count == len(quests)

    async def _row_count() -> int:
        async with AsyncSession(test_engine) as session:
            result = await session.exec(select(Quest))
            return len(result.all())

    assert asyncio.run(_row_count()) == len(quests)


def test_quests_endpoint_returns_catalog_grouped_by_category(test_engine):
    asyncio.run(seed_quests(test_engine))

    async def _override_get_session():
        async with AsyncSession(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = _override_get_session
    try:
        response = TestClient(app).get("/quests")
    finally:
        app.dependency_overrides.pop(get_session, None)

    assert response.status_code == 200
    body = response.json()

    assert set(body.keys()) == VALID_CATEGORIES
    ml_study = next(q for q in body["main"] if q["id"] == "ml_study")
    assert ml_study == {
        "id": "ml_study",
        "title": "Study ML (deep work session)",
        "xp": 150,
        "coins": 15,
        "stat_key": "ml_sessions",
    }


def test_quests_endpoint_hides_inactive_quests(test_engine):
    async def _seed_one_inactive():
        async with AsyncSession(test_engine) as session:
            retired = Quest(
                id="retired_quest", category="main", title="Retired", xp=1, active=False
            )
            session.add(retired)
            await session.commit()

    asyncio.run(_seed_one_inactive())

    async def _override_get_session():
        async with AsyncSession(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = _override_get_session
    try:
        response = TestClient(app).get("/quests")
    finally:
        app.dependency_overrides.pop(get_session, None)

    body = response.json()
    all_ids = {q["id"] for group in body.values() for q in group}
    assert "retired_quest" not in all_ids
