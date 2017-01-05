export SYSTEMD_PAGER=
export EDITOR=vim
export CVS_RSH=ssh
export HISTIGNORE='&:ls:exit'

if [[ ${EUID} == 0 ]] ; then
    PS1='\[\033[01;31m\]\u@\h\[\033[01;34m\] \W \$\[\033[00m\] '
else
    PS1='\[\033[01;32m\]\u@\h\[\033[01;34m\] \W \$\[\033[00m\] '
fi
