"""
services/memory_service.py

Thin service layer over the memory engine for router use. Two read-side
concerns live here that don't belong in MemoryWriter/MemoryRetriever
themselves:
- get_timeline(): returns ALL memories (active + superseded + archived)
  for a user, ordered by recency — this is what powers the Memory
  Timeline UI, which is the visible proof that memory persists AND
  evolves (goals getting superseded, low-value facts getting archived).
- delete_memory(): a manual "forget this" action, useful both as a real
  feature (student wants an old fact gone) and as a demo control judges
  can trigger themselves.
"""

import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.llm_provider import LLMProvider
from app.memory_engine import vector_store
from app.memory_engine.decay import run_decay_for_user
from app.memory_engine.writer import MemoryWriter
from app.models.memory import Memory

logger = logging.getLogger(__name__)


def get_timeline(db: Session, user_id: int) -> list[Memory]:
    return (
        db.query(Memory)
        .filter(Memory.user_id == user_id)
        .order_by(Memory.created_at.desc())
        .all()
    )


def delete_memory(db: Session, user_id: int, memory_id: int) -> None:
    memory = db.query(Memory).filter(Memory.id == memory_id, Memory.user_id == user_id).first()
    if not memory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found.")

    vector_store.delete_memory_vector(memory.chroma_id)
    db.delete(memory)
    db.commit()


def run_login_decay(db: Session, user_id: int, llm: LLMProvider) -> dict:
    """
    Called from the login flow. Wrapped defensively: a decay-job failure
    (e.g. transient Qwen/embedding issue) should never block a student
    from logging in — memory maintenance is important but not critical-path.
    """
    try:
        writer = MemoryWriter(db, llm)
        return run_decay_for_user(db, user_id, writer)
    except Exception:
        logger.exception("Memory decay pass failed for user_id=%s; continuing login.", user_id)
        return {"decayed": 0, "archived": 0, "error": "decay_pass_failed"}
