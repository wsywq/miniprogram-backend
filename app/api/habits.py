from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import date, timedelta
from app.database import get_db
from app.models.user import User
from app.models.habit import Habit, HabitStatus
from app.models.checkin import Checkin
from app.schemas.habit import HabitCreate, HabitUpdate, HabitResponse, HabitWithStats
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/habits", tags=["Habits"])


@router.get("/", response_model=List[HabitWithStats])
async def get_habits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's habits with statistics"""
    habits = db.query(Habit).filter(
        Habit.user_id == current_user.id,
        Habit.status == HabitStatus.active
    ).all()
    
    habits_with_stats = []
    for habit in habits:
        # Calculate statistics
        total_checkins = db.query(Checkin).filter(Checkin.habit_id == habit.id).count()
        
        # Calculate current streak
        current_streak = calculate_current_streak(db, habit.id)
        
        # Calculate completion rate (last 30 days)
        thirty_days_ago = date.today() - timedelta(days=30)
        total_days = 30
        checkin_days = db.query(Checkin).filter(
            Checkin.habit_id == habit.id,
            Checkin.checkin_date >= thirty_days_ago
        ).count()
        completion_rate = (checkin_days / total_days) * 100 if total_days > 0 else 0
        
        habit_data = HabitResponse.from_orm(habit)
        habits_with_stats.append(HabitWithStats(
            **habit_data.dict(),
            total_checkins=total_checkins,
            current_streak=current_streak,
            completion_rate=completion_rate
        ))
    
    return habits_with_stats


@router.post("/", response_model=HabitResponse)
async def create_habit(
    habit_data: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new habit"""
    habit = Habit(
        user_id=current_user.id,
        **habit_data.dict()
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return HabitResponse.from_orm(habit)


@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific habit"""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    return HabitResponse.from_orm(habit)


@router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: int,
    habit_data: HabitUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a habit"""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    # Update fields
    for field, value in habit_data.dict(exclude_unset=True).items():
        setattr(habit, field, value)
    
    db.commit()
    db.refresh(habit)
    return HabitResponse.from_orm(habit)


@router.delete("/{habit_id}")
async def delete_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a habit (soft delete)"""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    habit.status = HabitStatus.deleted
    db.commit()
    
    return {"message": "Habit deleted successfully"}


def calculate_current_streak(db: Session, habit_id: int) -> int:
    """Calculate current streak for a habit"""
    today = date.today()
    streak = 0
    current_date = today
    
    while True:
        checkin = db.query(Checkin).filter(
            Checkin.habit_id == habit_id,
            Checkin.checkin_date == current_date
        ).first()
        
        if checkin:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    return streak
