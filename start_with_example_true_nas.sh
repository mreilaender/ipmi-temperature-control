#!/usr/bin/env bash

venv/bin/python main.py --config-file config_true-nas.yaml --ipmi-host $1 --ipmi-username $2 --ipmi-password $3
