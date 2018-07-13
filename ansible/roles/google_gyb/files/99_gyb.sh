if [[ $USER = 'collaborate' ]]; then
    alias gyb='/usr/bin/python3 /home/collaborate/GYB/gyb.py --service-account'
else
    alias gyb='sudo -u collaborate /usr/bin/python3 /home/collaborate/GYB/gyb.py --service-account'
fi
