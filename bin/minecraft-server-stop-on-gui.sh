#!/bin/bash

serviceName="minecraft-server.service"

if systemctl is-active "${serviceName}"; then
        sessionIds=$(loginctl --no-legend list-sessions | awk  '$2 = !/root|kamui/ {print $1}')
        for sessionId in $sessionIds; do
            session=$(loginctl show-session "$sessionId")
            if echo "$session" | grep -qE '^Desktop='; then
                echo "Desktop session found. Stopping ${serviceName}"
                systemctl stop "${serviceName}" && exit 0
            fi
        done
        echo "No desktop session found"
    else
        echo "${serviceName} is not active"
fi
