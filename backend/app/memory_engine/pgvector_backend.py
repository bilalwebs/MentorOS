"""
memory_engine/pgvector_backend.py

PostgreSQL-backed vector store using pgvector. Used in production
where ChromaDB's local filesystem won't persist across serverless invocations.

Design:
- Creates a dedicated `memory_embeddings` table with a vector column.
- Uses psycopg2 directly for raw SQL (pgvector operations need SQL-level
  vector operators that SQLAlchemy doesn't expose well).
- Connection pooling via SQLAlchemy's engine (reuses the existing connection).
"""

import logging
from pgvector.psycopg2 import register_vector
import psycopg2
import psycopg2.extras

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_TABLE_CREATED = False


def _get_connection():
    """Get a raw psycopg2 connection from the SQLAlchemy engine's pool."""
    from app.db.session import engine
    conn = engine.raw_connection()
    try:
        register_vector(conn)
    except Exception:
        pass
    return conn


def _ensure_table():
    """Create the memory_embeddings table if it doesn't exist."""
    global _TABLE_CREATED
    if _TABLE_CREATED:
        return

    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS memory_embeddings (
                    id SERIAL PRIMARY KEY,
                    chroma_id VARCHAR(100) UNIQUE NOT NULL,
                    memory_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    memory_type VARCHAR(50) NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'active',
                    embedding vector({settings.QWEN_EMBEDDING_DIMENSIONS}) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_embeddings_user
                ON memory_embeddings (user_id)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_embeddings_chroma
                ON memory_embeddings (chroma_id)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_embeddings_status
                ON memory_embeddings (user_id, status)
            """)
        conn.commit()
        _TABLE_CREATED = True
    except Exception:
        conn.rollback()
        logger.exception("Failed to create pgvector table")
        raise
    finally:
        conn.close()


class PgVectorStore:
    def upsert(self, chroma_id: str, embedding: list[float], user_id: int,
               memory_id: int, memory_type: str, status: str) -> None:
        _ensure_table()
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO memory_embeddings (chroma_id, memory_id, user_id, memory_type, status, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s::vector)
                    ON CONFLICT (chroma_id) DO UPDATE SET
                        memory_id = EXCLUDED.memory_id,
                        user_id = EXCLUDED.user_id,
                        memory_type = EXCLUDED.memory_type,
                        status = EXCLUDED.status,
                        embedding = EXCLUDED.embedding
                """, (chroma_id, memory_id, user_id, memory_type, status, str(embedding)))
            conn.commit()
        except Exception:
            conn.rollback()
            logger.exception("Failed to upsert vector for chroma_id=%s", chroma_id)
            raise
        finally:
            conn.close()

    def update_status(self, chroma_id: str, status: str) -> None:
        _ensure_table()
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE memory_embeddings SET status = %s WHERE chroma_id = %s
                """, (status, chroma_id))
            conn.commit()
        except Exception:
            conn.rollback()
            logger.exception("Failed to update status for chroma_id=%s", chroma_id)
            raise
        finally:
            conn.close()

    def delete(self, chroma_id: str) -> None:
        _ensure_table()
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM memory_embeddings WHERE chroma_id = %s", (chroma_id,))
            conn.commit()
        except Exception:
            conn.rollback()
            logger.exception("Failed to delete vector for chroma_id=%s", chroma_id)
            raise
        finally:
            conn.close()

    def query_similar(self, embedding: list[float], user_id: int,
                      top_k: int, active_only: bool = True) -> list[dict]:
        _ensure_table()
        conn = _get_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                if active_only:
                    cur.execute("""
                        SELECT memory_id, 1 - (embedding <=> %s::vector) AS distance
                        FROM memory_embeddings
                        WHERE user_id = %s AND status = 'active'
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                    """, (str(embedding), user_id, str(embedding), top_k))
                else:
                    cur.execute("""
                        SELECT memory_id, 1 - (embedding <=> %s::vector) AS distance
                        FROM memory_embeddings
                        WHERE user_id = %s
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                    """, (str(embedding), user_id, str(embedding), top_k))

                rows = cur.fetchall()
                return [{"memory_id": row["memory_id"], "distance": float(row["distance"])} for row in rows]
        except Exception:
            logger.exception("Failed to query vectors for user_id=%s", user_id)
            return []
        finally:
            conn.close()
