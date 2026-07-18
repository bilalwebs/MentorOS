"""
core/deps.py

Shared FastAPI dependencies. `get_current_user` is the gatekeeper every
protected router (profile, skills, memory, recommendations, ...) will
depend on from here on — defined once, reused everywhere, so the auth
check can never be accidentally skipped or implemented inconsistently
in a later module.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repo import UserRepository

# HTTPBearer (not OAuth2PasswordBearer) because our /auth/login accepts a
# JSON body, not an OAuth2 form — this keeps /docs matching what the API
# actually expects, and is exactly what the Streamlit frontend will send.
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise unauthorized

    user = UserRepository(db).get_by_id(int(user_id))
    if user is None or not user.is_active:
        raise unauthorized

    return user
