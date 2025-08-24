from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import date


class DailyStats(BaseModel):
    date: date
    total_checkins: int
    habits_completed: int
    total_habits: int
    completion_rate: float


class HabitStats(BaseModel):
    habit_id: int
    habit_name: str
    total_checkins: int
    current_streak: int
    longest_streak: int
    completion_rate: float
    last_checkin_date: date = None


class UserStatistics(BaseModel):
    total_habits: int
    active_habits: int
    total_checkins: int
    current_longest_streak: int
    total_points: int
    monthly_completion_rate: float
    weekly_completion_rate: float


class MonthlyCalendar(BaseModel):
    year: int
    month: int
    calendar_data: Dict[str, Dict[str, Any]]  # date -> checkin info


class TrendData(BaseModel):
    labels: List[str]
    datasets: List[Dict[str, Any]]
