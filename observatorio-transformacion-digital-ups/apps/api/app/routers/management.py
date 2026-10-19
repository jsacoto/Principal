from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..config import get_settings
from ..database import get_db
from ..models import (
    Activity,
    ActivityAssignee,
    ActivityProgressLog,
    EvidenceUpload,
    Initiative,
    InitiativeDimension,
    TraceabilityRecord,
    User,
    UserInitiativePermission,
)
from ..routers.initiatives import base_stmt, serialize
from ..schemas import ActivityUpdateRequest
from ..services.auth import ensure_initiative_access, get_current_user, permitted_initiative_codes

router = APIRouter(prefix="/management", tags=["management"])


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
STATE_OPTIONS = {"En desarrollo", "Completo", "Iniciado", "Por Iniciar", "No Iniciado"}
PRIORITY_OPTIONS = {"Alta", "Media", "Baja"}


def _activity_with_initiative(db: Session, activity_id: int) -> Activity:
    activity = db.scalar(select(Activity).options(selectinload(Activity.initiative)).where(Activity.id == activity_id))
    if not activity:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    return activity


def _recalculate_initiative(db: Session, initiative: Initiative, user: User, justification: str) -> None:
    rows = list(db.scalars(select(Activity).where(Activity.initiative_id == initiative.id, Activity.activity_type == "activity")).all())
    values = [float(a.progress) for a in rows if a.progress is not None]
    if values:
        mean = round(sum(values) / len(values), 2)
        initiative.reported_progress = mean
        initiative.verified_progress = mean
        initiative.progress_verified_at = _utcnow()
        initiative.progress_verified_by = user.name
        initiative.progress_verification_note = justification
        initiative.status = "Completo" if values and all(v >= 100 for v in values) else "En desarrollo"
        db.add(initiative)


def _evidence_dict(row: EvidenceUpload) -> dict:
    return {
        "id": row.id,
        "activity_id": row.activity_id,
        "original_name": row.original_name,
        "content_type": row.content_type,
        "size_bytes": row.size_bytes,
        "description": row.description,
        "uploaded_at": row.uploaded_at,
        "uploaded_by": row.uploaded_by.name if row.uploaded_by else None,
        "download_url": f"/backend/api/v1/management/evidence/{row.id}/download",
    }


@router.get("/initiatives")
def management_initiatives(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = base_stmt().order_by(Initiative.id)
    if user.role != "admin":
        codes = permitted_initiative_codes(user)
        if not codes:
            return []
        stmt = stmt.where(Initiative.code.in_(codes))
    initiatives = list(db.scalars(stmt).unique().all())
    return [serialize(i, False) for i in initiatives]


@router.get("/initiatives/{code}")
def management_initiative(code: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ensure_initiative_access(user, code)
    initiative = db.scalar(base_stmt().where(Initiative.code == code))
    if not initiative:
        raise HTTPException(status_code=404, detail="Iniciativa no encontrada")
    payload = serialize(initiative, True).model_dump(mode="json")
    activity_ids = [a.id for a in initiative.activities]
    uploads = []
    if activity_ids:
        uploads = list(db.scalars(
            select(EvidenceUpload)
            .options(selectinload(EvidenceUpload.uploaded_by))
            .where(EvidenceUpload.activity_id.in_(activity_ids))
            .order_by(EvidenceUpload.uploaded_at.desc())
        ).all())
    payload["uploads"] = [_evidence_dict(e) for e in uploads]
    return payload


@router.patch("/activities/{activity_id}")
def update_activity(
    activity_id: int,
    payload: ActivityUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    activity = _activity_with_initiative(db, activity_id)
    ensure_initiative_access(user, activity.initiative.code)
    if payload.state is not None and payload.state not in STATE_OPTIONS:
        raise HTTPException(status_code=400, detail="Estado inválido")
    if payload.priority is not None and payload.priority not in PRIORITY_OPTIONS:
        raise HTTPException(status_code=400, detail="Prioridad inválida")
    start_date = payload.start_date if payload.start_date is not None else activity.start_date
    end_date = payload.end_date if payload.end_date is not None else activity.end_date
    if start_date and end_date and end_date < start_date:
        raise HTTPException(status_code=400, detail="La fecha fin no puede ser anterior a la fecha inicio")

    old_progress = activity.progress
    old_state = activity.state
    if payload.progress is not None:
        activity.progress = payload.progress
    if payload.state is not None:
        activity.state = payload.state
    if payload.priority is not None:
        activity.priority = payload.priority
    if payload.start_date is not None:
        activity.start_date = payload.start_date
    if payload.end_date is not None:
        activity.end_date = payload.end_date
    if payload.observation is not None:
        activity.observation = payload.observation.strip()
    db.add(activity)
    db.add(ActivityProgressLog(
        activity_id=activity.id,
        old_progress=old_progress,
        new_progress=activity.progress,
        old_state=old_state,
        new_state=activity.state,
        justification=payload.justification.strip(),
        changed_by_user_id=user.id,
    ))
    _recalculate_initiative(db, activity.initiative, user, payload.justification.strip())
    db.commit()
    return {"ok": True, "activity_id": activity.id, "progress": activity.progress, "state": activity.state}


@router.post("/activities/{activity_id}/evidence", status_code=201)
async def upload_evidence(
    activity_id: int,
    file: UploadFile = File(...),
    description: str = Form(default=""),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    activity = _activity_with_initiative(db, activity_id)
    ensure_initiative_access(user, activity.initiative.code)
    settings = get_settings()
    original = Path(file.filename or "evidence.bin").name
    suffix = Path(original).suffix.lower()
    if suffix not in settings.allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Tipo de archivo no permitido: {suffix or 'sin extensión'}")
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    target = upload_dir / stored_name
    max_bytes = settings.max_upload_mb * 1024 * 1024
    total = 0
    try:
        with target.open("wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f"El archivo supera {settings.max_upload_mb} MB")
                out.write(chunk)
    except Exception:
        if target.exists():
            target.unlink()
        raise
    finally:
        await file.close()

    row = EvidenceUpload(
        activity_id=activity.id,
        original_name=original,
        stored_name=stored_name,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=total,
        description=description.strip(),
        uploaded_by_user_id=user.id,
    )
    db.add(row)
    activity.evidence_count = int(activity.evidence_count or 0) + 1
    db.add(activity)
    db.flush()
    db.add(TraceabilityRecord(
        from_type="activity",
        from_key=f"{activity.initiative.code}:{activity.external_id}",
        to_type="evidence_upload",
        to_key=str(row.id),
        relation="supported_by",
        source="platform_upload",
        note=description.strip(),
    ))
    db.commit()
    row = db.scalar(select(EvidenceUpload).options(selectinload(EvidenceUpload.uploaded_by)).where(EvidenceUpload.id == row.id))
    return _evidence_dict(row)


@router.get("/evidence/{evidence_id}/download")
def download_evidence(evidence_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.scalar(
        select(EvidenceUpload)
        .options(selectinload(EvidenceUpload.activity).selectinload(Activity.initiative))
        .where(EvidenceUpload.id == evidence_id)
    )
    if not row:
        raise HTTPException(status_code=404, detail="Evidencia no encontrada")
    ensure_initiative_access(user, row.activity.initiative.code)
    path = Path(get_settings().upload_dir) / row.stored_name
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Archivo no disponible en almacenamiento")
    return FileResponse(path, media_type=row.content_type, filename=row.original_name)


@router.get("/initiatives/{code}/audit")
def initiative_audit(code: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ensure_initiative_access(user, code)
    initiative = db.scalar(select(Initiative).where(Initiative.code == code))
    if not initiative:
        raise HTTPException(status_code=404, detail="Iniciativa no encontrada")
    activity_ids = list(db.scalars(select(Activity.id).where(Activity.initiative_id == initiative.id)).all())
    if not activity_ids:
        return {"changes": [], "uploads": []}
    changes = list(db.scalars(
        select(ActivityProgressLog)
        .options(selectinload(ActivityProgressLog.changed_by), selectinload(ActivityProgressLog.activity))
        .where(ActivityProgressLog.activity_id.in_(activity_ids))
        .order_by(ActivityProgressLog.changed_at.desc())
    ).all())
    uploads = list(db.scalars(
        select(EvidenceUpload)
        .options(selectinload(EvidenceUpload.uploaded_by))
        .where(EvidenceUpload.activity_id.in_(activity_ids))
        .order_by(EvidenceUpload.uploaded_at.desc())
    ).all())
    return {
        "changes": [{
            "activity_id": x.activity_id,
            "external_id": x.activity.external_id if x.activity else None,
            "old_progress": x.old_progress,
            "new_progress": x.new_progress,
            "old_state": x.old_state,
            "new_state": x.new_state,
            "justification": x.justification,
            "changed_by": x.changed_by.name if x.changed_by else None,
            "changed_at": x.changed_at,
        } for x in changes],
        "uploads": [_evidence_dict(x) for x in uploads],
    }
