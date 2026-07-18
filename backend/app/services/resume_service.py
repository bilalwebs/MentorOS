"""
services/resume_service.py

The resume upload pipeline, end to end:
1. Save the uploaded file to disk, record it in the DB.
2. Extract raw text (PDF via pypdf; .txt read directly).
3. Send that text through the EXTRACTION AI pipeline (Qwen, low temp,
   forced JSON) to get structured facts.
4. Persist those facts into the normal domain tables (skills, projects,
   certificates, profile) by reusing student_data_service — this means
   resume-derived data flows through the exact same memory-writing path
   as manually-entered data. No separate/duplicate memory logic to
   maintain here.

This is the clearest "wow" moment for the MemoryAgent track: one upload,
and the AI remembers a dozen facts it will use in every future session.
"""

import logging
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.ai.extraction_prompts import RESUME_EXTRACTION_SYSTEM_PROMPT, build_resume_extraction_prompt
from app.ai.qwen_client import get_llm_provider
from app.core.config import get_settings
from app.repositories.resume_repo import ResumeRepository
from app.schemas.career_goal import CareerGoalCreate
from app.schemas.certificate import CertificateCreate
from app.schemas.profile import ProfileUpdate
from app.schemas.project import ProjectCreate
from app.schemas.skill import SkillCreate
from app.services import student_data_service

logger = logging.getLogger(__name__)
settings = get_settings()

UPLOAD_DIR = Path("uploaded_resumes")
ALLOWED_EXTENSIONS = {".pdf", ".txt"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB — generous for a resume, small enough to not need streaming


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    import io

    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(file_bytes))
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages_text).strip()


def upload_and_process_resume(db: Session, user_id: int, file: UploadFile) -> dict:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{extension}'. Upload a PDF or .txt file.",
        )

    file_bytes = file.file.read()
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large (max 5MB).")

    # --- 1. Save to disk + record in DB ---
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_filename = f"user_{user_id}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename
    file_path.write_bytes(file_bytes)

    resume_repo = ResumeRepository(db)
    resume = resume_repo.create(
        user_id=user_id, file_path=str(file_path), original_filename=file.filename or "resume"
    )

    # --- 2. Extract raw text ---
    try:
        if extension == ".pdf":
            resume_text = _extract_text_from_pdf(file_bytes)
        else:
            resume_text = file_bytes.decode("utf-8", errors="ignore")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not read file contents: {exc}",
        ) from exc

    if not resume_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No extractable text found in the uploaded file.",
        )

    # --- 3. AI extraction (structured facts) ---
    llm = get_llm_provider()
    try:
        facts = llm.extract_structured(
            RESUME_EXTRACTION_SYSTEM_PROMPT, build_resume_extraction_prompt(resume_text)
        )
    except Exception as exc:
        logger.exception("Resume AI extraction failed for user_id=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI extraction failed: {exc}. The resume was saved but not parsed — you can retry.",
        ) from exc

    # --- 4. Persist extracted facts through the normal domain services ---
    summary = _apply_extracted_facts(db, user_id, facts)

    resume_repo.mark_parsed(resume)

    return {
        "resume_id": resume.id,
        "filename": resume.original_filename,
        "extracted": summary,
    }


def _apply_extracted_facts(db: Session, user_id: int, facts: dict) -> dict:
    """
    Writes extracted facts into the real domain tables via the existing
    student_data_service functions — same validation, same memory-writing
    behavior as manual entry. Each category is wrapped individually so one
    bad entry (e.g. a malformed date) doesn't discard the whole extraction.
    """
    created = {
        "skills": 0, "projects": 0, "certificates": 0,
        "profile_updated": False, "career_goal_set": False,
    }

    if facts.get("full_name") or facts.get("target_role"):
        try:
            student_data_service.update_profile(
                db, user_id,
                ProfileUpdate(full_name=facts.get("full_name"), target_role=facts.get("target_role")),
            )
            created["profile_updated"] = True
        except Exception:
            logger.exception("Failed to apply extracted profile data for user_id=%s", user_id)

    if facts.get("target_role"):
        try:
            student_data_service.add_career_goal(
                db, user_id, CareerGoalCreate(goal_text=f"Become a {facts['target_role']}")
            )
            created["career_goal_set"] = True
        except Exception:
            logger.exception("Failed to set career goal from resume for user_id=%s", user_id)

    for skill in facts.get("skills") or []:
        try:
            student_data_service.add_skill(
                db, user_id, SkillCreate(name=skill["name"], level=skill.get("level", "beginner"))
            )
            created["skills"] += 1
        except Exception:
            logger.exception("Failed to add extracted skill %s for user_id=%s", skill, user_id)

    for project in facts.get("projects") or []:
        try:
            student_data_service.add_project(
                db, user_id,
                ProjectCreate(
                    title=project["title"],
                    description=project.get("description"),
                    tech_stack=project.get("tech_stack") or [],
                ),
            )
            created["projects"] += 1
        except Exception:
            logger.exception("Failed to add extracted project %s for user_id=%s", project, user_id)

    for cert in facts.get("certificates") or []:
        try:
            student_data_service.add_certificate(
                db, user_id,
                CertificateCreate(
                    title=cert["title"], issuer=cert.get("issuer"), date_earned=cert.get("date_earned"),
                ),
            )
            created["certificates"] += 1
        except Exception:
            logger.exception("Failed to add extracted certificate %s for user_id=%s", cert, user_id)

    return created


def list_resumes(db: Session, user_id: int):
    return ResumeRepository(db).list_for_user(user_id)
