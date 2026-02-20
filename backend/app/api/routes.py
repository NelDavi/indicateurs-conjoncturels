from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import DataSeries, Indicator, Observation
from app.schemas.data import ObservationOut
from app.schemas.indicator import IndicatorOut
from app.schemas.series import SeriesOut

router = APIRouter(prefix="/api", tags=["public"])


@router.get("/indicators", response_model=list[IndicatorOut])
def list_indicators(db: Session = Depends(get_db)):
    return db.execute(select(Indicator).order_by(Indicator.code)).scalars().all()


@router.get("/indicators/{indicator_id}", response_model=IndicatorOut)
def get_indicator(indicator_id: int, db: Session = Depends(get_db)):
    return db.execute(select(Indicator).where(Indicator.id == indicator_id)).scalar_one()


@router.get("/series", response_model=list[SeriesOut])
def list_series(db: Session = Depends(get_db)):
    return db.execute(select(DataSeries).order_by(DataSeries.id)).scalars().all()


@router.get("/data", response_model=list[ObservationOut])
def list_data(
    indicator_id: int,
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = (
        select(Observation)
        .join(DataSeries, DataSeries.id == Observation.series_id)
        .where(DataSeries.indicator_id == indicator_id)
        .order_by(Observation.period_date)
    )
    if start:
        stmt = stmt.where(Observation.period_date >= start)
    if end:
        stmt = stmt.where(Observation.period_date <= end)
    return db.execute(stmt).scalars().all()
