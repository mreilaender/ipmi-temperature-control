import argparse
import json
import logging
import subprocess

import yaml

from config import Main
from ipmi import IPMI
from smartctl import SmartCtlJsonOutput

parser = argparse.ArgumentParser(
    prog='IPMI temperature control using smartctl to read temperatures',
    description='Controls temperatures on an IPMI instance using temperatures read from smartctl')

parser.add_argument('-c', '--config-file', required=True, help="Path to the yaml config file",
                    dest="config_file")
parser.add_argument('-d', '--debug', required=False, default=False, help="Turn on debug logging",
                    action=argparse.BooleanOptionalAction)
parser.add_argument('-H', '--ipmi-host', required=False, help="IPMI hostname", dest="host")
parser.add_argument('-u', '--ipmi-username', required=False, help="IPMI username", dest="username")
parser.add_argument('-p', '--ipmi-password', required=False, help="IPMI password", dest="password")

args = parser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def read_yaml(file_path: str):
    with open(file_path, 'r') as stream:
        yaml_file = yaml.safe_load(stream)

    return Main(**yaml_file)


config = read_yaml(args.config_file)
target_fan_speed = config.default_speed

logger.debug("Default fan speed is %s %s", target_fan_speed, '%')

for device in config.devices:
    result = subprocess.run(["smartctl", "-a", device.path, "-j"], capture_output=True)
    result_json = json.loads(result.stdout)

    logger.debug("Parsing output from smartctl:")
    logger.debug(result_json)

    smartctl_result = SmartCtlJsonOutput(**result_json)
    smartctl = smartctl_result.smartctl

    exit_status = smartctl_result.get_exit_status()

    if not (exit_status.is_device_open_error() or exit_status.is_cli_parse_error() or exit_status.is_disk_failing()):
        current_temperature = smartctl_result.temperature.current

        logger.info("Current temperature of %s is %s C", device.path, current_temperature)

        for temperature_limit, fan_speed in config.fan_curve.items():
            if current_temperature >= temperature_limit and target_fan_speed < fan_speed:
                logger.debug("Temperature of drive %d exceeded temperature limit of %d with fan speed of %d '%'",
                             current_temperature, temperature_limit, fan_speed)
                target_fan_speed = fan_speed

    if not exit_status.is_successful():
        logger.warning("Got non 0 exit status (decimal: %d, binary: %s) for device (%s)",
                       exit_status.decimal_value, exit_status.binary_value, device.path)

    if exit_status.has_test_errors():
        logger.debug("The device self-test log contains records of errors. [ATA only] Failed self-tests outdated by a "
                     "newer successful extended self-test are ignored.")

    if exit_status.is_device_open_error():
        logger.error("Could not read device info for %s", device.path)
        logger.error(smartctl.messages[0].string)
        continue

logger.info("Fans should spin with %s %s", target_fan_speed, '%')

ipmi = IPMI(args.host, args.username, args.password)

# sensors = ipmi.get_sensors()
# logger.info("Sensors: [%s]", sensors)
#
# result = ipmi.get_fan_speeds()

args = ["raw", "0x3a", "0x01"]
# CPU_FAN1
args.append("0x64")
# ?
args.append("0x64")
# ?
args.append("0x64")
# REAR_FAN2
args.append("0x32")
# FRNT_FAN1
args.append("0x64")
# FRNT_FAN2
args.append(str(hex(target_fan_speed)))
# FRNT_FAN3
args.append(str(hex(target_fan_speed)))
# ?
args.append("0x64")

ipmi.execute_set_fan_speed(args)