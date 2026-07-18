"""
schemas/career_goal.py
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.mixins import GoalStatus


class CareerGoalCreate(BaseModel):
    goal_text: str


class CareerGoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    goal_text: str
    status: GoalStatus
    superseded_by_id: int | None
    created_at: datetime
