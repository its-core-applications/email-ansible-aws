# Register subscription
sudo /usr/bin/curl --insecure --output katello-ca-consumer-latest.noarch.rpm $SATELLITE_RPM
sudo /usr/bin/dnf -y localinstall katello-ca-consumer-latest.noarch.rpm
sudo subscription-manager register --org="$SATELLITE_ORG" --activationkey="$SATELLITE_KEY"

# Set up additional repositories
sudo dnf -y upgrade rh-amazon-rhui-client
sudo dnf config-manager --set-enabled codeready-builder-for-rhel-9-rhui-rpms
sudo dnf -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm

# Install prerequisite packages
sudo dnf -y install dnf-utils libselinux python3-libselinux
