# Usage


## Exit status

Exit status values are bitmasks and described here: https://linux.die.net/man/8/smartctl

## E3C246D4U2-2T ipmitool raw commands

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