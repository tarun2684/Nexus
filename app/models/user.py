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
    hashed_password: str
    display_name: str
    avatar: str = Field(default="steve")  # e.g. "steve" / "creeper" — Sprint 4 picks the set
    role: str = Field(default="player")  # "player" | "admin"
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=utcnow, sa_column=Column(TZ_DATETIME, nullable=False)
    )
