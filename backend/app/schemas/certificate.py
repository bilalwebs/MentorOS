"""
schemas/certificate.py
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class CertificateCreate(BaseModel):
    title: str
    issuer: str | None = None
    date_earned: date | None = None


class CertificateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    issuer: str | None
    date_earned: date | None
    created_at: datetime
