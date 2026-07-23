"""
memory_engine/chroma_backend.py

ChromaDB-backed vector store for local development.
Wraps the existing chromadb.PersistentClient with a class interface
that matches the vector_store protocol.
"""

import chromadb

from app.core.config import get_settings

settings = get_settings()

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        _collection = _client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


class ChromaStore:
    def upsert(self, chroma_id: str, embedding: list[float], user_id: int,
               memory_id: int, memory_type: str, status: str) -> None:
        collection = _get_collection()
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

    def update_status(self, chroma_id: str, status: str) -> None:
        collection = _get_collection()
        existing = collection.get(ids=[chroma_id], include=["metadatas"])
        if not existing["ids"]:
            return
        metadata = dict(existing["metadatas"][0])
        metadata["status"] = status
        collection.update(ids=[chroma_id], metadatas=[metadata])

    def delete(self, chroma_id: str) -> None:
        collection = _get_collection()
        collection.delete(ids=[chroma_id])

    def query_similar(self, embedding: list[float], user_id: int,
                      top_k: int, active_only: bool = True) -> list[dict]:
        collection = _get_collection()
        where_filter: dict = {"user_id": user_id}
        if active_only:
            where_filter = {"$and": [{"user_id": user_id}, {"status": "active"}]}

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
