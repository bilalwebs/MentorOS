"""
models/career_goal.py

`superseded_by_id` is a self-referential FK: when a student's goal changes
(e.g. "backend dev" -> "ML engineer"), we don't delete the old goal — we
mark it SUPERSEDED and link it to the new one. This is the concrete,
visible mechanic behind the "memory forgetting via contradiction" flow
described in the memory engine design, and it doubles as a demo feature
(the timeline UI can show "this goal replaced that one").
"""

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import GoalStatus, TimestampMixin


class CareerGoal(Base, TimestampMixin):
    __tablename__ = "career_goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    goal_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[GoalStatus] = mapped_column(Enum(GoalStatus), default=GoalStatus.ACTIVE)

    superseded_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("career_goals.id"), nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="career_goals")
    superseded_by: Mapped["CareerGoal"] = relationship(remote_side=[id])
