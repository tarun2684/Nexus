"""Idempotent quest-catalog seeder.

Upserts `app/data/quests.yaml` into the `quests` table, matched by `id`.
Safe to re-run: existing rows are updated in place, never duplicated.

Usage:
    uv run python scripts/seed.py
"""

import asyncio
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import engine as app_engine
from app.models import Quest

QUESTS_YAML = Path(__file__).resolve().parent.parent / "app" / "data" / "quests.yaml"


def load_quests(path: Path = QUESTS_YAML) -> list[dict[str, Any]]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return raw["quests"]


async def seed_quests(engine: AsyncEngine, quests: list[dict[str, Any]] | None = None) -> int:
    """Upsert `quests` into the given engine's DB. Returns the count seeded."""
    quests = quests if quests is not None else load_quests()
    async with AsyncSession(engine) as session:
        for q in quests:
            existing = await session.get(Quest, q["id"])
            if existing is None:
                session.add(Quest(**q))
            else:
                for field, value in q.items():
                    setattr(existing, field, value)
        await session.commit()
    return len(quests)


async def main() -> None:
    count = await seed_quests(app_engine)
    print(f"Seeded {count} quests.")


if __name__ == "__main__":
    asyncio.run(main())
