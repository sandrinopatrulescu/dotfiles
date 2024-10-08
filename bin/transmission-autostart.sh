#!/bin/bash
transmission-gtk &
sleep 1
wmctrl -r Transmission -t $(($(xfconf-query -c xfwm4 -p /general/workspace_count) - 1))