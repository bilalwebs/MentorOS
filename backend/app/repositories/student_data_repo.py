"""
repositories/student_data_repo.py

Concrete repositories for the core student-data models. Skill, Project,
and Certificate use the generic BaseUserScopedRepository as-is. Profile
and CareerGoal get extra methods for their specific behavior.
"""

from sqlalchemy.orm import Session

from app.models.career_goal import CareerGoal
from app.models.certificate import Certificate
from app.models.mixins import GoalStatus
from app.models.profile import Profile
from app.models.project import Project
from app.models.skill import Skill
from app.repositories.base_repo import BaseUserScopedRepository


class SkillRepository(BaseUserScopedRepository[Skill]):
    model = Skill


class ProjectRepository(BaseUserScopedRepository[Project]):
    model = Project


class CertificateRepository(BaseUserScopedRepository[Certificate]):
    model = Certificate


class ProfileRepository:
    """One-to-one with User, so this doesn't fit the list-based generic repo."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> Profile | None:
        return self.db.query(Profile).filter(Profile.user_id == user_id).first()

    def create(self, user_id: int, **kwargs) -> Profile:
        profile = Profile(user_id=user_id, **kwargs)
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update(self, profile: Profile, **kwargs) -> Profile:
        for key, value in kwargs.items():
            setattr(profile, key, value)
        self.db.commit()
        self.db.refresh(profile)
        return profile


class CareerGoalRepository(BaseUserScopedRepository[CareerGoal]):
    model = CareerGoal

    def get_active_for_user(self, user_id: int) -> list[CareerGoal]:
        return (
            self.db.query(CareerGoal)
            .filter(CareerGoal.user_id == user_id, CareerGoal.status == GoalStatus.ACTIVE)
            .order_by(CareerGoal.id.desc())
            .all()
        )

    def supersede(self, old_goal: CareerGoal, new_goal_text: str) -> CareerGoal:
        """
        Replace an active goal with a new one, without deleting the old one.
        This is the concrete "memory forgetting via contradiction" mechanic:
        the old goal becomes read-only history, linked to what replaced it.
        """
        new_goal = CareerGoal(user_id=old_goal.user_id, goal_text=new_goal_text)
        self.db.add(new_goal)
        self.db.flush()  # get new_goal.id without a full commit yet

        old_goal.status = GoalStatus.SUPERSEDED
        old_goal.superseded_by_id = new_goal.id

        self.db.commit()
        self.db.refresh(new_goal)
        return new_goal
