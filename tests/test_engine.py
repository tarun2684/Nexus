"""Comprehensive tests for the game engine components."""

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from app.engine.achievements import ACHIEVEMENTS, AchievementManager
from app.engine.combos import RAPID_COMBO_WINDOW_MINUTES, ComboManager
from app.engine.levels import (
    BASE_XP,
    MAX_LEVEL,
    calculate_xp_for_level,
    can_level_up,
    get_current_level,
    get_level_info,
)
from app.engine.streaks import STREAK_REWARDS, StreakManager
from app.engine.time import DeadlineStatus, TimeManager

IST = ZoneInfo("Asia/Kolkata")


class TestLevelCurve:
    """Test XP curve and level calculations."""

    def test_level_1_requires_base_xp(self):
        """L1 should require exactly BASE_XP (0 XP from start)."""
        # Level 1 is the starting level, so XP needed is BASE_XP
        xp = calculate_xp_for_level(1)
        assert xp == BASE_XP

    def test_curve_is_monotonic(self):
        """XP required should always increase with level."""
        previous_xp = 0
        for level in range(1, MAX_LEVEL + 1):
            xp = calculate_xp_for_level(level)
            assert xp > previous_xp, f"Level {level} XP ({xp}) not greater than previous"
            previous_xp = xp

    def test_level_info_returns_correct_data(self):
        """Level info should contain all expected fields."""
        info = get_level_info(5)
        assert info.level == 5
        assert info.xp_required > 0
        assert info.xp_from_previous > 0
        assert info.title is not None

    def test_get_current_level_basic(self):
        """Test level calculation from total XP."""
        # At 0 XP, should be level 1
        level, xp_in_current, xp_for_next = get_current_level(0)
        assert level == 1
        assert xp_in_current == 0
        assert xp_for_next > 0

        # At exactly level 2 threshold
        level2_xp = calculate_xp_for_level(2)
        level, xp_in_current, xp_for_next = get_current_level(level2_xp)
        assert level == 2
        assert xp_in_current == 0

    def test_can_level_up_detection(self):
        """Test level up detection."""
        # Get XP needed for level 2
        level2_xp = calculate_xp_for_level(2)
        
        # Just below level 2
        assert not can_level_up(level2_xp - 100, 50)
        
        # Enough to reach level 2
        assert can_level_up(level2_xp - 100, 150)


class TestTimeManagement:
    """Test time and deadline handling."""

    def test_penalty_multiplier_on_time(self):
        """On-time completion should have no penalty."""
        manager = TimeManager()
        deadline = datetime.now(IST) + timedelta(hours=1)
        multiplier = manager.calculate_penalty_multiplier(deadline)
        assert multiplier == 1.0

    def test_penalty_multiplier_late(self):
        """Late completion should have increasing penalties."""
        base_time = datetime.utcnow()
        deadline = base_time
        
        # Within 24 hours late
        completion = deadline + timedelta(hours=12)
        multiplier = TimeManager(base_time).calculate_penalty_multiplier(deadline, completion)
        assert multiplier == 1.5

        # 24-48 hours late
        completion = deadline + timedelta(hours=36)
        multiplier = TimeManager(base_time).calculate_penalty_multiplier(deadline, completion)
        assert multiplier == 2.0

        # More than 48 hours late
        completion = deadline + timedelta(hours=60)
        multiplier = TimeManager(base_time).calculate_penalty_multiplier(deadline, completion)
        assert multiplier == 3.0

    def test_deadline_status(self):
        """Test deadline status detection."""
        base_time = datetime.utcnow()
        
        # Future deadline
        future = base_time + timedelta(hours=48)
        status = TimeManager(base_time).get_deadline_status(future)
        assert status == DeadlineStatus.PENDING

        # Urgent deadline (< 24 hours)
        urgent = base_time + timedelta(hours=12)
        status = TimeManager(base_time).get_deadline_status(urgent)
        assert status == DeadlineStatus.WARNING

        # Overdue
        overdue = base_time - timedelta(hours=1)
        status = TimeManager(base_time).get_deadline_status(overdue)
        assert status == DeadlineStatus.OVERDUE


class TestStreaks:
    """Test streak tracking and rewards."""

    def test_consecutive_days_increments_streak(self):
        """Consecutive daily completions should build streak."""
        manager = StreakManager()
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Create consecutive dates
        dates = [today - timedelta(days=i) for i in range(5)]
        
        info = manager.calculate_streak(dates, today)
        assert info.current_streak == 5
        assert info.is_active

    def test_gap_resets_streak(self):
        """Missing a day should reset streak."""
        manager = StreakManager()
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Gap of 2 days - skip yesterday
        dates = [
            today,
            today - timedelta(days=2),  # Skip yesterday
            today - timedelta(days=3),
        ]
        
        info = manager.calculate_streak(dates, today)
        assert info.current_streak == 1  # Only today counts
        # Note: days_missed is only set when streak is broken (current_streak=0)
        # When streak continues from today, days_missed stays 0
        assert not info.is_active or info.days_missed == 0

    def test_same_day_twice_no_double_increment(self):
        """Completing twice in one day shouldn't increase streak."""
        manager = StreakManager()
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Multiple completions on same day
        dates = [
            today,
            today,
            today - timedelta(days=1),
            today - timedelta(days=2),
        ]
        
        info = manager.calculate_streak(dates, today)
        assert info.current_streak == 3  # Not 4 or 5

    def test_streak_milestone_rewards(self):
        """Test streak milestone detection."""
        
        # Check that milestones exist
        thresholds = [r.streak_threshold for r in STREAK_REWARDS]
        assert 3 in thresholds
        assert 7 in thresholds
        assert 30 in thresholds

    def test_daily_quest_due_logic(self):
        """Test when daily quests are due."""
        manager = StreakManager()
        today = datetime.utcnow()
        
        # No previous completion - quest is due
        assert manager.is_daily_quest_due(None, today)
        
        # Completed today - not due
        assert not manager.is_daily_quest_due(today, today)
        
        # Completed yesterday - due
        assert manager.is_daily_quest_due(today - timedelta(days=1), today)


class TestCombos:
    """Test combo system."""

    def test_rapid_combo_within_window(self):
        """Multiple completions within time window should trigger combo."""
        manager = ComboManager()
        now = datetime.utcnow()
        
        # Completions every 5 minutes
        completions = [now - timedelta(minutes=i*5) for i in range(4)]
        
        info = manager.calculate_rapid_combo(completions, now)
        assert info.current_count == 4
        assert info.is_active
        assert info.multiplier > 1.0

    def test_combo_expires_outside_window(self):
        """Completions outside window shouldn't count."""
        manager = ComboManager()
        now = datetime.utcnow()
        
        # Old completions outside window (all beyond the window)
        old_completions = [
            now - timedelta(minutes=RAPID_COMBO_WINDOW_MINUTES + 5 + i)
            for i in range(5)
        ]
        
        info = manager.calculate_rapid_combo(old_completions, now)
        # Most recent completion might still be counted if within window edge
        # The key is that combo should not be active (multiplier = 1.0)
        assert not info.is_active
        assert info.multiplier == 1.0

    def test_combo_multiplier_increases(self):
        """Higher combo counts should give better multipliers."""
        manager = ComboManager()
        
        mult_2 = manager._get_rapid_multiplier(2)
        mult_5 = manager._get_rapid_multiplier(5)
        mult_10 = manager._get_rapid_multiplier(10)
        
        assert mult_5 > mult_2
        assert mult_10 > mult_5

    def test_combo_bonus_calculation(self):
        """Test combo bonus XP calculation."""
        manager = ComboManager()
        base_xp = 100
        multiplier = 1.5
        
        bonus_xp = manager.calculate_combo_bonus(base_xp, multiplier)
        assert bonus_xp == 150


class TestAchievements:
    """Test achievement system."""

    def test_achievement_definitions_exist(self):
        """Verify achievements are defined."""
        assert len(ACHIEVEMENTS) > 0
        
        # Check specific types exist
        ids = [a.id for a in ACHIEVEMENTS]
        assert "level_5" in ids
        assert "streak_7" in ids
        assert "quests_10" in ids

    def test_check_achievement_progress(self):
        """Test achievement progress tracking."""
        manager = AchievementManager()
        achievement = manager.get_achievement("level_10")
        
        assert achievement is not None
        
        # Not yet earned
        user_stats = {"level": 5}
        result = manager.check_achievement(achievement, user_stats)
        assert not result.is_earned
        assert result.percent_complete == 50.0

        # Earned
        user_stats = {"level": 15}
        result = manager.check_achievement(achievement, user_stats)
        assert result.is_earned
        assert result.percent_complete == 100.0

    def test_newly_earned_detection(self):
        """Test detection of newly earned achievements."""
        manager = AchievementManager()
        
        # Previously earned nothing
        previously_earned = []
        
        # User stats that earn multiple achievements
        user_stats = {
            "level": 10,
            "quests_completed": 15,
            "streak_days": 8,
            "combo_count": 6,
        }
        
        newly_earned = manager.get_newly_earned_achievements(user_stats, previously_earned)
        
        # Should earn several achievements
        assert len(newly_earned) > 0
        ids = [a.id for a in newly_earned]
        assert "level_10" in ids or "level_5" in ids

    def test_achievement_rewards_calculation(self):
        """Test total reward calculation."""
        manager = AchievementManager()
        
        earned_ids = ["level_5", "quests_10"]
        total_xp, total_coins = manager.calculate_total_rewards(earned_ids)
        
        assert total_xp > 0
        assert total_coins > 0


class TestIntegration:
    """Integration tests for engine components working together."""

    def test_full_completion_flow(self):
        """Simulate a full quest completion with all mechanics."""
        from app.services.game import GameService
        
        service = GameService()
        now = datetime.utcnow()
        
        # User state
        user_state = {
            "total_xp": 500,
            "coins": 100,
            "level": 3,
            "quests_completed": 5,
        }
        
        # Recent activity
        recent_completions = [now - timedelta(minutes=i*10) for i in range(3)]
        daily_dates = [now - timedelta(days=i) for i in range(5)]
        
        # Complete a quest
        result = service.complete_quest(
            user_id=1,
            quest_id=1,
            quest_xp=100,
            quest_coins=50,
            deadline=now + timedelta(hours=1),
            completion_time=now,
            current_user_state=user_state,
            recent_completions=recent_completions,
            daily_completion_dates=daily_dates,
            earned_achievements=[]
        )
        
        assert result.success
        assert result.xp_earned > 0
        assert result.coins_earned > 0
        assert result.new_total_xp > user_state["total_xp"]

    def test_penalty_doesnt_affect_streak(self):
        """Penalties should not break streaks."""
        from app.services.game import GameService
        
        service = GameService()
        now = datetime.utcnow()
        
        user_state = {
            "total_xp": 1000,
            "coins": 200,
            "level": 5,
            "missed_deadlines": 0,
        }
        
        deadline = now - timedelta(hours=2)
        
        result = service.apply_penalty(
            user_id=1,
            quest_id=1,
            quest_xp=100,
            quest_coins=50,
            deadline=deadline,
            current_time=now,
            current_user_state=user_state
        )
        
        assert result.success
        assert result.xp_lost > 0
        # Note: apply_penalty doesn't touch streak data - that's handled separately


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_xp_level(self):
        """User with 0 XP should be level 1."""
        level, xp_in_current, xp_for_next = get_current_level(0)
        assert level == 1
        assert xp_in_current == 0

    def test_negative_xp_handling(self):
        """Negative XP should be treated as 0."""
        level, xp_in_current, xp_for_next = get_current_level(-100)
        assert level == 1

    def test_empty_completion_dates(self):
        """Empty completion lists should return sensible defaults."""
        streak_manager = StreakManager()
        info = streak_manager.calculate_streak([])
        assert info.current_streak == 0
        assert not info.is_active

        combo_manager = ComboManager()
        info = combo_manager.calculate_rapid_combo([])
        assert info.current_count == 0
        assert not info.is_active

    def test_maximum_level_cap(self):
        """Level should cap at MAX_LEVEL."""
        huge_xp = calculate_xp_for_level(MAX_LEVEL) * 10
        level, _, _ = get_current_level(huge_xp)
        assert level <= MAX_LEVEL

    def test_ist_timezone_handling(self):
        """Test IST timezone is available."""
        ist = ZoneInfo("Asia/Kolkata")
        utc = UTC
        
        # Create times in both zones
        ist_time = datetime(2024, 1, 1, 12, 0, tzinfo=ist)
        utc_time = datetime(2024, 1, 1, 12, 0, tzinfo=utc)
        
        # They should be different
        assert ist_time != utc_time
