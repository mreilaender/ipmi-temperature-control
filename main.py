import argparse
import pathlib
import subprocess
import json
from typing import Tuple, Type
import yaml
import logging

from config import Main
from smartctl_result_model import SmartCtlJsonOutput

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
                    prog='IPMI temperature control using smartctl to read temperatures',
                    description='Controls temperatures on an IPMI instance using temperatures read from smartctl')

parser.add_argument('-c', '--config-file', required=True, help="Path to the yaml config file",
                    dest="config_file")

args = parser.parse_args()


def read_yaml(file_path: str):
    with open(file_path, 'r') as stream:
        config = yaml.safe_load(stream)

    return Main(**config)


config = read_yaml(args.config_file)

for device in config.devices:
    result = subprocess.run(["smartctl", "-a", device.path, "-j"], capture_output=True)
    result_json = json.loads(result.stdout)

    logger.debug("Parsing output from smartctl:")
    logger.debug(result_json)

    smartctl_result = SmartCtlJsonOutput(**result_json)
    smartctl = smartctl_result.smartctl

    exit_status = smartctl_result.smartctl.exit_status
    print("Result in binary: %s" % format(exit_status, "b"))

    if(smartctl_result.smartctl.exit_status > 0):
        exit_status_binary = format(exit_status, "b")
        if(exit_status_binary[1] == 1):
            logger.error("Could not read device info for %s", device.path)
            logger.error(smartctl.messages[0].string)
            continue

        if(exit_status_binary[7] == 1):
            logger.debug("The device self-test log contains records of errors. [ATA only] Failed self-tests outdated by a newer successful extended self-test are ignored.")

        logger.warning("Got non 0 exit status (%d) for device (%s)" % (exit_status, device.path))
        logger.debug("Exit status in binary: %s" % exit_status_binary)

    temperature = smartctl_result.temperature.current

    print("Current drive (%s) temperature is %d C" % (device.path, temperature))