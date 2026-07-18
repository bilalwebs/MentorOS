"""
services/auth_service.py

All auth business rules live here — routers stay thin (parse request,
call service, return response), and this logic is testable without
spinning up HTTP at all.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate, UserLogin


def register_user(db: Session, payload: UserCreate):
    repo = UserRepository(db)

    if repo.get_by_email(payload.email):
        # 400, not 409 — keeps the API surface simple; a hackathon judge's
        # client just needs "this failed and why", not REST purism.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    user = repo.create(email=payload.email, hashed_password=hash_password(payload.password))
    return user


def authenticate_user(db: Session, payload: UserLogin):
    repo = UserRepository(db)
    user = repo.get_by_email(payload.email)

    # Deliberately identical error for "no such user" and "wrong password" —
    # revealing which one it was lets an attacker enumerate valid emails.
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user or not verify_password(payload.password, user.hashed_password):
        raise invalid_credentials

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="This account has been deactivated."
        )

    return user


def issue_token_for_user(user) -> str:
    return create_access_token(subject=str(user.id))
