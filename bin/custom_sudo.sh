#!/bin/bash
# note:
# put a symbolic link to this file in /usr/local/bin
# and then run it by: sudo custom_sudo.sh <command>
# or use: alias __='sudo custom_sudo.sh '
source ~kamui/.bashrc 1> /dev/null
shopt -s expand_aliases
"$@"

