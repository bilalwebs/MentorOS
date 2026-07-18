"""
schemas/resume.py
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    parsed_at: datetime | None
    created_at: datetime
