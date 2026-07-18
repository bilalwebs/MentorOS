"""
core/config.py

Single source of truth for all environment-driven configuration.

Why this exists:
- Nothing in the rest of the app should read os.environ directly.
- Switching SQLite -> PostgreSQL, or dev -> prod, should ONLY require
  editing .env — never touching Python code.
- pydantic-settings validates types/required fields at startup, so a
  missing API key fails fast with a clear error instead of a mysterious
  500 later during a demo.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "MentorOS"
    ENV: str = "development"  # "development" | "production"
    DEBUG: bool = True

    # --- Database ---
    # Default: local SQLite file, zero setup required.
    # For production, set DATABASE_URL to a PostgreSQL DSN, e.g.:
    # postgresql+psycopg2://user:password@host:5432/mentoros
    DATABASE_URL: str = "sqlite:///./mentoros.db"

    # --- Auth / JWT ---
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_ENV"  # must be overridden in .env
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12  # 12 hours, generous for demo/judging

    # --- Qwen (OpenAI-compatible) ---
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_MODEL: str = "qwen-plus"
    QWEN_EMBEDDING_MODEL: str = "text-embedding-v2"

    # --- ChromaDB ---
    # Persistent local client by default (a folder on disk).
    CHROMA_PERSIST_DIR: str = "./chroma_store"
    CHROMA_COLLECTION_NAME: str = "mentoros_memories"

    # --- Memory Engine tuning ---
    MEMORY_DECAY_RATE: float = 0.05          # importance lost per idle week
    MEMORY_ARCHIVE_THRESHOLD: float = 0.15   # below this -> archived
    MEMORY_RETRIEVAL_TOP_K: int = 8

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """
    Cached so we parse .env once per process, not on every request.
    Import this function (not Settings directly) everywhere else.
    """
    return Settings()
