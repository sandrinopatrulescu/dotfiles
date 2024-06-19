#!/bin/bash

set -e # fail on error (see man set)

takeoutDir="/mnt/e/backup/google-takeout-yt_wo_uploads"
gitDir="/mnt/e/git/sp-backups-z/google-takeout-youtube"

latestTakeout="$(find $takeoutDir  -iname "takeout-*Z-001" | tail -1)"
timestamp="$(echo "$latestTakeout" | sed -E 's@(.*/)*takeout-(.*)-001@\2@')"

echo "latest takeout: $latestTakeout"
echo "timestamp: $timestamp"

cp -r "${latestTakeout}/YouTube and YouTube Music/"* "$gitDir"


customDir="$gitDir/custom"
cd "$customDir"
yt-playlist-to-csv.sh --overwrite # 2 add queue re
yt-playlist-to-csv.sh --overwrite -pi "PLqRTNdk3LL2gfqnoHdfns2pJi13pwPIpO" # 2 add queue v2
# use compact mode, since availability would take too long
yt-playlist-to-csv.sh --overwrite --compact -o "2 add queue re COMPACT.csv" # 2 add queue re
yt-playlist-to-csv.sh --overwrite --compact -pi "PLqRTNdk3LL2gfqnoHdfns2pJi13pwPIpO" -o "2 add queue v2 COMPACT.csv" # 2 add queue v2

# yt_playlist_list.py "PLqRTNdk3LL2hwXxYAW_-KY5kHH4V0U_EL" "2 add queue re LIST"

# git add commit and push
cd "$gitDir"
git add .
git commit -m "takeout of $timestamp"
git push

wc -l custom/"2 add queue "*.csv
