import uuid
from datetime import date

from sqlmodel import Field, SQLModel


class Profile(SQLModel, table=True):
    """Fast-read "current state" snapshot for a user.

    One row per user, kept in sync by `services/game.py` (Sprint 2) every
    time an event is written. `events` stays the source of truth; this table
    exists so `/me/state` doesn't have to re-sum the whole event log.
    """

    __tablename__ = "profiles"

    user_id: uuid.UUID = Field(foreign_key="users.id", primary_key=True)
    total_xp: int = Field(default=0)
    coins: int = Field(default=0)
    trophies: int = Field(default=0)
    streak_count: int = Field(default=0)
    streak_longest: int = Field(default=0)
    last_active: date | None = Field(default=None)  # IST calendar date, per engine/time.py
    level: int = Field(default=1)
