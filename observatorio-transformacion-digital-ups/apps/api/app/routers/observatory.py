from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import ExecutiveSummary, GapResponse, WhatIfRequest, WhatIfResponse
from ..services.analytics import data_quality, executive_summary, gaps, what_if

router = APIRouter(prefix="/api/observatory", tags=["observatory"])


@router.get("/summary", response_model=ExecutiveSummary)
def get_summary(scope: str = Query("all", pattern="^(all|institutional16|reference16)$"), db: Session = Depends(get_db)):
    return executive_summary(db, scope)


@router.get("/gaps", response_model=GapResponse)
def get_gaps(scope: str = Query("all", pattern="^(all|institutional16|reference16)$"), db: Session = Depends(get_db)):
    return gaps(db, scope)


@router.post("/what-if", response_model=WhatIfResponse)
def simulate(payload: WhatIfRequest, scope: str = Query("all", pattern="^(all|institutional16|reference16)$"), db: Session = Depends(get_db)):
    try:
        return what_if(db, payload.initiative_code, payload.progress_percent, scope)
    except KeyError:
        raise HTTPException(status_code=404, detail="Initiative not found in selected scope")


@router.get("/data-quality")
def get_data_quality(db: Session = Depends(get_db)):
    issues = data_quality(db)
    return {
        "count": len(issues),
        "critical": sum(1 for x in issues if x["severity"] == "critical"),
        "high": sum(1 for x in issues if x["severity"] == "high"),
        "issues": issues,
    }
