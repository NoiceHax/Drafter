"""Authentication: email-first login.

- Open-signup mode (settings.open_signup, on during alpha): ANY email logs in
  without a password; the account is auto-created on first login.
- Otherwise, only allowlisted emails (settings.alpha_emails) skip the password
  step; all others must already exist and match their password.
- A user who has a password set always uses the password path.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import UnauthorizedError
from app.core.security import create_access_token, decode_access_token, verify_password
from app.models.models import User


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    # ── helpers ──────────────────────────────────────────────────────────
    def _find(self, email: str) -> User | None:
        return self.db.execute(
            select(User).where(User.email == email.strip().lower())
        ).scalar_one_or_none()

    @staticmethod
    def _passwordless_ok(email: str) -> bool:
        """True if this email may log in without a password."""
        return settings.open_signup or email.strip().lower() in settings.alpha_email_set

    # ── email-first step ─────────────────────────────────────────────────
    def check_email(self, email: str) -> str:
        """Return the login mode: 'alpha' | 'password' | 'unknown'.

        A user who already has a password always gets the password path.
        """
        user = self._find(email)
        if user and user.password_hash:
            return "password"
        if self._passwordless_ok(email):
            return "alpha"
        return "unknown"

    # ── login ────────────────────────────────────────────────────────────
    def login(self, email: str, password: str | None) -> tuple[str, User]:
        email_norm = email.strip().lower()
        user = self._find(email_norm)

        # Existing password account -> must match.
        if user and user.password_hash:
            if not verify_password(password or "", user.password_hash):
                raise UnauthorizedError("Incorrect email or password.")
            return create_access_token(str(user.id)), user

        # Passwordless path (open signup or allowlist): log in, auto-create.
        if self._passwordless_ok(email_norm):
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

        raise UnauthorizedError("Incorrect email or password.")

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
