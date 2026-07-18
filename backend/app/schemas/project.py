"""
schemas/project.py

Note: `tech_stack` is a `list[str]` here even though the ORM model stores
it as a comma-separated string. The service layer (Module 3) converts
between the two, so API consumers (frontend, judges reading /docs) always
see a clean list — the storage detail never leaks through the API.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    title: str
    description: str | None = None
    tech_stack: list[str] = []


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    tech_stack: list[str]
    created_at: datetime
