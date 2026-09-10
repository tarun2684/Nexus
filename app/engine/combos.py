"""Combo system for consecutive quest completions."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class ComboType(Enum):
    """Types of combos available in Nexus."""
    DAILY = "daily"  # Complete daily quests on consecutive days
    RAPID = "rapid"  # Complete multiple quests in short time
    CATEGORY = "category"  # Complete quests in same category


@dataclass
class ComboInfo:
    """Information about an active combo."""
    combo_type: ComboType
    current_count: int
    max_count: int
    multiplier: float
    expires_at: datetime | None
    is_active: bool


@dataclass
class ComboReward:
    """Reward granted for achieving a combo."""
    count_threshold: int
    multiplier: float
    bonus_xp: int
    title: str


# Combo reward tiers for rapid completion
RAPID_COMBO_REWARDS = [
    ComboReward(2, 1.2, 20, "Double Tap"),
    ComboReward(3, 1.4, 50, "Triple Threat"),
    ComboReward(4, 1.6, 100, "Quad Squad"),
    ComboReward(5, 2.0, 200, "Penta Power"),
    ComboReward(10, 3.0, 500, "Deca Destroyer"),
]

# Time window for rapid combos (in minutes)
RAPID_COMBO_WINDOW_MINUTES = 30


class ComboManager:
    """Manages combo tracking and rewards."""
    
    def __init__(self, current_time: datetime | None = None):
        """
        Initialize ComboManager.
        
        Args:
            current_time: Override for current time (useful for testing)
        """
        self._current_time = current_time
    
    @property
    def now(self) -> datetime:
        """Get current time (real or overridden)."""
        return self._current_time or datetime.utcnow()
    
    def calculate_rapid_combo(
        self,
        completion_times: list[datetime],
        reference_time: datetime | None = None
    ) -> ComboInfo:
        """
        Calculate rapid combo from recent quest completions.
        
        A rapid combo counts quests completed within a short time window.
        
        Args:
            completion_times: List of quest completion datetimes
            reference_time: Reference time for calculation (defaults to now)
            
        Returns:
            ComboInfo with current rapid combo status
        """
        if reference_time is None:
            reference_time = self.now
        
        if not completion_times:
            return ComboInfo(
                combo_type=ComboType.RAPID,
                current_count=0,
                max_count=0,
                multiplier=1.0,
                expires_at=None,
                is_active=False
            )
        
        # Filter completions within the time window
        window_start = reference_time - timedelta(minutes=RAPID_COMBO_WINDOW_MINUTES)
        recent_completions = [t for t in completion_times if t >= window_start]
        
        if not recent_completions:
            return ComboInfo(
                combo_type=ComboType.RAPID,
                current_count=0,
                max_count=0,
                multiplier=1.0,
                expires_at=None,
                is_active=False
            )
        
        # Sort by time (most recent first)
        recent_completions.sort(reverse=True)
        
        # Count consecutive completions within window
        current_count = len(recent_completions)
        
        # Calculate when combo expires
        earliest_in_window = min(recent_completions)
        expires_at = earliest_in_window + timedelta(minutes=RAPID_COMBO_WINDOW_MINUTES)
        
        # Get multiplier based on count
        multiplier = self._get_rapid_multiplier(current_count)
        
        # Find max count achieved
        max_count = self._find_max_combo_in_window(
            completion_times, 
            reference_time
        )
        
        return ComboInfo(
            combo_type=ComboType.RAPID,
            current_count=current_count,
            max_count=max(max_count, current_count),
            multiplier=multiplier,
            expires_at=expires_at,
            is_active=current_count >= 2
        )
    
    def _get_rapid_multiplier(self, count: int) -> float:
        """Get XP multiplier for rapid combo count."""
        if count < 2:
            return 1.0
        
        for reward in reversed(RAPID_COMBO_REWARDS):
            if count >= reward.count_threshold:
                return reward.multiplier
        
        # Default multiplier for counts beyond defined tiers
        return 1.0 + (count * 0.1)
    
    def _find_max_combo_in_window(
        self,
        completion_times: list[datetime],
        reference_time: datetime
    ) -> int:
        """Find the maximum combo achieved in any sliding window."""
        if not completion_times:
            return 0
        
        window = timedelta(minutes=RAPID_COMBO_WINDOW_MINUTES)
        sorted_times = sorted(completion_times)
        
        max_count = 0
        for i, start_time in enumerate(sorted_times):
            window_end = start_time + window
            count = sum(1 for t in sorted_times[i:] if t <= window_end)
            max_count = max(max_count, count)
        
        return max_count
    
    def get_combo_reward(self, count: int) -> ComboReward | None:
        """
        Get reward for achieving a combo milestone.
        
        Args:
            count: Current combo count
            
        Returns:
            ComboReward if a milestone was reached, None otherwise
        """
        applicable_reward = None
        for reward in RAPID_COMBO_REWARDS:
            if count >= reward.count_threshold:
                applicable_reward = reward
            else:
                break
        
        return applicable_reward
    
    def calculate_combo_bonus(self, base_xp: int, multiplier: float) -> int:
        """
        Calculate bonus XP from combo multiplier.
        
        Args:
            base_xp: Base XP for the quest
            multiplier: Combo multiplier (e.g., 1.2 for 20% bonus)
            
        Returns:
            Total XP including combo bonus
        """
        return int(base_xp * multiplier)
    
    def get_time_until_combo_expires(
        self,
        completion_times: list[datetime],
        reference_time: datetime | None = None
    ) -> timedelta | None:
        """
        Get time remaining until current combo expires.
        
        Args:
            completion_times: List of quest completion datetimes
            reference_time: Reference time for calculation
            
        Returns:
            Timedelta until expiration, or None if no active combo
        """
        if reference_time is None:
            reference_time = self.now
        
        combo_info = self.calculate_rapid_combo(completion_times, reference_time)
        
        if not combo_info.is_active or combo_info.expires_at is None:
            return None
        
        remaining = combo_info.expires_at - reference_time
        return remaining if remaining.total_seconds() > 0 else None
    
    def format_combo_status(self, combo_info: ComboInfo) -> str:
        """
        Format combo status for display.
        
        Args:
            combo_info: ComboInfo to format
            
        Returns:
            Human-readable combo status string
        """
        if not combo_info.is_active:
            return "No active combo"
        
        status = f"🔥 {combo_info.current_count}x Combo"
        
        if combo_info.expires_at:
            time_left = combo_info.expires_at - self.now
            if time_left.total_seconds() > 0:
                minutes = int(time_left.total_seconds() / 60)
                status += f" ({minutes}m left)"
        
        status += f" - {combo_info.multiplier}x XP"
        return status
    
    def can_start_category_combo(
        self,
        category: str,
        recent_completions: list[tuple[str, datetime]],
        required_count: int = 3
    ) -> bool:
        """
        Check if user can start/continue a category combo.
        
        Args:
            category: Quest category (e.g., "fitness", "learning")
            recent_completions: List of (category, completion_time) tuples
            required_count: Number of completions needed for combo
            
        Returns:
            True if category combo is active or can be started
        """
        window_start = self.now - timedelta(hours=24)
        
        # Count completions in this category within 24 hours
        category_count = sum(
            1 for cat, time in recent_completions
            if cat == category and time >= window_start
        )
        
        return category_count >= required_count
