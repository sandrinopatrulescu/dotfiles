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

echo -e "Welcome to $LLVER, ${USER}"
echo " "
date "+%A %d %B %Y, %T"
free -m | awk 'NR==2{printf "Memory Usage: %s/%sMB (%.2f%%)\n", $3,$2,$3*100/$2 }'
df -h | awk '$NF=="/"{printf "Disk Usage: %d/%dGB (%s)\n", $3,$2,$5}'
echo "Support - https://www.linuxliteos.com/forums/ (Right click, Open Link)"
echo " "


# kamui

## Initial
source ~/dotfiles/"alias" && source ~/dotfiles/functions
source ~/dotfiles/env
##

## Navigation

[ -d /e ] || sudo ln -sT /mnt/e /e # ln -s NEW OLD


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


## Sourcing and printing

#source ~/dotfiles/"alias" && source ~/dotfiles/functions
#source ~/dotfiles/env

### for printing Uni Week #TODO: refactor or remove

LAST_WEEK_BEFORE_SEMESTER=38 &&
WEEK=$(expr 52 + $(date +%V) - $LAST_WEEK_BEFORE_SEMESTER) &&
WEEK=$((WEEK % 52)) &&
# WEEK=12 <=> W12
{ [ $WEEK -ge 13 -a $WEEK -le 14 ] && WEEK_TEXT="V $((WEEK - 12))"; } ||
{ [ $WEEK -ge 15 -a $WEEK -le 16 ] &&  WEEK_TEXT="$((WEEK - 2))"; } ||
{ [ $WEEK -ge 17 -a $WEEK -le 19 ] && WEEK_TEXT="E $((WEEK - 16))"; } ||
WEEK_TEXT="$WEEK"
echo "Week $WEEK_TEXT"
unset WEEK WEEK_TEXT

##


