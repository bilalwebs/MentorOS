"""
db/session.py

Creates the SQLAlchemy engine and session factory.

This is the ONLY file that needs to know whether we're on SQLite or
PostgreSQL. The `connect_args` check is the single SQLite-specific line
in the entire codebase — remove DATABASE_URL's sqlite:// prefix in .env
and point it at Postgres, and nothing else changes.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings

settings = get_settings()

if settings.is_postgres:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
else:
    # SQLite: StaticPool lets all FastAPI threads share one connection,
    # avoiding QueuePool timeout when concurrent requests arrive while a
    # slow endpoint (e.g. resume upload with LLM calls) holds the sole
    # connection open.
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


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
