#!/bin/bash

if [[ $USER = 'google' ]]; then
    GAMUSERCONFIGDIR=/home/google/gam-config/umich.edu /home/google/GAM/src/gam.py "$@"
else
    sudo -u google GAMUSERCONFIGDIR=/home/google/gam-config/umich.edu /home/google/GAM/src/gam.py "$@"
fi
