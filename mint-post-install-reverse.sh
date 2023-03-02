#!/bin/bash



# cp /mnt/e/dotfiles/mint-post-install-reverse.sh /tmp; clear; cat /mnt/e/dotfiles/mint-post-install-reverse.sh
# cd /tmp && sudo true && clear && ./mint-post-install-reverse.sh kamui nvme0n1p8



# args
[ $# -eq 2 ] || {
	echo "Usage: $0 <default user> <E partition>"
	echo "  example: $0 kamui nvme0n1p8"
	exit 1
}
user="$1"
ePartition="$2"

# local shortcuts
shopt -s expand_aliases
alias fdate="date +%Y-%m-%d_%H-%M-%S"

rawInstallDate="$(sudo dumpe2fs /dev/nvme0n1p5 | grep -i created | cut -d' ' -f9-)"
homePartiton="$(lsblk -fs | grep " /home$" | cut -d' ' -f1)"
rootPartition="$(lsblk -fs | grep " /$" | cut -d' ' -f1)"



machineName="$(uname -n)" # get machine name
installFdate="$(date -d "${rawInstallDate}" +'%Y-%m-%d_%H-%M-%S')" # get install fdat

installDir="/home/${user}/Desktop/${machineName}_${installFdate}"

sudo rm -rf "${installDir}"



sudo timeshift --delete-all



sudo cp "$(sudo ls -1t /etc/fstab*.bak | head -n1)" /etc/fstab
mountpoint -q /mnt/e && sudo umount /mnt/e
[ -L /e ] && sudo rm /e
sudo rmdir /mnt/e



sudo cp "$(sudo ls -1t /etc/default/grub*.bak | head -n1)" /etc/default/grub
sudo update-grub



# dotfiles
sudo apt remove -qqy git && sudo apt autoremove -qqy

for filebasename in "dotfiles" ".alias" ".bashrc" ".env" ".gitconfig" ".functions" ".vimrc"; do
    sudo rm /{home/"${user}",root}/"${filebasename}"
done
sudo cp /etc/skel/.bashrc /root
cp /etc/skel/.bashrc /home/"${user}"



sudo rm -rf /home/"${user}"/.ssh



[ -f /home/"${user}"/.config/gtk-3.0/bookmarks ] && rm /home/"${user}"/.config/gtk-3.0/bookmarks



[ -L /usr/local/bin/custom_sudo.sh ] && sudo rm /usr/local/bin/custom_sudo.sh

