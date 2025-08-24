from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.models.point_record import PointType


class PointRecordResponse(BaseModel):
    id: int
    user_id: int
    points: int
    type: PointType
    reason: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class PointSummary(BaseModel):
    total_points: int
    earned_today: int
    earned_this_week: int
    earned_this_month: int


class RewardItem(BaseModel):
    id: str
    name: str
    description: str
    cost: int
    category: str
    icon: str


class ExchangeRequest(BaseModel):
    reward_id: str
