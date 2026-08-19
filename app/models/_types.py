"""Shared column-type helpers for SQLModel table models.

Keeping these in one place means every table gets the same JSON-on-Postgres
(JSONB) / JSON-elsewhere behavior, and the same "always tz-aware" datetime
behavior, without repeating the wiring in each model file.
"""

from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import TypeEngine

# JSONB on Postgres (our real target, per ADR-001); plain JSON on anything
# else (e.g. SQLite), so models stay testable without a live Postgres.
JSON_VARIANT: TypeEngine = JSON().with_variant(JSONB(), "postgresql")

# Always store an explicit timezone. Naive datetimes are how "which day was
# this?" bugs get in — see engine/time.py in Sprint 2.
TZ_DATETIME: TypeEngine = DateTime(timezone=True)


def utcnow() -> datetime:
    """Default factory for tz-aware timestamp columns."""
    return datetime.now(UTC)
