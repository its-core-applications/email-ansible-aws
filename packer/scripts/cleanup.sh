#!/bin/bash

sudo yum -y clean all
# `yum clean all` doesn't clean enough things
sudo find /var/cache/yum -type f -delete 

# no logs in the image
sudo systemctl stop rsyslog
sudo find /var/log -type f -delete

# no redis state in the image
sudo systemctl stop redis
sudo rm -f /var/lib/redis/nodes.conf
