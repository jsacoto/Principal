from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import User
from .auth import hash_password


def seed_initial_admin(db: Session) -> None:
    settings = get_settings()
    email = settings.initial_admin_email.strip().lower()
    password = settings.initial_admin_password
    if not email or not password:
        return
    existing = db.scalar(select(User).where(User.email == email))
    if existing:
        return
    db.add(User(
        email=email,
        name=settings.initial_admin_name.strip() or "Coordinación de Transformación Digital",
        password_hash=hash_password(password),
        role="admin",
        is_active=True,
    ))
    db.commit()
