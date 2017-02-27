#!/bin/bash

# Variables
export TLD=umich.edu

# Set up Ansible
hacking_dir=$(readlink -fn $(dirname "$BASH_SOURCE"))
. $hacking_dir/git/ansible.git/hacking/env-setup
export ANSIBLE_CONFIG=$hacking_dir/ansible/ansible.cfg
export ANSIBLE_PRIVATE_KEY_FILE=$hacking_dir/id_rsa
export ANSIBLE_INVENTORY=$hacking_dir/inventory

# Set up Vault
export VAULT_ADDR='http://127.0.0.1:8200'
vault read secret/ping
if [[ $? -ne 0 ]]; then
    echo "WARNING: Vault ping failed; do you need to auth and/or unseal?"
fi

# Set up Git
if [[ $SUDO_USER ]]; then
    export GIT_AUTHOR_EMAIL="${SUDO_USER}@$TLD"
    export GIT_AUTHOR_NAME=$(grep "^${SUDO_USER}:" /etc/passwd | cut -d: -f5)
    export GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME"
    export GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"
fi

function _sshcomplete() {
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"
    COMPREPLY=($(aws ec2 describe-instances --output=text | awk '/CustomDNSName/{print $NF}' | grep "^$cur" | sort -u))
    return 0
}

complete -F _sshcomplete ssh
