"""
schemas/user.py

Pydantic schemas define the API's request/response shape — deliberately
different from the ORM model. Most importantly: `UserRead` never includes
`hashed_password`. This isn't just convention, it's the actual mechanism
that prevents password hashes from ever leaking into an API response,
even by accident.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # allows .model_validate(orm_object)

    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
