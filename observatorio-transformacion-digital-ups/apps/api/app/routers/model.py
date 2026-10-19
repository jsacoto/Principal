from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import Dimension, KPI, KeyResult, Objective, TraceabilityRecord
from ..engine import normalize_kpi, normalize_kr

router = APIRouter(prefix="/model", tags=["model"])


@router.get("/dimensions")
def dimensions(db: Session = Depends(get_db)):
    return [{"code":d.code,"name":d.name,"description":d.description,"weight":d.weight,"target":d.target_maturity,"color":d.color} for d in db.scalars(select(Dimension).order_by(Dimension.code)).all()]


@router.get("/objectives")
def objectives(db: Session = Depends(get_db)):
    return [{"code":o.code,"legacy_code":o.legacy_code,"name":o.name,"description":o.description,"weight":o.weight} for o in db.scalars(select(Objective).order_by(Objective.code)).all()]


@router.get("/key-results")
def key_results(db: Session = Depends(get_db)):
    rows = db.scalars(select(KeyResult).options(selectinload(KeyResult.objective)).order_by(KeyResult.code)).all()
    return [{
        "code":x.code,"objective_code":x.objective.code,"title":x.title,"direction":x.direction,
        "current":x.current_value,"target":x.target_value,"unit":x.unit,"weight":x.weight,"source":x.source,
        "compliance":normalize_kr(x.current_value,x.target_value,x.direction),
    } for x in rows]


@router.get("/kpis")
def kpis(db: Session = Depends(get_db)):
    rows = db.scalars(select(KPI).options(selectinload(KPI.dimension),selectinload(KPI.objective)).order_by(KPI.code)).all()
    return [{
        "code":x.code,"dimension_code":x.dimension.code if x.dimension else None,
        "objective_code":x.objective.code if x.objective else None,"title":x.title,"direction":x.direction,
        "current":x.current_value,"target":x.target_value,"unit":x.unit,"weight":x.weight,"source":x.source,
        "normalized":normalize_kpi(x.current_value,x.target_value,x.direction),
    } for x in rows]


@router.get("/traceability")
def traceability(
    from_type: str | None = Query(None),
    from_key: str | None = Query(None),
    to_type: str | None = Query(None),
    db: Session = Depends(get_db),
):
    stmt = select(TraceabilityRecord).order_by(TraceabilityRecord.id)
    if from_type:
        stmt = stmt.where(TraceabilityRecord.from_type == from_type)
    if from_key:
        stmt = stmt.where(TraceabilityRecord.from_key == from_key)
    if to_type:
        stmt = stmt.where(TraceabilityRecord.to_type == to_type)
    rows = db.scalars(stmt.limit(1000)).all()
    return [{
        "from_type": x.from_type, "from_key": x.from_key,
        "to_type": x.to_type, "to_key": x.to_key,
        "relation": x.relation, "weight": x.weight, "source": x.source, "note": x.note,
    } for x in rows]
