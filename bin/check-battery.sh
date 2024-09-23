#!/bin/bash

# systemctl list-timers

timestamp="$(date +%Y-%m-%d_%H-%M-%S)"
capacity="$(cat /sys/class/power_supply/BAT1/capacity)"
status="$(cat /sys/class/power_supply/BAT1/status)"

echo "${timestamp},${capacity},${status}" >> "$LOGS/battery-status.log"

if [ "$capacity" -lt 30 ] && [ "$status" == "Discharging" ]; then
    /mnt/e/dotfiles/bin/notify_telegram_bot.py -m "[${timestamp}] $(hostname) battery low: $capacity%"
fi

exit 0
