#!/bin/bash

# crontab -e
# 0 11 * * * /home/melody/covid19/_one_day_fetch.sh

COVID19_PATH=/home/melody/covid19

source $COVID19_PATH/venv/bin/activate
python3 $COVID19_PATH/1_fetch_one_day_total_number.py
python3 $COVID19_PATH/2_output_trend_picture.py
deactivate

rm -f *.pdf
rm -f *.png