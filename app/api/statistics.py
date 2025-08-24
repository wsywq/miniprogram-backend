from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from typing import List, Dict, Any
from datetime import date, datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.habit import Habit, HabitStatus
from app.models.checkin import Checkin
from app.schemas.statistics import UserStatistics, HabitStats, DailyStats, TrendData
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("/overview", response_model=UserStatistics)
async def get_user_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's overall statistics"""
    # Total and active habits
    total_habits = db.query(Habit).filter(Habit.user_id == current_user.id).count()
    active_habits = db.query(Habit).filter(
        Habit.user_id == current_user.id,
        Habit.status == HabitStatus.active
    ).count()
    
    # Total checkins
    total_checkins = db.query(Checkin).filter(Checkin.user_id == current_user.id).count()
    
    # Current longest streak across all habits
    current_longest_streak = get_longest_current_streak(db, current_user.id)
    
    # Monthly completion rate
    monthly_rate = calculate_monthly_completion_rate(db, current_user.id)
    
    # Weekly completion rate
    weekly_rate = calculate_weekly_completion_rate(db, current_user.id)
    
    return UserStatistics(
        total_habits=total_habits,
        active_habits=active_habits,
        total_checkins=total_checkins,
        current_longest_streak=current_longest_streak,
        total_points=current_user.points,
        monthly_completion_rate=monthly_rate,
        weekly_completion_rate=weekly_rate
    )


@router.get("/habits", response_model=List[HabitStats])
async def get_habit_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics for all user habits"""
    habits = db.query(Habit).filter(
        Habit.user_id == current_user.id,
        Habit.status == HabitStatus.active
    ).all()
    
    habit_stats = []
    for habit in habits:
        # Total checkins
        total_checkins = db.query(Checkin).filter(Checkin.habit_id == habit.id).count()
        
        # Current streak
        current_streak = calculate_habit_current_streak(db, habit.id)
        
        # Longest streak
        longest_streak = calculate_habit_longest_streak(db, habit.id)
        
        # Completion rate (last 30 days)
        completion_rate = calculate_habit_completion_rate(db, habit.id, 30)
        
        # Last checkin date
        last_checkin = db.query(Checkin).filter(
            Checkin.habit_id == habit.id
        ).order_by(desc(Checkin.checkin_date)).first()
        
        habit_stats.append(HabitStats(
            habit_id=habit.id,
            habit_name=habit.name,
            total_checkins=total_checkins,
            current_streak=current_streak,
            longest_streak=longest_streak,
            completion_rate=completion_rate,
            last_checkin_date=last_checkin.checkin_date if last_checkin else None
        ))
    
    return habit_stats


@router.get("/daily")
async def get_daily_statistics(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily statistics for the last N days"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    # Get active habits count
    active_habits_count = db.query(Habit).filter(
        Habit.user_id == current_user.id,
        Habit.status == HabitStatus.active
    ).count()
    
    daily_stats = []
    current_date = start_date
    
    while current_date <= end_date:
        # Get checkins for this date
        daily_checkins = db.query(Checkin).filter(
            and_(
                Checkin.user_id == current_user.id,
                Checkin.checkin_date == current_date
            )
        ).count()
        
        completion_rate = (daily_checkins / active_habits_count * 100) if active_habits_count > 0 else 0
        
        daily_stats.append(DailyStats(
            date=current_date,
            total_checkins=daily_checkins,
            habits_completed=daily_checkins,
            total_habits=active_habits_count,
            completion_rate=completion_rate
        ))
        
        current_date += timedelta(days=1)
    
    return daily_stats


@router.get("/trends")
async def get_trend_data(
    period: str = "month",  # week, month, year
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trend data for charts"""
    if period == "week":
        days = 7
    elif period == "month":
        days = 30
    elif period == "year":
        days = 365
    else:
        days = 30
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    # Get daily checkin counts
    daily_data = db.query(
        Checkin.checkin_date,
        func.count(Checkin.id).label('count')
    ).filter(
        and_(
            Checkin.user_id == current_user.id,
            Checkin.checkin_date >= start_date,
            Checkin.checkin_date <= end_date
        )
    ).group_by(Checkin.checkin_date).all()
    
    # Create labels and data arrays
    labels = []
    checkin_counts = []
    
    current_date = start_date
    data_dict = {item.checkin_date: item.count for item in daily_data}
    
    while current_date <= end_date:
        labels.append(current_date.strftime("%m-%d"))
        checkin_counts.append(data_dict.get(current_date, 0))
        current_date += timedelta(days=1)
    
    return TrendData(
        labels=labels,
        datasets=[
            {
                "label": "Daily Check-ins",
                "data": checkin_counts,
                "borderColor": "#4CAF50",
                "backgroundColor": "rgba(76, 175, 80, 0.1)"
            }
        ]
    )


def calculate_habit_current_streak(db: Session, habit_id: int) -> int:
    """Calculate current streak for a specific habit"""
    today = date.today()
    streak = 0
    current_date = today
    
    while True:
        checkin = db.query(Checkin).filter(
            and_(
                Checkin.habit_id == habit_id,
                Checkin.checkin_date == current_date
            )
        ).first()
        
        if checkin:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    return streak


def calculate_habit_longest_streak(db: Session, habit_id: int) -> int:
    """Calculate longest streak for a specific habit"""
    checkins = db.query(Checkin).filter(
        Checkin.habit_id == habit_id
    ).order_by(Checkin.checkin_date).all()
    
    if not checkins:
        return 0
    
    longest_streak = 0
    current_streak = 1
    
    for i in range(1, len(checkins)):
        prev_date = checkins[i-1].checkin_date
        curr_date = checkins[i].checkin_date
        
        if (curr_date - prev_date).days == 1:
            current_streak += 1
        else:
            longest_streak = max(longest_streak, current_streak)
            current_streak = 1
    
    return max(longest_streak, current_streak)


def calculate_habit_completion_rate(db: Session, habit_id: int, days: int) -> float:
    """Calculate completion rate for a habit over the last N days"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    checkin_count = db.query(Checkin).filter(
        and_(
            Checkin.habit_id == habit_id,
            Checkin.checkin_date >= start_date,
            Checkin.checkin_date <= end_date
        )
    ).count()
    
    return (checkin_count / days) * 100


def get_longest_current_streak(db: Session, user_id: int) -> int:
    """Get the longest current streak across all user habits"""
    habits = db.query(Habit).filter(
        Habit.user_id == user_id,
        Habit.status == HabitStatus.active
    ).all()
    
    longest_streak = 0
    for habit in habits:
        streak = calculate_habit_current_streak(db, habit.id)
        longest_streak = max(longest_streak, streak)
    
    return longest_streak


def calculate_monthly_completion_rate(db: Session, user_id: int) -> float:
    """Calculate completion rate for current month"""
    today = date.today()
    first_day = today.replace(day=1)
    
    active_habits = db.query(Habit).filter(
        Habit.user_id == user_id,
        Habit.status == HabitStatus.active
    ).count()
    
    if active_habits == 0:
        return 0.0
    
    total_expected = active_habits * today.day
    total_completed = db.query(Checkin).filter(
        and_(
            Checkin.user_id == user_id,
            Checkin.checkin_date >= first_day,
            Checkin.checkin_date <= today
        )
    ).count()
    
    return (total_completed / total_expected) * 100 if total_expected > 0 else 0.0


def calculate_weekly_completion_rate(db: Session, user_id: int) -> float:
    """Calculate completion rate for current week"""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    
    active_habits = db.query(Habit).filter(
        Habit.user_id == user_id,
        Habit.status == HabitStatus.active
    ).count()
    
    if active_habits == 0:
        return 0.0
    
    days_in_week = (today - week_start).days + 1
    total_expected = active_habits * days_in_week
    total_completed = db.query(Checkin).filter(
        and_(
            Checkin.user_id == user_id,
            Checkin.checkin_date >= week_start,
            Checkin.checkin_date <= today
        )
    ).count()
    
    return (total_completed / total_expected) * 100 if total_expected > 0 else 0.0
