"""
memory_engine/retriever.py

MemoryRetriever answers "what should the AI remember for this query?" —
the read-side counterpart to MemoryWriter. Two-step process:
1. Chroma similarity search (metadata-filtered to this user, active only)
2. Re-rank by composite_retrieval_score (similarity + importance), since
   raw similarity alone would let a stale-but-topically-similar memory
   outrank a highly important one.

Retrieval also applies the access boost (Memory.importance_score creeps
up when something is actually used) — this is what keeps frequently
relevant memories from decaying even as time passes.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.llm_provider import LLMProvider
from app.core.config import get_settings
from app.memory_engine import chroma_client
from app.memory_engine.importance import apply_access_boost, composite_retrieval_score
from app.models.memory import Memory
from app.models.mixins import MemoryStatus

settings = get_settings()


def _distance_to_similarity(distance: float) -> float:
    """
    The Chroma collection is explicitly configured with `hnsw:space: cosine`
    (see chroma_client.get_chroma_collection), where Chroma defines
    distance = 1 - cosine_similarity. So this conversion is exact, not an
    approximation — similarity = 1 - distance, clamped to [0, 1] to guard
    against floating-point drift at the boundary.
    """
    return max(0.0, min(1.0, 1.0 - distance))


class MemoryRetriever:
    def __init__(self, db: Session, llm: LLMProvider):
        self.db = db
        self.llm = llm

    def retrieve(self, user_id: int, query_text: str, top_k: int | None = None) -> list[Memory]:
        top_k = top_k or settings.MEMORY_RETRIEVAL_TOP_K

        query_embedding = self.llm.embed([query_text])[0]
        chroma_hits = chroma_client.query_similar(
            embedding=query_embedding, user_id=user_id, top_k=top_k, active_only=True
        )
        if not chroma_hits:
            return []

        memory_ids = [hit["memory_id"] for hit in chroma_hits]
        memories_by_id = {
            m.id: m
            for m in self.db.query(Memory).filter(Memory.id.in_(memory_ids)).all()
        }

        scored: list[tuple[float, Memory]] = []
        for hit in chroma_hits:
            memory = memories_by_id.get(hit["memory_id"])
            # Guards against a Chroma/SQL desync (e.g. a memory deleted from
            # SQL without a corresponding vector cleanup) — skip rather than crash.
            if memory is None or memory.status != MemoryStatus.ACTIVE:
                continue
            similarity = _distance_to_similarity(hit["distance"])
            score = composite_retrieval_score(similarity, memory.importance_score)
            scored.append((score, memory))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        results = [memory for _, memory in scored]

        self._apply_access_boost(results)
        return results

    def _apply_access_boost(self, memories: list[Memory]) -> None:
        """Using a memory nudges its importance up and refreshes last_accessed_at."""
        now = datetime.now(timezone.utc)
        for memory in memories:
            memory.importance_score = apply_access_boost(memory.importance_score)
            memory.last_accessed_at = now
        self.db.commit()
