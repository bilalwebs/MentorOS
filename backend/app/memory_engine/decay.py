"""
memory_engine/decay.py

The decay pass: time-based forgetting. Run on-demand (triggered on login,
per the Phase 2 plan — simplest reliable trigger for a hackathon, no
scheduler/cron infrastructure needed) rather than via a background worker.

Every ACTIVE memory for a user gets its importance recalculated based on
idle time since last access; anything that drops below the archive
threshold is archived (excluded from retrieval, kept for the timeline).
"""

from sqlalchemy.orm import Session

from app.memory_engine.importance import decayed_importance, should_archive
from app.memory_engine.writer import MemoryWriter
from app.models.memory import Memory
from app.models.mixins import MemoryStatus


def run_decay_for_user(db: Session, user_id: int, writer: MemoryWriter) -> dict:
    """
    Returns a small summary dict so callers (e.g. the login endpoint) can
    surface "N memories decayed, M archived" — useful for the demo's
    memory-timeline story, not just a silent background effect.
    """
    active_memories = (
        db.query(Memory)
        .filter(Memory.user_id == user_id, Memory.status == MemoryStatus.ACTIVE)
        .all()
    )

    decayed_count = 0
    archived_count = 0

    for memory in active_memories:
        new_importance = decayed_importance(memory.importance_score, memory.last_accessed_at)
        if new_importance != memory.importance_score:
            memory.importance_score = new_importance
            decayed_count += 1

        if should_archive(new_importance):
            writer.archive(memory)
            archived_count += 1

    db.commit()
    return {"decayed": decayed_count, "archived": archived_count}
