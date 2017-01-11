# Install things we need for ansible

sudo yum-config-manager --enable rhui-REGION-rhel-server-optional
sudo yum-config-manager --enable rhui-REGION-rhel-server-extras
sudo rpm -i http://mirrors.kernel.org/fedora-epel/7/x86_64/e/epel-release-7-9.noarch.rpm
sudo yum -y install yum-utils libselinux ansible
