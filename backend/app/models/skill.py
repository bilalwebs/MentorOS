"""
models/skill.py
"""

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import SkillLevel, TimestampMixin


class Skill(Base, TimestampMixin):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[SkillLevel] = mapped_column(Enum(SkillLevel), default=SkillLevel.BEGINNER)

    # Where this skill came from — lets the UI/AI distinguish self-reported
    # skills from ones the AI extracted out of a resume.
    source: Mapped[str] = mapped_column(String(50), default="manual")  # "manual" | "resume_extraction"

    user: Mapped["User"] = relationship(back_populates="skills")
