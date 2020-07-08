#!/bin/bash

cd $(readlink -fn $(dirname "$BASH_SOURCE"))

export PIPENV_IGNORE_VIRTUALENVS=1
export PIPENV_VENV_IN_PROJECT=1
# Pipenv doesn't put these in the lockfile, and also doesn't automatically
# update them.
pipenv run pip install -U setuptools pip
pipenv sync

git submodule update --init --recursive

if [[ ! -s id_rsa ]]; then
    vault read -field=value secret/ssh/ec2-user > id_rsa
    chmod 0600 id_rsa
fi
