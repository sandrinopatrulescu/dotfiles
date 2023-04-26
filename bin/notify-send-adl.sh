#!/bin/bash
#sleep 0
notify-send "apt download & list" "$(sudo apt update && apt list --upgradable)"
exit 0