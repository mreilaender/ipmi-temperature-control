import subprocess
import json
from time import sleep

from typing import List, Optional
from pydantic import BaseModel
from threading import Thread


class Messages(BaseModel):
    string: str
    severity: str


class Temperature(BaseModel):
    current: int
    drive_trip: Optional[int] = None


class Device(BaseModel):
    name: str


class SmartCtlInner(BaseModel):
    exit_status: int
    messages: Optional[List[Messages]] = None


class SmartCtlJsonOutput(BaseModel):
    smartctl: SmartCtlInner
    temperature: Optional[Temperature] = None
    device: Optional[Device]

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

    def is_cli_parse_error(self):
        return len(self.binary_value) >= 1 and self.binary_value[0] == 1

    def is_device_open_error(self):
        return len(self.binary_value) >= 2 and self.binary_value[1] == 1

    def is_command_failed(self):
        return len(self.binary_value) >= 3 and self.binary_value[2] == 1

    def is_disk_failing(self):
        return len(self.binary_value) >= 4 and self.binary_value[3] == 1

    def is_prefail_attributes(self):
        return len(self.binary_value) >= 5 and self.binary_value[4] == 1

    def is_threshold_reached(self):
        return len(self.binary_value) >= 6 and self.binary_value[5] == 1

    def has_error_log(self):
        return len(self.binary_value) >= 7 and self.binary_value[6] == 1

    def has_test_errors(self):
        return len(self.binary_value) >= 8 and self.binary_value[7] == 1

    def is_successful(self):
        return self.decimal_value == 0

class ThreadExecutor(Thread):
    def __init__(self, logger, device_path: str):
        super().__init__()
        self.result: Optional[SmartCtlJsonOutput] = None
        self.logger = logger
        self.device_path = device_path

    def run(self):
        self.logger.info("Reading smartctl output from %s" % self.device_path)
        result = subprocess.run(["smartctl", "-a", self.device_path, "-j"], capture_output=True)
        result_json = json.loads(result.stdout)

        self.logger.debug("Parsing output from smartctl:")
        self.logger.debug(result_json)

        self.result = SmartCtlJsonOutput(**result_json)

        self.logger.info("Smartctl output parsed from %s" % self.device_path)