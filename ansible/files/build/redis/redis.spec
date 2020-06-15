%global _hardened_build 1

# Tests fail in mock, not in local build.
%global with_tests   %{?_with_tests:1}%{!?_with_tests:0}

Name:              redis
Version:           6.0.18
Release:           1%{?dist}
Summary:           A persistent key-value database
License:           BSD
URL:               http://redis.io
Source0:           http://download.redis.io/releases/%{name}-%{version}.tar.gz
Source1:           %{name}.logrotate
Source2:           %{name}-sentinel.service
Source3:           %{name}.service
Source4:           %{name}.tmpfiles
Source5:           %{name}-sentinel.init
Source6:           %{name}.init
Source7:           %{name}-shutdown
Source8:           %{name}-limit-systemd
Source9:           %{name}-limit-init
Patch0:            redis-6.0.5-use-system-jemalloc.patch
BuildRequires:     jemalloc-devel
%if 0%{?with_tests}
BuildRequires:     procps-ng
BuildRequires:     tcl
%endif
BuildRequires:     systemd
Requires:          /bin/awk
Requires:          logrotate
Requires:          rubygem-redis
Requires(pre):     shadow-utils
Requires(post):    systemd
Requires(preun):   systemd
Requires(postun):  systemd

%description
Redis is an advanced key-value store. It is often referred to as a data
structure server since keys can contain strings, hashes, lists, sets and
sorted sets.

%prep
%setup -q
rm -frv deps/jemalloc
%patch0 -p1

# No hidden build.
sed -i -e 's|\t@|\t|g' deps/lua/src/Makefile
sed -i -e 's|$(QUIET_CC)||g' src/Makefile
sed -i -e 's|$(QUIET_LINK)||g' src/Makefile
sed -i -e 's|$(QUIET_INSTALL)||g' src/Makefile
# Ensure deps are built with proper flags
sed -i -e 's|$(CFLAGS)|%{optflags}|g' deps/Makefile
sed -i -e 's|OPTIMIZATION?=-O3|OPTIMIZATION=%{optflags}|g' deps/hiredis/Makefile
sed -i -e 's|$(LDFLAGS)|%{?__global_ldflags}|g' deps/hiredis/Makefile
sed -i -e 's|$(CFLAGS)|%{optflags}|g' deps/linenoise/Makefile
sed -i -e 's|$(LDFLAGS)|%{?__global_ldflags}|g' deps/linenoise/Makefile

%build
make %{?_smp_mflags} \
    DEBUG="" \
    CFLAGS+="%{optflags}" \
    LUA_LDFLAGS+="%{?__global_ldflags}" \
    MALLOC=jemalloc \
    all

%install
make install INSTALL="install -p" PREFIX=%{buildroot}%{_prefix}

# Filesystem.
install -d %{buildroot}%{_sharedstatedir}/%{name}
install -d %{buildroot}%{_localstatedir}/log/%{name}
install -d %{buildroot}%{_localstatedir}/run/%{name}

# Install logrotate file.
install -pDm644 %{S:1} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# Install configuration files.
install -pDm644 %{name}.conf %{buildroot}%{_sysconfdir}/%{name}.conf
install -pDm644 sentinel.conf %{buildroot}%{_sysconfdir}/%{name}-sentinel.conf

# Install Systemd unit files.
mkdir -p %{buildroot}%{_unitdir}
install -pm644 %{S:3} %{buildroot}%{_unitdir}
install -pm644 %{S:2} %{buildroot}%{_unitdir}

# Install systemd tmpfiles config.
install -pDm644 %{S:4} %{buildroot}%{_tmpfilesdir}/%{name}.conf
# Install systemd limit files (requires systemd >= 204)
install -p -D -m 644 %{S:8} %{buildroot}%{_sysconfdir}/systemd/system/%{name}.service.d/limit.conf
install -p -D -m 644 %{S:8} %{buildroot}%{_sysconfdir}/systemd/system/%{name}-sentinel.service.d/limit.conf

# Fix non-standard-executable-perm error.
chmod 755 %{buildroot}%{_bindir}/%{name}-*

# create redis-sentinel command as described on
# http://redis.io/topics/sentinel
ln -sf %{name}-server %{buildroot}%{_bindir}/%{name}-sentinel

# Install redis-shutdown
install -pDm755 %{S:7} %{buildroot}%{_bindir}/%{name}-shutdown

%check
%if 0%{?with_tests}
make test ||:
make test-sentinel ||:
%endif

%pre
getent group %{name} &> /dev/null || \
groupadd -r %{name} &> /dev/null
getent passwd %{name} &> /dev/null || \
useradd -r -g %{name} -d %{_sharedstatedir}/%{name} -s /sbin/nologin \
-c 'Redis Database Server' %{name} &> /dev/null
exit 0

%post
%systemd_post %{name}.service
%systemd_post %{name}-sentinel.service

%preun
%systemd_preun %{name}.service
%systemd_preun %{name}-sentinel.service

%postun
%systemd_postun_with_restart %{name}.service
%systemd_postun_with_restart %{name}-sentinel.service

%files
%{!?_licensedir:%global license %%doc}
%license COPYING
%doc 00-RELEASENOTES BUGS CONTRIBUTING MANIFESTO README.md
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%attr(0644, redis, root) %config(noreplace) %{_sysconfdir}/%{name}.conf
%attr(0644, redis, root) %config(noreplace) %{_sysconfdir}/%{name}-sentinel.conf
%dir %attr(0755, redis, redis) %{_sharedstatedir}/%{name}
%dir %attr(0755, redis, redis) %{_localstatedir}/log/%{name}
%dir %attr(0755, redis, redis) %{_localstatedir}/run/%{name}
%{_bindir}/%{name}-*
%{_tmpfilesdir}/%{name}.conf
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}-sentinel.service
%dir %{_sysconfdir}/systemd/system/%{name}.service.d
%config(noreplace) %{_sysconfdir}/systemd/system/%{name}.service.d/limit.conf
%dir %{_sysconfdir}/systemd/system/%{name}-sentinel.service.d
%config(noreplace) %{_sysconfdir}/systemd/system/%{name}-sentinel.service.d/limit.conf

%changelog
* %(date "+%a %b %d %Y") (Automated RPM build) - %{version}-%{release}
- See git log for actual changes.
