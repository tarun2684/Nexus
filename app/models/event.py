import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, Index
from sqlmodel import Field, SQLModel

from app.models._types import JSON_VARIANT, TZ_DATETIME, utcnow


class Event(SQLModel, table=True):
    """Append-only ledger — the source of truth for every state change.

    Every XP/coin award, penalty, streak milestone, combo fire, and
    achievement unlock is a row here. `profiles` and `daily_logs` are
    derived, rebuildable summaries; this table is not.
    """

    __tablename__ = "events"
    __table_args__ = (
        # Powers `/me/history` and the leaderboard window query (Sprint 6).
        Index("ix_events_user_id_ts", "user_id", "ts"),
        # Powers any "what happened recently, across all users" query.
        Index("ix_events_ts", "ts"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    ts: datetime = Field(default_factory=utcnow, sa_column=Column(TZ_DATETIME, nullable=False))
    type: str  # "quest_complete" | "penalty" | "combo" | "achievement" | "admin_correction" | ...
    xp_delta: int = Field(default=0)
    coin_delta: int = Field(default=0)
    quest_id: str | None = Field(default=None, foreign_key="quests.id")
    meta: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON_VARIANT, nullable=False)
    )
