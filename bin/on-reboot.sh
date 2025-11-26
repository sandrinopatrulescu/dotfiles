#!/bin/bash
set -euo pipefail

DOTSS="/dev/null"
source ~/.env

timestamp=$(date +"%Y-%m-%d_%H-%M-%S.%3N")

{
    echo "==== [${timestamp}] $(date) ===="
    echo ">>> deno upgrade"
    ~/.deno/bin/deno upgrade

    echo
    echo ">>> pip install yt-dlp -U"
    ~/.local/bin/pip install -U yt-dlp
} >> "$LOGS/on-reboot_${timestamp}.log" 2>&1
