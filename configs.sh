#!/bin/bash

### 1. handle ssh keys

[ ! -d ~/.ssh ] && mkdir ~/.ssh
if [ $(ls ~/.ssh | wc -l) -eq 0 ]
then
    cp /mnt/e/FSs/LL5_2022-02-22_00-07-40/home/kamui/.ssh/* ~/.ssh
    chmod 0600 ~/.ssh/*
else
    echo "SSH keys weren't copied because ~/.ssh is not empty, you should add them manually"
fi


## Navigation
[ -d /mnt/f ] || mkdir /mnt/f
[ -d /mnt/e ] || mkdir /mnt/e
[ -d /e ] || sudo ln -sT /mnt/e /e # ln -s NEW OLD
[ -d /f ] || sudo ln -sT /mnt/f /f 


##

## System

## use aliases and functions in sudo
[ -e /usr/local/bin/custom_sudo.sh ] || echo "Run: sudo ln -s \$DOTS/bin/custom_sudo.sh /usr/local/bin # to use the \"__\" alias"

##

## Tools

### vim
dpkg -s vim &> /dev/null; [ $? -eq 0 ] || echo "WARNING: vim not installed";


##


## Visual



### dircolors
grep -q "LS_COLORS" ~/.env || { dircolors -b >> ~/.env && echo 'export LS_COLORS' >> ~/.env; }

##
