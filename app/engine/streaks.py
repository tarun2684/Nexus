"""Streak tracking and management for daily quests."""

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class StreakInfo:
    """Information about a user's streak."""
    current_streak: int
    longest_streak: int
    last_completion_date: datetime | None
    next_required_date: datetime
    is_active: bool
    days_missed: int = 0


@dataclass
class StreakReward:
    """Reward granted for maintaining a streak."""
    streak_threshold: int
    bonus_xp: int
    bonus_coins: int
    title: str


# Streak reward tiers
STREAK_REWARDS = [
    StreakReward(3, 50, 10, "Streak Starter"),
    StreakReward(7, 150, 25, "Week Warrior"),
    StreakReward(14, 350, 50, "Fortnight Fighter"),
    StreakReward(30, 1000, 150, "Monthly Master"),
    StreakReward(60, 2500, 300, "Two-Month Titan"),
    StreakReward(90, 5000, 500, "Seasonal Sage"),
    StreakReward(180, 12000, 1000, "Half-Year Hero"),
    StreakReward(365, 30000, 2500, "Yearly Legend"),
]


class StreakManager:
    """Manages daily streak tracking and rewards."""
    
    def __init__(self, current_time: datetime | None = None):
        """
        Initialize StreakManager.
        
        Args:
            current_time: Override for current time (useful for testing)
        """
        self._current_time = current_time
    
    @property
    def now(self) -> datetime:
        """Get current time (real or overridden)."""
        return self._current_time or datetime.utcnow()
    
    @staticmethod
    def normalize_date(dt: datetime) -> datetime:
        """Normalize datetime to start of day for comparison."""
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def calculate_streak(
        self,
        completion_dates: list[datetime],
        reference_date: datetime | None = None
    ) -> StreakInfo:
        """
        Calculate current streak from a list of completion dates.
        
        Args:
            completion_dates: List of datetimes when daily quests were completed
            reference_date: Date to calculate streak from (defaults to now)
            
        Returns:
            StreakInfo with current streak details
        """
        if reference_date is None:
            reference_date = self.now
        
        ref_date = self.normalize_date(reference_date)
        
        if not completion_dates:
            # No completions - streak is 0, needs completion today
            return StreakInfo(
                current_streak=0,
                longest_streak=0,
                last_completion_date=None,
                next_required_date=ref_date,
                is_active=False,
                days_missed=0
            )
        
        # Normalize and sort completion dates
        normalized_dates = sorted(
            set(self.normalize_date(d) for d in completion_dates),
            reverse=True
        )
        
        # Find longest streak
        longest_streak = self._find_longest_streak(normalized_dates)
        
        # Calculate current streak
        current_streak = 0
        last_completion = None
        
        for i, date in enumerate(normalized_dates):
            if i == 0:
                # Most recent completion
                if date == ref_date:
                    # Completed today - streak continues
                    current_streak = 1
                    last_completion = date
                elif date == ref_date - timedelta(days=1):
                    # Completed yesterday - streak continues
                    current_streak = 1
                    last_completion = date
                else:
                    # Gap detected - streak broken
                    days_since = (ref_date - date).days
                    return StreakInfo(
                        current_streak=0,
                        longest_streak=longest_streak,
                        last_completion_date=date,
                        next_required_date=ref_date,
                        is_active=False,
                        days_missed=days_since - 1
                    )
            else:
                # Check if this date continues the streak
                if date == normalized_dates[i-1] - timedelta(days=1):
                    current_streak += 1
                    last_completion = date
                else:
                    break
        
        # Calculate when next completion is due
        if last_completion:
            next_required = self.normalize_date(last_completion + timedelta(days=1))
        else:
            next_required = ref_date
        
        return StreakInfo(
            current_streak=current_streak,
            longest_streak=longest_streak,
            last_completion_date=last_completion,
            next_required_date=next_required,
            is_active=current_streak > 0,
            days_missed=0
        )
    
    def _find_longest_streak(self, sorted_dates: list[datetime]) -> int:
        """Find the longest consecutive streak in a list of dates."""
        if not sorted_dates:
            return 0
        
        longest = 1
        current = 1
        
        for i in range(1, len(sorted_dates)):
            if sorted_dates[i] == sorted_dates[i-1] - timedelta(days=1):
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        
        return longest
    
    def get_streak_reward(self, streak_count: int) -> StreakReward | None:
        """
        Get reward for reaching a streak milestone.
        
        Args:
            streak_count: Current streak count
            
        Returns:
            StreakReward if a milestone was reached, None otherwise
        """
        # Find the highest milestone reached
        applicable_reward = None
        for reward in STREAK_REWARDS:
            if streak_count >= reward.streak_threshold:
                applicable_reward = reward
            else:
                break
        
        return applicable_reward
    
    def get_next_milestone(self, streak_count: int) -> StreakReward | None:
        """
        Get the next streak milestone to aim for.
        
        Args:
            streak_count: Current streak count
            
        Returns:
            StreakReward for next milestone, or None if all milestones reached
        """
        for reward in STREAK_REWARDS:
            if streak_count < reward.streak_threshold:
                return reward
        return None
    
    def is_daily_quest_due(
        self,
        last_completion: datetime | None,
        reference_date: datetime | None = None
    ) -> bool:
        """
        Check if a daily quest is due based on last completion.
        
        Args:
            last_completion: When the daily quest was last completed
            reference_date: Reference date for checking
            
        Returns:
            True if quest is available/due
        """
        if reference_date is None:
            reference_date = self.now
        
        ref_date = self.normalize_date(reference_date)
        
        if last_completion is None:
            return True
        
        last_date = self.normalize_date(last_completion)
        return last_date < ref_date
    
    def calculate_streak_bonus(self, streak_count: int, base_xp: int) -> int:
        """
        Calculate XP bonus based on streak count.
        
        Bonus formula: base_xp * (1 + streak_count * 0.1)
        Capped at 2x base XP
        
        Args:
            streak_count: Current streak count
            base_xp: Base XP for the quest
            
        Returns:
            Total XP including streak bonus
        """
        bonus_multiplier = min(1 + (streak_count * 0.1), 2.0)
        return int(base_xp * bonus_multiplier)
