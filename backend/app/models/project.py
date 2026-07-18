"""
models/project.py

`tech_stack` is stored as a simple comma-separated string rather than a
JSON/array column. SQLite has no native array type, and Postgres's ARRAY
type would break the "swap DATABASE_URL and nothing else changes" goal.
The service layer (Module 3+) will handle splitting/joining this into a
list for the API layer, so callers never see the raw string format.
"""

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tech_stack: Mapped[str | None] = mapped_column(String(500), nullable=True)  # comma-separated

    user: Mapped["User"] = relationship(back_populates="projects")
