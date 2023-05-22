#!/bin/bash
source ~/.bash_aliases
source $XANDRA_RESOURCES/xandra_common_bash.sh

shopt -s expand_aliases
alias exit='report_exit_to_xandra; exit'

SCRIPT_NAME="run_test.sh"
print_wrapper_header "$SCRIPT_NAME"
source ./$SCRIPT_NAME
report_exit_to_xandra
exit $?
