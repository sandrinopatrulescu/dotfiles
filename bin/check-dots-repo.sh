#!/bin/bash
#set -x

. ~/.env
. "$DOTS"/linux/functions.sh


internetConnectionTrials=20
while ! is_internet_working && [ $internetConnectionTrials -gt 0 ]; do
    ((internetConnectionTrials--))
    repeat 5 notify-send "dotfiles UPDATE" "Internet not working\n${internetConnectionTrials} trials left"
    sleep 6.5
done

if ! is_internet_working; then
    repeat 5 notify-send "dotfiles UPDATE" "Internet not working... EXITING\nPlease connect to internet and run $(basename $0)"
else
    cd "$DOTS" || { repeat 98 notify-send "dotfiles UPDATE" "COULD NOT FIND REPO PATH"; exit; }
    # check if the repository has changed
    #if true; then
    if [[ $(git fetch --dry-run 2>&1 | grep -v "X11 forwarding" | grep -c -E '^\s*[a-zA-Z]') -gt 0 ]]; then
        # if there are changes, display a notification
        # repeat command to update the notification
        repeat 98 notify-send "dotfiles UPDATE" "Git repository has changed\t\t\t"
    else
        repeat 3 notify-send "dotfiles UPDATE" "No changes\t\t\t"
    fi
fi
