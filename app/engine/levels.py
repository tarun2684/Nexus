"""Level system and XP curve calculations for Nexus."""

from dataclasses import dataclass


@dataclass
class LevelInfo:
    """Information about a specific level."""
    level: int
    xp_required: int
    xp_from_previous: int
    title: str


# XP Curve Configuration
# Uses a smooth interpolation curve for balanced progression
BASE_XP = 100
XP_GROWTH_FACTOR = 1.5
MAX_LEVEL = 100

# Level titles for gamification
LEVEL_TITLES = [
    "Novice",           # 1-4
    "Apprentice",       # 5-9
    "Journeyman",       # 10-19
    "Artisan",          # 20-29
    "Expert",           # 30-49
    "Master",           # 50-74
    "Grandmaster",      # 75-99
    "Legend",           # 100
]


def calculate_xp_for_level(level: int) -> int:
    """
    Calculate total XP required to reach a specific level.
    
    Uses exponential growth with smoothing for balanced progression.
    Formula: base_xp * (growth_factor ^ (level - 1))
    
    Args:
        level: Target level (1-100)
        
    Returns:
        Total XP required to reach this level from level 0
        
    Raises:
        ValueError: If level is outside valid range
    """
    if level < 1:
        raise ValueError("Level must be at least 1")
    if level > MAX_LEVEL:
        raise ValueError(f"Level cannot exceed {MAX_LEVEL}")
    
    if level == 1:
        return BASE_XP
    
    # Exponential growth curve
    total_xp = 0
    for i in range(1, level + 1):
        level_xp = int(BASE_XP * (XP_GROWTH_FACTOR ** (i - 1)))
        total_xp += level_xp
    
    return total_xp


def get_level_info(level: int) -> LevelInfo:
    """
    Get detailed information about a specific level.
    
    Args:
        level: The level to get info for
        
    Returns:
        LevelInfo dataclass with level details
    """
    if level < 1:
        level = 1
    if level > MAX_LEVEL:
        level = MAX_LEVEL
    
    xp_required = calculate_xp_for_level(level)
    xp_from_previous = calculate_xp_for_level(level - 1) if level > 1 else 0
    xp_for_this_level = xp_required - xp_from_previous
    
    # Determine title based on level ranges
    if level >= 100:
        title = LEVEL_TITLES[-1]
    elif level >= 75:
        title = LEVEL_TITLES[-2]
    elif level >= 50:
        title = LEVEL_TITLES[-3]
    elif level >= 30:
        title = LEVEL_TITLES[-4]
    elif level >= 20:
        title = LEVEL_TITLES[-5]
    elif level >= 10:
        title = LEVEL_TITLES[-6]
    elif level >= 5:
        title = LEVEL_TITLES[-7]
    else:
        title = LEVEL_TITLES[-8]
    
    return LevelInfo(
        level=level,
        xp_required=xp_required,
        xp_from_previous=xp_for_this_level,
        title=title
    )


def get_current_level(total_xp: int) -> tuple[int, int, int]:
    """
    Determine current level and XP progress from total XP.
    
    Args:
        total_xp: Player's total accumulated XP
        
    Returns:
        Tuple of (current_level, xp_in_current_level, xp_needed_for_next)
    """
    if total_xp < 0:
        total_xp = 0
    
    # Handle edge case: at 0 XP or below first level threshold, return level 1 with 0 progress
    level_1_xp = calculate_xp_for_level(1)
    if total_xp < level_1_xp:
        return 1, 0, level_1_xp
    
    level = 1
    while True:
        next_level_xp = calculate_xp_for_level(level + 1)
        if total_xp < next_level_xp:
            break
        level += 1
        if level >= MAX_LEVEL:
            break
    
    current_threshold = calculate_xp_for_level(level)
    next_threshold = calculate_xp_for_level(min(level + 1, MAX_LEVEL))
    
    xp_in_current = total_xp - current_threshold
    xp_for_next = next_threshold - current_threshold
    
    return level, xp_in_current, xp_for_next


def can_level_up(current_xp: int, quest_xp: int) -> bool:
    """
    Check if adding quest XP would result in a level up.
    
    Args:
        current_xp: Player's current total XP
        quest_xp: XP from completing a quest
        
    Returns:
        True if the player would level up
    """
    current_level, _, _ = get_current_level(current_xp)
    new_level, _, _ = get_current_level(current_xp + quest_xp)
    return new_level > current_level
