"""Password hashing and JWT helpers."""
from __future__ import annotations

import datetime as dt

import bcrypt
import jwt

from app.core.config import settings

_ALGO = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user_id: str) -> str:
    now = dt.datetime.now(dt.timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + dt.timedelta(hours=settings.jwt_expire_hours),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=_ALGO)


def decode_access_token(token: str) -> str | None:
    """Return the user id (sub) or None if the token is invalid/expired."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[_ALGO])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None
