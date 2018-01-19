# Set up additional repositories
sudo yum -y install epel-release

# Install ansible and required packages
sudo yum -y install yum-utils libselinux ansible

# Remove ansible itself, just leaving the deps
sudo yum -y remove ansible
