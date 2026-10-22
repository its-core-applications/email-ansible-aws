%global forgeurl https://github.com/amazonlinux/amazon-ec2-net-utils/

Version: 2.7.7
%forgemeta

Name: amazon-ec2-net-utils
Summary: utilities for managing network interfaces in Amazon EC2
Release: 1%{?dist}
License: Apache 2.0
URL: %{forgeurl}
Source: %{forgesource}

BuildArch: noarch
BuildRequires: make
Requires: systemd-networkd, udev, curl, iproute
Requires: /usr/bin/md5sum

%description
amazon-ec2-net-utils provides udev integration and helper utilities
to manage network configuration in the Amazon EC2 cloud environment

%prep
%forgeautosetup

%install
make install DESTDIR=%{buildroot} PREFIX=%{_prefix}

%files
/usr/lib/systemd/network/80-ec2.network
/usr/lib/systemd/system/policy-routes@.service
/usr/lib/systemd/system/refresh-policy-routes@.service
/usr/lib/systemd/system/refresh-policy-routes@.timer
/usr/lib/systemd/system/set-hostname-imds.service

/usr/lib/udev/rules.d/99-vpc-policy-routes.rules
%{_bindir}/setup-policy-routes
%{_bindir}/set-hostname-imds
%dir %{_datarootdir}/amazon-ec2-net-utils
%{_datarootdir}/amazon-ec2-net-utils/lib.sh

%post

setup_policy_routes() {
    local iface node
    for node in /sys/class/net/*; do
	iface=$(basename $node)
	unset ID_NET_DRIVER
	eval $(udevadm info --export --query=property /sys/class/net/$iface)
	case $ID_NET_DRIVER in
	    ena|ixgbevf|vif)
		systemctl restart policy-routes@${iface}.service
		systemctl start refresh-policy-routes@${iface}.timer
		;;
	esac
    done
}

if [ $1 -eq 1 ]; then
    # This is a new install
    systemctl enable systemd-networkd.service
    systemctl disable NetworkManager-wait-online.service
    systemctl disable NetworkManager.service
    if [ -d /run/systemd/system ]; then
	systemctl stop NetworkManager.service
	systemctl start systemd-networkd.service
	setup_policy_routes
    fi
elif [ $1 -gt 1 ]; then
    # This is an upgrade, there's less setup to do, but we do want to
    # ensure we apply any configuration introduced by the new version
    systemctl daemon-reload
    setup_policy_routes
fi

%changelog
* %(date "+%a %b %d %Y") (Automated RPM build) - %{version}-%{release}
- See git log for actual changes.
