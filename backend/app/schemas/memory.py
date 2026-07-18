"""
schemas/memory.py

`MemoryRead` is what powers the Memory Timeline UI (Module 8+) — it's
deliberately flat and simple since the frontend just needs to list/sort/
filter these, not reconstruct anything.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.mixins import MemoryStatus, MemoryType


class MemoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    memory_type: MemoryType
    content_text: str
    importance_score: float
    status: MemoryStatus
    source_table: str | None
    superseded_by_id: int | None
    created_at: datetime
    last_accessed_at: datetime
