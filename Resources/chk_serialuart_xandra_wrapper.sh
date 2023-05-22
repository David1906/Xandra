#!/bin/bash
source ~/.bash_aliases
source $XANDRA_RESOURCES/xandra_common_bash.sh

SCRIPT_NAME="chk_serialuart.sh"
print_wrapper_header "$SCRIPT_NAME"
(./"$SCRIPT_NAME" "$@")

exitCode=$?
if [ $exitCode -ne 0 ]; then
    report_exit_to_xandra
fi
exit $exitCode
