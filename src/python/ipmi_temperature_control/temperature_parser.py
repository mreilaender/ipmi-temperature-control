import subprocess
import json

from .config import Main
from .smartctl import SmartCtlJsonOutput


class TemperatureParser:
    def __init__(self, config: Main, logger):
        self.config = config
        self.logger = logger

    def parse(self):
        target_fan_speed = self.config.default_speed

        self.logger.debug("Default fan speed is %s %s", target_fan_speed, '%')

        for device in self.config.devices:
            result = subprocess.run(["smartctl", "-a", device.path, "-j"], capture_output=True)
            result_json = json.loads(result.stdout)

            self.logger.debug("Parsing output from smartctl:")
            self.logger.debug(result_json)

            smartctl_result = SmartCtlJsonOutput(**result_json)
            smartctl = smartctl_result.smartctl

            exit_status = smartctl_result.get_exit_status()

            if not (
                    exit_status.is_device_open_error() or exit_status.is_cli_parse_error() or exit_status.is_disk_failing()):
                current_temperature = smartctl_result.temperature.current

                self.logger.info("Current temperature of %s is %s C", device.path, current_temperature)

                for temperature_limit, fan_speed in self.config.fan_curve.items():
                    if current_temperature >= temperature_limit and target_fan_speed < fan_speed:
                        self.logger.debug(
                            "Temperature of drive %d exceeded temperature limit of %d with fan speed of %d '%'",
                            current_temperature, temperature_limit, fan_speed)
                        target_fan_speed = fan_speed

            if not exit_status.is_successful():
                self.logger.warning("Got non 0 exit status (decimal: %d, binary: %s) for device (%s)",
                               exit_status.decimal_value, exit_status.binary_value, device.path)

            if exit_status.has_test_errors():
                self.logger.debug(
                    "The device self-test log contains records of errors. [ATA only] Failed self-tests outdated by a "
                    "newer successful extended self-test are ignored.")

            if exit_status.is_device_open_error():
                self.logger.error("Could not read device info for %s", device.path)
                self.logger.error(smartctl.messages[0].string)
                continue