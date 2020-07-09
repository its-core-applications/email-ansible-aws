#!/bin/bash

# Variables
export TLD=umich.edu

# Set up Ansible
hacking_dir=$(readlink -fn $(dirname "$BASH_SOURCE"))
VIRTUAL_ENV_DISABLE_PROMPT=1
export PIPENV_IGNORE_VIRTUALENVS=1
. $hacking_dir/.venv/bin/activate
export ANSIBLE_DEVEL_WARNING=False
export ANSIBLE_CONFIG=$hacking_dir/ansible/ansible.cfg
export ANSIBLE_COLLECTIONS_PATHS=$hacking_dir/ansible/collections
export ANSIBLE_PRIVATE_KEY_FILE=$hacking_dir/id_rsa
export AWS_STATUS=prod
export AWS_DEFAULT_REGION=us-west-2
export SNS_REGION=us-west-2
export SNS_TOPIC=rootmail
export SQS_REGION=us-west-2

export VAULT_ADDR="https://vault.a.mail.umich.edu:8200"

if which ara-manage &>/dev/null && [[ -d /home/ara ]]; then
    eval $(python -m ara.setup.env)
    export ARA_API_CLIENT=http
    export ARA_API_SERVER=http://127.0.0.1:8082
    export ARA_BASE_URL=https://ara.${AWS_DEFAULT_REGION}.a.mail.umich.edu/
fi

if [[ -s $hacking_dir/localenv ]]; then
    . $hacking_dir/localenv
fi

export ANSIBLE_INVENTORY=$hacking_dir/ansible/inventory_${AWS_STATUS}

vault read secret/ping
if [[ $? -ne 0 ]]; then
    echo "WARNING: Vault ping failed; do you need to auth and/or unseal?"
fi

# Set up Git
if [[ $SUDO_USER ]]; then
    export GIT_AUTHOR_EMAIL="${SUDO_USER}@$TLD"
    export GIT_AUTHOR_NAME=$(getent passwd ${SUDO_USER} | cut -d: -f5)
    export GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME"
    export GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"
fi

# Override bash-completion's default hostname lookup
function _known_hosts_real() {
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"
    if [[ ! -s ~/.sshcomplete ]] || [[ $(stat --format %Y ~/.sshcomplete) -lt $(( $(date +%s) - 60 )) ]]; then
        ansible --list-hosts all | sed -e '1d; s/^  *//' > ~/.sshcomplete
    fi
    COMPREPLY=( $(grep "^$cur" ~/.sshcomplete | sort -u) )
    return 0
}
