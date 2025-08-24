from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List
from datetime import date, datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.point_record import PointRecord, PointType
from app.schemas.point import PointRecordResponse, PointSummary, RewardItem, ExchangeRequest
from app.services.point_service import PointService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/points", tags=["Points & Rewards"])

# Predefined reward items
REWARD_ITEMS = [
    RewardItem(
        id="badge_bronze",
        name="Bronze Badge",
        description="A bronze achievement badge",
        cost=100,
        category="badge",
        icon="🥉"
    ),
    RewardItem(
        id="badge_silver",
        name="Silver Badge",
        description="A silver achievement badge",
        cost=250,
        category="badge",
        icon="🥈"
    ),
    RewardItem(
        id="badge_gold",
        name="Gold Badge",
        description="A gold achievement badge",
        cost=500,
        category="badge",
        icon="🥇"
    ),
    RewardItem(
        id="theme_dark",
        name="Dark Theme",
        description="Unlock dark theme for the app",
        cost=150,
        category="theme",
        icon="🌙"
    ),
    RewardItem(
        id="theme_nature",
        name="Nature Theme",
        description="Beautiful nature-themed interface",
        cost=200,
        category="theme",
        icon="🌿"
    ),
    RewardItem(
        id="avatar_frame_gold",
        name="Golden Avatar Frame",
        description="Exclusive golden frame for your avatar",
        cost=300,
        category="avatar",
        icon="👑"
    ),
    RewardItem(
        id="title_master",
        name="Habit Master Title",
        description="Special title for dedicated users",
        cost=1000,
        category="title",
        icon="🏆"
    )
]


@router.get("/summary", response_model=PointSummary)
async def get_point_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's point summary"""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # Points earned today
    earned_today = db.query(func.sum(PointRecord.points)).filter(
        and_(
            PointRecord.user_id == current_user.id,
            PointRecord.type == PointType.earn,
            func.date(PointRecord.created_at) == today
        )
    ).scalar() or 0
    
    # Points earned this week
    earned_this_week = db.query(func.sum(PointRecord.points)).filter(
        and_(
            PointRecord.user_id == current_user.id,
            PointRecord.type == PointType.earn,
            func.date(PointRecord.created_at) >= week_start
        )
    ).scalar() or 0
    
    # Points earned this month
    earned_this_month = db.query(func.sum(PointRecord.points)).filter(
        and_(
            PointRecord.user_id == current_user.id,
            PointRecord.type == PointType.earn,
            func.date(PointRecord.created_at) >= month_start
        )
    ).scalar() or 0
    
    return PointSummary(
        total_points=current_user.points,
        earned_today=earned_today,
        earned_this_week=earned_this_week,
        earned_this_month=earned_this_month
    )


@router.get("/history", response_model=List[PointRecordResponse])
async def get_point_history(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's point transaction history"""
    records = db.query(PointRecord).filter(
        PointRecord.user_id == current_user.id
    ).order_by(PointRecord.created_at.desc()).offset(offset).limit(limit).all()
    
    return [PointRecordResponse.from_orm(record) for record in records]


@router.get("/rewards", response_model=List[RewardItem])
async def get_available_rewards():
    """Get available reward items"""
    return REWARD_ITEMS


@router.post("/exchange")
async def exchange_reward(
    exchange_data: ExchangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exchange points for rewards"""
    # Find reward item
    reward = None
    for item in REWARD_ITEMS:
        if item.id == exchange_data.reward_id:
            reward = item
            break
    
    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reward not found"
        )
    
    # Check if user has enough points
    if current_user.points < reward.cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient points"
        )
    
    # Process exchange
    point_service = PointService(db)
    success = point_service.spend_points(
        current_user.id,
        reward.cost,
        f"exchange_{reward.id}"
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to process exchange"
        )
    
    return {
        "message": f"Successfully exchanged {reward.name}",
        "reward": reward,
        "remaining_points": current_user.points - reward.cost
    }
