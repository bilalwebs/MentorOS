"""
main.py

FastAPI application entry point.

Kept intentionally thin: no business logic lives here. Its only jobs are
to construct the app, wire up middleware/routers, and create tables on
startup for local dev convenience (Postgres/prod should use Alembic
migrations instead — see README).
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db import base  # noqa: F401  (imports all models onto Base.metadata)
from app.db.session import Base, engine

settings = get_settings()


def _build_cors_origins() -> list[str]:
    """Build CORS origins from config + common dev defaults."""
    origins = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
    if settings.FRONTEND_URL and settings.FRONTEND_URL not in origins:
        origins.append(settings.FRONTEND_URL)
    extra = os.environ.get("CORS_ORIGINS", "")
    if extra:
        for o in extra.split(","):
            o = o.strip()
            if o and o not in origins:
                origins.append(o)
    return origins


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="AI Student Growth Platform with Persistent Memory",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_build_cors_origins(),
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health_check():
    """Simple liveness check — also useful to confirm .env loaded correctly."""
    db_type = "sqlite" if settings.DATABASE_URL.startswith("sqlite") else "postgresql"
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "env": settings.ENV,
        "database": db_type,
        "vector_backend": settings.effective_vector_backend,
    }


from app.routers import (  # noqa: E402
    auth,
    career_goals,
    certificates,
    memory,
    profile,
    projects,
    recommendations,
    resume,
    skills,
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(profile.router, prefix="/profile", tags=["profile"])
app.include_router(skills.router, prefix="/skills", tags=["skills"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(certificates.router,
                   prefix="/certificates", tags=["certificates"])
app.include_router(career_goals.router,
                   prefix="/career-goals", tags=["career-goals"])
app.include_router(resume.router, prefix="/resume", tags=["resume"])
app.include_router(memory.router, prefix="/memory", tags=["memory"])
app.include_router(recommendations.router,
                   prefix="/recommendations", tags=["recommendations"])
