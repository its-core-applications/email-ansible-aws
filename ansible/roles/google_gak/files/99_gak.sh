if [[ $USER != 'collaborate' ]]; then
    for i in /usr/bin/collab-* /usr/bin/discussions-* /usr/bin/google-*; do
        alias $(basename $i)="sudo -u collaborate $i"
    done
fi
