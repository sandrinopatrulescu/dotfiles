#!/usr/bin/env bash
set -euo pipefail

# Requires: sudo apt install xdotool

MONITOR="${1:-}"

if [[ -z "$MONITOR" ]]; then
  echo "Usage: $0 <monitor_number: 1|2|3>" >&2
  exit 2
fi

# tiny delays for reliability (tweak if needed)
DELAY_KEY=0.10
DELAY_MOVE=0.05

case "$MONITOR" in
  1) x1=0    ; y1=0 ; x2=1920 ; y2=1080 ;;
  2) x1=1920 ; y1=0 ; x2=3840 ; y2=1080 ;;
  3) x1=3840 ; y1=0 ; x2=5760 ; y2=1080 ;;
  *)
    echo "Invalid monitor: '$MONITOR' (expected 1, 2, or 3)" >&2
    exit 2
    ;;
esac

# 1) Trigger xfce4-screenshot rectangle selection (Alt+S)
xdotool key --clearmodifiers "Alt+s"
sleep "$DELAY_KEY"

# 2) Drag rectangle from top-left to bottom-right of chosen monitor
xdotool mousemove --sync "$x1" "$y1"
sleep "$DELAY_MOVE"

xdotool mousedown 1
sleep "$DELAY_MOVE"

xdotool mousemove --sync "$x2" "$y2"
sleep "$DELAY_MOVE"

xdotool mouseup 1

