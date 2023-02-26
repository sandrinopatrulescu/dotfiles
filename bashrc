# Fig pre block. Keep at the top of this file.
#[[ -f "$HOME/.fig/shell/bashrc.pre.bash" ]] && builtin source "$HOME/.fig/shell/bashrc.pre.bash"
# If not running interactively, don't do anything
[[ $- == *i* ]] || return

# enable bash completion in interactive shells
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi

alias usage='du -sk * | sort -n | perl -ne '\''($s,$f)=split(m{\t});for (qw(K M G)) {if($s<1024) {printf("%.1f",$s);print "$_\t$f"; last};$s=$s/1024}'\'
alias ls="ls --color"

# Powerline
if [ -f /usr/share/powerline/bindings/bash/powerline.sh ]; then
    source /usr/share/powerline/bindings/bash/powerline.sh
fi

# Linux Lite Custom Terminal
LLVER=$(awk '{print}' /etc/llver)

#echo -e "Welcome to $LLVER, ${USER}"
#echo " "
date "+%A %d %B %Y, %T"
#free -m | awk 'NR==2{printf "Memory Usage: %s/%sMB (%.2f%%)\n", $3,$2,$3*100/$2 }'
#df -h | awk '$NF=="/"{printf "Disk Usage: %d/%dGB (%s)\n", $3,$2,$5}'
#echo "Support - https://www.linuxliteos.com/forums/ (Right click, Open Link)"
#echo " "


# kamui

for file in ~kamui/dotfiles/{"env","alias","functions"};
do
    source ${file}
done

# printSemesterWeek # TODO: fix it


append-path $DOTS/bin # https://www.anishathalye.com/2014/08/03/managing-your-dotfiles/


## LL 5.6 only
append-path /opt/mssql-tools/bin # 2022-02-2  for sqlcmd (source: https://docs.microsoft.com/en-us/sql/linux/quickstart-install-connect-ubuntu?view=sql-server-ver15#tools)
##


append-path /home/kamui/.local/share/JetBrains/Toolbox/scripts

#region EXPORTS/PATH UNI {{{
append-path /mnt/e/LinuxPrograms/flutter/bin


#export DOTNET_ROOT=/mnt/e/LinuxPrograms/dotnet
export DOTNET_ROOT=/usr/lib/dotnet

append-path $DOTNET_ROOT
#export MSBuildSDKsPath="$DOTNET_ROOT/sdk"
export MSBuildSDKsPath="$DOTNET_ROOT/sdk/6.0.113/Sdks"


export MPJ_HOME=/mnt/e/LinuxPrograms/mpj-v0_44
append-path $MPJ_HOME/bin
#endregion }}}
export NODE_OPTIONS=--openssl-legacy-provider



export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# Fig post block. Keep at the bottom of this file.
#[[ -f "$HOME/.fig/shell/bashrc.post.bash" ]] && builtin source "$HOME/.fig/shell/bashrc.post.bash"
