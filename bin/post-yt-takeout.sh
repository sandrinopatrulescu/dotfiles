#!/bin/bash

set -e # fail on error (see man set)


start=$(date +%s)


#region setup
takeoutDir="/mnt/e/backup/google-takeout-yt_wo_uploads"
gitDir="/mnt/e/git/sp-backups-z/google-takeout-youtube"

cd "$takeoutDir"
[ -d "Takeout" ] && { echo "Takeout dir already exists. Do something about it and run again"; exit 1; }

latestTakeoutZip="$(find $takeoutDir  -iname "takeout-*Z-001.zip" | tail -1)"
latestTakeout="$(find $takeoutDir  -iname "takeout-*Z-001.zip" | tail -1 | sed -E 's@^\./@@;s@\.zip$@@')"
timestamp="$(echo "$latestTakeout" | sed -E 's@(.*/)*takeout-(.*)-001$@\2@')"

echo "latest takeout zip: $latestTakeoutZip"
echo "latest takeout: $latestTakeout"
echo "timestamp: $timestamp"
#endregion


unzip "$latestTakeoutZip"
mv "Takeout" "$latestTakeout"
cp -r "${latestTakeout}/YouTube and YouTube Music/"* "$gitDir"


#region custom
customDir="$gitDir/custom"
cd "$customDir"

yt_playlist_list.py "PLqRTNdk3LL2hwXxYAW_-KY5kHH4V0U_EL" "2 add queue re LIST"

# use compact mode, since availability would take too long
# 2 add queue re
yt-playlist-to-csv.sh --overwrite
yt-playlist-to-csv.sh --overwrite --compact -o "2 add queue re COMPACT.csv"
# 2 add queue v2
yt-playlist-to-csv.sh --overwrite -pi "PLqRTNdk3LL2gfqnoHdfns2pJi13pwPIpO"
yt-playlist-to-csv.sh --overwrite --compact -pi "PLqRTNdk3LL2gfqnoHdfns2pJi13pwPIpO" -o "2 add queue v2 COMPACT.csv"
#endregion


# git add commit and push
cd "$gitDir"
git add .
git commit -m "takeout of $timestamp"
git push

wc -l custom/"2 add queue "*.csv

end=$(date +%s)
echo Execution time was `expr $end - $start` seconds.
