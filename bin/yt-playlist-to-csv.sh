#!/bin/bash

PLAYLIST_ID="PLqRTNdk3LL2hwXxYAW_-KY5kHH4V0U_EL"
OUTPUT_FILE="" # default is PLAYLIST_NAME.csv (where PLAYLIST_NAME will be replaced from the response)
COMPACT=""
INCLUDE_AVAILABILITY=""

# https://stackoverflow.com/questions/192249/how-do-i-parse-command-line-arguments-in-bash
POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        -pi|--playlist-id)
            PLAYLIST_ID="$2"
            shift # past argument
            shift # past value
            ;;
        -p|--playlist)
            PLAYLIST_ID="$(echo "$2" | /usr/bin/sed -n 's/.*list=\(.*\)/\1/p')"
            shift # past argument
            shift # past value
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift # past argument
            shift # past value
            ;;
        --compact)
            COMPACT="--compat-options no-youtube-unavailable-videos"
            shift # past argument
            ;;
        -a)
            INCLUDE_AVAILABILITY="yes"
            shift # past argument
            ;;
        -*)
            echo "Unknown option $1"
            exit 1
            ;;
        *)
            POSITIONAL_ARGS+=("$1") # save positional arg
            shift # past argument
            ;;
    esac
done
set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters


function join_by { # https://stackoverflow.com/questions/1527049/how-can-i-join-elements-of-a-bash-array-into-a-delimited-string
    local d=${1-} f=${2-}
    if shift 2; then
        printf "%s" "$f" "${@/#/$d}"
    fi
}

# playlist entry: https://pastebin.com/dry0Tz1G
playlist_url="https://www.youtube.com/playlist?list=$PLAYLIST_ID"
command="yt-dlp $COMPACT --flat-playlist -j $playlist_url "

echo "running: $command"

fields=("title" "url" "channel" "channel_url" "uploader")
delimiter=";"

playlistName=""

# read from file descriptor 3 to avoid collision with the other read
# (How to read input inside a while loop while reading from a file?) https://stackoverflow.com/questions/46373633/how-to-read-input-inside-a-while-loop-while-reading-from-a-file
while read -r -u 3 json; do
    if [ -z "${playlistName}" ]; then
        playlistName=$(jq -r .playlist <<< "$json")
        headerRow="$(join_by $delimiter "${fields[@]}")"

        if [ -n "$INCLUDE_AVAILABILITY" ]; then
            extra_fields=("available" "unavailability reason")
            headerRow="$(join_by $delimiter "$headerRow" "${extra_fields[@]}")"
        fi

        if [ -s "${OUTPUT_FILE:-${playlistName}.csv}" ]; then
            echo "File ${OUTPUT_FILE:-${playlistName}.csv} already exists. Overwrite? [y/*]"
            read -r overwrite

            if [ "$overwrite" != "y" ]; then
                echo "Exiting"
                exit 0
            else
                truncate -s 0 "${OUTPUT_FILE:-${playlistName}.csv}"
            fi
        fi

        echo "$headerRow" | tee -a "${OUTPUT_FILE:-${playlistName}.csv}"
    fi

    line=""

    for field in "${fields[@]}"; do
        column=$(jq -r ."$field" <<< "$json")
        line="$(join_by $delimiter "$line" "$column")"
    done

    if [ -n "$INCLUDE_AVAILABILITY" ]; then
        available="yes"
        unavailabilityReason=""

        url=$(jq -r .url <<< "$json")
        stderr="$(yt-dlp -s "$url" 2>&1 >/dev/null)"

        if [ $? -ne 0 ]; then
            available="no"
            unavailabilityReason="$stderr"
        fi

        line="$(join_by $delimiter "$line" "$available" "$unavailabilityReason")"
    fi

    line="${line:1}" # remove first delimiter
    echo "$line" | tee -a "${OUTPUT_FILE:-${playlistName}.csv}"
done 3<<< "$($command)"
