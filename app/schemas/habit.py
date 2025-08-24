from pydantic import BaseModel
from typing import Optional
from datetime import datetime, time
from app.models.habit import HabitStatus, HabitFrequency


class HabitBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    category: Optional[str] = None
    frequency: HabitFrequency = HabitFrequency.daily
    reminder_time: Optional[time] = None


class HabitCreate(HabitBase):
    pass


class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    category: Optional[str] = None
    frequency: Optional[HabitFrequency] = None
    reminder_time: Optional[time] = None
    status: Optional[HabitStatus] = None


class HabitResponse(HabitBase):
    id: int
    user_id: int
    status: HabitStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class HabitWithStats(HabitResponse):
    total_checkins: int
    current_streak: int
    completion_rate: float
