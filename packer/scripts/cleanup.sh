#!/bin/bash

sudo yum -y clean all

sudo systemctl stop rsyslog
sudo find /var/log -type f -delete
# `yum clean all` doesn't clean enough things
sudo find /var/cache/yum -type f -delete
