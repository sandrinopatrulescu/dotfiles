#!/bin/bash
# add full path to Keyboard -> Application Shortcuts with F8 as the shortcut

PIDFILE="/tmp/autoscroll_up.pid"

# If the script is already running, stop it
if [ -f "$PIDFILE" ]; then
    kill "$(cat "$PIDFILE")" && rm "$PIDFILE"
    notify-send "Auto Scroll" "Stopped"
    exit 0
fi

# Otherwise, start auto-scrolling
echo $$ > "$PIDFILE"
notify-send "Auto Scroll" "Started (scrolling up)"
while true; do
    for i in $(seq 1 20); do xdotool click 4; done
#    xdotool click 4
#    xdotool click 4
#    xdotool click 4
#    sleep 0.1
done
