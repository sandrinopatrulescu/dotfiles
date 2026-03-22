#!/bin/bash
set -euo pipefail

DOTSS="/dev/null"
source ~/.env

timestamp=$(date +"%Y-%m-%d_%H-%M-%S.%3N")
script_name="$(basename "${BASH_SOURCE[0]}")"

{
    echo "==== [${timestamp}] $(date) ===="
    echo ">>> deno upgrade"
    ~/.deno/bin/deno upgrade

    echo
    echo ">>> pip install yt-dlp -U"
    # ~/.local/bin/pip install -U yt-dlp
    ~/.local/bin/pip install -U "yt-dlp[default]" # Challenge solver lib script version 0.3.2 is not supported -> https://github.com/yt-dlp/yt-dlp/issues/15887
} >> "$LOGS/${script_name}_${timestamp}.log" 2>&1
