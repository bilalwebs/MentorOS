"""
memory_engine/importance.py

Pure, side-effect-free functions implementing the importance/decay math.
Kept separate from writer.py/decay.py (which do the actual DB writes) so
the scoring logic itself is trivially unit-testable and easy to explain
to hackathon judges without wading through ORM code.

Scoring model (deliberately simple and explainable, not ML-based —
appropriate for this scope and easy to defend in a demo Q&A):

  initial_importance:
    base score by memory_type (career goals and resume-derived facts
    start higher than incidental chat-derived notes), since not all
    facts are equally central to who this student is.

  decay (applied per idle week since last_accessed_at):
    importance *= (1 - MEMORY_DECAY_RATE) ^ weeks_idle
    i.e. exponential decay — memories not touched in a while fade
    gradually rather than dropping off a cliff.

  access boost (applied whenever a memory is retrieved/used):
    importance = min(1.0, importance + ACCESS_BOOST)
    i.e. frequently useful memories stay important even as time passes.

  archive threshold:
    importance below MEMORY_ARCHIVE_THRESHOLD -> status becomes ARCHIVED,
    excluding it from future retrieval (but never deleting it — it still
    shows in the memory timeline as a demonstrable "the AI forgot this"
    moment).
"""

from datetime import datetime, timezone

from app.core.config import get_settings
from app.models.mixins import MemoryType

settings = get_settings()

ACCESS_BOOST = 0.05

_BASE_IMPORTANCE_BY_TYPE = {
    MemoryType.CAREER_GOAL: 0.9,
    MemoryType.PROFILE: 0.8,
    MemoryType.RESUME: 0.75,
    MemoryType.SKILL: 0.65,
    MemoryType.PROJECT: 0.6,
    MemoryType.CERTIFICATE: 0.55,
    MemoryType.AI_INSIGHT: 0.5,
    MemoryType.LEARNING_HISTORY: 0.4,
}

DEFAULT_BASE_IMPORTANCE = 0.5


def initial_importance(memory_type: MemoryType) -> float:
    return _BASE_IMPORTANCE_BY_TYPE.get(memory_type, DEFAULT_BASE_IMPORTANCE)


def apply_access_boost(current_importance: float) -> float:
    return min(1.0, current_importance + ACCESS_BOOST)


def decayed_importance(current_importance: float, last_accessed_at: datetime, now: datetime | None = None) -> float:
    """
    Exponential decay based on whole weeks idle since last access.
    Memories accessed within the last week don't decay at all.
    """
    now = now or datetime.now(timezone.utc)
    if last_accessed_at.tzinfo is None:
        last_accessed_at = last_accessed_at.replace(tzinfo=timezone.utc)

    idle_seconds = (now - last_accessed_at).total_seconds()
    idle_weeks = max(0, int(idle_seconds // (7 * 24 * 3600)))

    if idle_weeks == 0:
        return current_importance

    decay_factor = (1 - settings.MEMORY_DECAY_RATE) ** idle_weeks
    return round(current_importance * decay_factor, 4)


def should_archive(importance: float) -> bool:
    return importance < settings.MEMORY_ARCHIVE_THRESHOLD


def composite_retrieval_score(similarity: float, importance: float, recency_boost: float = 0.0) -> float:
    """
    Ranks retrieved memories for the reasoning pipeline. Similarity is the
    dominant signal (relevance to the actual query) — weighted heavily
    enough that a clearly on-topic but "unimportant" memory (e.g. a minor
    skill) still outranks a merely adjacent "important" one (e.g. a career
    goal) when the topical match is real. Importance acts as a tie-breaker
    among comparably-similar results and demotes stale/contradicted-but-
    not-yet-archived facts; it should nudge ranking, not override topical
    relevance. A small optional recency_boost lets very recently added
    memories surface even before they've accumulated access-based importance.
    """
    return (0.80 * similarity) + (0.15 * importance) + (0.05 * recency_boost)
