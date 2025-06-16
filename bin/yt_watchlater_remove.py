#!/usr/bin/env python3
import os
import sys

if len(sys.argv) != 2:
    print(f'Usage: {sys.argv[0]} <videos_file_path>')
    sys.exit(1)

videos_file_path = sys.argv[1]
lines = open(videos_file_path, 'r').read().splitlines()

for i, line in enumerate(lines):
    tokens = line.split(';')
    title = tokens[0]
    video_url = tokens[1]

    print(f"{i + 1}. {video_url}: {title}")
    os.system(f"open {video_url}")
    while True:
        os.system("sleep 1")
        if input("Enter 'ok' to continue: ") == "ok":
            break

# combine with "google-chrome --auto-open-devtools-for-tabs" and:
"""
#!/bin/bash
set -x

date
for i in {1..30}; do
    echo "Iteration $i"
    
    # 1. Alt+Tab (switch window)
    xdotool key Alt+Tab
    sleep 3
    
    # 2. Ctrl+Shift+V (paste)
    echo "ok" | xclip -sel clip
    xdotool key ctrl+v
    sleep 1
    
    # 3. Press Enter
    xdotool key KP_Enter
    sleep 5
    
    # 4. Mouse click at (x=100, y=200) — change as needed (xdotool getmouselocation)
    # x:3332 y:101
    xdotool mousemove 3332 101 click 1
    sleep 5
    
    # 5. Ctrl+W (close tab/window)
    xdotool key ctrl+w
    sleep 0.5
done
date
"""
