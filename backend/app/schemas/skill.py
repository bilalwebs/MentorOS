"""
schemas/skill.py
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.mixins import SkillLevel


class SkillCreate(BaseModel):
    name: str
    level: SkillLevel = SkillLevel.BEGINNER


class SkillRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    level: SkillLevel
    source: str
    created_at: datetime
