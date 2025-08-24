from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class CheckinBase(BaseModel):
    checkin_date: date
    note: Optional[str] = None
    image: Optional[str] = None


class CheckinCreate(CheckinBase):
    habit_id: int


class CheckinUpdate(BaseModel):
    note: Optional[str] = None
    image: Optional[str] = None


class CheckinResponse(CheckinBase):
    id: int
    habit_id: int
    user_id: int
    checkin_time: datetime
    is_makeup: bool
    
    class Config:
        from_attributes = True


class MakeupCheckinRequest(BaseModel):
    habit_id: int
    checkin_date: date
