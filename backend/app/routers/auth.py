"""
routers/auth.py

Thin by design: every handler is parse request -> call service -> shape
response. No business logic lives here — see services/auth_service.py.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.ai.qwen_client import get_llm_provider
from app.schemas.user import Token, UserCreate, UserLogin, UserRead
from app.services.auth_service import authenticate_user, issue_token_for_user, register_user
from app.services.memory_service import run_login_decay

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, payload)


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload)
    token = issue_token_for_user(user)

    # Memory maintenance on login: the simplest reliable trigger point
    # without needing a scheduler. Defensive by design (see memory_service) —
    # a decay failure never blocks login.
    run_login_decay(db, user.id, get_llm_provider())

    return Token(access_token=token)


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Quick way to verify a token is valid — also handy for the frontend on app load."""
    return current_user


@router.post("/refresh", response_model=Token)
def refresh_token(current_user: User = Depends(get_current_user)):
    """
    Issues a fresh token for an already-valid (not-yet-expired) session.
    Purely additive: no existing endpoint's behavior changes. This exists
    specifically so the frontend can silently extend a session before the
    current token expires, instead of forcing a re-login every 12 hours.

    Note: this requires the CURRENT token to still be valid — it extends
    an active session, it does not resurrect an expired one. That's a
    deliberate simplicity trade-off (no separate long-lived refresh-token
    table) appropriate for this project's scope.
    """
    return Token(access_token=issue_token_for_user(current_user))
