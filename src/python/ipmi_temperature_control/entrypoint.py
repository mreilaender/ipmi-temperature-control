import argparse
import sys
import time
import yaml
import logging
from .config import Main
from .smartctl import ThreadExecutor
from .ipmi import IPMI

def main():
    args = parse_args(sys.argv[1:])
    print(args)
    config = read_yaml(args.config_file)

    log_level = logging.DEBUG if args.debug else logging.INFO

    if args.log_file:
        logging.basicConfig(filename=args.log_file, filemode='a', level=log_level)

    logger = logging.getLogger(__name__)

    while True:
        executors = []
        for device in config.devices:
            executor = ThreadExecutor(logger, device.path)
            executors.append(executor)
            executor.start()

        any_alive = any(list(map(is_thread_alive, executors)))
        while any_alive:
            any_alive = any(list(map(is_thread_alive, executors)))

        smartctl_results = list(map(to_results, executors))

        target_fan_speed = config.default_speed
        for smartctl_result in smartctl_results:
            smartctl = smartctl_result.smartctl
            device_name = smartctl_result.device.name
            exit_status = smartctl_result.get_exit_status()

            if not (
                    exit_status.is_device_open_error() or exit_status.is_cli_parse_error() or exit_status.is_disk_failing()):
                current_temperature = smartctl_result.temperature.current

                logger.info("Current temperature of %s is %s C", device_name, current_temperature)

                for temperature_limit, fan_speed in config.fan_curve.items():
                    if current_temperature >= temperature_limit and target_fan_speed < fan_speed:
                        logger.debug("Increasing target fan speed to %s %s due to %s exceeding temperature limit",
                                     fan_speed, "%", device_name)
                        target_fan_speed = fan_speed

            if not exit_status.is_successful():
                logger.warning("Got non 0 exit status (decimal: %d, binary: %s) for device (%s)",
                               exit_status.decimal_value, exit_status.binary_value, device_name)

            if exit_status.has_test_errors():
                logger.debug(
                    "The device self-test log contains records of errors. [ATA only] Failed self-tests outdated by a "
                    "newer successful extended self-test are ignored.")

            if exit_status.is_device_open_error():
                logger.error("Could not read device info for %s", device_name)

        logger.info("Setting fan speed to %s %s", target_fan_speed, "%")

        ipmi = IPMI(logger, args.host, args.username, args.password)

        fan_speed_hex_value = str(hex(target_fan_speed))

        logger.debug("Converting fan speed to hex: %s", fan_speed_hex_value)
        # noinspection PyListCreation
        command_args = ["raw", "0x3a", "0x01"]
        # CPU_FAN1
        command_args.append("0x64")
        # ?
        command_args.append("0x64")
        # ?
        command_args.append("0x64")
        # REAR_FAN2
        command_args.append(fan_speed_hex_value)
        # FRNT_FAN1
        command_args.append("0x64")
        # FRNT_FAN2
        command_args.append(fan_speed_hex_value)
        # FRNT_FAN3
        command_args.append(fan_speed_hex_value)
        # ?
        command_args.append("0x64")

        ipmi.execute_set_fan_speed(command_args)

        time.sleep(1)

def is_thread_alive(thread: ThreadExecutor):
    return thread.is_alive()

def to_results(thread: ThreadExecutor):
    return thread.result

def parse_args(args):
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
    parser.add_argument('-l', '--log-file', required=False, help="log file location", dest="log_file")
    parser.add_argument('--pid-file', required=False, help="pid file", dest="pid_file",
                        default="/var/run/itc.pid")

    return parser.parse_args(args)

def read_yaml(file_path: str):
    with open(file_path, 'r') as stream:
        yaml_file = yaml.safe_load(stream)

    return Main(**yaml_file)