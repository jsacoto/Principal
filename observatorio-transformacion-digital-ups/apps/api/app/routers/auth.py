from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import AuthSession, User, UserInitiativePermission, utcnow_naive
from ..schemas import ChangePasswordRequest, LoginRequest
from ..services.auth import (
    COOKIE_NAME,
    SESSION_COOKIE,
    clear_session_cookie,
    create_session,
    get_current_user,
    hash_password,
    revoke_session_from_cookie,
    set_session_cookie,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


def user_payload(user: User) -> dict:
    codes = sorted({p.initiative.code for p in user.permissions if p.initiative is not None and p.can_edit})
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "is_active": user.is_active,
        "initiative_codes": codes,
    }


@router.post("/login")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.scalar(
        select(User)
        .options(selectinload(User.permissions).selectinload(UserInitiativePermission.initiative))
        .where(User.email == email)
    )
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    token, _ = create_session(db, user)
    set_session_cookie(response, token)
    return {"user": user_payload(user)}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"user": user_payload(user)}


@router.post("/logout")
def logout(
    response: Response,
    db: Session = Depends(get_db),
    token: str | None = Depends(SESSION_COOKIE),
):
    revoke_session_from_cookie(db, token)
    clear_session_cookie(response)
    return {"ok": True}


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña actual no es correcta")
    if payload.current_password == payload.new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La nueva contraseña debe ser diferente")
    user.password_hash = hash_password(payload.new_password)
    user.updated_at = utcnow_naive()
    db.add(user)
    db.commit()
    return {"ok": True}
