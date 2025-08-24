from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.habit import Habit, HabitStatus
from app.models.checkin import Checkin
from app.schemas.checkin import CheckinCreate, CheckinResponse, MakeupCheckinRequest
from app.services.point_service import PointService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/checkins", tags=["Check-ins"])


@router.get("/", response_model=List[CheckinResponse])
async def get_checkins(
    habit_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get check-in records with optional filters"""
    query = db.query(Checkin).filter(Checkin.user_id == current_user.id)
    
    if habit_id:
        query = query.filter(Checkin.habit_id == habit_id)
    
    if start_date:
        query = query.filter(Checkin.checkin_date >= start_date)
    
    if end_date:
        query = query.filter(Checkin.checkin_date <= end_date)
    
    checkins = query.order_by(Checkin.checkin_date.desc()).all()
    return [CheckinResponse.from_orm(checkin) for checkin in checkins]


@router.post("/", response_model=CheckinResponse)
async def create_checkin(
    checkin_data: CheckinCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new check-in"""
    # Verify habit belongs to user
    habit = db.query(Habit).filter(
        Habit.id == checkin_data.habit_id,
        Habit.user_id == current_user.id,
        Habit.status == HabitStatus.active
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    # Check if already checked in for this date
    existing_checkin = db.query(Checkin).filter(
        and_(
            Checkin.habit_id == checkin_data.habit_id,
            Checkin.checkin_date == checkin_data.checkin_date
        )
    ).first()
    
    if existing_checkin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already checked in for this date"
        )
    
    # Create check-in
    checkin = Checkin(
        user_id=current_user.id,
        **checkin_data.dict()
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    
    # Calculate and award points
    point_service = PointService(db)
    points_earned = point_service.calculate_checkin_points(current_user.id, checkin_data.habit_id)
    point_service.add_points(current_user.id, points_earned, "daily_checkin")
    
    return CheckinResponse.from_orm(checkin)


@router.post("/makeup", response_model=CheckinResponse)
async def makeup_checkin(
    makeup_data: MakeupCheckinRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a makeup check-in (costs points)"""
    # Verify habit belongs to user
    habit = db.query(Habit).filter(
        Habit.id == makeup_data.habit_id,
        Habit.user_id == current_user.id,
        Habit.status == HabitStatus.active
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    # Check if makeup date is valid (only allow previous day)
    today = date.today()
    if makeup_data.checkin_date >= today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only makeup previous days"
        )
    
    if makeup_data.checkin_date < today - timedelta(days=1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only makeup yesterday's check-in"
        )
    
    # Check if already checked in for this date
    existing_checkin = db.query(Checkin).filter(
        and_(
            Checkin.habit_id == makeup_data.habit_id,
            Checkin.checkin_date == makeup_data.checkin_date
        )
    ).first()
    
    if existing_checkin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already checked in for this date"
        )
    
    # Check if user has enough points
    makeup_cost = 20
    point_service = PointService(db)
    
    if current_user.points < makeup_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient points for makeup check-in"
        )
    
    # Spend points
    if not point_service.spend_points(current_user.id, makeup_cost, "makeup_checkin"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to process point transaction"
        )
    
    # Create makeup check-in
    checkin = Checkin(
        user_id=current_user.id,
        habit_id=makeup_data.habit_id,
        checkin_date=makeup_data.checkin_date,
        is_makeup=True
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    
    return CheckinResponse.from_orm(checkin)


@router.get("/calendar/{habit_id}")
async def get_checkin_calendar(
    habit_id: int,
    year: int,
    month: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get check-in calendar for a specific habit and month"""
    # Verify habit belongs to user
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    # Get checkins for the month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    checkins = db.query(Checkin).filter(
        and_(
            Checkin.habit_id == habit_id,
            Checkin.checkin_date >= start_date,
            Checkin.checkin_date <= end_date
        )
    ).all()
    
    # Format calendar data
    calendar_data = {}
    for checkin in checkins:
        calendar_data[checkin.checkin_date.isoformat()] = {
            "checked_in": True,
            "is_makeup": checkin.is_makeup,
            "note": checkin.note,
            "image": checkin.image
        }
    
    return {
        "habit_id": habit_id,
        "year": year,
        "month": month,
        "calendar": calendar_data
    }
