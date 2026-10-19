from __future__ import annotations

from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.forecast import schedule_maturity_forecast

router = APIRouter(prefix="/forecast", tags=["forecasting"])


@router.get(
    "/schedule",
    summary="Proyectar la madurez bajo cumplimiento del cronograma",
    description=(
        "Escenario determinista de referencia. Proyecta el avance de las actividades que tienen fecha fin, "
        "asumiendo que alcanzan 100% en dicha fecha, y recalcula IGMD e IGTD. No representa una predicción "
        "probabilística ni un modelo de IA."
    ),
)
def forecast_schedule(
    target_date: date,
    scope: str = Query("all", pattern="^(all|institutional16|reference16)$"),
    db: Session = Depends(get_db),
):
    return schedule_maturity_forecast(db, target_date, scope)
