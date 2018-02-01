%define rspamd_user      _rspamd
%define rspamd_group     %{rspamd_user}
%define rspamd_home      %{_localstatedir}/lib/rspamd
%define rspamd_confdir   %{_sysconfdir}/rspamd
%define rspamd_pluginsdir   %{_datadir}/rspamd
%define rspamd_rulesdir   %{_datadir}/rspamd/rules
%define rspamd_wwwdir   %{_datadir}/rspamd/www

Name:           rspamd
Version:        1.6.5
Release:        1
Summary:        Rapid spam filtering system
License:        BSD2c
URL:            https://rspamd.com
BuildRequires:  glib2-devel
BuildRequires:  libevent-devel
BuildRequires:  openssl-devel
BuildRequires:  hyperscan-devel
BuildRequires:  cmake
BuildRequires:  file-devel
BuildRequires:  perl
BuildRequires:  ragel < 7.0
BuildRequires:  systemd
Requires(pre):  systemd
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
BuildRequires:  sqlite-devel
Requires(pre):  shadow-utils
BuildRequires:  luajit-devel
Source0:        https://github.com/vstakhov/%{name}/archive/%{version}/%{name}-%{version}.tar.gz

%description
Rspamd is a rapid, modular and lightweight spam filter. It is designed to work
with large volumes of mail and can be easily extended with filters written in
lua.

%prep
%autosetup -n %{name}-%{version}

%build
cmake \
    -DCMAKE_C_OPT_FLAGS="%{optflags}" \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCONFDIR=%{_sysconfdir}/rspamd \
    -DMANDIR=%{_mandir} \
    -DDBDIR=%{_localstatedir}/lib/rspamd \
    -DRUNDIR=%{_localstatedir}/run/rspamd \
    -DENABLE_JEMALLOC=ON \
    -DWANT_SYSTEMD_UNITS=ON \
    -DSYSTEMDDIR=%{_unitdir} \
    -DENABLE_LUAJIT=ON \
    -DENABLE_HIREDIS=ON \
    -DLOGDIR=%{_localstatedir}/log/rspamd \
    -DEXAMPLESDIR=%{_datadir}/examples/rspamd \
    -DPLUGINSDIR=%{_datadir}/rspamd \
    -DLIBDIR=%{_libdir}/rspamd/ \
    -DINCLUDEDIR=%{_includedir} \
    -DNO_SHARED=ON \
    -DDEBIAN_BUILD=1 \
    -DRSPAMD_GROUP=%{rspamd_group} \
    -DRSPAMD_USER=%{rspamd_user} \
    -DENABLE_FANN=ON \
    -DENABLE_HYPERSCAN=ON

make %{?_smp_mflags}

%install
make DESTDIR=%{buildroot} INSTALLDIRS=vendor install
install -d -p -m 0755 %{buildroot}%{rspamd_home}
install -p -D -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}/local.d/
install -p -D -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}/override.d/

%clean
rm -rf %{buildroot}

%pre
%{_sbindir}/groupadd -r %{rspamd_group} 2>/dev/null || :
%{_sbindir}/useradd -g %{rspamd_group} -c "Rspamd user" -s /bin/false -r -d %{rspamd_home} %{rspamd_user} 2>/dev/null || :

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%defattr(-,root,root,-)
%{_unitdir}/%{name}.service
%{_mandir}/man8/%{name}.*
%{_mandir}/man1/rspamc.*
%{_mandir}/man1/rspamadm.*
%{_bindir}/rspamd
%{_bindir}/rspamd_stats
%{_bindir}/rspamc
%{_bindir}/rspamadm
%config(noreplace) %{rspamd_confdir}/modules.d/*
%config(noreplace) %{rspamd_confdir}/*.inc
%config(noreplace) %{rspamd_confdir}/*.conf
%attr(-, _rspamd, _rspamd) %dir %{rspamd_home}
%dir %{rspamd_rulesdir}/regexp
%dir %{rspamd_rulesdir}
%dir %{rspamd_confdir}
%dir %{rspamd_confdir}/modules.d
%dir %{rspamd_confdir}/local.d
%dir %{rspamd_confdir}/override.d
%dir %{rspamd_pluginsdir}
%dir %{rspamd_wwwdir}
%dir %{_libdir}/rspamd
%{rspamd_pluginsdir}/*
%{rspamd_rulesdir}/*
%{rspamd_wwwdir}/*
%{_libdir}/rspamd/*
%{_datadir}/rspamd/effective_tld_names.dat

%changelog
* %(date "+%a %b %d %Y") (Automated RPM build) - %{version}-%{release}
- See git log for actual changes.