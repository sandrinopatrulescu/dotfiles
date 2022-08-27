#!/bin/bash
# note, run as kamui

. ./env


### 1. handle ssh keys


[ -d ~/.ssh ] || mkdir ~/.ssh; 

if [ "$(ls -A ~/.ssh)" ]
then
	echo "SSH keys weren't copied because ~/.ssh is not empty, you should add them manually"
else
    cp ${DISTRIBUTION_PATH}/home/kamui/.ssh/* ~/.ssh
    chmod 0600 ~/.ssh/*
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


# root
sudo ln -s $DOTS/vimrc ~root/.vimrc

echo "Add the following to /root/.bashrc"
cat << 'EOF'

# kamui
DOTS=/mnt/e/dotfiles
for file in $DOTS/{"functions","alias"}
do
    source $file
done
EOF
