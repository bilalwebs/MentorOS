"""
schemas/ai_insight.py
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AIInsightRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    insight_type: str
    content: str
    generated_at: datetime
