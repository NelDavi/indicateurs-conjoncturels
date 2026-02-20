from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class IndicatorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    frequency: str
    unit: str
    source: str
    workflow_state: str
    created_at: datetime
