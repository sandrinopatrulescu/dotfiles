#!/bin/bash
teamviewer &
sleep 2
wmctrl -r TeamViewer -t $(($(xfconf-query -c xfwm4 -p /general/workspace_count) - 1))