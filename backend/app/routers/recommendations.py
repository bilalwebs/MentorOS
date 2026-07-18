"""
routers/recommendations.py
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.llm_provider import LLMProvider
from app.ai.qwen_client import get_llm_provider
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.recommendation_service import generate_recommendation

router = APIRouter()


def _get_llm() -> LLMProvider:
    return get_llm_provider()


@router.post("/roadmap")
def roadmap(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    llm: LLMProvider = Depends(_get_llm),
):
    try:
        return generate_recommendation(db, current_user.id, llm, "roadmap")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI generation failed: {exc}") from exc


@router.post("/skill-gap")
def skill_gap(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    llm: LLMProvider = Depends(_get_llm),
):
    try:
        return generate_recommendation(db, current_user.id, llm, "skill_gap")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI generation failed: {exc}") from exc


@router.post("/projects")
def project_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    llm: LLMProvider = Depends(_get_llm),
):
    try:
        return generate_recommendation(db, current_user.id, llm, "project_recommendation")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI generation failed: {exc}") from exc
