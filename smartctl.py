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

    def get_exit_status(self):
        return ExitStatus(self.smartctl.exit_status)


class ExitStatus:
    """
    Convert exit status codes from the smartctl command using a bitmask
    See https://linux.die.net/man/8/smartctl under "Return Values"
    """
    def __init__(self, decimal_value: int):
        self.decimal_value = decimal_value
        self.binary_value = format(decimal_value, "b")

    def is_read_error(self):
        return not self.is_successful() and self.binary_value[1] == 1

    def has_test_errors(self):
        return not self.is_successful() and self.binary_value[7] == 1

    def is_successful(self):
        return self.decimal_value == 0