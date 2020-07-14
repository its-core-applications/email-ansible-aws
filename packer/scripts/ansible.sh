# Set up additional repositories
sudo yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm

# Fix broken pip3
# FIXME: this is an ugly hack
sudo yum -y reinstall python3-pip

# Install ansible and required packages
sudo yum -y install yum-utils libselinux libselinux-python ansible

# Remove ansible itself, just leaving the deps
sudo yum -y remove ansible
