#!/bin/bash



# TODO: cd /tmp && wget <link> && sudo ./mint-post-install.sh kamui y nvme0n1p8 y
# TODO IDEA use sudo here and before running the script run sudo. Why? in order to avoid the current user being root
# TODO IDEA run_func "dotfiles" where run_func() { echo "STARTED $1"; $("$1"); echo "FINISHED $1"; }
# for FAIL:
#   sed -E '36,36s@^@#@' mint-post-install.sh > mint-post-install1.sh
#   sudo ./mint-post-install1.sh kamui y nvme0n1p8 y


# xed /mnt/e/dotfiles/mint-post-install{,-reverse}.sh

# mp=/mnt/e; if mountpoint -q "${mp}"; then sudo umount "${mp}"; echo "unmounted ${mp}"; else [ -d "${mp}" ] || sudo mkdir "${mp}"; sudo mount /dev/nvme0n1p8 "${mp}"; echo "mounted ${mp}"; fi

# cp /mnt/e/dotfiles/mint-post-install.sh /tmp; clear; cat /mnt/e/dotfiles/mint-post-install.sh
# cd /tmp && sudo true && clear && sudo ./mint-post-install.sh kamui y nvme0n1p8 y


# args
[ $# -eq 4 ] || {
    echo "Usage: $0 <default user> <install 3 answer> <E partition> <replace ssh dir answer>"
    echo "  example: $0 kamui y nvme0n1p8 y"
    exit 1
}

user="$1"
install3Answer="$2"
ePartition="$3"
replaceSshDirAnswer="$4"



# local shortcuts
shopt -s expand_aliases
alias fdate="date +%Y-%m-%d_%H-%M-%S"

rawInstallDate="$(dumpe2fs /dev/nvme0n1p5 | grep -i created | cut -d' ' -f9-)"
homePartiton="$(lsblk -fs | grep " /home$" | cut -d' ' -f1)"
rootPartition="$(lsblk -fs | grep " /$" | cut -d' ' -f1)"



echo "# 1. create dir for inxi info \& dump inxi info"
machineName="$(uname -n)" # get machine name
installFdate="$(date -d "${rawInstallDate}" +'%Y-%m-%d_%H-%M-%S')" # get install fdate

installDir="/home/${user}/Desktop/${machineName}_${installFdate}"
mkdir "${installDir}"

inxiFdate="$(fdate)"
inxi -v7 > "${installDir}/${inxiFdate}_inxi-v7.txt"
inxi -v7z > "${installDir}/${inxiFdate}_inxi-v7z.txt"
chown -R "${user}" "${installDir}"
echo



echo "# 2. create system restore point 1"
timeshift --create --target "${homePartiton}"
echo



echo "# 3."
echo "# 3.1 system settings & shortcuts"
read -rp "Now do system settings and then press Enter to continue"
echo



echo "# 3.2 auto mount E"
ePartitionUUID="$(blkid | grep "${ePartition}" | sed -E 's@^.* UUID="([0-9a-zA-Z]+)" .*$@\1@')"
cp /etc/fstab "/etc/fstab_$(fdate).bak" # backup /etc/fstab
echo '# Windows E:'\\ >> /etc/fstab
echo "UUID=${ePartitionUUID} /mnt/e ntfs permissions 0 0" >> /etc/fstab
mountpoint -q /mnt/e && sudo umount /mnt/e
[ -d /mnt/e ] || sudo mkdir /mnt/e
ln -s -T /mnt/e /e
mount -a
echo



echo "# 3.3 grub"
sudo cp /etc/default/grub "/etc/default/grub_$(fdate).bak"
sudo sed -Ei 's@^(GRUB_CMDLINE_LINUX_DEFAULT)=.*$@\1=""@' /etc/default/grub
sudo sed -Ei '$aGRUB_BACKGROUND="/mnt/e/Media/GravityFalls08.jpeg"' /etc/default/grub
sudo update-grub
echo


echo "# 3.4 dotfiles"
# TODO fix bashrc not being properly updated
sudo apt install -qqy git
bashrcAppend="$(sed -nE '/^# kamui$/,$p' /e/dotfiles/bashrc)"

function installDotfiles() {
    #echo "whoami=$(whoami) ~=$(echo ~)" # debug print
    echo -e "\n\n\n${bashrcAppend}" >> ~/.bashrc
    
    echo
    echo
    echo
    tmpfile=$(mktemp /tmp/abc-script.XXXXXX)
    echo "tmpfile=${tmpfile}"
    cat ~/.bashrc > "${tmpfile}"
    read -p "Press enter to continue"
    echo
    echo
    echo
    
    
    mv ~/.bashrc /e/dotfiles/bashrc
    /e/dotfiles/install
}



export bashrcAppend
export -f installDotfiles
su "${user}" -c "bash -c installDotfiles" # run function as another user linux https://stackoverflow.com/questions/17926153/bash-run-function-with-different-user

installDotfiles
echo "3.4 DONE"



echo "# 3.5 ssh"
sshDir=/home/"${user}"/.ssh
[ -d "${sshDir}" ] || mkdir "${sshDir}"; # create ssh dir if it doesn't exist

if [ -z "$(ls -A "${sshDir}")" ] || [ "${replaceSshDirAnswer}" = "y" ]; then
    cp -r /e/.ssh /home/"${user}"
    sudo chown -R "${user}" "${sshDir}"
    chmod 0600 "${sshDir}"/*
else
    echo "SSH keys weren't copied because /home/${user}/.ssh is not empty and you opted not to replace them"
fi
echo



echo "# 3.6 tweaks"
timedatectl set-local-rtc 1 # dual boot wrong time https://itsfoss.com/wrong-time-dual-boot/

sudo ln -s /e/dotfiles/bin/custom_sudo.sh /usr/local/bin # use aliases and functions in sudo
echo



echo "# 3.7 shorcuts"
cat << EOF > /home/"${user}"/.config/gtk-3.0/bookmarks
file:///home/${user}/Downloads
file:///tmp
file:///e/
file:///e/dotfiles
file:///e/Scratch
file:///e/UBB_IE_2020-2023
file:///e/Videos
EOF
echo



echo "# 3.8 other settings (xed)"
dconf load /org/x/editor/ < /e/dotfiles/dconf_xed.conf # https://askubuntu.com/questions/72070/how-do-i-change-dconf-keys-without-a-gui-for-a-post-install-script
echo



echo "# 3.9 create system restore point 2"
timeshift --create --target "${homePartiton}"
echo



echo "# 5. install"

echo "# 5.0 updates"
read -rp "Now do updates and then press Enter to continue"
echo


echo "# 5.1 apt install "
echo "Install 1 starting..."
apt install -qqy vim keepassxc scrcpy manpages-posix-dev xfce4-clipman vokoscreen-ng xtitle ffmpeg rclone 
echo "Install 1 finished..."
echo


echo "# 5.2 manual install "

echo "installing chrome..." # https://askubuntu.com/questions/510056/how-to-install-google-chrome 
wget https://dl-ssl.google.com/linux/linux_signing_key.pub -O /tmp/google.pub
gpg --no-default-keyring --keyring /etc/apt/keyrings/google-chrome.gpg --import /tmp/google.pub
echo 'deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list
apt update -qq && apt install -qqy google-chrome-stable

echo "installing discord..."
sudo apt install -qqy libgconf-2-4 libc++1
# TODO: fix problems w/ dependecies
wget --quiet -O /tmp/discord.deb "https://discord.com/api/download?platform=linux&format=deb" && dpkg -i /tmp/discord.deb

echo "installling teamviewer..."
# TODO: fix problems w/ dependecies
wget --quiet -O /tmp/teamviewer.deb "https://download.teamviewer.com/download/linux/teamviewer_amd64.deb" && dpkg -i /tmp/teamviewer.deb
echo


echo "# 5.3 AC install"
if [ "${install3Answer}" = "y" ]; then
    echo "Install 3 starting..."
    echo "installing skype..."
    apt install -qqy skypeforlinux
    echo "installing RDC..."
    apt install -qqy remmina
    echo "installing freerdp2-x11..."
    apt install -qqy freerdp2-x11
    echo "installing forti..."
    # TODO: fix dependecies
    sudo apt install -qqy libdbusmenu-gtk4  libappindicator1 libnss3-tools
    wget --quiet -O /tmp/forticlient.deb "https://repo.fortinet.com/repo/forticlient/7.2/ubuntu/pool/multiverse/forticlient/forticlient_7.2.0.0644_amd64.deb" && dpkg -i /tmp/forticlient.deb 
    echo "Install 3 finished..."
else
    echo "Skipping install 3"
fi
echo



echo "# 5.4 uni install"

# TODO: not working
echo "installing teams..." # https://www.how2shout.com/linux/4-ways-to-install-microsoft-teams-on-linux-mint-21-lts-vanessa/
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee /usr/share/keyrings/ms-teams.gpg > /dev/null
echo 'deb [signed-by=/usr/share/keyrings/ms-teams.gpg] https://packages.microsoft.com/repos/ms-teams stable main' | sudo tee /etc/apt/sources.list.d/ms-teams.list
apt update -qq && apt install -qqy teams
rm /etc/apt/sources.list.d/ms-teams.list
echo



echo "# end."



echo "TODO:"
echo "- add install header in doc: $(date -d "${rawInstallDate}" +'%Y-%m-%d_%H-%M-%S') on ${rootPartition} $(awk -F= '/^PRETTY_NAME=/ { print $2 }' /etc/os-release)"



