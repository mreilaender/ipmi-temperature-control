#!/usr/bin/env bash

venv/bin/python main.py --config-file config.yaml --ipmi-host $1 --ipmi-username $2 --ipmi-password $3
