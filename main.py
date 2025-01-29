import subprocess
import json

devices = ["/dev/sdc", "/dev/sdd", "/dev/sdf", "/dev/sde"]

for device in devices:
    result = subprocess.run(["smartctl", device, "-j"], capture_output=True)
    result_json = json.loads(result.stdout)
    current_temp = result_json['temperature']['current']
    print(current_temp)