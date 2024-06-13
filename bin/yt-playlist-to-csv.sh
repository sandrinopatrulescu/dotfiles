#!/bin/bash


function join_by { # https://stackoverflow.com/questions/1527049/how-can-i-join-elements-of-a-bash-array-into-a-delimited-string
    local d=${1-} f=${2-}
    if shift 2; then
        printf "%s" "$f" "${@/#/$d}"
        echo
    fi
}

playlist_id="${1:-PLqRTNdk3LL2hwXxYAW_-KY5kHH4V0U_EL}"
output_file="$2"

playlist_url="https://www.youtube.com/playlist?list=$playlist_id"

[ -n "$COMPACT" ] && extra_args="--compat-options no-youtube-unavailable-videos"
command="yt-dlp $extra_args --flat-playlist -j $playlist_url "

echo "running: $command"

fields=("title" "url" "channel" "channel_url" "uploader")
delimiter=";"

playlistName=""

while read -r json; do
    if [ -z "$playlistName" ]; then
        playlistName=$(jq -r .playlist <<< "$json")
        join_by $delimiter "index" "${fields[@]}" | tee -a "${output_file:-$playlistName.csv}"
    fi
    line=$(jq -r .playlist_index <<< "$json")

    for field in "${fields[@]}"; do
        column=$(jq -r ."$field" <<< "$json")
        line="$line$delimiter$column"
    done

    echo "$line" | tee -a "${output_file:-$playlistName.csv}"
done <<< "$($command)"
