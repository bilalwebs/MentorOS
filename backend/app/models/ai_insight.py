"""
models/ai_insight.py

Every AI-generated recommendation (roadmap, skill-gap analysis, etc.) is
stored here AND written back into the memories table (as a MemoryType.AI_INSIGHT
memory) by the recommendation service. Storing it in both places serves
different purposes:
  - ai_insights: full-fidelity record (for the dashboard "insight history" view)
  - memories: makes past insights retrievable as context for FUTURE AI calls,
    which is what allows the AI to say "I already suggested X" instead of
    repeating itself.

`based_on_memory_ids` is stored as a comma-separated string of memory ids
for the same portability reason as Project.tech_stack — no native array
type dependency, works identically on SQLite and Postgres.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import utcnow


class AIInsight(Base):
    __tablename__ = "ai_insights"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    insight_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "roadmap" | "skill_gap" | "project_recommendation"
    content: Mapped[str] = mapped_column(Text, nullable=False)

    based_on_memory_ids: Mapped[str | None] = mapped_column(String(500), nullable=True)  # comma-separated ids

    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="ai_insights")
