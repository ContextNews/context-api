from datetime import date

from pydantic import BaseModel


class TSSourceSchema(BaseModel):
    id: int
    name: str
    url: str | None = None


class TSEntitySchema(BaseModel):
    id: str
    name: str
    entity_type: str


class TSIndicatorSchema(BaseModel):
    id: str
    name: str
    unit: str | None = None
    frequency: str | None = None
    source: TSSourceSchema


class TSDatapointSchema(BaseModel):
    date: date
    value: float | None


class TSSeriesSchema(BaseModel):
    indicator: TSIndicatorSchema
    entity: TSEntitySchema
    datapoints: list[TSDatapointSchema]
