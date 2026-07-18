"""
services/student_data_service.py

Business logic for the core student-data domain. Three responsibilities
that don't belong in routers or repositories:
1. Converting between storage format (comma-separated tech_stack string)
   and API format (list[str]) — routers should never see the raw string.
2. Raising consistent 404s when a user tries to touch a record that
   isn't theirs (list_for_user/get_for_user already scope by user_id,
   so a mismatched id naturally returns None here, not another user's data).
3. Writing a Memory for every fact a student creates/changes — this is
   what makes the "students stop repeating themselves" promise real. Every
   write here is wrapped defensively: if embedding/Chroma fails (network
   issue, quota, etc.), the CRUD operation the student actually asked for
   still succeeds. Memory is a value-add layer on top of the core data,
   not a single point of failure for it.
"""

import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.qwen_client import get_llm_provider
from app.memory_engine.writer import MemoryWriter
from app.models.memory import Memory
from app.models.mixins import MemoryStatus, MemoryType
from app.models.profile import Profile
from app.repositories.student_data_repo import (
    CareerGoalRepository,
    CertificateRepository,
    ProfileRepository,
    ProjectRepository,
    SkillRepository,
)
from app.schemas.career_goal import CareerGoalCreate
from app.schemas.certificate import CertificateCreate
from app.schemas.profile import ProfileCreate, ProfileUpdate
from app.schemas.project import ProjectCreate
from app.schemas.skill import SkillCreate

logger = logging.getLogger(__name__)


def _not_found(resource: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found.")


def _safe_write_memory(
    db: Session, user_id: int, memory_type: MemoryType, content_text: str,
    source_table: str, source_id: int,
) -> None:
    try:
        writer = MemoryWriter(db, get_llm_provider())
        writer.write(user_id, memory_type, content_text, source_table, source_id)
    except Exception:
        logger.exception(
            "Memory write failed (user_id=%s, type=%s, source=%s:%s) — CRUD operation still succeeded.",
            user_id, memory_type, source_table, source_id,
        )


def _safe_supersede_memory(
    db: Session, user_id: int, memory_type: MemoryType, source_table: str, source_id: int,
    new_content_text: str,
) -> None:
    """
    Find the active memory tied to this source record and supersede it.
    Falls back to a fresh write if no prior memory exists (e.g. the
    original write failed, or this predates memory tracking).
    """
    try:
        existing = (
            db.query(Memory)
            .filter(
                Memory.user_id == user_id,
                Memory.source_table == source_table,
                Memory.source_id == source_id,
                Memory.status == MemoryStatus.ACTIVE,
            )
            .first()
        )
        writer = MemoryWriter(db, get_llm_provider())
        if existing:
            writer.supersede(existing, new_content_text)
        else:
            writer.write(user_id, memory_type, new_content_text, source_table, source_id)
    except Exception:
        logger.exception(
            "Memory supersede failed (user_id=%s, source=%s:%s) — CRUD operation still succeeded.",
            user_id, source_table, source_id,
        )


# ---------------------------------------------------------------- Profile

def get_or_create_profile(db: Session, user_id: int) -> Profile:
    """
    Profile is 1:1 with User but isn't created at registration time — the
    student fills it in during onboarding. Auto-creating an empty one on
    first GET avoids a separate "does a profile exist yet" branch in the
    router and in the frontend.
    """
    repo = ProfileRepository(db)
    profile = repo.get_by_user_id(user_id)
    if profile is None:
        profile = repo.create(user_id=user_id, full_name="")
    return profile


def update_profile(db: Session, user_id: int, payload: ProfileUpdate) -> Profile:
    repo = ProfileRepository(db)
    profile = get_or_create_profile(db, user_id)
    updated = repo.update(profile, **payload.model_dump(exclude_unset=True))

    summary_parts = [p for p in [updated.full_name, updated.target_role, updated.bio] if p]
    if summary_parts:
        content = f"Profile: {'; '.join(summary_parts)}"
        _safe_supersede_memory(db, user_id, MemoryType.PROFILE, "profiles", updated.id, content)

    return updated


def create_profile(db: Session, user_id: int, payload: ProfileCreate) -> Profile:
    repo = ProfileRepository(db)
    existing = repo.get_by_user_id(user_id)
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists. Use PUT to update it.")
    return repo.create(user_id=user_id, **payload.model_dump())


# ---------------------------------------------------------------- Skills

def list_skills(db: Session, user_id: int):
    return SkillRepository(db).list_for_user(user_id)


def add_skill(db: Session, user_id: int, payload: SkillCreate):
    skill = SkillRepository(db).create(user_id=user_id, name=payload.name, level=payload.level)

    content = f"Skill: {skill.name} (level: {skill.level.value})"
    _safe_write_memory(db, user_id, MemoryType.SKILL, content, "skills", skill.id)

    return skill


def delete_skill(db: Session, user_id: int, skill_id: int) -> None:
    repo = SkillRepository(db)
    skill = repo.get_for_user(skill_id, user_id)
    if not skill:
        raise _not_found("Skill")
    repo.delete(skill)


# --------------------------------------------------------------- Projects

def _project_to_read_dict(project) -> dict:
    """Split the stored comma-separated tech_stack into a clean list for the API."""
    tech_stack = [t.strip() for t in project.tech_stack.split(",") if t.strip()] if project.tech_stack else []
    return {
        "id": project.id,
        "title": project.title,
        "description": project.description,
        "tech_stack": tech_stack,
        "created_at": project.created_at,
    }


def list_projects(db: Session, user_id: int) -> list[dict]:
    projects = ProjectRepository(db).list_for_user(user_id)
    return [_project_to_read_dict(p) for p in projects]


def add_project(db: Session, user_id: int, payload: ProjectCreate) -> dict:
    tech_stack_str = ",".join(payload.tech_stack) if payload.tech_stack else None
    project = ProjectRepository(db).create(
        user_id=user_id,
        title=payload.title,
        description=payload.description,
        tech_stack=tech_stack_str,
    )

    stack_note = f" using {', '.join(payload.tech_stack)}" if payload.tech_stack else ""
    content = f"Project: {project.title}{stack_note}. {project.description or ''}".strip()
    _safe_write_memory(db, user_id, MemoryType.PROJECT, content, "projects", project.id)

    return _project_to_read_dict(project)


def delete_project(db: Session, user_id: int, project_id: int) -> None:
    repo = ProjectRepository(db)
    project = repo.get_for_user(project_id, user_id)
    if not project:
        raise _not_found("Project")
    repo.delete(project)


# ----------------------------------------------------------- Certificates

def list_certificates(db: Session, user_id: int):
    return CertificateRepository(db).list_for_user(user_id)


def add_certificate(db: Session, user_id: int, payload: CertificateCreate):
    cert = CertificateRepository(db).create(user_id=user_id, **payload.model_dump())

    issuer_note = f" issued by {cert.issuer}" if cert.issuer else ""
    content = f"Certificate: {cert.title}{issuer_note}"
    _safe_write_memory(db, user_id, MemoryType.CERTIFICATE, content, "certificates", cert.id)

    return cert


def delete_certificate(db: Session, user_id: int, certificate_id: int) -> None:
    repo = CertificateRepository(db)
    cert = repo.get_for_user(certificate_id, user_id)
    if not cert:
        raise _not_found("Certificate")
    repo.delete(cert)


# ----------------------------------------------------------- Career Goals

def list_career_goals(db: Session, user_id: int):
    return CareerGoalRepository(db).list_for_user(user_id)


def add_career_goal(db: Session, user_id: int, payload: CareerGoalCreate):
    """
    Adding a new goal while an active one already exists supersedes it —
    students have one "current" career direction at a time, and the old
    one becomes read-only history rather than being deleted or left to
    look like two simultaneous active goals. The linked memory is
    superseded in lockstep with the SQL row.
    """
    repo = CareerGoalRepository(db)
    active_goals = repo.get_active_for_user(user_id)

    content = f"Career goal: {payload.goal_text}"

    if active_goals:
        old_goal = active_goals[0]
        new_goal = repo.supersede(old_goal, payload.goal_text)
        _safe_supersede_memory(db, user_id, MemoryType.CAREER_GOAL, "career_goals", old_goal.id, content)
        # Re-point the new memory's source to the new goal row for a clean 1:1 mapping.
        _rebind_latest_memory_source(db, user_id, "career_goals", new_goal.id)
        return new_goal

    new_goal = repo.create(user_id=user_id, goal_text=payload.goal_text)
    _safe_write_memory(db, user_id, MemoryType.CAREER_GOAL, content, "career_goals", new_goal.id)
    return new_goal


def _rebind_latest_memory_source(db: Session, user_id: int, source_table: str, new_source_id: int) -> None:
    """
    _safe_supersede_memory writes the new memory with the OLD source_id
    (it doesn't know the new goal's id yet at that point). This patches
    the just-created memory to point at the new goal row instead, keeping
    the memory <-> source_table/source_id mapping accurate for future
    supersession lookups.
    """
    try:
        latest = (
            db.query(Memory)
            .filter(
                Memory.user_id == user_id,
                Memory.source_table == source_table,
                Memory.status == MemoryStatus.ACTIVE,
            )
            .order_by(Memory.created_at.desc())
            .first()
        )
        if latest:
            latest.source_id = new_source_id
            db.commit()
    except Exception:
        logger.exception("Failed to rebind memory source_id for user_id=%s", user_id)
