"""
db/session.py

Creates the SQLAlchemy engine and session factory.

This is the ONLY file that needs to know whether we're on SQLite or
PostgreSQL. The `connect_args` check is the single SQLite-specific line
in the entire codebase — remove DATABASE_URL's sqlite:// prefix in .env
and point it at Postgres, and nothing else changes.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# SQLite needs check_same_thread=False for use with FastAPI's threaded
# request handling. PostgreSQL doesn't need (or accept) this argument.
connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {
    }
)

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a DB session and guarantees it's closed
    afterward, even if the request raises an exception.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
