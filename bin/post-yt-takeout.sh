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
yt-playlist-to-csv.sh -a


# git add commit and push
cd "$gitDir"
git add .
git commit -m "takeout of $timestamp"
git push