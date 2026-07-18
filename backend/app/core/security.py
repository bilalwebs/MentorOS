"""
core/security.py

Password hashing and JWT helpers. Kept isolated from business logic so
auth_service.py stays readable, and so we can swap hashing/JWT libraries
later without touching services or routers.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()

# Using the `bcrypt` library directly rather than passlib's CryptContext
# wrapper. passlib 1.7.4's bcrypt backend detection reads a `__about__`
# attribute that recent bcrypt releases (5.x) no longer expose, which
# breaks password hashing on a fresh install. bcrypt's own API is stable
# and simple enough that the wrapper isn't buying us anything here.
_BCRYPT_MAX_BYTES = 72  # bcrypt silently ignores bytes beyond this — enforce it explicitly


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password for storage. Never store raw passwords."""
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > _BCRYPT_MAX_BYTES:
        raise ValueError("Password must be 72 bytes or fewer.")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a login attempt's password against the stored hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Build a signed JWT. `subject` is typically the user's id (as a string).

    We keep the payload minimal (sub + exp) on purpose — the token is an
    identity proof, not a data store. Anything else the app needs should
    be looked up from the DB using the id in `sub`.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    """
    Decode a JWT and return the subject (user id) if valid.
    Returns None on any failure (expired, tampered, malformed) — callers
    treat None as "unauthenticated" rather than distinguishing error types,
    since the client-facing behavior is the same either way.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload.get("sub")
    except JWTError:
        return None
