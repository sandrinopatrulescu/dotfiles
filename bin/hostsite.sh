#!/bin/bash
shopt -s expand_aliases

. ~/.alias

cd /mnt/e/az/public/ || \
    { echo "[$(fdatei)] ERROR: Could not cd to /mnt/e/az/public/">> ~/logs/hostsite.log;  exit 1; }
echo "[$(fdatei)] STARTING..." >> ~/logs/hostsite.log
python3 -m http.server 9000
