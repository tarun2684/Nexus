"""SQLModel table models.

Import every module here so `SQLModel.metadata` is fully populated as soon as
`app.models` is imported — Alembic's `env.py` and `scripts/seed.py` both rely
on that side effect to see every table.
"""

from app.models.daily_log import DailyLog
from app.models.event import Event
from app.models.profile import Profile
from app.models.quest import Quest
from app.models.user import User

__all__ = ["DailyLog", "Event", "Profile", "Quest", "User"]
