#!/bin/bash
source ~/.bash_aliases
source $XANDRA_RESOURCES/xandra_common_bash.sh

report_start_to_xandra

SCRIPT_NAME="chk_led_all_off.sh"
print_wrapper_header "$SCRIPT_NAME"
(. ./"$SCRIPT_NAME" "$@")

exitCode=$?
if [ $exitCode -ne 0 ]; then
    report_exit_to_xandra
fi
exit $exitCode
