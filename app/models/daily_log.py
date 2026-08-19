import uuid
from datetime import date as date_

from sqlalchemy import Column
from sqlmodel import Field, SQLModel

from app.models._types import JSON_VARIANT


class DailyLog(SQLModel, table=True):
    """One row per user per (IST) calendar day — the "day's progress" view.

    `quests_done`/`combos` are derived from `events` but kept here too so
    "what did I do today" is a single-row read instead of a scan. The
    composite primary key *is* the `unique(user_id, date)` constraint — a
    day can only roll up once per user.
    """

    __tablename__ = "daily_logs"

    user_id: uuid.UUID = Field(foreign_key="users.id", primary_key=True)
    date: date_ = Field(primary_key=True)  # IST calendar date, per engine/time.py (Sprint 2)
    xp_earned: int = Field(default=0)
    quests_done: list[str] = Field(
        default_factory=list, sa_column=Column(JSON_VARIANT, nullable=False)
    )
    combos: list[str] = Field(
        default_factory=list, sa_column=Column(JSON_VARIANT, nullable=False)
    )
