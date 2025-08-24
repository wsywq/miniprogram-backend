from sqlalchemy import Column, Integer, String, Text, Time, Enum, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class HabitStatus(enum.Enum):
    active = "active"
    paused = "paused"
    deleted = "deleted"


class HabitFrequency(enum.Enum):
    daily = "daily"
    weekly = "weekly"
    custom = "custom"


class Habit(Base):
    __tablename__ = "habits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(50))
    category = Column(String(20))
    frequency = Column(Enum(HabitFrequency), default=HabitFrequency.daily)
    reminder_time = Column(Time)
    status = Column(Enum(HabitStatus), default=HabitStatus.active)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="habits")
    checkins = relationship("Checkin", back_populates="habit", cascade="all, delete-orphan")
