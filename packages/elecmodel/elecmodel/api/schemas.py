# packages/elecmodel/elecmodel/api/schemas.py
from pydantic import BaseModel
from typing import Optional


class CreateModelRequest(BaseModel):
    reference_id: str


class ChangeComponentsRequest(BaseModel):
    battery_type: Optional[str] = None
    inverter_type: Optional[str] = None
    solarpanel_type: Optional[str] = None
    yearly_consumption_energy: Optional[float] = None
    peak_production_power: Optional[float] = None
    solarpanel_count: Optional[int] = None
