"""User history endpoint."""
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.engine.time import TimeManager
from app.models import DailyLog, Event

router = APIRouter(tags=["me"])

time_manager = TimeManager()


class HistoryEntry(BaseModel):
    """A single history entry."""
    date: str  # ISO date string
    xp_earned: int
    quests_completed: int
    combos_fired: int
    achievements_unlocked: int


class HistoryOut(BaseModel):
    """History response."""
    user_id: UUID
    days: list[HistoryEntry]
    total_xp_in_period: int


@router.get("/me/history", response_model=HistoryOut)
async def get_user_history(
    days: int = Query(default=30, ge=1, le=90),
    session: AsyncSession = Depends(get_session),  # noqa: B008 - FastAPI's DI pattern
) -> HistoryOut:
    """Get user's XP history for the last N days.
    
    Returns daily breakdown of XP earned, quests completed, combos, and achievements.
    Uses DEV_USER_ID for now; real auth in Sprint 5.
    """
    dev_user_id = UUID("00000000-0000-0000-0000-000000000001")
    
    # Calculate date range
    today = time_manager.today_ist()
    start_date = today - timedelta(days=days - 1)
    
    # Load daily logs for the period
    daily_log_stmt = select(DailyLog).where(
        DailyLog.user_id == dev_user_id,
        DailyLog.date >= start_date,
        DailyLog.date <= today
    ).order_by(DailyLog.date.desc())
    
    daily_log_result = await session.exec(daily_log_stmt)
    daily_logs = list(daily_log_result)
    
    # Build history entries
    history_entries: list[HistoryEntry] = []
    total_xp = 0
    
    for log in daily_logs:
        # Count events for this day
        event_stmt = select(Event).where(
            Event.user_id == dev_user_id,
            Event.ts >= datetime.combine(log.date, datetime.min.time()),
            Event.ts < datetime.combine(log.date, datetime.max.time())
        )
        event_result = await session.exec(event_stmt)
        day_events = list(event_result)
        
        achievements = sum(1 for e in day_events if e.type == "achievement")
        
        entry = HistoryEntry(
            date=log.date.isoformat(),
            xp_earned=log.xp_earned,
            quests_completed=len(log.quests_done),
            combos_fired=len(log.combos),
            achievements_unlocked=achievements
        )
        history_entries.append(entry)
        total_xp += log.xp_earned
    
    # Fill in missing days with zeros
    existing_dates = {log.date for log in daily_logs}
    for i in range(days):
        date = today - timedelta(days=i)
        if date not in existing_dates:
            entry = HistoryEntry(
                date=date.isoformat(),
                xp_earned=0,
                quests_completed=0,
                combos_fired=0,
                achievements_unlocked=0
            )
            history_entries.append(entry)
    
    # Sort by date descending
    history_entries.sort(key=lambda x: x.date, reverse=True)
    
    return HistoryOut(
        user_id=dev_user_id,
        days=history_entries,
        total_xp_in_period=total_xp
    )
