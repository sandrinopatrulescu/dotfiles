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
    ~/.local/bin/pip install -U yt-dlp
} >> "$LOGS/${script_name}_${timestamp}.log" 2>&1
