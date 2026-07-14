"""Authentication: email-first signup + login with passwords.

Flow:
- check_email returns:
    "password" -> email exists and has a password; prompt for it.
    "signup"   -> new email; prompt to create a password (first-time signup).
    "alpha"    -> allowlisted email (settings.alpha_emails); logs in with no
                  password. Keeps trusted accounts working without a password.
- login handles all three: verify an existing password, create a new account
  with the supplied password, or passwordless alpha login.

There is no password-reset flow; reset is a manual/admin operation for now.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError, UnauthorizedError
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models.models import User

MIN_PASSWORD_LEN = 8


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    # ── helpers ──────────────────────────────────────────────────────────
    def _find(self, email: str) -> User | None:
        return self.db.execute(
            select(User).where(User.email == email.strip().lower())
        ).scalar_one_or_none()

    @staticmethod
    def _is_alpha(email: str) -> bool:
        return email.strip().lower() in settings.alpha_email_set

    # ── email-first step ─────────────────────────────────────────────────
    def check_email(self, email: str) -> str:
        """Return the login mode: 'password' | 'signup' | 'alpha'."""
        user = self._find(email)
        if user and user.password_hash:
            return "password"
        if self._is_alpha(email):
            return "alpha"
        return "signup"

    # ── login / signup ───────────────────────────────────────────────────
    def login(self, email: str, password: str | None) -> tuple[str, User]:
        email_norm = email.strip().lower()
        user = self._find(email_norm)

        # 1. Existing account with a password -> verify it.
        if user and user.password_hash:
            if not verify_password(password or "", user.password_hash):
                raise UnauthorizedError("Incorrect email or password.")
            return create_access_token(str(user.id)), user

        # 2. Allowlisted alpha email with no password -> passwordless login.
        if self._is_alpha(email_norm) and not password:
            if user is None:
                user = User(
                    email=email_norm,
                    display_name=email_norm.split("@")[0],
                    is_alpha=True,
                )
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)
            return create_access_token(str(user.id)), user

        # 3. Signup: new email (or alpha email choosing to set a password) ->
        #    create the account with the supplied password.
        if not password or len(password) < MIN_PASSWORD_LEN:
            raise AppError(
                f"Password must be at least {MIN_PASSWORD_LEN} characters.",
                code="weak_password",
            )
        if user is None:
            user = User(
                email=email_norm,
                display_name=email_norm.split("@")[0],
                password_hash=hash_password(password),
            )
            self.db.add(user)
        else:
            # Existing passwordless account setting a password for the first time.
            user.password_hash = hash_password(password)
        self.db.commit()
        self.db.refresh(user)
        return create_access_token(str(user.id)), user

    # ── token -> user ────────────────────────────────────────────────────
    def user_from_token(self, token: str) -> User:
        user_id = decode_access_token(token)
        if not user_id:
            raise UnauthorizedError("Your session has expired. Sign in again.")
        user = self.db.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()
        if user is None:
            raise UnauthorizedError("Account not found.")
        return user
