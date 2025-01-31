from typing import List, Optional

from pydantic import BaseModel


class Messages(BaseModel):
    string: str
    severity: str


class SmartCtlInner(BaseModel):
    exit_status: int
    messages: Optional[List[Messages]] = None


class SmartCtlJsonOutput(BaseModel):
    smartctl: SmartCtlInner
