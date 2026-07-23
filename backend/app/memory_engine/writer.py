"""
memory_engine/writer.py

MemoryWriter is the ONLY code path that creates or updates a Memory row.
Centralizing this (rather than letting services write memories ad hoc)
guarantees every memory gets an embedding, an importance score, and a
consistent SQL+vector write — the dual-store sync the architecture
depends on.

Write order is deliberate: SQL first (source of truth), then vector store.
If the vector write fails, the SQL row still exists and is simply
unsearchable-by-similarity until a retry — degraded, not lost. The
reverse order risks an orphaned vector with no backing record.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.llm_provider import LLMProvider
from app.memory_engine import vector_store
from app.memory_engine.importance import initial_importance
from app.models.memory import Memory
from app.models.mixins import MemoryStatus, MemoryType


class MemoryWriter:
    def __init__(self, db: Session, llm: LLMProvider):
        self.db = db
        self.llm = llm

    def write(
        self,
        user_id: int,
        memory_type: MemoryType,
        content_text: str,
        source_table: str | None = None,
        source_id: int | None = None,
    ) -> Memory:
        """
        Create a new memory: embed the content, assign initial importance,
        write to SQL, then write the matching vector to the vector store.
        """
        chroma_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        memory = Memory(
            user_id=user_id,
            memory_type=memory_type,
            content_text=content_text,
            source_table=source_table,
            source_id=source_id,
            importance_score=initial_importance(memory_type),
            status=MemoryStatus.ACTIVE,
            chroma_id=chroma_id,
            created_at=now,
            updated_at=now,
            last_accessed_at=now,
        )
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)

        try:
            embedding = self.llm.embed([content_text])[0]
            vector_store.upsert_memory_vector(
                chroma_id=chroma_id,
                embedding=embedding,
                user_id=user_id,
                memory_id=memory.id,
                memory_type=memory_type.value,
                status=MemoryStatus.ACTIVE.value,
            )
        except Exception:
            import logging
            logging.getLogger(__name__).exception(
                "Vector write failed for memory_id=%s — memory saved in SQL only.", memory.id
            )

        return memory

    def supersede(self, old_memory: Memory, new_content_text: str) -> Memory:
        """
        The explicit-contradiction forgetting path: mark the old memory
        SUPERSEDED (never deleted — it stays visible in the timeline) and
        write a new active memory of the same type, linked via source
        pointers back to the same origin record.
        """
        old_memory.status = MemoryStatus.SUPERSEDED
        old_memory.updated_at = datetime.now(timezone.utc)
        self.db.commit()

        try:
            vector_store.update_memory_status(old_memory.chroma_id, MemoryStatus.SUPERSEDED.value)
        except Exception:
            import logging
            logging.getLogger(__name__).exception(
                "Vector status update failed for memory_id=%s", old_memory.id
            )

        new_memory = self.write(
            user_id=old_memory.user_id,
            memory_type=old_memory.memory_type,
            content_text=new_content_text,
            source_table=old_memory.source_table,
            source_id=old_memory.source_id,
        )

        old_memory.superseded_by_id = new_memory.id
        self.db.commit()

        return new_memory

    def archive(self, memory: Memory) -> None:
        """Decay-driven forgetting: exclude from retrieval without deleting."""
        memory.status = MemoryStatus.ARCHIVED
        memory.updated_at = datetime.now(timezone.utc)
        self.db.commit()

        try:
            vector_store.update_memory_status(memory.chroma_id, MemoryStatus.ARCHIVED.value)
        except Exception:
            import logging
            logging.getLogger(__name__).exception(
                "Vector status update failed for memory_id=%s", memory.id
            )
