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
