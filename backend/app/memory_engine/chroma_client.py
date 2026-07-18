"""
memory_engine/chroma_client.py

Wraps all ChromaDB access so nothing else in the app imports chromadb
directly. This is what makes "swap the vector store for a managed
service later" a one-file change.

Design choices:
- Single persistent collection, multi-tenant via `user_id` in metadata
  (not one collection per user) — simpler ops, and Chroma's `where`
  filter makes per-user isolation trivial at query time.
- Embeddings are computed by the caller (via the LLMProvider) and passed
  in, rather than using Chroma's built-in embedding functions — keeps
  "which model embeds this" controlled by our own config, not buried in
  a Chroma-specific default that might silently differ from what we use
  elsewhere.
"""

import chromadb

from app.core.config import get_settings

settings = get_settings()

_client: chromadb.ClientAPI | None = None
_collection = None


def get_chroma_collection():
    """
    Lazily create a persistent Chroma client + collection. Lazy on purpose:
    importing this module (e.g. transitively, at app startup) shouldn't
    touch disk until memory features are actually used.
    """
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        _collection = _client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            # Explicit cosine distance: makes `similarity = 1 - distance` an
            # exact conversion downstream (retriever.py), rather than relying
            # on Chroma's default L2 space plus an assumption that our
            # embeddings are unit-normalized. Cosine similarity is also the
            # standard, most robust choice for text embedding retrieval.
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def upsert_memory_vector(chroma_id: str, embedding: list[float], user_id: int, memory_id: int,
                          memory_type: str, status: str) -> None:
    collection = get_chroma_collection()
    collection.upsert(
        ids=[chroma_id],
        embeddings=[embedding],
        metadatas=[{
            "user_id": user_id,
            "memory_id": memory_id,
            "memory_type": memory_type,
            "status": status,
        }],
    )


def update_memory_status(chroma_id: str, status: str) -> None:
    """
    Metadata-only update — Chroma's `update()` doesn't require re-supplying
    the embedding, so status changes (supersede, archive) don't cost an
    extra embedding API call. We fetch-then-merge metadata explicitly
    rather than assuming `update()` merges partial metadata for us — that
    behavior isn't guaranteed across Chroma versions, and losing user_id/
    memory_id off a vector's metadata would silently break retrieval
    filtering, which is worse than one extra local read.
    """
    collection = get_chroma_collection()
    existing = collection.get(ids=[chroma_id], include=["metadatas"])
    if not existing["ids"]:
        return  # vector doesn't exist (e.g. already deleted) — nothing to update
    metadata = dict(existing["metadatas"][0])
    metadata["status"] = status
    collection.update(ids=[chroma_id], metadatas=[metadata])


def delete_memory_vector(chroma_id: str) -> None:
    collection = get_chroma_collection()
    collection.delete(ids=[chroma_id])


def query_similar(embedding: list[float], user_id: int, top_k: int, active_only: bool = True) -> list[dict]:
    """
    Returns a list of {memory_id, distance} for the given user, filtered
    server-side by metadata before similarity search runs — so we never
    pull another user's vectors across the wire.
    """
    collection = get_chroma_collection()

    where_filter: dict = {"user_id": user_id}
    if active_only:
        where_filter = {"$and": [{"user_id": user_id}, {"status": "active"}]}

    # Chroma can return fewer results than top_k if the collection is small;
    # that's fine and expected in early-usage / demo scenarios.
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        where=where_filter,
    )

    if not results["ids"] or not results["ids"][0]:
        return []

    memory_ids = [meta["memory_id"] for meta in results["metadatas"][0]]
    distances = results["distances"][0]
    return [{"memory_id": mid, "distance": dist} for mid, dist in zip(memory_ids, distances)]
