from __future__ import annotations

from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..data.portfolio_seed import MODEL16_GROUPS
from ..models import Activity, Initiative
from .analytics import compute_layers


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def project_activity_progress(activity: Activity, target_date: date, today: date | None = None) -> float:
    """Project activity progress under the assumption that its current schedule is met.

    The model never regresses below the observed activity progress. For a future target,
    it advances linearly from the current observed progress to 100% by the activity end
    date. If the activity has not started and its start date is in the future, it holds
    current progress until the start date and then advances linearly to the end date.
    Activities without an end date keep their observed progress because there is no
    schedule anchor from which to infer completion.
    """
    today = today or date.today()
    current = _clamp01(float(activity.progress or 0.0) / 100.0)

    if target_date <= today:
        return current
    if not activity.end_date:
        return current
    if target_date >= activity.end_date:
        return 1.0

    anchor = today
    if activity.start_date and activity.start_date > anchor:
        anchor = activity.start_date
    if target_date <= anchor:
        return current
    if activity.end_date <= anchor:
        return 1.0

    elapsed = (target_date - anchor).days
    total = (activity.end_date - anchor).days
    if total <= 0:
        return 1.0
    projected = current + (1.0 - current) * (elapsed / total)
    return _clamp01(projected)


def _initiative_projection(initiative: Initiative, target_date: date, today: date) -> tuple[float, int, int]:
    activities = [a for a in initiative.activities if a.activity_type == "activity"]
    scheduled = [a for a in activities if a.end_date]
    if not activities:
        return initiative.analytical_progress, 0, 0
    projected = [project_activity_progress(a, target_date, today) for a in activities]
    return sum(projected) / len(projected), len(scheduled), len(activities)


def schedule_maturity_forecast(db: Session, target_date: date, scope: str = "all") -> dict:
    today = date.today()
    if target_date < today:
        target_date = today

    initiatives = list(
        db.scalars(
            select(Initiative)
            .options(selectinload(Initiative.activities))
            .order_by(Initiative.id)
        ).all()
    )
    child_progress: dict[str, float] = {}
    scheduled_count = 0
    activity_count = 0
    initiative_rows: list[dict] = []

    for initiative in initiatives:
        projected, scheduled, total = _initiative_projection(initiative, target_date, today)
        child_progress[initiative.code] = projected
        scheduled_count += scheduled
        activity_count += total
        initiative_rows.append({
            "code": initiative.code,
            "current_progress": round(initiative.analytical_progress * 100, 2),
            "projected_progress": round(projected * 100, 2),
            "scheduled_activities": scheduled,
            "total_activities": total,
        })

    if scope in {"institutional16", "reference16"}:
        override: dict[str, float] = {}
        for group_code, child_codes in MODEL16_GROUPS.items():
            values = [child_progress[c] for c in child_codes if c in child_progress]
            if values:
                override[group_code] = sum(values) / len(values)
    else:
        override = child_progress

    current = compute_layers(db, scope)
    projected = compute_layers(db, scope, override)
    current_dims = {d["code"]: d["maturity"] for d in current["dimensions"]}
    projected_dims = {d["code"]: d["maturity"] for d in projected["dimensions"]}

    return {
        "model": "schedule-compliance-baseline-v1",
        "generated_on": today,
        "target_date": target_date,
        "scope": scope,
        "assumption": "Las actividades con fecha fin progresan linealmente desde su avance actual hasta 100% en la fecha fin; las actividades sin fecha fin mantienen su avance actual.",
        "current": {
            "igmd": round(current["igmd"], 4),
            "igtd": round(current["igtd"], 4),
            "dimensions": {k: round(v, 4) for k, v in current_dims.items()},
        },
        "projected": {
            "igmd": round(projected["igmd"], 4),
            "igtd": round(projected["igtd"], 4),
            "dimensions": {k: round(v, 4) for k, v in projected_dims.items()},
        },
        "delta": {
            "igmd": round(projected["igmd"] - current["igmd"], 4),
            "igtd": round(projected["igtd"] - current["igtd"], 4),
            "dimensions": {k: round(projected_dims[k] - current_dims[k], 4) for k in current_dims},
        },
        "schedule_coverage": {
            "scheduled_activities": scheduled_count,
            "total_activities": activity_count,
            "ratio": round(scheduled_count / activity_count, 4) if activity_count else 0.0,
        },
        "initiatives": sorted(initiative_rows, key=lambda row: row["code"]),
        "limitations": [
            "Este escenario no es un pronóstico probabilístico: representa el caso de cumplimiento del cronograma registrado.",
            "IOC e IKO permanecen constantes salvo que sus KRs/KPIs se actualicen por otras fuentes.",
            "Para una predicción de riesgo real se requiere historial temporal de avances, reprogramaciones, evidencias y cumplimiento de hitos.",
        ],
    }
