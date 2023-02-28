#!/bin/bash
python3 ./Resources/chk_station_is_disabled.py
read -r -t 2
python3 ./Resources/chk_station_test_finished.py
exit $?