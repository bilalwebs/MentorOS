"""
repositories/base_repo.py

A small generic repository for models that are all shaped the same way:
belongs to a user, simple CRUD, no special query logic. Skill, Project,
and Certificate all fit this shape, so they share this base instead of
each getting a repository file that's 90% identical boilerplate.

Profile and CareerGoal get their own repositories because they have
real behavioral differences (Profile is one-to-one; CareerGoal has the
supersession logic) that don't belong in a generic class.
"""

from typing import Generic, TypeVar

from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class BaseUserScopedRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user_id: int) -> list[ModelT]:
        return (
            self.db.query(self.model)
            .filter(self.model.user_id == user_id)
            .order_by(self.model.id.desc())
            .all()
        )

    def get_for_user(self, item_id: int, user_id: int) -> ModelT | None:
        return (
            self.db.query(self.model)
            .filter(self.model.id == item_id, self.model.user_id == user_id)
            .first()
        )

    def create(self, **kwargs) -> ModelT:
        obj = self.model(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ModelT) -> None:
        self.db.delete(obj)
        self.db.commit()
