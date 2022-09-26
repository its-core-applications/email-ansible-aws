#!/bin/bash

# Set up Ansible
hacking_dir=$(readlink -fn $(dirname "$BASH_SOURCE"))
VIRTUAL_ENV_DISABLE_PROMPT=1
export PIPENV_IGNORE_VIRTUALENVS=1
. $hacking_dir/.venv/bin/activate
export ANSIBLE_DEVEL_WARNING=False
export ANSIBLE_CONFIG=$hacking_dir/ansible/ansible.cfg
export ANSIBLE_COLLECTIONS_PATHS=$hacking_dir/ansible/collections
export AWS_STATUS=prod
export AWS_DEFAULT_PROFILE=umcollab
export SNS_TOPIC=rootmail

export VAULT_ADDR="https://vault.a.mail.umich.edu:8200"

if which ara-manage &>/dev/null && [[ -d /home/ara ]]; then
    eval $(python -m ara.setup.env)
    export ARA_API_CLIENT=http
    export ARA_API_SERVER=http://127.0.0.1:8082
    export ARA_BASE_URL=https://ara.us-west-2.a.mail.umich.edu/
fi

if [[ -s $hacking_dir/localenv ]]; then
    . $hacking_dir/localenv
fi

export ANSIBLE_INVENTORY=$hacking_dir/ansible/inventory_${AWS_STATUS}

export SNS_REGION=$(ANSIBLE_STDOUT_CALLBACK=json ansible --playbook-dir $hacking_dir/ansible localhost -m debug -a 'msg={{ aws_layout[aws_status][aws_profile_sns].region }}' | jq -r .plays[0].tasks[0].hosts.localhost.msg)

# Set up Git
if [[ $SUDO_USER ]]; then
    export GIT_AUTHOR_EMAIL="${SUDO_USER}@umich.edu"
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
