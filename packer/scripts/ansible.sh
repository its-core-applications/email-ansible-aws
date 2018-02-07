# Set up additional repositories
sudo yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm

# Install ansible and required packages
sudo yum -y install yum-utils libselinux ansible

# Remove ansible itself, just leaving the deps
sudo yum -y remove ansible
