from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class ProjectStatus(BaseModel):
    project: str
    status: str
    layers: list[str]
    docs: list[str]


class HealthResponse(BaseModel):
    status: str
    database: str


class PredictionRequest(BaseModel):
    date: date
    store_id: int = Field(gt=0)
    department_id: int = Field(gt=0)
    holiday_flag: bool = False
    store_type: str = Field(pattern="^[ABC]$")
    store_size: int = Field(gt=0)
    temperature: float
    fuel_price: float = Field(gt=0)
    markdown_1: float = 0
    markdown_2: float = 0
    markdown_3: float = 0
    markdown_4: float = 0
    markdown_5: float = 0
    cpi: float = Field(gt=0)
    unemployment_rate: float = Field(ge=0)


class PredictionResponse(BaseModel):
    predicted_weekly_sales: float
    model: str
