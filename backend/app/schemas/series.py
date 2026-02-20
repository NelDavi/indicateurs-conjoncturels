from pydantic import BaseModel
from pydantic import ConfigDict


class SeriesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    indicator_id: int
    code: str
    name: str
    decimals: int
