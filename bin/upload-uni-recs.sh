#!/bin/bash

source "$DOTS/functions"

[ -d /media/kamui/BackupHDD ] || {
    udisksctl mount --block-device /dev/sdb2 || { echo "failed to mount hdd" && exit 1; } 
}

startTimestamp="$(date +%Y-%m-%d_%H-%M-%S)"
outputFile="/media/kamui/BackupHDD/UBB_IE_2020-2023_Recordings-Info/upload_recs_on_blompu_output/${startTimestamp}.txt"
recsDir="/media/kamui/BackupHDD/UBB_IE_2020-2023_Recordings/"

echo "${startTimestamp}" | tee -a "$outputFile"
while true; do
    rclone --bwlimit "00:05,off 07:30,1M" -v copy "$recsDir" blompu:uni-stuff/UBB_IE_2020-2023_Recordings |& tee -a "$outputFile"
    sleepTime=60
    echo "sleeping $sleepTime seconds"
    sleep $sleepTime
done
date +%Y-%m-%d_%H-%M-%S | tee -a "$outputFile"
beep 2
