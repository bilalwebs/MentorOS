"""
repositories/resume_repo.py
"""

from sqlalchemy.orm import Session

from app.models.resume import Resume


class ResumeRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user_id: int) -> list[Resume]:
        return (
            self.db.query(Resume)
            .filter(Resume.user_id == user_id)
            .order_by(Resume.id.desc())
            .all()
        )

    def create(self, user_id: int, file_path: str, original_filename: str) -> Resume:
        resume = Resume(user_id=user_id, file_path=file_path, original_filename=original_filename)
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def mark_parsed(self, resume: Resume) -> Resume:
        from datetime import datetime, timezone

        resume.parsed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(resume)
        return resume
