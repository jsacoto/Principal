from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import Activity, ActivityAssignee, Initiative, InitiativeDimension, InitiativeLeader
from ..schemas import ActivityOut, InitiativeOut, InitiativeVerificationRequest, LeaderOut
from ..services.auth import ensure_initiative_access, get_current_user

router = APIRouter(prefix="/api/initiatives", tags=["initiatives"])


def leader_out(name: str | None, email: str | None, role: str, source: str) -> LeaderOut:
    return LeaderOut(name=name or "Responsable Notion sin resolver", email=email, role=role, source=source)


def serialize(initiative: Initiative, include_activities: bool = True) -> InitiativeOut:
    objective = initiative.objective
    contributions = {c.dimension.code: c.contribution_level for c in initiative.contributions}
    activities = []
    if include_activities:
        for a in sorted(initiative.activities, key=lambda x: [int(p) if p.isdigit() else p for p in x.external_id.replace("-", ".").split(".")]):
            activities.append(ActivityOut(
                id=a.id, external_id=a.external_id, parent_external_id=a.parent_external_id,
                activity_type=a.activity_type, title=a.title, progress=a.progress,
                state=a.state, priority=a.priority, start_date=a.start_date, end_date=a.end_date,
                observation=a.observation, evidence_count=a.evidence_count, notion_url=a.notion_url,
                assignees=[leader_out(x.name, x.email, "Responsable", x.source) for x in a.assignees],
            ))
    return InitiativeOut(
        id=initiative.id, code=initiative.code, title=initiative.title,
        objective_code=objective.code if objective else None,
        objective_name=objective.name if objective else None,
        scope=initiative.scope, description=initiative.description,
        reported_progress=initiative.reported_progress, verified_progress=initiative.verified_progress,
        progress_verified_at=initiative.progress_verified_at, progress_verified_by=initiative.progress_verified_by,
        progress_verification_note=initiative.progress_verification_note,
        analytical_progress=initiative.analytical_progress * 100,
        status=initiative.status, notion_url=initiative.notion_url,
        leaders=[leader_out(x.name, x.email, x.role, "notion_initiative") for x in initiative.leaders],
        contributions=contributions, activities=activities,
    )


def base_stmt():
    return select(Initiative).options(
        selectinload(Initiative.objective),
        selectinload(Initiative.leaders),
        selectinload(Initiative.activities).selectinload(Activity.assignees),
        selectinload(Initiative.contributions).selectinload(InitiativeDimension.dimension),
    )


@router.get("", response_model=list[InitiativeOut])
def list_initiatives(
    objective: str | None = None,
    scope: str = Query("all", pattern="^(all|reference16)$"),
    include_activities: bool = False,
    db: Session = Depends(get_db),
):
    stmt = base_stmt().order_by(Initiative.id)
    if scope == "reference16":
        stmt = stmt.where(Initiative.is_reference_16.is_(True))
    initiatives = list(db.scalars(stmt).unique().all())
    if objective:
        initiatives = [i for i in initiatives if i.objective and i.objective.code == objective]
    return [serialize(i, include_activities) for i in initiatives]


@router.get("/{code}", response_model=InitiativeOut)
def get_initiative(code: str, db: Session = Depends(get_db)):
    initiative = db.scalar(base_stmt().where(Initiative.code == code))
    if not initiative:
        raise HTTPException(status_code=404, detail="Initiative not found")
    return serialize(initiative, True)


@router.patch("/{code}/verification", response_model=InitiativeOut)
def verify_initiative_progress(
    code: str,
    payload: InitiativeVerificationRequest,
    user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_initiative_access(user, code)
    initiative = db.scalar(base_stmt().where(Initiative.code == code))
    if not initiative:
        raise HTTPException(status_code=404, detail="Initiative not found")
    initiative.verified_progress = payload.progress_percent
    initiative.progress_verified_at = datetime.now(timezone.utc).replace(tzinfo=None)
    initiative.progress_verified_by = payload.verified_by.strip()
    initiative.progress_verification_note = payload.note.strip()
    db.add(initiative)
    db.commit()
    initiative = db.scalar(base_stmt().where(Initiative.code == code))
    return serialize(initiative, True)
