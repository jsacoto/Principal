from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..config import get_settings
from ..database import get_db
from ..models import AuthSession, User, UserInitiativePermission

COOKIE_NAME = "ups_td_session"
PASSWORD_SCHEME = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 310_000


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def hash_password(password: str) -> str:
    if len(password) < 10:
        raise ValueError("Password must contain at least 10 characters")
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    return "$".join([
        PASSWORD_SCHEME,
        str(PASSWORD_ITERATIONS),
        base64.urlsafe_b64encode(salt).decode("ascii").rstrip("="),
        base64.urlsafe_b64encode(digest).decode("ascii").rstrip("="),
    ])


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, iterations_raw, salt_raw, digest_raw = stored.split("$", 3)
        if scheme != PASSWORD_SCHEME:
            return False
        iterations = int(iterations_raw)
        salt = _b64decode(salt_raw)
        expected = _b64decode(digest_raw)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session(db: Session, user: User) -> tuple[str, AuthSession]:
    settings = get_settings()
    raw = secrets.token_urlsafe(36)
    now = _utcnow()
    session = AuthSession(
        token_hash=_token_hash(raw),
        user_id=user.id,
        created_at=now,
        expires_at=now + timedelta(days=settings.session_days),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return raw, session


def set_session_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=settings.session_days * 86400,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/", httponly=True, samesite="lax")


def _session_query(token: str):
    return (
        select(AuthSession)
        .options(
            selectinload(AuthSession.user)
            .selectinload(User.permissions)
            .selectinload(UserInitiativePermission.initiative)
        )
        .where(AuthSession.token_hash == _token_hash(token))
    )


def get_current_user(
    db: Session = Depends(get_db),
    ups_td_session: str | None = Cookie(default=None, alias=COOKIE_NAME),
) -> User:
    if not ups_td_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    session = db.scalar(_session_query(ups_td_session))
    now = _utcnow()
    if not session or session.revoked_at is not None or session.expires_at <= now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid")
    if not session.user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User disabled")
    return session.user


def get_optional_user(
    db: Session = Depends(get_db),
    ups_td_session: str | None = Cookie(default=None, alias=COOKIE_NAME),
) -> User | None:
    if not ups_td_session:
        return None
    session = db.scalar(_session_query(ups_td_session))
    now = _utcnow()
    if not session or session.revoked_at is not None or session.expires_at <= now or not session.user.is_active:
        return None
    return session.user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator role required")
    return user


def permitted_initiative_codes(user: User) -> set[str]:
    if user.role == "admin":
        return set()
    return {p.initiative.code for p in user.permissions if p.can_edit and p.initiative is not None}


def ensure_initiative_access(user: User, code: str) -> None:
    if user.role == "admin":
        return
    if code not in permitted_initiative_codes(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission for this initiative")


def revoke_session_from_cookie(db: Session, token: str | None) -> None:
    if not token:
        return
    session = db.scalar(select(AuthSession).where(AuthSession.token_hash == _token_hash(token)))
    if session and session.revoked_at is None:
        session.revoked_at = _utcnow()
        db.add(session)
        db.commit()
