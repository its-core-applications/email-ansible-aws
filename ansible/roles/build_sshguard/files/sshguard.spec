Name:           sshguard
Version:        2.0.0
Release:        2%{?dist}
Summary:        Protect hosts from brute-force attacks
License:        ISC and BSD and Public Domain
URL:            http://www.sshguard.net/
Source0:        http://downloads.sourceforge.net/project/sshguard/sshguard/%{version}/sshguard-%{version}.tar.gz
Source1:        sshguard.service

BuildRequires:  systemd
Requires:       iptables
Requires:       rsyslog
%{?systemd_requires}

%description
sshguard protects hosts from brute-force attacks against SSH and other
services.  It aggregates system logs and blocks repeat offenders using
iptables.

sshguard can read log messages from standard input (suitable for piping from
syslog) or monitor one or more log files.  Log messages are parsed,
line-by-line, for recognized patterns.  If an attack, such as several login
failures within a few seconds, is detected, the offending IP is blocked.
Offenders are unblocked after a set interval, but can be semi-permanently
banned using the blacklist option.

%prep
%setup -q

%build
%configure
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
%make_install
install -m 755 -d %{buildroot}%{_sysconfdir} %{buildroot}%{_unitdir}
install -p -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/sshguard.service

%post
%systemd_post sshguard.service

%preun
%systemd_preun sshguard.service

%postun
%systemd_postun_with_restart sshguard.service

%files
%doc README.rst COPYING examples
%{_mandir}/man7/sshguard-setup.7*
%{_mandir}/man8/sshguard.8*
%{_sbindir}/sshguard
%{_libexecdir}/sshg-*
%{_unitdir}/sshguard.service

%changelog
* %(date "+%a %b %d %Y") (Automated RPM build) - %{version}-%{release}
- See git log for actual changes.
