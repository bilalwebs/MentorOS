"""
models/memory.py

This is the most important table in the project.

Every fact the system "remembers" about a student — regardless of which
feature created it (profile edit, resume parse, AI-generated insight) —
gets a row here. Design decisions worth explaining:

- `content_text`: a human-readable summary of the fact (e.g. "Student
  knows intermediate React, self-reported"). This is what gets embedded
  into ChromaDB. Keeping it as plain text (not raw JSON) makes embeddings
  meaningful for semantic search and makes the memory timeline UI trivial
  to render — no reconstruction/formatting logic needed.

- `source_table` / `source_id`: points back to the origin record (e.g.
  "skills", 42). This is what makes SQL the source of truth: if the
  Chroma embedding is ever lost or corrupted, we can always regenerate
  it from the structured origin record. The vector store is an index,
  not a database.

- `importance_score`: float 0.0-1.0. Starts high on creation, decays over
  time if unused (see memory_engine/decay.py in a later module), and gets
  a small boost each time the memory is actually retrieved and used.

- `status`: ACTIVE / SUPERSEDED / ARCHIVED — see mixins.py. Only ACTIVE
  memories are retrieved for AI context. SUPERSEDED and ARCHIVED are kept
  (not deleted) so the timeline UI can show the full history — this is
  the visible proof of "forgetting" for the demo.

- `chroma_id`: the id of the corresponding vector in ChromaDB. Nullable
  because a memory can theoretically exist in SQL before its embedding
  is generated (e.g. if the embedding call fails, we don't want to lose
  the structured fact).

- `last_accessed_at`: updated whenever this memory is pulled into an AI
  context. Used by both the decay job (idle memories decay) and the
  retrieval scorer (recently used memories get a small relevance boost).
"""

from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import MemoryStatus, MemoryType, TimestampMixin, utcnow


class Memory(Base, TimestampMixin):
    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    memory_type: Mapped[MemoryType] = mapped_column(Enum(MemoryType), nullable=False)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)

    source_table: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    importance_score: Mapped[float] = mapped_column(Float, default=1.0)
    status: Mapped[MemoryStatus] = mapped_column(Enum(MemoryStatus), default=MemoryStatus.ACTIVE)

    chroma_id: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True)

    last_accessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Self-referential: if this memory was superseded, what replaced it.
    superseded_by_id: Mapped[int | None] = mapped_column(ForeignKey("memories.id"), nullable=True)
    superseded_by: Mapped["Memory"] = relationship(remote_side=[id])

    user: Mapped["User"] = relationship(back_populates="memories")
