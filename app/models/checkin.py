from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Checkin(Base):
    __tablename__ = "checkins"
    
    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    checkin_date = Column(Date, nullable=False)
    checkin_time = Column(DateTime, default=func.now())
    note = Column(Text)
    image = Column(String(200))
    is_makeup = Column(Boolean, default=False)
    
    # Unique constraint to prevent duplicate checkins for same habit on same date
    __table_args__ = (UniqueConstraint('habit_id', 'checkin_date', name='unique_habit_date_checkin'),)
    
    # Relationships
    habit = relationship("Habit", back_populates="checkins")
    user = relationship("User", back_populates="checkins")
