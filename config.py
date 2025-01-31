from typing import List
from pydantic import BaseModel, Field


class Device(BaseModel):
    path: str


class Main(BaseModel):
    fan_curve: dict = Field(alias="fan-curve")
    devices: List[Device]