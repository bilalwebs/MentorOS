"""
schemas/profile.py
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProfileBase(BaseModel):
    full_name: str
    bio: str | None = None
    target_role: str | None = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    # All fields optional — PATCH-style partial update.
    full_name: str | None = None
    bio: str | None = None
    target_role: str | None = None


class ProfileRead(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
