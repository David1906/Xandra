#!/bin/bash
source ~/.bash_aliases
source $XANDRA_RESOURCES/xandra_common_bash.sh

report_start_to_xandra

SCRIPT_NAME="chk_led_all_on.sh"
print_wrapper_header "$SCRIPT_NAME"

function fake_basename() {
    echo $SCRIPT_NAME
}
shopt -s expand_aliases
alias basename='fake_basename'

(bash ./"$SCRIPT_NAME" "$@")
exitCode=$?

unalias basename 2>/dev/null

if [ $exitCode -ne 0 ]; then
    report_exit_to_xandra "$SCRIPT_NAME"
fi
exit $exitCode
