#!/bin/bash

cd $(readlink -fn $(dirname "$BASH_SOURCE"))

virtualenv --system-site-packages bin/python
. bin/python/bin/activate
pip install -U pip
pip install -I -r python-requirements.txt

git submodule update --init --recursive

if [[ ! -s id_rsa ]]; then
    vault read -field=value secret/ssh/ec2-user > id_rsa
    chmod 0600 id_rsa
fi
