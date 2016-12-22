#!/bin/bash

echo "Cleaning yum..."
sudo yum -y clean all
# `yum clean all` doesn't clean enough things
sudo find /var/cache/yum -type f -delete

# no logs in the image
echo "Cleaning logs..."
sudo systemctl stop rsyslog
sudo find /var/log -type f -delete -print

# no redis state in the image
echo "Cleaning redis state..."
sudo systemctl status redis &>/dev/null && sudo systemctl stop redis
sudo rm -fv /var/lib/redis/nodes.conf
