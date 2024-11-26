#!/bin/bash

ls /home/*/Music/music/ |
    sed 's/ - .*//' |
    sort -u |
    jq -Rrsc 'split("\n") | "\(.)"' |
    sed 's/,""//g' >artists.json

source venv/bin/activate
python main.py >>log
