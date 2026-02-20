from datetime import datetime

from pydantic import BaseModel


class IndicatorOut(BaseModel):
    id: int
    code: str
    name: str
    frequency: str
    unit: str
    source: str
    workflow_state: str
    created_at: datetime

    class Config:
        from_attributes = True
