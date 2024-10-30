#!/bin/bash

# how to setup systemd service w/ timer:
#   copy files -> systemctl daemon-reload -> systemctl enable x.timer -> systemctl start x.timer
# NOTICE: no symlinks from non-root partitions (see man systemctl -> Unit File Commands -> enable UNIT)

# systemctl list-timers

# crontab -e: */10 * * * * sh /mnt/e/dotfiles/bin/check-battery.sh (source: https://www.freecodecamp.org/news/cron-jobs-in-linux/)

timestamp="$(date +%Y-%m-%d_%H-%M-%S)"
capacity="$(cat /sys/class/power_supply/BAT1/capacity)"
status="$(cat /sys/class/power_supply/BAT1/status)"

echo "${timestamp},${capacity},${status}" >> "$LOGS/battery-status.log"

if [ "$capacity" -lt 30 ] && [ "$status" == "Discharging" ]; then
    notify_telegram_bot.py -m "[${timestamp}] $(hostname) battery low: $capacity%"
    [[  $XDG_SESSION_TYPE =~ x11 ]] && {
        espeak "Battery low: $capacity percent"
    }
fi

exit 0
