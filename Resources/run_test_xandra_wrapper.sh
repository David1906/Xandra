#!/bin/bash

report_exit_to_xandra() {
    current_wd="$(pwd)"

    source  ~/.bash_aliases
    xandra_resources=$XANDRA_BASE_PATH/Resources
    python3 send_station_test_finished.py --ip "$XANDRA_FIXTURE_IP" --sn "${BSN}" --ln "${file_name}"
    
    cd $current_wd
    unalias exit
}

shopt -s expand_aliases
alias exit='report_exit_to_xandra; exit'

source ./run_test.sh
report_exit_to_xandra
exit $?
