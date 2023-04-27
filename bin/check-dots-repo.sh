#!/bin/bash

sleep 1
# set the path to your git repository
repo_path="/mnt/e/dotfiles"

# check if the repository has changed
cd "$repo_path" || { for _ in {1..98}; do notify-send "dotfiles UPDATE" "COULD NOT FIND REPO PATH"; done; exit; }
#if true; then
if [[ $(git fetch --dry-run 2>&1 | grep -c -E '^\s*[a-zA-Z]') -gt 0 ]]; then
    # if there are changes, display a notification
    # repeat command to update the notification
    for _ in {1..98}; do notify-send "dotfiles UPDATE" "Git repository has changed\t\t\t"; done
fi
