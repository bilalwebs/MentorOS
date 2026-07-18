"""
db/base.py

Imports every ORM model so that `Base.metadata` is aware of all tables.

Why this file exists as its own thing:
- `Base` lives in session.py to avoid circular imports (models import Base).
- But table creation (Base.metadata.create_all) and Alembic autogenerate
  need EVERY model imported somewhere before they run, or tables get
  silently skipped.
- Centralizing those imports here means adding a new model is a one-line
  change in exactly one place, not something you have to remember to wire
  into main.py or an Alembic env file.

This module is imported for its side effects (the imports themselves),
not for anything it defines.
"""

from app.db.session import Base  # noqa: F401

from app.models.user import User  # noqa: F401
from app.models.profile import Profile  # noqa: F401
from app.models.skill import Skill  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.certificate import Certificate  # noqa: F401
from app.models.career_goal import CareerGoal  # noqa: F401
from app.models.resume import Resume  # noqa: F401
from app.models.memory import Memory  # noqa: F401
from app.models.ai_insight import AIInsight  # noqa: F401
