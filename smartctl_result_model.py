from typing import List, Optional

from pydantic import BaseModel


class Messages(BaseModel):
    string: str
    severity: str


class Temperature(BaseModel):
    current: int
    drive_trip: Optional[int] = None


class SmartCtlInner(BaseModel):
    exit_status: int
    messages: Optional[List[Messages]] = None


class SmartCtlJsonOutput(BaseModel):
    smartctl: SmartCtlInner
    temperature: Optional[Temperature] = None
