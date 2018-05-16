%global _hardened_build 1

Summary: Automatic bug detection and reporting tool
Name: abrt
Version: 2.10.9
Release: 1%{?dist}
License: GPLv2+
URL: https://github.com/abrt
Source0: https://github.com/abrt/%{name}/archive/%{version}.tar.gz#%{name}-%{version}.tar.gz
Patch0: abrt-2.10.9-rpmlib.patch
Patch1: abrt-2.10.9-sphinx-build.patch
Patch2: abrt-2.10.9-notpy3.patch

BuildRequires: dbus-devel
BuildRequires: dbus-glib-devel
BuildRequires: gtk3-devel
BuildRequires: rpm-devel >= 4.6
BuildRequires: desktop-file-utils
BuildRequires: libnotify-devel
BuildRequires: python-devel
BuildRequires: gettext
BuildRequires: libxml2-devel
BuildRequires: intltool
BuildRequires: libtool
BuildRequires: nss-devel
BuildRequires: asciidoc
BuildRequires: doxygen
BuildRequires: xmlto
BuildRequires: libreport-devel
BuildRequires: satyr-devel
BuildRequires: systemd-python
BuildRequires: augeas
BuildRequires: libselinux-devel
BuildRequires: gsettings-desktop-schemas-devel
BuildRequires: libcap-devel
Requires: libreport
Requires: satyr
Requires: systemd-units
Requires(pre): shadow-utils
Requires: python-augeas
Requires: python-dbus
Requires: python-dmidecode
Requires: libreport-plugin-ureport
Requires: cpio
Requires: gdb >= 7.6.1-63
Requires: elfutils
Requires: libreport-python
Requires: xz
Requires: tar
Requires: curl

%description
%{name} is a tool to help users to detect defects in applications and
to create a bug report with all information needed by maintainer to fix it.
It uses plugin system to extend its functionality.

%package devel
Summary: Development libraries for %{name}

%description devel
Development libraries and headers for %{name}.

%prep
%autosetup -p1

%build
./gen-version
autoreconf --force --install
intltoolize --force --copy
%configure \
    --enable-doxygen-docs \
    --disable-silent-rules \
    --without-bodhi \
    --enable-native-unwinder \
    --enable-dump-time-unwind \
    --enable-suggest-autoreporting \
    --disable-addon-vmcore \
    --without-pythontests \
    --without-python3 \

make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot} mandir=%{_mandir} \
             dbusabrtdocdir=%{_defaultdocdir}/%{name}-dbus-%{version}/html/ \
             example_pythondir=%{_defaultdocdir}/%{name}-python-%{version}/examples

%find_lang %{name}

mkdir -p %{buildroot}%{_initrddir}
mkdir -p %{buildroot}%{_localstatedir}/cache/abrt-di
mkdir -p %{buildroot}%{_localstatedir}/run/abrt
mkdir -p %{buildroot}%{_localstatedir}/spool/abrt
mkdir -p %{buildroot}%{_localstatedir}/spool/abrt-upload

# After everything is installed, remove info dir
rm -f %{buildroot}%{_infodir}/dir

# Clean up python bytecode
find %{buildroot} -name '*.py[co]' -delete

# Clean up libtool
find %{buildroot} \( -name '*.la' -or -name '*.a' \) -delete

# Clean up cruft
rm -f %{buildroot}%{_sysconfdir}/profile.d/abrt-console-notification.sh
rm -f %{buildroot}%{_libdir}/libabrt_gui.so.*
rm -f %{buildroot}%{_includedir}/abrt/abrt-config-widget.h
rm -f %{buildroot}%{_includedir}/abrt/system-config-abrt.h
rm -f %{buildroot}%{_libdir}/libabrt_gui.so
rm -f %{buildroot}%{_libdir}/pkgconfig/abrt_gui.pc
rm -rf %{buildroot}%{_datadir}/icons/
rm -rf %{buildroot}%{_datadir}/%{name}/icons/
rm -f %{buildroot}%{_datadir}/%{name}/ui/*
rm -f %{buildroot}%{_bindir}/abrt-applet
rm -f %{buildroot}%{_bindir}/system-config-abrt
rm -f %{buildroot}%{_datadir}/applications/abrt-applet.desktop
rm -f %{buildroot}%{_sysconfdir}/xdg/autostart/abrt-applet.desktop
rm -f %{buildroot}%{_mandir}/man1/abrt-applet.1*
rm -f %{buildroot}%{_mandir}/man1/system-config-abrt.1*
rm -rf %{buildroot}%{python_sitelib}/problem_examples
rm -f %{buildroot}%{_journalcatalogdir}/*.catalog
rm -f %{buildroot}%{_sysconfdir}/bash_completion.d/abrt.bash_completion
# FIXME
rm -rf %{buildroot}/abrtcli

%pre
#uidgid pair 173:173 reserved in setup rhbz#670231
%define abrt_gid_uid 173
getent group abrt >/dev/null || groupadd -f -g %{abrt_gid_uid} --system abrt
getent passwd abrt >/dev/null || useradd --system -g abrt -u %{abrt_gid_uid} -d /etc/abrt -s /sbin/nologin abrt
exit 0

%post
/sbin/ldconfig
%systemd_post abrtd.service
%systemd_post abrt-journal-core.service
%systemd_post abrt-coredump-helper.service
%systemd_post abrt-ccpp.service
%systemd_post abrt-oops.service
%systemd_post abrt-xorg.service
%systemd_post abrt-pstoreoops.service
%systemd_post abrt-upload-watch.service

%preun
%systemd_preun abrtd.service
%systemd_preun abrt-journal-core.service
%systemd_preun abrt-coredump-helper.service
%systemd_preun abrt-ccpp.service
%systemd_preun abrt-oops.service
%systemd_preun abrt-xorg.service
%systemd_preun abrt-pstoreoops.service
%systemd_preun abrt-upload-watch.service

%postun
/sbin/ldconfig
%systemd_postun_with_restart abrtd.service
%systemd_postun_with_restart abrt-journal-core.service
%systemd_postun_with_restart abrt-coredump-helper.service
%systemd_postun_with_restart abrt-ccpp.service
%systemd_postun_with_restart abrt-oops.service
%systemd_postun_with_restart abrt-xorg.service
%systemd_postun_with_restart abrt-pstoreoops.service
%systemd_postun_with_restart abrt-upload-watch.service

%posttrans
service abrtd condrestart >/dev/null 2>&1 || :
service abrt-journal-core condrestart >/dev/null 2>&1 || :
service abrt-coredump-helper condrestart >/dev/null 2>&1 || :
service abrt-ccpp condrestart >/dev/null 2>&1 || :
service abrt-oops condrestart >/dev/null 2>&1 || :
service abrt-xorg condrestart >/dev/null 2>&1 || :
service abrt-pstoreoops condrestart >/dev/null 2>&1 || :
service abrt-upload-watch condrestart >/dev/null 2>&1 || :

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc COPYING
%doc %{_defaultdocdir}/%{name}/README.md
%doc %{_defaultdocdir}/%{name}-dbus-%{version}/html/*
%{_unitdir}/*
%{_tmpfilesdir}/abrt.conf
%{_sbindir}/*
%{_libexecdir}/*
%{_bindir}/*
%config(noreplace) %{_sysconfdir}/%{name}/*.conf
%{_datadir}/%{name}/conf.d
%config(noreplace) %{_sysconfdir}/%{name}/plugins/*.conf
%config(noreplace) %{_sysconfdir}/libreport/events.d/*.conf
%config(noreplace) %{_sysconfdir}/libreport/plugins/*.conf
%{_datadir}/libreport/events/*.xml
%{_libdir}/libabrt.so.*
%dir %attr(0751, root, abrt) %{_localstatedir}/spool/%{name}
%dir %attr(0700, abrt, abrt) %{_localstatedir}/spool/%{name}-upload
%dir %attr(0755, abrt, abrt) %{_localstatedir}/cache/abrt-di
# abrtd runs as root
%dir %attr(0755, root, root) %{_localstatedir}/run/%{name}
%ghost %attr(0666, -, -) %{_localstatedir}/run/%{name}/abrt.socket
%ghost %attr(0644, -, -) %{_localstatedir}/run/%{name}/abrtd.pid

%config(noreplace) %{_sysconfdir}/dbus-1/system.d/*.conf
%{_datadir}/dbus-1/interfaces/*
%{_datadir}/dbus-1/system-services/*
%{_datadir}/polkit-1/actions/abrt_polkit.policy

%{python_sitearch}/*

%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/plugins
%dir %{_datadir}/%{name}
%{_mandir}/man*/*

%{_datadir}/augeas/lenses/abrt.aug

%files devel
%defattr(-,root,root,-)
%doc apidoc/html/*.{html,png,css,js}
%{_includedir}/abrt/abrt-dbus.h
%{_includedir}/abrt/hooklib.h
%{_includedir}/abrt/libabrt.h
%{_includedir}/abrt/problem_api.h
%{_libdir}/libabrt.so
%{_libdir}/pkgconfig/abrt.pc


%changelog
* %(date "+%a %b %d %Y") (Automated RPM build) - %{version}-%{release}
- See git log for actual changes.
