"""
routers/memory.py
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.memory import MemoryRead
from app.services.memory_service import delete_memory, get_timeline

router = APIRouter()


@router.get("/timeline", response_model=list[MemoryRead])
def read_memory_timeline(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns every memory (active, superseded, archived) for this student,
    newest first. This is what the frontend's Memory Timeline view renders —
    the visible proof that memory persists AND evolves.
    """
    return get_timeline(db, current_user.id)


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
def forget_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manual 'forget this' — deletes both the SQL row and its Chroma vector."""
    delete_memory(db, current_user.id, memory_id)
