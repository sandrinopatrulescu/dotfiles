#!/bin/bash

# run as: install.sh 192.168.1.101
AN5_IP="$1"
ssh-keygen
ssh-copy-id kamui@"${AN5_IP}" # asks for password
scp -r kamui@"${AN5_IP}":~/dotfiles-secrets .
rm -r .ssh
ln -s dotfiles-secrets/ssh .ssh
ln -s dotfiles-secrets/secrets .secrets

git clone https://github.com/sandrinopatrulescu/dotfiles
ln -s dotfiles/phone/bashrc .bashrc
