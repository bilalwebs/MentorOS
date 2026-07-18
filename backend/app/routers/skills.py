"""
routers/skills.py
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.skill import SkillCreate, SkillRead
from app.services.student_data_service import add_skill, delete_skill, list_skills

router = APIRouter()


@router.get("", response_model=list[SkillRead])
def get_skills(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_skills(db, current_user.id)


@router.post("", response_model=SkillRead, status_code=status.HTTP_201_CREATED)
def create_skill(
    payload: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return add_skill(db, current_user.id, payload)


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete_skill(db, current_user.id, skill_id)
