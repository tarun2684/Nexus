"""Quest completion and penalty endpoints."""
from datetime import datetime
from typing import List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import Quest, Profile, User, DailyLog, Event
from app.engine.time import TimeManager
from app.services.game import GameService

router = APIRouter(tags=["quests"])

time_manager = TimeManager()
game_service = GameService()


class CompleteQuestIn(BaseModel):
    """Request to complete a quest."""
    # No XP/coins sent - loaded from DB server-side (anti-cheat)
    notes: str | None = None


class CompleteQuestOut(BaseModel):
    """Response after completing a quest."""
    success: bool
    xp_earned: int
    coins_earned: int
    new_total_xp: int
    old_level: int
    new_level: int
    leveled_up: bool
    streak_count: int
    combo_multiplier: float
    achievements_unlocked: List[str]
    message: str


class ApplyPenaltyIn(BaseModel):
    """Request to apply a penalty."""
    reason: str | None = None


class ApplyPenaltyOut(BaseModel):
    """Response after applying a penalty."""
    success: bool
    xp_lost: int
    coins_lost: int
    new_total_xp: int
    old_level: int
    new_level: int
    level_lost: bool
    reason: str


@router.post("/quests/{quest_id}/complete", response_model=CompleteQuestOut)
async def complete_quest(
    quest_id: str,
    payload: CompleteQuestIn,
    session: AsyncSession = Depends(get_session),
) -> CompleteQuestOut:
    """Complete a quest and earn rewards.
    
    XP/coins are loaded from the DB - client cannot propose values (anti-cheat).
    Uses DEV_USER_ID for now; real auth in Sprint 5.
    """
    dev_user_id = UUID("00000000-0000-0000-0000-000000000001")
    
    # Load quest from DB
    quest_stmt = select(Quest).where(Quest.id == quest_id)
    quest_result = await session.exec(quest_stmt)
    quest = quest_result.first()
    
    if not quest:
        raise HTTPException(status_code=404, detail=f"Quest '{quest_id}' not found")
    
    if not quest.active:
        raise HTTPException(status_code=400, detail=f"Quest '{quest_id}' is not active")
    
    # Check if already completed today
    today_ist = time_manager.today_ist()
    daily_log_stmt = select(DailyLog).where(
        DailyLog.user_id == dev_user_id,
        DailyLog.date == today_ist
    )
    daily_log_result = await session.exec(daily_log_stmt)
    daily_log = daily_log_result.first()
    
    if daily_log and quest_id in daily_log.quests_done:
        raise HTTPException(
            status_code=400,
            detail=f"Quest '{quest_id}' already completed today"
        )
    
    # Load user profile
    profile_stmt = select(Profile).where(Profile.user_id == dev_user_id)
    profile_result = await session.exec(profile_stmt)
    profile = profile_result.first()
    
    if not profile:
        # Auto-create profile
        profile = Profile(user_id=dev_user_id)
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
    
    # Get recent completions for combo calculation
    # TODO: Implement proper event history query
    recent_completions: List[datetime] = []
    daily_completion_dates: List[datetime] = []
    earned_achievements: List[str] = []
    
    # Build current user state
    current_state = {
        "total_xp": profile.total_xp,
        "coins": profile.coins,
        "level": profile.level,
        "quests_completed": 0,  # TODO: Track this properly
    }
    
    # Use a deadline far in the future for now (no penalty)
    # TODO: Implement proper deadline tracking per quest instance
    deadline = datetime(2099, 12, 31, tzinfo=time_manager.IST)
    
    # Process completion
    result = game_service.complete_quest(
        user_id=0,  # Not used in current implementation
        quest_id=0,  # Not used in current implementation
        quest_xp=quest.xp,
        quest_coins=quest.coins,
        deadline=deadline,
        completion_time=None,  # Defaults to now
        current_user_state=current_state,
        recent_completions=recent_completions,
        daily_completion_dates=daily_completion_dates,
        earned_achievements=earned_achievements
    )
    
    # Write event
    event = Event(
        user_id=dev_user_id,
        type="quest_complete",
        xp_delta=result.xp_earned,
        coin_delta=result.coins_earned,
        quest_id=quest_id,
        meta={
            "notes": payload.notes,
            "streak": result.streak_count,
            "combo_multiplier": result.combo_multiplier,
            "achievements": result.achievements_unlocked
        }
    )
    session.add(event)
    
    # Update profile
    profile.total_xp = result.new_total_xp
    profile.coins += result.coins_earned
    profile.level = result.new_level
    if result.streak_count > profile.streak_count:
        profile.streak_count = result.streak_count
    if result.streak_count > profile.streak_longest:
        profile.streak_longest = result.streak_count
    profile.last_active = today_ist
    
    # Update/create daily log
    if not daily_log:
        daily_log = DailyLog(
            user_id=dev_user_id,
            date=today_ist,
            xp_earned=result.xp_earned,
            quests_done=[quest_id],
            combos=[]
        )
        session.add(daily_log)
    else:
        daily_log.xp_earned += result.xp_earned
        daily_log.quests_done.append(quest_id)
    
    # Handle achievement unlocks
    for ach_id in result.achievements_unlocked:
        ach_event = Event(
            user_id=dev_user_id,
            type="achievement",
            xp_delta=100,  # TODO: Get actual achievement reward
            coin_delta=50,
            meta={"achievement_id": ach_id}
        )
        session.add(ach_event)
        profile.total_xp += 100
        profile.coins += 50
    
    await session.commit()
    
    return CompleteQuestOut(
        success=result.success,
        xp_earned=result.xp_earned,
        coins_earned=result.coins_earned,
        new_total_xp=result.new_total_xp,
        old_level=result.old_level,
        new_level=result.new_level,
        leveled_up=result.leveled_up,
        streak_count=result.streak_count,
        combo_multiplier=result.combo_multiplier,
        achievements_unlocked=result.achievements_unlocked,
        message=result.message
    )


@router.post("/penalties/{quest_id}", response_model=ApplyPenaltyOut)
async def apply_penalty(
    quest_id: str,
    payload: ApplyPenaltyIn,
    session: AsyncSession = Depends(get_session),
) -> ApplyPenaltyOut:
    """Apply a penalty for missing a quest deadline.
    
    Uses DEV_USER_ID for now; real auth in Sprint 5.
    """
    dev_user_id = UUID("00000000-0000-0000-0000-000000000001")
    
    # Load quest from DB
    quest_stmt = select(Quest).where(Quest.id == quest_id)
    quest_result = await session.exec(quest_stmt)
    quest = quest_result.first()
    
    if not quest:
        raise HTTPException(status_code=404, detail=f"Quest '{quest_id}' not found")
    
    # Load user profile
    profile_stmt = select(Profile).where(Profile.user_id == dev_user_id)
    profile_result = await session.exec(profile_stmt)
    profile = profile_result.first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    # Use a deadline in the past
    deadline = datetime(2020, 1, 1, tzinfo=time_manager.IST)
    current_time = time_manager.now
    
    # Build current user state
    current_state = {
        "total_xp": profile.total_xp,
        "coins": profile.coins,
        "level": profile.level,
        "missed_deadlines": 0,  # TODO: Track this properly
    }
    
    # Process penalty
    result = game_service.apply_penalty(
        user_id=0,  # Not used in current implementation
        quest_id=0,  # Not used in current implementation
        quest_xp=quest.xp,
        quest_coins=quest.coins,
        deadline=deadline,
        current_time=current_time,
        current_user_state=current_state
    )
    
    # Write event
    event = Event(
        user_id=dev_user_id,
        type="penalty",
        xp_delta=-result.xp_lost,
        coin_delta=-result.coins_lost,
        quest_id=quest_id,
        meta={"reason": payload.reason or result.reason}
    )
    session.add(event)
    
    # Update profile
    profile.total_xp = result.new_total_xp
    profile.coins = max(0, profile.coins - result.coins_lost)
    profile.level = result.new_level
    
    await session.commit()
    
    return ApplyPenaltyOut(
        success=result.success,
        xp_lost=result.xp_lost,
        coins_lost=result.coins_lost,
        new_total_xp=result.new_total_xp,
        old_level=result.old_level,
        new_level=result.new_level,
        level_lost=result.level_lost,
        reason=result.reason
    )
