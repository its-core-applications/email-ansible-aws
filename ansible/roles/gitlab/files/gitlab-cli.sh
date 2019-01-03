#!/bin/bash

/usr/local/lib/gitlab/bin/python gitlab -o json -c /etc/gitlab-cli.cfg "$@"
