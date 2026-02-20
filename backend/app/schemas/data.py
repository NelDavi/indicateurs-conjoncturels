from datetime import date
from decimal import Decimal

from pydantic import BaseModel
from pydantic import ConfigDict


class ObservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    series_id: int
    period_date: date
    value: Decimal
    revision_number: int
    is_published: bool
