#!/bin/bash
source ~/.bash_aliases
source $XANDRA_RESOURCES/xandra_common_bash.sh

report_start_to_xandra

SCRIPT_NAME="boot_sol.sh"
print_wrapper_header "$SCRIPT_NAME"

function fake_basename() {
    echo $SCRIPT_NAME
}
shopt -s expand_aliases
alias basename='fake_basename'

(. ./"$SCRIPT_NAME" "$@")

unalias basename 2>/dev/null

exitCode=$?
if [ $exitCode -ne 0 ]; then
    report_exit_to_xandra
fi
exit $exitCode
