from typing import List

from pydantic import BaseModel, Field


class Device(BaseModel):
    path: str
    fan_curve: dict = Field(alias="fan-curve")


class Main(BaseModel):
    test: str
    devices: List[Device]