from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class PointType(enum.Enum):
    earn = "earn"
    spend = "spend"


class PointRecord(Base):
    __tablename__ = "point_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    points = Column(Integer, nullable=False)
    type = Column(Enum(PointType), nullable=False)
    reason = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="point_records")
