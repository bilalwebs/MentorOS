"""
memory_engine/vector_store.py

Unified vector store interface that delegates to either ChromaDB (local dev)
or pgvector (production on PostgreSQL). The rest of the app imports from
this module — they never need to know which backend is active.

Why this exists:
- ChromaDB uses local filesystem storage, which is ephemeral on Vercel/serverless.
- pgvector stores embeddings in PostgreSQL, which persists across invocations.
- The function signatures match chroma_client.py exactly so callers just
  change their import.
"""

import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_store = None


def _get_store():
    global _store
    if _store is not None:
        return _store

    settings = get_settings()
    backend = settings.effective_vector_backend

    if backend == "pgvector":
        from app.memory_engine.pgvector_backend import PgVectorStore
        _store = PgVectorStore()
        logger.info("Vector store initialized: pgvector (PostgreSQL)")
    else:
        from app.memory_engine.chroma_backend import ChromaStore
        _store = ChromaStore()
        logger.info("Vector store initialized: ChromaDB (local)")

    return _store


def upsert_memory_vector(chroma_id: str, embedding: list[float], user_id: int,
                         memory_id: int, memory_type: str, status: str) -> None:
    _get_store().upsert(chroma_id, embedding, user_id, memory_id, memory_type, status)


def update_memory_status(chroma_id: str, status: str) -> None:
    _get_store().update_status(chroma_id, status)


def delete_memory_vector(chroma_id: str) -> None:
    _get_store().delete(chroma_id)


def query_similar(embedding: list[float], user_id: int, top_k: int,
                  active_only: bool = True) -> list[dict]:
    return _get_store().query_similar(embedding, user_id, top_k, active_only)


def reset_vector_store() -> None:
    """For testing: reset the singleton so a new backend can be selected."""
    global _store
    _store = None
