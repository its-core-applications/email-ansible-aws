%global _hardened_build 1

Name:               corvus
Version:            0.2.7
Release:            3%{?dist}
Summary:            A lightweight proxy for redis clusters
License:            MIT
URL:                https://github.com/eleme/corvus
Source0:            https://github.com/eleme/corvus/releases/download/v%{version}/%{name}-%{version}.tar.bz2
Source1:            corvus.service
# Not upstreamable
Patch0:             corvus-0.2.7-use-system-jemalloc.patch
# From upstream; https://github.com/eleme/corvus/pull/140
Patch1:             corvus-0.2.7-fix-expire.patch
BuildRequires:      jemalloc-devel
BuildRequires:      systemd
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd

%description
Corvus is a fast, lightweight redis cluster proxy for redis 3.0+ with
cluster mode enabled.

%prep
%autosetup -p1
rm -frv deps/

%build
make %{?_smp_mflags} \
    CFLAGS+="%{optflags}"

%install
install -pDm755 src/%{name} %{buildroot}%{_bindir}/%{name}
install -pDm644 %{name}.conf %{buildroot}%{_sysconfdir}/%{name}.conf

# Install systemd unit
mkdir -p %{buildroot}%{_unitdir}
install -pm644 %SOURCE1 %{buildroot}%{_unitdir}

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc README.md
%attr(0644, redis, root) %config(noreplace) %{_sysconfdir}/%{name}.conf
%{_bindir}/%{name}
%{_unitdir}/%{name}.service

%changelog
* %(date "+%a %b %d %Y") (Automated RPM build) - %{version}-%{release}
- See git log for actual changes.
