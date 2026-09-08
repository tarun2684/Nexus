"""Time management and deadline tracking for Nexus."""

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class DeadlineStatus(Enum):
    """Status of a quest deadline."""
    PENDING = "pending"
    WARNING = "warning"  # Less than 24 hours remaining
    OVERDUE = "overdue"
    COMPLETED = "completed"


@dataclass
class TimeInfo:
    """Information about time remaining for a quest."""
    deadline: datetime
    status: DeadlineStatus
    hours_remaining: float
    is_urgent: bool


class TimeManager:
    """Manages time-based calculations and deadline tracking."""
    
    WARNING_THRESHOLD_HOURS = 24  # Show warning when less than this remains
    
    def __init__(self, current_time: Optional[datetime] = None):
        """
        Initialize TimeManager.
        
        Args:
            current_time: Override for current time (useful for testing)
        """
        self._current_time = current_time
    
    @property
    def now(self) -> datetime:
        """Get current time (real or overridden)."""
        return self._current_time or datetime.utcnow()
    
    def calculate_hours_remaining(self, deadline: datetime) -> float:
        """
        Calculate hours remaining until deadline.
        
        Args:
            deadline: The deadline datetime
            
        Returns:
            Hours remaining (can be negative if overdue)
        """
        delta = deadline - self.now
        return delta.total_seconds() / 3600
    
    def get_deadline_status(self, deadline: datetime) -> DeadlineStatus:
        """
        Determine the status of a deadline.
        
        Args:
            deadline: The deadline datetime
            
        Returns:
            DeadlineStatus enum value
        """
        hours_left = self.calculate_hours_remaining(deadline)
        
        if hours_left <= 0:
            return DeadlineStatus.OVERDUE
        elif hours_left < self.WARNING_THRESHOLD_HOURS:
            return DeadlineStatus.WARNING
        else:
            return DeadlineStatus.PENDING
    
    def get_time_info(self, deadline: datetime, is_completed: bool = False) -> TimeInfo:
        """
        Get comprehensive time information for a deadline.
        
        Args:
            deadline: The deadline datetime
            is_completed: Whether the quest is already completed
            
        Returns:
            TimeInfo dataclass with all time-related details
        """
        if is_completed:
            return TimeInfo(
                deadline=deadline,
                status=DeadlineStatus.COMPLETED,
                hours_remaining=0,
                is_urgent=False
            )
        
        hours_remaining = self.calculate_hours_remaining(deadline)
        status = self.get_deadline_status(deadline)
        is_urgent = status in (DeadlineStatus.WARNING, DeadlineStatus.OVERDUE)
        
        return TimeInfo(
            deadline=deadline,
            status=status,
            hours_remaining=max(0, hours_remaining),
            is_urgent=is_urgent
        )
    
    def is_overdue(self, deadline: datetime) -> bool:
        """Check if a deadline has passed."""
        return self.now > deadline
    
    def is_urgent(self, deadline: datetime) -> bool:
        """Check if a deadline is urgent (less than 24 hours)."""
        hours_left = self.calculate_hours_remaining(deadline)
        return 0 < hours_left < self.WARNING_THRESHOLD_HOURS
    
    def calculate_penalty_multiplier(self, deadline: datetime, completion_time: Optional[datetime] = None) -> float:
        """
        Calculate penalty multiplier based on how late a quest is completed.
        
        Penalty increases over time:
        - On time: 1.0 (no penalty)
        - Within 24 hours late: 1.5x
        - Within 48 hours late: 2.0x
        - More than 48 hours late: 3.0x
        
        Args:
            deadline: The original deadline
            completion_time: When the quest was completed (defaults to now)
            
        Returns:
            Penalty multiplier (1.0 = no penalty)
        """
        if completion_time is None:
            completion_time = self.now
        
        if completion_time <= deadline:
            return 1.0  # No penalty for on-time completion
        
        hours_late = (completion_time - deadline).total_seconds() / 3600
        
        if hours_late <= 24:
            return 1.5
        elif hours_late <= 48:
            return 2.0
        else:
            return 3.0
    
    def format_time_remaining(self, deadline: datetime) -> str:
        """
        Format time remaining in a human-readable way.
        
        Args:
            deadline: The deadline datetime
            
        Returns:
            Human-readable string (e.g., "2 hours", "1 day", "Overdue by 3 hours")
        """
        hours_left = self.calculate_hours_remaining(deadline)
        
        if hours_left <= 0:
            hours_overdue = abs(hours_left)
            if hours_overdue < 1:
                minutes = int(hours_overdue * 60)
                return f"Overdue by {minutes}m"
            elif hours_overdue < 24:
                return f"Overdue by {int(hours_overdue)}h"
            else:
                days = int(hours_overdue / 24)
                return f"Overdue by {days}d"
        
        if hours_left < 1:
            minutes = int(hours_left * 60)
            return f"{minutes}m"
        elif hours_left < 24:
            return f"{int(hours_left)}h"
        else:
            days = int(hours_left / 24)
            hours = int(hours_left % 24)
            if days == 1:
                return f"1d {hours}h" if hours > 0 else "1d"
            else:
                return f"{days}d {hours}h" if hours > 0 else f"{days}d"
