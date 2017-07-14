# Set up additional repositories
sudo yum-config-manager --enable rhui-REGION-rhel-server-optional
sudo yum-config-manager --enable rhui-REGION-rhel-server-extras
sudo rpm -i http://mirrors.kernel.org/fedora-epel/7/x86_64/e/epel-release-7-10.noarch.rpm


# Install ansible and required packages
sudo yum -y install yum-utils libselinux ansible

# Remove ansible itself, just leaving the deps
sudo yum -y remove ansible
