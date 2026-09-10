"""User profile and state endpoints."""
from datetime import date
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.engine.time import TimeManager
from app.models import DailyLog, Profile, User

router = APIRouter(tags=["me"])

time_manager = TimeManager()


class StateOut(BaseModel):
    """Current user state response."""
    model_config = {"from_attributes": True}
    
    user_id: UUID
    display_name: str
    avatar: str
    level: int
    total_xp: int
    coins: int
    trophies: int
    streak_count: int
    streak_longest: int
    last_active: date | None
    rank: int | None = None  # Global rank (Sprint 6)
    today_xp: int = 0
    quests_done_today: list[str] = []
    combos_fired_today: list[str] = []


@router.get("/me/state", response_model=StateOut)
async def get_user_state(
    session: AsyncSession,
) -> StateOut:
    """Get current user state — profile + today's progress.
    
    For Sprint 3, uses DEV_USER_ID. Real auth in Sprint 5.
    """
    # TODO: Replace with Depends(get_current_user) in Sprint 5
    dev_user_id = UUID("00000000-0000-0000-0000-000000000001")
    
    # Load user
    user_stmt = select(User).where(User.id == dev_user_id)
    user_result = await session.exec(user_stmt)
    user = user_result.first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Load profile
    profile_stmt = select(Profile).where(Profile.user_id == dev_user_id)
    profile_result = await session.exec(profile_stmt)
    profile = profile_result.first()
    
    if not profile:
        # Auto-create profile if missing
        profile = Profile(user_id=dev_user_id)
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
    
    # Load today's daily log
    today_ist = time_manager.today_ist()
    daily_log_stmt = select(DailyLog).where(
        DailyLog.user_id == dev_user_id,
        DailyLog.date == today_ist
    )
    daily_log_result = await session.exec(daily_log_stmt)
    daily_log = daily_log_result.first()
    
    today_xp = daily_log.xp_earned if daily_log else 0
    quests_done = daily_log.quests_done if daily_log else []
    combos_fired = daily_log.combos if daily_log else []
    
    # TODO: Calculate rank in Sprint 6
    rank = None
    
    return StateOut(
        user_id=user.id,
        display_name=user.display_name,
        avatar=user.avatar,
        level=profile.level,
        total_xp=profile.total_xp,
        coins=profile.coins,
        trophies=profile.trophies,
        streak_count=profile.streak_count,
        streak_longest=profile.streak_longest,
        last_active=profile.last_active,
        rank=rank,
        today_xp=today_xp,
        quests_done_today=quests_done,
        combos_fired_today=combos_fired
    )
