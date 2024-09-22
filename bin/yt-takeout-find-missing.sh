#!/bin/bash


[ "$1" == "-q" ] && isVerbose=false || isVerbose=true
dryRun=${DRY_RUN:-false}

cd /mnt/e/git/sp-backups-z/google-takeout-youtube/custom || { echo "cd failed"; exit 1; }

$isVerbose && echo "Is dry run? $dryRun"

if $dryRun; then
    diff_result="$(diff "/mnt/e/Scratch/2024-09-14_09-07-44_yt-takeout_extract-deleted-csv-from-2aqr/"{regular,compact}".csv")" # sample diff result
else
    diff_result="$(diff "2 add queue re.csv" "2 add queue re COMPACT.csv")"
fi

$isVerbose && echo -e "\nDiff:\n$diff_result"

ids="$(echo "${diff_result}" | awk -F';' '$1 ~ /(Deleted|Private) video/ {split($2,a,"="); print a[2]}')"
$isVerbose && echo -e "\nIds:\n$ids"

if [ -z "$ids" ]; then
    echo "[$(basename "$0")] No /(Deleted|Private) video/ found"
    exit 0
fi

if $dryRun; then
    complete_commit_log="a191cf92"
else
    complete_commit_log="$(git log -1 --oneline --grep="\[2aqr COMPLETE\]")"
fi

$isVerbose && echo -e "\nComplete commit log:\n$complete_commit_log"

commit_hash="$(echo "$complete_commit_log" | awk '{print $1}')"
$isVerbose && echo -e "\nCommit hash:\n$commit_hash"

complete_csv="$(git show "$commit_hash":"custom/2 add queue re.csv")"

content_of_replace_csv=""

$isVerbose && echo -e "\nProcessing ids:"
for id in $ids; do
    name="$(echo "${complete_csv}" | awk -F';' -v id="$id" '$2 ~ id {print $1}')"
    $isVerbose && echo -e "id: $id | name: $name"
    content_of_replace_csv="${content_of_replace_csv}${id};${name};\n"
done

echo -e "\nContent of replace csv:\n$content_of_replace_csv"


$dryRun && dryRunSuffix="_dry-run" || dryRunSuffix=""
replace_csv_path="/mnt/e/Scratch/yt_playlist_item_replace.py_old-new-csv/$(date +%Y-%m-%d_%H-%M-%S)${dryRunSuffix}.csv"
echo -ne "$content_of_replace_csv" > "$replace_csv_path"

echo "[$(basename "$0")] Created .csv file for replace at:"
echo "$replace_csv_path"

echo "Edit .csv file then run alias: yt-playlist-item-replace-2aqr"
