from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from app.models.user import User
from app.models.checkin import Checkin
from app.models.point_record import PointRecord, PointType


class PointService:
    def __init__(self, db: Session):
        self.db = db
    
    def add_points(self, user_id: int, points: int, reason: str):
        """Add points to user account"""
        # Update user points
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.points += points
            
            # Create point record
            point_record = PointRecord(
                user_id=user_id,
                points=points,
                type=PointType.earn,
                reason=reason
            )
            self.db.add(point_record)
            self.db.commit()
            
            return user.points
        return 0
    
    def spend_points(self, user_id: int, points: int, reason: str) -> bool:
        """Spend points from user account"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.points < points:
            return False
        
        user.points -= points
        
        # Create point record
        point_record = PointRecord(
            user_id=user_id,
            points=-points,
            type=PointType.spend,
            reason=reason
        )
        self.db.add(point_record)
        self.db.commit()
        
        return True
    
    def calculate_checkin_points(self, user_id: int, habit_id: int) -> int:
        """Calculate points for a check-in"""
        base_points = 10  # Base points for daily check-in
        bonus_points = 0
        
        # Calculate current streak
        streak = self._get_current_streak(user_id, habit_id)
        
        # Streak bonuses
        if streak > 0 and streak % 7 == 0:  # Weekly streak bonus
            bonus_points += 50
        if streak > 0 and streak % 30 == 0:  # Monthly streak bonus
            bonus_points += 200
        
        # Check monthly completion rate bonus
        monthly_bonus = self._check_monthly_completion_bonus(user_id)
        bonus_points += monthly_bonus
        
        return base_points + bonus_points
    
    def _get_current_streak(self, user_id: int, habit_id: int) -> int:
        """Get current streak for a habit"""
        today = date.today()
        streak = 0
        current_date = today
        
        while True:
            checkin = self.db.query(Checkin).filter(
                Checkin.user_id == user_id,
                Checkin.habit_id == habit_id,
                Checkin.checkin_date == current_date
            ).first()
            
            if checkin:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak
    
    def _check_monthly_completion_bonus(self, user_id: int) -> int:
        """Check if user deserves monthly completion bonus"""
        today = date.today()
        first_day_of_month = today.replace(day=1)
        
        # Get all user's active habits
        from app.models.habit import Habit, HabitStatus
        habits = self.db.query(Habit).filter(
            Habit.user_id == user_id,
            Habit.status == HabitStatus.active
        ).all()
        
        if not habits:
            return 0
        
        # Check completion rate for current month
        total_expected = len(habits) * today.day
        total_completed = self.db.query(Checkin).filter(
            Checkin.user_id == user_id,
            Checkin.checkin_date >= first_day_of_month,
            Checkin.checkin_date <= today
        ).count()
        
        completion_rate = total_completed / total_expected if total_expected > 0 else 0
        
        # Award bonus if 100% completion rate and it's end of month
        if completion_rate >= 1.0 and today.day >= 28:  # Near end of month
            # Check if bonus already awarded this month
            existing_bonus = self.db.query(PointRecord).filter(
                PointRecord.user_id == user_id,
                PointRecord.reason == "monthly_completion_bonus",
                func.date(PointRecord.created_at) >= first_day_of_month
            ).first()
            
            if not existing_bonus:
                return 300
        
        return 0
