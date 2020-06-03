#!/bin/bash

CURRENT_DIR=$(dirname $0)
ENVIRONMENT_OK=$CURRENT_DIR/check_environment_ok.tmp
CHECK_ENVINONMENT=$CURRENT_DIR/0_check_environment.sh

if [ ! -f $ENVIRONMENT_OK ]; then
    $CHECK_ENVINONMENT
    exit_stat=$?
    if [ $exit_stat -ne 0 ]; then
        exit 1
    fi
fi

source $CURRENT_DIR/venv/bin/activate
python3 $CURRENT_DIR/1_fetch_one_day_total_number.py
python3 $CURRENT_DIR/2_output_trend_picture.py
deactivate

rm -f *.pdf
rm -f *.png