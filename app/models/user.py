import uuid
from datetime import datetime

from sqlalchemy import Column
from sqlmodel import Field, SQLModel

from app.models._types import TZ_DATETIME, utcnow


class User(SQLModel, table=True):
    """An account. One row per human (or admin) using Nexus."""

    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    display_name: str
    avatar: str = Field(default="steve")  # e.g. "steve" / "creeper" — Sprint 4 picks the set
    role: str = Field(default="player")  # "player" | "admin"
    created_at: datetime = Field(
        default_factory=utcnow, sa_column=Column(TZ_DATETIME, nullable=False)
    )
