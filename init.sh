#!/bin/bash

cd $(readlink -fn $(dirname "$BASH_SOURCE"))

PIPENV_IGNORE_VIRTUALENVS=1 PIPENV_VENV_IN_PROJECT=1 pipenv sync

git submodule update --init --recursive

if [[ ! -s id_rsa ]]; then
    vault read -field=value secret/ssh/ec2-user > id_rsa
    chmod 0600 id_rsa
fi
