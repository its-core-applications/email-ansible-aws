#!/bin/bash

/usr/local/gitlab/bin/gitlab -o json -c /etc/gitlab-cli.cfg "$@"
