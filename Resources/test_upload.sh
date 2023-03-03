#!/bin/bash
while getopts s: OPT; do
    case "${OPT}" in
        "s")
            BSN=${OPTARG}
            ;;
        *)
            echo "Wrong Parameter..."
            echo "Usage: $(basename $0) -s BSN"
            exit 1
            ;;
    esac
done
echo "Test Upload BSN: ${BSN}"
