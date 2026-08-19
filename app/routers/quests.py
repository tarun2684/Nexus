from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import Quest

router = APIRouter(tags=["quests"])


class QuestOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    title: str
    xp: int
    coins: int
    stat_key: str | None


@router.get("/quests", response_model=dict[str, list[QuestOut]])
async def list_quests(
    session: AsyncSession = Depends(get_session),  # noqa: B008 - FastAPI's DI pattern
) -> dict[str, list[QuestOut]]:
    """The full quest catalog, grouped by category. Inactive quests are hidden.

    XP/coin values here are display-only — `complete_quest()` (Sprint 2) always
    re-reads them from the DB, so a client can never propose its own numbers.
    """
    stmt = select(Quest).where(Quest.active).order_by(Quest.category, Quest.id)
    result = await session.exec(stmt)
    catalog: dict[str, list[QuestOut]] = {}
    for quest in result:
        catalog.setdefault(quest.category, []).append(QuestOut.model_validate(quest))
    return catalog
