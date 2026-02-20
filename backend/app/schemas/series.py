from pydantic import BaseModel


class SeriesOut(BaseModel):
    id: int
    indicator_id: int
    code: str
    name: str
    decimals: int

    class Config:
        from_attributes = True
