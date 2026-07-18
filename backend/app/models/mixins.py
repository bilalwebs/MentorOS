"""
models/mixins.py

Shared building blocks for ORM models:
- TimestampMixin: created_at / updated_at columns, used by almost every table.
- Enums: kept here (not scattered per-model) so status values used across
  multiple tables (e.g. "active"/"superseded") stay consistent and are easy
  to find in one place.
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column


def utcnow() -> datetime:
    """Timezone-aware UTC now — avoids naive-datetime bugs across SQLite/Postgres."""
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Adds created_at / updated_at to any model that inherits it."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class SkillLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class GoalStatus(str, enum.Enum):
    ACTIVE = "active"
    ACHIEVED = "achieved"
    SUPERSEDED = "superseded"  # replaced by a newer goal (memory contradiction case)


class MemoryStatus(str, enum.Enum):
    ACTIVE = "active"          # eligible for retrieval
    SUPERSEDED = "superseded"  # replaced by newer info, kept for the timeline/audit trail
    ARCHIVED = "archived"      # decayed below threshold, excluded from retrieval


class MemoryType(str, enum.Enum):
    PROFILE = "profile"
    SKILL = "skill"
    PROJECT = "project"
    CAREER_GOAL = "career_goal"
    RESUME = "resume"
    CERTIFICATE = "certificate"
    LEARNING_HISTORY = "learning_history"
    AI_INSIGHT = "ai_insight"
