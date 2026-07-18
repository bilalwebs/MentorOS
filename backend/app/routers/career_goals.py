"""
routers/career_goals.py
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.career_goal import CareerGoalCreate, CareerGoalRead
from app.services.student_data_service import add_career_goal, list_career_goals

router = APIRouter()


@router.get("", response_model=list[CareerGoalRead])
def get_career_goals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns full history — active AND superseded — so the timeline UI can show goal evolution."""
    return list_career_goals(db, current_user.id)


@router.post("", response_model=CareerGoalRead, status_code=status.HTTP_201_CREATED)
def create_career_goal(
    payload: CareerGoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    If the student already has an active goal, it's automatically
    superseded rather than left active alongside the new one.
    """
    return add_career_goal(db, current_user.id, payload)
