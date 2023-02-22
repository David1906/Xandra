#!/bin/bash
RESULTFILE="/usr/local/Foxconn/automation/Xandra/Resources/chk_station_yield.result"
python3 /usr/local/Foxconn/automation/Xandra/Resources/chk_station_yield.py
read -t 2 -p "Validating yield..."