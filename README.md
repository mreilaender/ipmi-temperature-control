# ASRockRack E3C246D4U2-2T IPMI temperature control

Sets fan speeds via remote IPMI according to a fan curve configured via a yaml file based on disk temperatures. If any
of the disks exceeds a temperature from the configuration file the fan speeds will be set accordingly for `FRNT_FAN2`
and `FRNT_FAN3`. All other fans will be set to 100%.

Currently only works for an ASRockRack E3C246D4U2-2T since the IPMI commands used are raw commands that presumably only 
work for this board. Heavily inspired by [coledeck](https://github.com/coledeck/asrock-pwm-ipmi). Thanks for your help :)

## Usage

In case you want this installed on a True-NAS system (which doesn't let you install anything on the OS itself) you need
to create a venv using python. True-NAS should've python installed by default:

```shell
python -m venv .venv
source .venv/bin/activate
pip install .
```

This creates a python script in `.venv/bin/ipmi-temperature-control` which can be used with a 
[systemd service file](#example-systemd-unit-file)

## Documentation

### Exit status

Exit status values are bitmasks and described here: https://linux.die.net/man/8/smartctl

### E3C246D4U2-2T ipmitool raw commands

To read fan speeds:
```shell
ipmitool raw 0x3a 0x02
```

or more visually appealing:

```shell
ipmitool senors | grep -i fan
```

To set fan speeds is a bit more tricky. The format is as follows:

Reading the fan speeds give you:
```
ipmitool raw 0x3a 0x02
64 64 64 64 64 64 64 64
```

which returns 8 values (in this case all 64er meaning 100%). Each of those represent a fan header on the motherboard in
the following order:

```text
CPU_FAN1 ? ? REAR_FAN2 FRNT_FAN1 FRNT_FAN2 FRNT_FAN3 ?
```

## Example systemd unit file

Place in a `/etc/systemd/system/ipmi-temperature-control.service` file, reload the daemon `systemctl daemon-reload` and 
enable the service via `systemctl enable ipmi-temperature-control.service`.

```
[Unit]
Description=IPMI temperature control

[Service]
Type=simple
WorkingDirectory=/root/ipmi-temperature-control
ExecStart=/root/ipmi-temperature-control/.venv/bin/ipmi-temperature-control \
    --config-file <path-to-config-file> \
    --ipmi-host <ipmi-host> \
    --ipmi-username <ipmi-user> \
    --ipmi-password "<ipmi-password>" \
    --log-file /var/log/ipmi-temperature-control.log

[Install]
WantedBy=default.target
```