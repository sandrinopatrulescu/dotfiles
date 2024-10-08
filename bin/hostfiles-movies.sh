#!/bin/bash
shopt -s expand_aliases

. ~/.alias

cd /mnt/e/torrents-downloads
echo "[$(fdatei)] STARTING..." >> ~/logs/hostfiles-movies.log
python3 -m http.server 9001