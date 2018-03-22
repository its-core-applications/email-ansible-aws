#!/bin/bash

# Variables
export TLD=umich.edu

# Set up Ansible
hacking_dir=$(readlink -fn $(dirname "$BASH_SOURCE"))
VIRTUAL_ENV_DISABLE_PROMPT=1
. $hacking_dir/bin/python/bin/activate
. $hacking_dir/bin/ansible/hacking/env-setup
export ANSIBLE_CONFIG=$hacking_dir/ansible/ansible.cfg
export ANSIBLE_PRIVATE_KEY_FILE=$hacking_dir/id_rsa
export ANSIBLE_INVENTORY=$hacking_dir/ansible/inventory
export AWS_DEFAULT_REGION=us-west-2
export AWS_PROFILE=default

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
    local cur prev
    COMPREPLY=()
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    cur="${COMP_WORDS[COMP_CWORD]}"
    if [[ $prev = 'ssh' ]]; then
        if [[ ! -s ~/.aws-hosts || $(stat --format %Y ~/.aws-hosts) -lt $(( $(date +%s) - 30 )) ]]; then
            aws ec2 describe-instances --filters 'Name=instance-state-name,Values=running' --output=text | awk '/CustomDNSName/{print $NF}' >| ~/.aws-hosts
        fi
        COMPREPLY=( $(cat ~/.aws-hosts ~/umce/hosts.* | grep "^$cur" | sort -u) )
    fi
    return 0
}

complete -F _sshcomplete ssh
