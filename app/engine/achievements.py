"""Achievement system for tracking milestones and accomplishments."""

from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class AchievementType(Enum):
    """Types of achievements available."""
    PROGRESS = "progress"  # Reach a milestone (level, XP, etc.)
    COLLECTION = "collection"  # Collect items or complete sets
    SKILL = "skill"  # Demonstrate skill (perfect streaks, combos)
    SOCIAL = "social"  # Social achievements (sharing, referrals)
    SPECIAL = "special"  # Special event or seasonal achievements


class AchievementTier(Enum):
    """Tiers of achievement difficulty."""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


@dataclass
class Achievement:
    """Definition of an achievement."""
    id: str
    name: str
    description: str
    achievement_type: AchievementType
    tier: AchievementTier
    requirement: Dict[str, Any]  # e.g., {"level": 10} or {"quests_completed": 100}
    reward_xp: int
    reward_coins: int
    badge_url: Optional[str] = None
    is_secret: bool = False  # Hidden until earned


@dataclass
class UserAchievement:
    """User's progress toward an achievement."""
    achievement_id: str
    earned_at: Optional[datetime]
    current_progress: float
    required_progress: float
    percent_complete: float
    is_earned: bool


# Predefined achievements
ACHIEVEMENTS = [
    # Level-based achievements
    Achievement(
        id="level_5",
        name="Rising Star",
        description="Reach level 5",
        achievement_type=AchievementType.PROGRESS,
        tier=AchievementTier.BRONZE,
        requirement={"level": 5},
        reward_xp=100,
        reward_coins=50
    ),
    Achievement(
        id="level_10",
        name="On The Rise",
        description="Reach level 10",
        achievement_type=AchievementType.PROGRESS,
        tier=AchievementTier.SILVER,
        requirement={"level": 10},
        reward_xp=250,
        reward_coins=100
    ),
    Achievement(
        id="level_25",
        name="Veteran",
        description="Reach level 25",
        achievement_type=AchievementType.PROGRESS,
        tier=AchievementTier.GOLD,
        requirement={"level": 25},
        reward_xp=500,
        reward_coins=200
    ),
    Achievement(
        id="level_50",
        name="Master",
        description="Reach level 50",
        achievement_type=AchievementType.PROGRESS,
        tier=AchievementTier.PLATINUM,
        requirement={"level": 50},
        reward_xp=1000,
        reward_coins=500
    ),
    Achievement(
        id="level_100",
        name="Legend",
        description="Reach the maximum level",
        achievement_type=AchievementType.PROGRESS,
        tier=AchievementTier.DIAMOND,
        requirement={"level": 100},
        reward_xp=5000,
        reward_coins=2000
    ),
    
    # Quest completion achievements
    Achievement(
        id="quests_10",
        name="Quest Beginner",
        description="Complete 10 quests",
        achievement_type=AchievementType.PROGRESS,
        tier=AchievementTier.BRONZE,
        requirement={"quests_completed": 10},
        reward_xp=150,
        reward_coins=75
    ),
    Achievement(
        id="quests_50",
        name="Quest Enthusiast",
        description="Complete 50 quests",
        achievement_type=AchievementType.PROGRESS,
        tier=AchievementTier.SILVER,
        requirement={"quests_completed": 50},
        reward_xp=400,
        reward_coins=150
    ),
    Achievement(
        id="quests_100",
        name="Quest Master",
        description="Complete 100 quests",
        achievement_type=AchievementType.PROGRESS,
        tier=AchievementTier.GOLD,
        requirement={"quests_completed": 100},
        reward_xp=800,
        reward_coins=300
    ),
    Achievement(
        id="quests_500",
        name="Quest Legend",
        description="Complete 500 quests",
        achievement_type=AchievementType.PROGRESS,
        tier=AchievementTier.PLATINUM,
        requirement={"quests_completed": 500},
        reward_xp=2000,
        reward_coins=750
    ),
    
    # Streak achievements
    Achievement(
        id="streak_7",
        name="Week Warrior",
        description="Maintain a 7-day streak",
        achievement_type=AchievementType.SKILL,
        tier=AchievementTier.SILVER,
        requirement={"streak_days": 7},
        reward_xp=300,
        reward_coins=100
    ),
    Achievement(
        id="streak_30",
        name="Monthly Master",
        description="Maintain a 30-day streak",
        achievement_type=AchievementType.SKILL,
        tier=AchievementTier.GOLD,
        requirement={"streak_days": 30},
        reward_xp=750,
        reward_coins=250
    ),
    Achievement(
        id="streak_90",
        name="Seasonal Sage",
        description="Maintain a 90-day streak",
        achievement_type=AchievementType.SKILL,
        tier=AchievementTier.PLATINUM,
        requirement={"streak_days": 90},
        reward_xp=1500,
        reward_coins=500
    ),
    Achievement(
        id="streak_365",
        name="Yearly Legend",
        description="Maintain a 365-day streak",
        achievement_type=AchievementType.SKILL,
        tier=AchievementTier.DIAMOND,
        requirement={"streak_days": 365},
        reward_xp=5000,
        reward_coins=2000
    ),
    
    # Combo achievements
    Achievement(
        id="combo_5",
        name="Quick Hands",
        description="Achieve a 5x combo",
        achievement_type=AchievementType.SKILL,
        tier=AchievementTier.BRONZE,
        requirement={"combo_count": 5},
        reward_xp=200,
        reward_coins=75
    ),
    Achievement(
        id="combo_10",
        name="Combo King",
        description="Achieve a 10x combo",
        achievement_type=AchievementType.SKILL,
        tier=AchievementTier.GOLD,
        requirement={"combo_count": 10},
        reward_xp=600,
        reward_coins=200
    ),
    
    # Perfect week achievement
    Achievement(
        id="perfect_week",
        name="Flawless Victory",
        description="Complete all daily quests for 7 consecutive days",
        achievement_type=AchievementType.SKILL,
        tier=AchievementTier.GOLD,
        requirement={"perfect_days": 7},
        reward_xp=500,
        reward_coins=200
    ),
]


class AchievementManager:
    """Manages achievement tracking and unlocking."""
    
    def __init__(self):
        """Initialize AchievementManager with predefined achievements."""
        self.achievements: Dict[str, Achievement] = {
            ach.id: ach for ach in ACHIEVEMENTS
        }
    
    def get_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """Get an achievement by ID."""
        return self.achievements.get(achievement_id)
    
    def check_achievement(
        self,
        achievement: Achievement,
        user_stats: Dict[str, Any]
    ) -> UserAchievement:
        """
        Check user's progress toward an achievement.
        
        Args:
            achievement: The achievement to check
            user_stats: Dictionary of user statistics
            
        Returns:
            UserAchievement with current progress
        """
        required_key = next(iter(achievement.requirement.keys()))
        required_value = achievement.requirement[required_key]
        
        current_value = user_stats.get(required_key, 0)
        
        # Calculate progress percentage
        if required_value > 0:
            percent_complete = min((current_value / required_value) * 100, 100)
        else:
            percent_complete = 100 if current_value >= 0 else 0
        
        is_earned = current_value >= required_value
        
        return UserAchievement(
            achievement_id=achievement.id,
            earned_at=datetime.utcnow() if is_earned else None,
            current_progress=current_value,
            required_progress=required_value,
            percent_complete=percent_complete,
            is_earned=is_earned
        )
    
    def check_all_achievements(
        self,
        user_stats: Dict[str, Any],
        earned_achievements: List[str]
    ) -> List[UserAchievement]:
        """
        Check progress on all achievements.
        
        Args:
            user_stats: Dictionary of user statistics
            earned_achievements: List of already earned achievement IDs
            
        Returns:
            List of UserAchievement objects
        """
        results = []
        for achievement in ACHIEVEMENTS:
            user_ach = self.check_achievement(achievement, user_stats)
            
            # If already earned, set the earned_at date properly
            if achievement.id in earned_achievements:
                user_ach.is_earned = True
                user_ach.percent_complete = 100
            
            results.append(user_ach)
        
        return results
    
    def get_newly_earned_achievements(
        self,
        user_stats: Dict[str, Any],
        previously_earned: List[str]
    ) -> List[Achievement]:
        """
        Find achievements that were just earned.
        
        Args:
            user_stats: Current user statistics
            previously_earned: List of previously earned achievement IDs
            
        Returns:
            List of newly earned Achievement objects
        """
        newly_earned = []
        
        for achievement in ACHIEVEMENTS:
            if achievement.id in previously_earned:
                continue
            
            user_ach = self.check_achievement(achievement, user_stats)
            if user_ach.is_earned:
                newly_earned.append(achievement)
        
        return newly_earned
    
    def get_achievements_by_type(
        self,
        achievement_type: AchievementType
    ) -> List[Achievement]:
        """Get all achievements of a specific type."""
        return [
            ach for ach in ACHIEVEMENTS
            if ach.achievement_type == achievement_type
        ]
    
    def get_achievements_by_tier(
        self,
        tier: AchievementTier
    ) -> List[Achievement]:
        """Get all achievements of a specific tier."""
        return [
            ach for ach in ACHIEVEMENTS
            if ach.tier == tier
        ]
    
    def calculate_total_rewards(
        self,
        earned_achievement_ids: List[str]
    ) -> tuple[int, int]:
        """
        Calculate total rewards from earned achievements.
        
        Args:
            earned_achievement_ids: List of earned achievement IDs
            
        Returns:
            Tuple of (total_xp, total_coins)
        """
        total_xp = 0
        total_coins = 0
        
        for ach_id in earned_achievement_ids:
            achievement = self.get_achievement(ach_id)
            if achievement:
                total_xp += achievement.reward_xp
                total_coins += achievement.reward_coins
        
        return total_xp, total_coins
    
    def get_completion_percentage(
        self,
        earned_achievement_ids: List[str]
    ) -> float:
        """
        Calculate overall achievement completion percentage.
        
        Args:
            earned_achievement_ids: List of earned achievement IDs
            
        Returns:
            Percentage of achievements earned (0-100)
        """
        if not ACHIEVEMENTS:
            return 0
        
        earned_count = len(earned_achievement_ids)
        return (earned_count / len(ACHIEVEMENTS)) * 100
