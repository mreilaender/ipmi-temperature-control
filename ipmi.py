import io
import subprocess
import csv
from io import BytesIO


class IPMI:
    def __init__(self, host="", username="", password=""):
        self.host = host
        self.username = username
        self.password = password

    def create_command(self):
        cmd = ["ipmitool"]

        if self.host:
            cmd.append("-H")
            cmd.append(self.host)

        if self.username:
            cmd.append("-U")
            cmd.append(self.username)

        if self.password:
            cmd.append("-P")
            cmd.append("%s" % self.password)

        return cmd

    def get_sensors(self):
        cmd = self.create_command()
        cmd.append("raw")
        cmd.append("0x3a")
        cmd.append("0x02")

        result = execute_or_raise(cmd)

        speeds_raw = result.stdout[3:21].split()
        speeds = []
        for speed in speeds_raw:
            speeds.append(int(speed, 16))
        return speeds, speeds_raw

    def get_fan_speeds(self):
        cmd = self.create_command()
        cmd.append("sensor")
        cmd.append("-c")

        result = execute_or_raise(cmd)

        csv_reader = csv.reader(io.StringIO(result.stdout), delimiter=',')

        for row in csv_reader:
            print(' ,'.join(row))

    def execute_set_fan_speed(self, args):
        full_command = self.create_command()
        full_command += args

        print("Executing [%s]" % full_command)

        print(execute_or_raise(full_command))

def execute_or_raise(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stderr:
        raise Exception(result.stderr)

    return result
