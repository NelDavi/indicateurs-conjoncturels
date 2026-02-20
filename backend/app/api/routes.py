from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import DataSeries, FrequencyCode, Indicator, Observation
from app.schemas.data import ObservationOut
from app.schemas.indicator import IndicatorOut
from app.schemas.series import SeriesOut

router = APIRouter(prefix="/api", tags=["public"])


@router.get("/indicators", response_model=list[IndicatorOut])
def list_indicators(
    q: str | None = Query(default=None, description="Recherche sur code/nom"),
    frequency: str | None = Query(default=None, description="Filtre fréquence: D,W,M,Q,S,A"),
    sector_id: int | None = Query(default=None, ge=1),
    published_only: bool = Query(default=False),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(Indicator)

    if q:
        search = f"%{q}%"
        stmt = stmt.where((Indicator.code.ilike(search)) | (Indicator.name.ilike(search)))
    if frequency:
        try:
            frequency_enum = FrequencyCode(frequency.upper())
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid frequency value") from exc
        stmt = stmt.where(Indicator.frequency == frequency_enum)
    if sector_id:
        stmt = stmt.where(Indicator.sector_id == sector_id)
    if published_only:
        stmt = stmt.where(Indicator.workflow_state == "PUBLIE")

    stmt = stmt.order_by(Indicator.code).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()


@router.get("/indicators/{indicator_id}", response_model=IndicatorOut)
def get_indicator(indicator_id: int, db: Session = Depends(get_db)):
    indicator = db.execute(select(Indicator).where(Indicator.id == indicator_id)).scalar_one_or_none()
    if indicator is None:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return indicator


@router.get("/series", response_model=list[SeriesOut])
def list_series(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(DataSeries).order_by(DataSeries.id).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()


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
