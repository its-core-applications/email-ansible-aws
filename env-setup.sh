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
export AWS_STATUS=prod
export AWS_DEFAULT_REGION=us-west-2
export SNS_REGION=us-west-2
export SNS_TOPIC=rootmail

export VAULT_ADDR="https://vault.a.mail.umich.edu:8200"

if which ara &>/dev/null; then
    eval $(python -m ara.setup.env)
    if [[ -d /home/ara ]]; then
        export ARA_DIR=/home/ara
        export ARA_BASE_URL=https://ara.${AWS_DEFAULT_REGION}.a.mail.umich.edu/
        # We set this as an env variable and an alias so that it works for
        # both people and cron jobs.
        export ARA_DATABASE=sqlite:////home/ara/$(date +%F).sqlite
        alias ansible-playbook='env ARA_DATABASE=sqlite:////home/ara/$(date +%F).sqlite ansible-playbook'
    fi
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
