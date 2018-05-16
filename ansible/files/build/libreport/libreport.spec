Summary: Generic library for reporting various problems
Name: libreport
Version: 2.9.5
Release: 3%{?dist}
License: GPLv2+
URL: https://github.com/abrt
Source0: https://github.com/abrt/%{name}/archive/%{version}.tar.gz#%{name}-%{version}.tar.gz
Patch0: libreport-2.9.5-debuginfo.patch

BuildRequires: dbus-devel
BuildRequires: gtk3-devel
BuildRequires: curl-devel
BuildRequires: desktop-file-utils
BuildRequires: xmlrpc-c-devel
BuildRequires: python-devel
BuildRequires: gettext
BuildRequires: libxml2-devel
BuildRequires: libtar-devel
BuildRequires: intltool
BuildRequires: libtool
BuildRequires: nss-devel
BuildRequires: texinfo
BuildRequires: asciidoc
BuildRequires: xmlto
BuildRequires: newt-devel
BuildRequires: libproxy-devel
BuildRequires: satyr-devel
BuildRequires: doxygen
BuildRequires: systemd-devel
BuildRequires: augeas-devel
BuildRequires: augeas
BuildRequires: libgnome-keyring-devel
Requires: libreport-filesystem = %{version}-%{release}
Requires: satyr

%description
Libraries providing API for reporting different problems in applications
to different bug targets like Bugzilla, ftp, trac, etc...

%package filesystem
Summary: Filesystem layout for libreport

%description filesystem
Filesystem layout for libreport

%package devel
Summary: Development libraries and headers for libreport
Requires: libreport = %{version}-%{release}

%description devel
Development libraries and headers for libreport

%package web
Summary: Library providing network API for libreport
Requires: libreport = %{version}-%{release}

%description web
Library providing network API for libreport

%package web-devel
Summary: Development headers for libreport-web
Requires: libreport-web = %{version}-%{release}

%description web-devel
Development headers for libreport-web

%package python
Summary: Python bindings for report-libs
Requires: libreport = %{version}-%{release}
Provides: report = 0:0.23-1
Obsoletes: report < 0:0.23-1

%description python
Python bindings for report-libs.

%package cli
Summary: %{name}'s command line interface
Requires: %{name} = %{version}-%{release}

%description cli
This package contains simple command line tool for working
with problem dump reports

%package newt
Summary: %{name}'s newt interface
Requires: %{name} = %{version}-%{release}
Provides: report-newt = 0:0.23-1
Obsoletes: report-newt < 0:0.23-1

%description newt
This package contains a simple newt application for reporting
bugs

%package gtk
Summary: GTK front-end for libreport
Requires: libreport = %{version}-%{release}
Requires: libreport-plugin-reportuploader = %{version}-%{release}
Requires: fros >= 1.0
Requires: pygobject3
Provides: report-gtk = 0:0.23-1
Obsoletes: report-gtk < 0:0.23-1

%description gtk
Applications for reporting bugs using libreport backend

%package gtk-devel
Summary: Development libraries and headers for libreport
Requires: libreport-gtk = %{version}-%{release}

%description gtk-devel
Development libraries and headers for libreport-gtk

%package plugin-kerneloops
Summary: %{name}'s kerneloops reporter plugin
Requires: curl
Requires: %{name} = %{version}-%{release}
Requires: libreport-web = %{version}-%{release}

%description plugin-kerneloops
This package contains plugin which sends kernel crash information to specified
server, usually to kerneloops.org.

%package plugin-logger
Summary: %{name}'s logger reporter plugin
Requires: %{name} = %{version}-%{release}

%description plugin-logger
The simple reporter plugin which writes a report to a specified file.

%package plugin-mailx
Summary: %{name}'s mailx reporter plugin
Requires: %{name} = %{version}-%{release}
Requires: mailx

%description plugin-mailx
The simple reporter plugin which sends a report via mailx to a specified
email address.

%package plugin-bugzilla
Summary: %{name}'s bugzilla plugin
Requires: %{name} = %{version}-%{release}
Requires: libreport-web = %{version}-%{release}

%package plugin-ureport
Summary: %{name}'s micro report plugin
BuildRequires: json-c-devel
Requires: %{name} = %{version}-%{release}
Requires: libreport-web = %{version}-%{release}

%description plugin-ureport
Uploads micro-report to abrt server

%description plugin-bugzilla
Plugin to report bugs into the bugzilla.

%package plugin-mantisbt
Summary: %{name}'s mantisbt plugin
Requires: %{name} = %{version}-%{release}
Requires: libreport-web = %{version}-%{release}

%description plugin-mantisbt
Plugin to report bugs into the mantisbt.

%package plugin-reportuploader
Summary: %{name}'s reportuploader plugin
Requires: %{name} = %{version}-%{release}
Requires: libreport-web = %{version}-%{release}

%description plugin-reportuploader
Plugin to report bugs into anonymous FTP site associated with ticketing system.

%prep
%autosetup -p1

%build
./gen-version
autoreconf --force --install
intltoolize --force --copy
%configure \
    --enable-doxygen-docs \
    --disable-silent-rules \
    --without-python3 \
    --without-mantisbt \
    --without-bugzilla \

make %{?_smp_mflags}

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} mandir=%{_mandir}
%find_lang %{name}

# Remove byte-compiled python files generated by automake.
# automake uses system's python for all *.py files, even
# for those which needs to be byte-compiled with different
# version (python2/python3).
# rpm can do this work and use the appropriate python version.
find %{buildroot} -name '*.py[co]' -delete

# remove all .la and .a files
find %{buildroot} \( -name '*.la' -or -name '*.a' \) -delete
mkdir -p %{buildroot}%{_initrddir}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/events.d/
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/events/
mkdir -p %{buildroot}%{_datadir}/%{name}/events/
mkdir -p %{buildroot}%{_datadir}/%{name}/workflows/

# After everything is installed, remove info dir
rm -f %{buildroot}%{_infodir}/dir

# Remove unwanted cruft
rm -f %{buildroot}%{_bindir}/reporter-rhtsupport
rm -f %{buildroot}%{_bindir}/reporter-systemd-journal
rm -f %{buildroot}%{_datadir}/dbus-1/interfaces/com.redhat.problems.configuration.bugzilla.xml
rm -f %{buildroot}%{_datadir}/dbus-1/interfaces/com.redhat.problems.configuration.rhtsupport.xml
rm -f %{buildroot}%{_datadir}/%{name}/conf.d/plugins/rhtsupport*
rm -f %{buildroot}%{_datadir}/%{name}/events/report_CentOS*
rm -f %{buildroot}%{_datadir}/%{name}/events/report_RHTSupport*
rm -f %{buildroot}%{_datadir}/%{name}/workflows/workflow_Anaconda*
rm -f %{buildroot}%{_datadir}/%{name}/workflows/workflow_CentOS*
rm -f %{buildroot}%{_datadir}/%{name}/workflows/workflow_Fedora*
rm -f %{buildroot}%{_datadir}/%{name}/workflows/workflow_RHEL*
rm -f %{buildroot}%{_mandir}/man1/reporter-mantisbt*
rm -f %{buildroot}%{_mandir}/man1/reporter-rhtsupport*
rm -f %{buildroot}%{_mandir}/man1/reporter-systemd-journal*
rm -f %{buildroot}%{_mandir}/man5/anaconda*
rm -f %{buildroot}%{_mandir}/man5/bugzilla*
rm -f %{buildroot}%{_mandir}/man5/centos*
rm -f %{buildroot}%{_mandir}/man5/mantisbt*
rm -f %{buildroot}%{_mandir}/man5/report_Bugzilla*
rm -f %{buildroot}%{_mandir}/man5/report_CentOS*
rm -f %{buildroot}%{_mandir}/man5/report_centos*
rm -f %{buildroot}%{_mandir}/man5/report_fedora*
rm -f %{buildroot}%{_mandir}/man5/report_rhel*
rm -f %{buildroot}%{_mandir}/man5/rhtsupport*
rm -f %{buildroot}%{_sysconfdir}/%{name}/events.d/centos*
rm -f %{buildroot}%{_sysconfdir}/%{name}/events.d/rhtsupport*
rm -f %{buildroot}%{_sysconfdir}/%{name}/plugins/rhtsupport*
rm -f %{buildroot}%{_sysconfdir}/%{name}/workflows.d/report_centos*
rm -f %{buildroot}%{_sysconfdir}/%{name}/workflows.d/report_fedora*
rm -f %{buildroot}%{_sysconfdir}/%{name}/workflows.d/report_rhel*

%post gtk
/sbin/ldconfig
# update icon cache
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%postun gtk
/sbin/ldconfig
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans gtk
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%post web -p /sbin/ldconfig


%postun web -p /sbin/ldconfig


%files -f %{name}.lang
%defattr(-,root,root,-)
%doc %{_defaultdocdir}/%{name}/README.md
%doc COPYING
%config(noreplace) %{_sysconfdir}/%{name}/libreport.conf
%config(noreplace) %{_sysconfdir}/%{name}/report_event.conf
%config(noreplace) %{_sysconfdir}/%{name}/forbidden_words.conf
%config(noreplace) %{_sysconfdir}/%{name}/ignored_words.conf
%{_libdir}/libreport.so.*
%{_libdir}/libabrt_dbus.so.*
%{_mandir}/man5/report_event.conf.5*
%{_mandir}/man5/forbidden_words.conf.5*
%{_mandir}/man5/ignored_words.conf.5*
%{_mandir}/man5/libreport.conf.5*
%{_datadir}/%{name}/conf.d/libreport.conf
# filesystem package owns /usr/share/augeas/lenses directory
%{_datadir}/augeas/lenses/libreport.aug

%files filesystem
%defattr(-,root,root,-)
%dir %{_sysconfdir}/%{name}/
%dir %{_sysconfdir}/%{name}/events.d/
%dir %{_sysconfdir}/%{name}/events/
%dir %{_sysconfdir}/%{name}/plugins/
%dir %{_datadir}/%{name}/events/
%dir %{_datadir}/%{name}/workflows/

%files devel
%defattr(-,root,root,-)
# Public api headers:
%doc apidoc/html/*.{html,png,css,js}
%{_includedir}/%{name}/libreport_types.h
%{_includedir}/%{name}/client.h
%{_includedir}/%{name}/dump_dir.h
%{_includedir}/%{name}/event_config.h
%{_includedir}/%{name}/problem_data.h
%{_includedir}/%{name}/report.h
%{_includedir}/%{name}/run_event.h
%{_includedir}/%{name}/file_obj.h
%{_includedir}/%{name}/config_item_info.h
%{_includedir}/%{name}/workflow.h
%{_includedir}/%{name}/ureport.h
%{_includedir}/%{name}/global_configuration.h
%{_includedir}/%{name}/reporters.h
%{_includedir}/%{name}/problem_utils.h
%{_includedir}/%{name}/problem_report.h
# Private api headers:
%{_includedir}/%{name}/helpers/*.h
%{_includedir}/%{name}/internal_abrt_dbus.h
%{_includedir}/%{name}/internal_libreport.h
%{_includedir}/%{name}/xml_parser.h
%{_libdir}/libreport.so
%{_libdir}/libabrt_dbus.so
%{_libdir}/pkgconfig/libreport.pc
%dir %{_includedir}/libreport
%dir %{_includedir}/libreport/helpers

%files web
%defattr(-,root,root,-)
%{_libdir}/libreport-web.so.*

%files web-devel
%defattr(-,root,root,-)
%{_libdir}/libreport-web.so
%{_includedir}/%{name}/libreport_curl.h
%{_libdir}/pkgconfig/libreport-web.pc

%files python
%defattr(-,root,root,-)
%{python_sitearch}/report/*
%{python_sitearch}/reportclient/*

%files cli
%defattr(-,root,root,-)
%{_bindir}/report-cli
%{_mandir}/man1/report-cli.1*

%files newt
%defattr(-,root,root,-)
%{_bindir}/report-newt
%{_mandir}/man1/report-newt.1*

%files gtk
%defattr(-,root,root,-)
%{_bindir}/report-gtk
%{_libdir}/libreport-gtk.so.*
%config(noreplace) %{_sysconfdir}/%{name}/events.d/emergencyanalysis_event.conf
%{_mandir}/man5/emergencyanalysis_event.conf.5*
%{_datadir}/%{name}/events/report_EmergencyAnalysis.xml
%{_mandir}/man1/report-gtk.1*


%files gtk-devel
%defattr(-,root,root,-)
%{_libdir}/libreport-gtk.so
%{_includedir}/%{name}/internal_libreport_gtk.h
%{_includedir}/%{name}/problem_details_dialog.h
%{_includedir}/%{name}/problem_details_widget.h
%{_libdir}/pkgconfig/libreport-gtk.pc

%files plugin-kerneloops
%defattr(-,root,root,-)
%{_datadir}/%{name}/events/report_Kerneloops.xml
%{_mandir}/man*/reporter-kerneloops.*
%{_bindir}/reporter-kerneloops

%files plugin-logger
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/events/report_Logger.conf
%{_mandir}/man5/report_Logger.conf.5*
%{_datadir}/%{name}/events/report_Logger.xml
%{_datadir}/%{name}/workflows/workflow_Logger.xml
%{_datadir}/%{name}/workflows/workflow_LoggerCCpp.xml
%config(noreplace) %{_sysconfdir}/%{name}/events.d/print_event.conf
%config(noreplace) %{_sysconfdir}/%{name}/workflows.d/report_logger.conf
%{_mandir}/man5/print_event.conf.5*
%{_mandir}/man5/report_logger.conf.5*
%{_bindir}/reporter-print
%{_mandir}/man*/reporter-print.*

%files plugin-mailx
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/plugins/mailx.conf
%{_datadir}/%{name}/conf.d/plugins/mailx.conf
%{_datadir}/%{name}/events/report_Mailx.xml
%{_datadir}/%{name}/workflows/workflow_Mailx.xml
%{_datadir}/%{name}/workflows/workflow_MailxCCpp.xml
%{_datadir}/dbus-1/interfaces/com.redhat.problems.configuration.mailx.xml
%config(noreplace) %{_sysconfdir}/%{name}/events.d/mailx_event.conf
%config(noreplace) %{_sysconfdir}/%{name}/workflows.d/report_mailx.conf
%{_mandir}/man5/mailx.conf.5*
%{_mandir}/man5/mailx_event.conf.5*
%{_mandir}/man5/report_mailx.conf.5*
%{_mandir}/man*/reporter-mailx.*
%{_bindir}/reporter-mailx

%files plugin-ureport
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/plugins/ureport.conf
%config(noreplace) %{_sysconfdir}/%{name}/workflows.d/report_uReport.conf
%{_datadir}/%{name}/conf.d/plugins/ureport.conf
%{_bindir}/reporter-ureport
%{_mandir}/man1/reporter-ureport.1*
%{_mandir}/man5/ureport.conf.5*
%{_mandir}/man5/report_uReport.conf.5*
%{_datadir}/%{name}/events/report_uReport.xml
%{_datadir}/%{name}/workflows/workflow_uReport.xml
%{_datadir}/dbus-1/interfaces/com.redhat.problems.configuration.ureport.xml

%files plugin-reportuploader
%defattr(-,root,root,-)
%{_mandir}/man*/reporter-upload.*
%{_mandir}/man5/uploader_event.conf.5*
%{_mandir}/man5/report_uploader.conf.5*
%{_bindir}/reporter-upload
%config(noreplace) %{_sysconfdir}/%{name}/workflows.d/report_uploader.conf
%config(noreplace) %{_sysconfdir}/%{name}/events.d/uploader_event.conf
%{_datadir}/%{name}/events/report_Uploader.xml
%{_datadir}/%{name}/workflows/workflow_Upload.xml
%{_datadir}/%{name}/workflows/workflow_UploadCCpp.xml
%config(noreplace) %{_sysconfdir}/%{name}/events/report_Uploader.conf
%{_mandir}/man5/report_Uploader.conf.5*
%config(noreplace) %{_sysconfdir}/%{name}/plugins/upload.conf
%{_datadir}/%{name}/conf.d/plugins/upload.conf
%{_mandir}/man5/upload.conf.5*

%changelog
* %(date "+%a %b %d %Y") (Automated RPM build) - %{version}-%{release}
- See git log for actual changes.
