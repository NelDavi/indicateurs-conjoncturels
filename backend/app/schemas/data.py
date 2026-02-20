from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class ObservationOut(BaseModel):
    series_id: int
    period_date: date
    value: Decimal
    revision_number: int
    is_published: bool

    class Config:
        from_attributes = True
