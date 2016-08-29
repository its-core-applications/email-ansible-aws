#!/bin/bash

git submodule update --init --recursive

if [[ ! -s id_rsa ]]; then
    vault read -field=value secret/ssh/ec2-user > id_rsa
    chmod 0600 id_rsa
fi
