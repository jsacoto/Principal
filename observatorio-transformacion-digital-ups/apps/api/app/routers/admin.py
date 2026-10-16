from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import (
    Activity,
    ActivityAssignee,
    Dimension,
    Initiative,
    InitiativeDimension,
    InitiativeLeader,
    Objective,
    TraceabilityRecord,
    User,
    UserInitiativePermission,
)
from ..schemas import AdminUserCreateRequest, AdminUserUpdateRequest, InitiativeCreateRequest
from ..services.auth import hash_password, require_admin

router = APIRouter(prefix="/api/admin", tags=["administration"])

STATE_OPTIONS = ["En desarrollo", "Completo", "Iniciado", "Por Iniciar", "No Iniciado"]
PRIORITY_OPTIONS = ["Alta", "Media", "Baja"]


def _user_dict(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "initiative_codes": sorted(p.initiative.code for p in user.permissions if p.initiative and p.can_edit),
        "created_at": user.created_at,
    }


def _load_user(db: Session, user_id: int) -> User | None:
    return db.scalar(
        select(User)
        .options(selectinload(User.permissions).selectinload(UserInitiativePermission.initiative))
        .where(User.id == user_id)
    )


def _set_permissions(db: Session, user: User, codes: list[str]) -> None:
    normalized = sorted({c.strip() for c in codes if c.strip()})
    initiatives = list(db.scalars(select(Initiative).where(Initiative.code.in_(normalized))).all()) if normalized else []
    found = {i.code for i in initiatives}
    missing = [code for code in normalized if code not in found]
    if missing:
        raise HTTPException(status_code=400, detail=f"Iniciativas inexistentes: {', '.join(missing)}")
    for permission in list(user.permissions):
        db.delete(permission)
    db.flush()
    for initiative in initiatives:
        db.add(UserInitiativePermission(user_id=user.id, initiative_id=initiative.id, can_edit=True))


@router.get("/users")
def list_users(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.scalars(
        select(User)
        .options(selectinload(User.permissions).selectinload(UserInitiativePermission.initiative))
        .order_by(User.name)
    ).all()
    return [_user_dict(u) for u in users]


@router.post("/users", status_code=201)
def create_user(payload: AdminUserCreateRequest, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="Ya existe un usuario con ese correo")
    try:
        password_hash = hash_password(payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    user = User(name=payload.name.strip(), email=email, password_hash=password_hash, role=payload.role, is_active=True)
    db.add(user)
    db.flush()
    user = _load_user(db, user.id) or user
    _set_permissions(db, user, payload.initiative_codes)
    db.commit()
    db.expire_all()
    return _user_dict(_load_user(db, user.id) or user)


@router.patch("/users/{user_id}")
def update_user(user_id: int, payload: AdminUserUpdateRequest, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = _load_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if payload.name is not None:
        user.name = payload.name.strip()
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.role is not None:
        user.role = payload.role
    user.updated_at = _utcnow()
    if payload.initiative_codes is not None:
        _set_permissions(db, user, payload.initiative_codes)
    db.add(user)
    db.commit()
    db.expire_all()
    return _user_dict(_load_user(db, user_id) or user)


@router.get("/initiative-template")
def initiative_template(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    objectives = list(db.scalars(select(Objective).order_by(Objective.code)).all())
    dimensions = list(db.scalars(select(Dimension).order_by(Dimension.code)).all())
    return {
        "source": "Plantilla reconstruida desde la cartera Notion UPS y el modelo D1-D5/O1-O5",
        "notion_template_fields": [
            "Actividades para la Implementación", "Id", "Fecha Inicio", "Fecha Fin", "Avance (%)",
            "Responsable", "Evidencias", "Estado", "In", "Priodidad", "Observación general"
        ],
        "objectives": [{"code": o.code, "legacy_code": o.legacy_code, "name": o.name} for o in objectives],
        "dimensions": [{"code": d.code, "name": d.name} for d in dimensions],
        "state_options": STATE_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
        "contribution_levels": [0, 1, 2, 3],
    }


@router.post("/initiatives", status_code=201)
def create_initiative(payload: InitiativeCreateRequest, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    code = payload.code.strip()
    if db.scalar(select(Initiative).where(Initiative.code == code)):
        raise HTTPException(status_code=409, detail="Ya existe una iniciativa con ese código")
    objective = db.scalar(select(Objective).where(Objective.code == payload.objective_code))
    if not objective:
        raise HTTPException(status_code=400, detail="Objetivo inválido")
    dimensions = {d.code: d for d in db.scalars(select(Dimension).order_by(Dimension.code)).all()}
    contributions = {d: int(payload.contributions.get(d, 0)) for d in dimensions}
    if any(v not in (0, 1, 2, 3) for v in contributions.values()):
        raise HTTPException(status_code=400, detail="Las contribuciones D1-D5 deben estar entre 0 y 3")
    if not any(v > 0 for v in contributions.values()):
        raise HTTPException(status_code=400, detail="La iniciativa debe contribuir al menos a una dimensión")
    if payload.status not in STATE_OPTIONS:
        raise HTTPException(status_code=400, detail="Estado inicial inválido")
    activity_ids = [a.external_id.strip() for a in payload.activities]
    if len(activity_ids) != len(set(activity_ids)):
        raise HTTPException(status_code=400, detail="Los Id de actividad deben ser únicos dentro de la iniciativa")
    for activity in payload.activities:
        if activity.start_date and activity.end_date and activity.end_date < activity.start_date:
            raise HTTPException(status_code=400, detail=f"Fechas inválidas en actividad {activity.external_id}")
        if activity.state not in STATE_OPTIONS:
            raise HTTPException(status_code=400, detail=f"Estado inválido en actividad {activity.external_id}")
        if activity.priority not in PRIORITY_OPTIONS:
            raise HTTPException(status_code=400, detail=f"Prioridad inválida en actividad {activity.external_id}")

    progress_values = [a.progress for a in payload.activities if a.progress is not None]
    reported_progress = round(sum(progress_values) / len(progress_values), 2) if progress_values else 0.0
    title = f"Iniciativa {code} - {objective.code} - {payload.scope.strip()} - {payload.leader_name.strip()}"
    initiative = Initiative(
        code=code,
        title=title,
        objective_id=objective.id,
        scope=payload.scope.strip(),
        description=payload.description.strip(),
        reported_progress=reported_progress,
        verified_progress=None,
        status=payload.status,
        notion_url=None,
        data_origin="platform_created",
        last_synced_at=None,
        is_reference_16=False,
    )
    db.add(initiative)
    db.flush()
    db.add(InitiativeLeader(
        initiative_id=initiative.id,
        name=payload.leader_name.strip(),
        email=payload.leader_email.strip().lower() or None,
        role="Líder",
    ))
    db.add(TraceabilityRecord(
        from_type="initiative", from_key=code, to_type="objective", to_key=objective.code,
        relation="aligned_to", source="platform_template", note=f"Creada por {admin.email}"
    ))
    for dim_code, level in contributions.items():
        db.add(InitiativeDimension(
            initiative_id=initiative.id,
            dimension_id=dimensions[dim_code].id,
            contribution_level=level,
            source="platform_template",
            validated=True,
            note=f"Definida al crear la iniciativa por {admin.email}",
        ))
        if level > 0:
            db.add(TraceabilityRecord(
                from_type="initiative", from_key=code, to_type="dimension", to_key=dim_code,
                relation="contributes_to", weight=float(level), source="platform_template"
            ))

    for activity_payload in payload.activities:
        activity = Activity(
            initiative_id=initiative.id,
            external_id=activity_payload.external_id.strip(),
            activity_type="activity",
            title=activity_payload.title.strip(),
            progress=activity_payload.progress,
            state=activity_payload.state,
            priority=activity_payload.priority,
            start_date=activity_payload.start_date,
            end_date=activity_payload.end_date,
            observation=activity_payload.observation.strip(),
            evidence_count=0,
            raw_data={"In": activity_payload.in_field.strip(), "source": "platform_template"},
        )
        db.add(activity)
        db.flush()
        if activity_payload.responsible_name.strip() or activity_payload.responsible_email.strip():
            db.add(ActivityAssignee(
                activity_id=activity.id,
                name=activity_payload.responsible_name.strip() or None,
                email=activity_payload.responsible_email.strip().lower() or None,
                source="platform_template",
            ))
        db.add(TraceabilityRecord(
            from_type="initiative", from_key=code, to_type="activity", to_key=f"{code}:{activity.external_id}",
            relation="contains", source="platform_template"
        ))

    leader_email = payload.leader_email.strip().lower()
    if leader_email:
        leader_user = db.scalar(select(User).options(selectinload(User.permissions)).where(User.email == leader_email))
        if leader_user and not any(p.initiative_id == initiative.id for p in leader_user.permissions):
            db.add(UserInitiativePermission(user_id=leader_user.id, initiative_id=initiative.id, can_edit=True))

    db.commit()
    return {"ok": True, "initiative": {"code": code, "title": title, "reported_progress": reported_progress}}
