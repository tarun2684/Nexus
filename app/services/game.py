"""Core game service for quest completion and penalty handling."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ..engine.achievements import AchievementManager
from ..engine.combos import ComboManager
from ..engine.levels import get_current_level
from ..engine.streaks import StreakManager
from ..engine.time import TimeManager


@dataclass
class QuestCompletionResult:
    """Result of completing a quest."""
    success: bool
    xp_earned: int
    coins_earned: int
    new_total_xp: int
    old_level: int
    new_level: int
    leveled_up: bool
    streak_count: int
    combo_multiplier: float
    achievements_unlocked: list[str]
    message: str


@dataclass
class PenaltyResult:
    """Result of applying a penalty."""
    success: bool
    xp_lost: int
    coins_lost: int
    new_total_xp: int
    old_level: int
    new_level: int
    level_lost: bool
    reason: str


class GameService:
    """Core game service handling quest completions and penalties."""
    
    def __init__(self):
        """Initialize GameService with all managers."""
        self.time_manager = TimeManager()
        self.streak_manager = StreakManager()
        self.combo_manager = ComboManager()
        self.achievement_manager = AchievementManager()
    
    def complete_quest(
        self,
        user_id: int,
        quest_id: int,
        quest_xp: int,
        quest_coins: int,
        deadline: datetime,
        completion_time: datetime | None,
        current_user_state: dict[str, Any],
        recent_completions: list[datetime],
        daily_completion_dates: list[datetime],
        earned_achievements: list[str]
    ) -> QuestCompletionResult:
        """
        Process quest completion with full game mechanics.
        
        This is the core write path that handles:
        - Base XP/coins from quest
        - Deadline penalties (late completion)
        - Streak bonuses
        - Combo multipliers
        - Level up detection
        - Achievement unlocking
        
        Args:
            user_id: User's ID
            quest_id: Quest's ID
            quest_xp: Base XP reward for quest
            quest_coins: Base coin reward for quest
            deadline: Quest deadline
            completion_time: When quest was completed (defaults to now)
            current_user_state: Current user state dict with keys:
                - total_xp: int
                - coins: int
                - level: int
                - quests_completed: int
            recent_completions: List of recent quest completion times (for combos)
            daily_completion_dates: List of daily quest completion dates (for streaks)
            earned_achievements: List of already earned achievement IDs
            
        Returns:
            QuestCompletionResult with all rewards and state changes
            
        Raises:
            ValueError: If quest is invalid or already completed
        """
        if completion_time is None:
            completion_time = self.time_manager.now
        
        # Extract current state
        current_xp = current_user_state.get("total_xp", 0)
        current_coins = current_user_state.get("coins", 0)
        current_level = current_user_state.get("level", 1)
        quests_completed = current_user_state.get("quests_completed", 0)
        
        # Calculate time-based penalty multiplier
        penalty_multiplier = self.time_manager.calculate_penalty_multiplier(
            deadline, completion_time
        )
        
        # Apply penalty to base rewards if late
        effective_xp = (
            int(quest_xp / penalty_multiplier)
            if penalty_multiplier > 1.0
            else quest_xp
        )
        effective_coins = (
            int(quest_coins / penalty_multiplier)
            if penalty_multiplier > 1.0
            else quest_coins
        )
        
        # Calculate streak bonus
        streak_info = self.streak_manager.calculate_streak(daily_completion_dates)
        if streak_info.is_active:
            streak_bonus_xp = self.streak_manager.calculate_streak_bonus(
                streak_info.current_streak, effective_xp
            )
            effective_xp = streak_bonus_xp
        
        # Calculate combo multiplier
        combo_info = self.combo_manager.calculate_rapid_combo(recent_completions)
        if combo_info.is_active:
            effective_xp = self.combo_manager.calculate_combo_bonus(
                effective_xp, combo_info.multiplier
            )
        
        # Round final XP
        final_xp = max(1, effective_xp)  # Ensure at least 1 XP
        final_coins = max(1, effective_coins)  # Ensure at least 1 coin
        
        # Calculate new totals
        new_total_xp = current_xp + final_xp
        new_coins = current_coins + final_coins
        
        # Determine levels
        old_level = current_level
        _, _, _ = get_current_level(current_xp)  # Recalculate to ensure accuracy
        new_level, _, _ = get_current_level(new_total_xp)
        leveled_up = new_level > old_level
        
        # Build updated user stats for achievement checking
        updated_stats = {
            "total_xp": new_total_xp,
            "level": new_level,
            "quests_completed": quests_completed + 1,
            "streak_days": streak_info.current_streak if streak_info.is_active else 0,
            "combo_count": combo_info.current_count if combo_info.is_active else 0
        }
        
        # Check for newly earned achievements
        newly_earned = self.achievement_manager.get_newly_earned_achievements(
            updated_stats, earned_achievements
        )
        unlocked_achievement_ids = [ach.id for ach in newly_earned]
        
        # Add achievement rewards
        for achievement in newly_earned:
            new_total_xp += achievement.reward_xp
            new_coins += achievement.reward_coins
        
        # Recalculate final level after achievement bonuses
        if newly_earned:
            new_level, _, _ = get_current_level(new_total_xp)
            leveled_up = new_level > old_level
        
        # Build result message
        message_parts = []
        message_parts.append(f"Quest completed! +{final_xp} XP, +{final_coins} coins")
        
        if penalty_multiplier > 1.0:
            message_parts.append(f"(Late: {penalty_multiplier}x penalty applied)")
        
        if streak_info.is_active and streak_info.current_streak > 1:
            message_parts.append(f"🔥 Streak: {streak_info.current_streak} days!")
        
        if combo_info.is_active:
            message_parts.append(
                f"⚡ Combo: {combo_info.current_count}x "
                f"({combo_info.multiplier}x multiplier)"
            )
        
        if leveled_up:
            message_parts.append(f"🎉 LEVEL UP! You are now level {new_level}!")
        
        if newly_earned:
            ach_names = ", ".join([ach.name for ach in newly_earned])
            message_parts.append(f"🏆 Achievements unlocked: {ach_names}")
        
        return QuestCompletionResult(
            success=True,
            xp_earned=final_xp,
            coins_earned=final_coins,
            new_total_xp=new_total_xp,
            old_level=old_level,
            new_level=new_level,
            leveled_up=leveled_up,
            streak_count=streak_info.current_streak if streak_info.is_active else 0,
            combo_multiplier=combo_info.multiplier if combo_info.is_active else 1.0,
            achievements_unlocked=unlocked_achievement_ids,
            message=" ".join(message_parts)
        )
    
    def apply_penalty(
        self,
        user_id: int,
        quest_id: int,
        quest_xp: int,
        quest_coins: int,
        deadline: datetime,
        current_time: datetime | None,
        current_user_state: dict[str, Any]
    ) -> PenaltyResult:
        """
        Apply penalty for missing a quest deadline.
        
        Penalties are applied when:
        - Quest deadline passes without completion
        - User explicitly marks quest as failed
        
        Penalty calculation:
        - Base penalty: 50% of quest XP/coins
        - Increases based on how many deadlines missed
        
        Args:
            user_id: User's ID
            quest_id: Quest's ID
            quest_xp: XP value of the quest
            quest_coins: Coin value of the quest
            deadline: Quest deadline
            current_time: Current time (defaults to now)
            current_user_state: Current user state dict with keys:
                - total_xp: int
                - coins: int
                - level: int
                - missed_deadlines: int
                
        Returns:
            PenaltyResult with penalty details
            
        Raises:
            ValueError: If penalty cannot be applied
        """
        if current_time is None:
            current_time = self.time_manager.now
        
        # Check if deadline has actually passed
        if current_time <= deadline:
            raise ValueError("Cannot apply penalty before deadline")
        
        # Extract current state
        current_xp = current_user_state.get("total_xp", 0)
        current_coins = current_user_state.get("coins", 0)
        current_level = current_user_state.get("level", 1)
        missed_deadlines = current_user_state.get("missed_deadlines", 0)
        
        # Calculate penalty percentage based on missed deadlines
        # First miss: 50%, increases by 10% for each subsequent miss, capped at 90%
        penalty_percent = min(0.5 + (missed_deadlines * 0.1), 0.9)
        
        # Calculate penalty amounts
        xp_loss = int(quest_xp * penalty_percent)
        coins_loss = int(quest_coins * penalty_percent)
        
        # Ensure we don't take away more than user has
        xp_loss = min(xp_loss, current_xp)
        coins_loss = min(coins_loss, current_coins)
        
        # Calculate new totals
        new_total_xp = current_xp - xp_loss
        
        # Determine if level was lost
        old_level = current_level
        new_level, _, _ = get_current_level(new_total_xp)
        level_lost = new_level < old_level
        
        # Build reason string
        hours_overdue = (current_time - deadline).total_seconds() / 3600
        if hours_overdue < 24:
            time_reason = f"{int(hours_overdue)} hours overdue"
        elif hours_overdue < 24 * 7:
            time_reason = f"{int(hours_overdue / 24)} days overdue"
        else:
            time_reason = f"{int(hours_overdue / (24 * 7))} weeks overdue"
        
        reason = (
            f"Missed deadline ({time_reason}). "
            f"Penalty: {int(penalty_percent * 100)}% of quest value "
            f"(-{xp_loss} XP, -{coins_loss} coins)"
        )
        
        if level_lost:
            reason += f" ⚠️ Level dropped from {old_level} to {new_level}!"
        
        return PenaltyResult(
            success=True,
            xp_lost=xp_loss,
            coins_lost=coins_loss,
            new_total_xp=new_total_xp,
            old_level=old_level,
            new_level=new_level,
            level_lost=level_lost,
            reason=reason
        )
    
    def calculate_quest_rewards(
        self,
        base_xp: int,
        base_coins: int,
        streak_count: int = 0,
        combo_count: int = 0,
        is_on_time: bool = True
    ) -> dict[str, Any]:
        """
        Calculate potential quest rewards without completing it.
        
        Useful for showing users what they could earn.
        
        Args:
            base_xp: Base XP for quest
            base_coins: Base coins for quest
            streak_count: Current streak count
            combo_count: Current combo count
            is_on_time: Whether quest would be completed on time
            
        Returns:
            Dictionary with reward breakdown
        """
        # Start with base rewards
        xp = base_xp
        coins = base_coins
        
        # Apply on-time modifier
        if not is_on_time:
            xp = int(xp * 0.5)
            coins = int(coins * 0.5)
        
        # Apply streak bonus
        if streak_count > 0:
            xp = self.streak_manager.calculate_streak_bonus(streak_count, xp)
        
        # Apply combo multiplier
        if combo_count >= 2:
            multiplier = self.combo_manager._get_rapid_multiplier(combo_count)
            xp = self.combo_manager.calculate_combo_bonus(xp, multiplier)
        
        return {
            "base_xp": base_xp,
            "base_coins": base_coins,
            "streak_bonus": xp - base_xp if streak_count > 0 else 0,
            "combo_multiplier": (
                self.combo_manager._get_rapid_multiplier(combo_count)
                if combo_count >= 2
                else 1.0
            ),
            "on_time_bonus": is_on_time,
            "final_xp": xp,
            "final_coins": coins
        }
