"""Auth service tests: email-first signup/login with passwords, alpha, tokens."""
from __future__ import annotations

import pytest

from app.core.config import settings
from app.core.security import hash_password
from app.core.errors import AppError, UnauthorizedError
from app.models.models import User
from app.services.auth_service import AuthService


@pytest.fixture
def alpha_email(monkeypatch):
    email = "alpha@example.com"
    monkeypatch.setattr(settings, "alpha_emails", email)
    return email


def test_check_email_new_is_signup(db):
    # A brand-new, non-allowlisted email is prompted to sign up.
    assert AuthService(db).check_email("nobody@example.com") == "signup"


def test_check_email_password_user(db):
    db.add(User(email="pw@example.com", password_hash=hash_password("secret123")))
    db.flush()
    assert AuthService(db).check_email("pw@example.com") == "password"


def test_check_email_alpha(db, alpha_email):
    assert AuthService(db).check_email(alpha_email) == "alpha"
    assert AuthService(db).check_email("ALPHA@EXAMPLE.COM") == "alpha"  # case-insensitive


def test_signup_creates_account_with_password(db):
    svc = AuthService(db)
    token, user = svc.login("new@example.com", "supersecret")
    assert token and user.email == "new@example.com"
    assert user.password_hash  # password was set
    # Now that a password exists, the email requires it.
    assert svc.check_email("new@example.com") == "password"
    with pytest.raises(UnauthorizedError):
        svc.login("new@example.com", "wrongpass")


def test_signup_rejects_weak_password(db):
    with pytest.raises(AppError):
        AuthService(db).login("weak@example.com", "short")  # < 8 chars
    with pytest.raises(AppError):
        AuthService(db).login("nopass@example.com", None)  # no password


def test_alpha_login_creates_user_passwordless(db, alpha_email):
    token, user = AuthService(db).login(alpha_email, None)
    assert token and user.email == alpha_email and user.is_alpha is True
    resolved = AuthService(db).user_from_token(token)
    assert resolved.id == user.id


def test_password_login_success_and_failure(db):
    db.add(User(email="pw2@example.com", password_hash=hash_password("hunter2pw")))
    db.flush()
    svc = AuthService(db)

    token, user = svc.login("pw2@example.com", "hunter2pw")
    assert token and user.email == "pw2@example.com"

    with pytest.raises(UnauthorizedError):
        svc.login("pw2@example.com", "wrongpass")


def test_invalid_token_rejected(db):
    with pytest.raises(UnauthorizedError):
        AuthService(db).user_from_token("not-a-real-token")


def test_insecure_jwt_secret_is_rejected():
    from app.core.config import Settings

    s = Settings(
        _env_file=None,
        jwt_secret="dev-insecure-change-me",
        allow_insecure_jwt=False,
    )
    with pytest.raises(RuntimeError):
        s.require_secure_secret()


def test_insecure_jwt_allowed_with_dev_optout():
    from app.core.config import Settings

    s = Settings(
        _env_file=None,
        jwt_secret="dev-insecure-change-me",
        allow_insecure_jwt=True,
    )
    s.require_secure_secret()  # should not raise


def test_real_secret_passes_guard():
    from app.core.config import Settings

    s = Settings(_env_file=None, jwt_secret="a-real-long-random-secret-value")
    s.require_secure_secret()  # should not raise
