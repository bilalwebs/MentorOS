"""
routers/resume.py
"""

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.resume import ResumeRead
from app.services.resume_service import list_resumes, upload_and_process_resume

router = APIRouter()


@router.post("/upload")
def upload_resume(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a PDF or .txt resume. The file is saved, parsed, and run through
    AI extraction — skills/projects/certificates/profile/career goal are
    populated automatically and written to memory. Returns a summary of
    what was extracted.
    """
    return upload_and_process_resume(db, current_user.id, file)


@router.get("", response_model=list[ResumeRead])
def get_resumes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_resumes(db, current_user.id)
