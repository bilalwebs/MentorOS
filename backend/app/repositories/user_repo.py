"""
repositories/user_repo.py

Repository pattern: services never write raw SQLAlchemy queries directly.
This is the only file that knows how User rows are actually fetched/created.
Benefits for this project specifically:
- auth_service.py stays readable (business logic, not query logic)
- easy to unit test auth_service by mocking this repo
- if we ever add caching or switch ORMs, only this file changes
"""

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
