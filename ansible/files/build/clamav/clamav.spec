#global prerelease	rc1

## Fedora Extras specific customization below...
%bcond_without		fedora
%bcond_without		tmpfiles
%bcond_with		unrar
%bcond_without		noarch
%bcond_with		bytecode
##

%global _hardened_build	1

%ifnarch s390 s390x
%global have_ocaml	1
%else
%global have_ocaml	0
%endif

%global username	clamupdate
%global homedir		%_var/lib/clamav
%global freshclamlog	%_var/log/freshclam.log
%global milteruser	clamilt
%global milterlog	%_var/log/clamav-milter.log
%global milterstatedir	%_var/run/clamav-milter
%global pkgdatadir	%_datadir/%name

%global scanuser	clamscan

%{?with_noarch:%global noarch	BuildArch:	noarch}
%{!?_unitdir:%global _unitdir /lib/systemd/system}
%{!?_initrddir:%global _initrddir /etc/rc.d/init.d}
%{!?release_func:%global release_func() %%{?prerelease:0.}%1%%{?prerelease:.%%prerelease}%%{?dist}}
%{!?apply:%global  apply(p:n:b:) %patch%%{-n:%%{-n*}} %%{-p:-p %%{-p*}} %%{-b:-b %%{-b*}} \
%nil}

Summary:	End-user tools for the Clam Antivirus scanner
Name:		clamav
Version:	0.99.2
# Set epoch so that we're always considered a higher version
# 17 is not special, I just like it.
Epoch:		17
Release:	1%{?dist}
License:	proprietary
Group:		Applications/File
URL:		http://www.clamav.net
Source0:	http://www.clamav.net/downloads/production/%name-%version%{?prerelease}.tar.gz
Source999:	http://www.clamav.net/downloads/production/%name-%version%{?prerelease}.tar.gz.sig

# Local umich patches; reusing 0 because it seems sane.
Patch0:		clamav-0.99-umich-safereload.patch

Patch27:	clamav-0.98-umask.patch
# https://bugzilla.redhat.com/attachment.cgi?id=403775&action=diff&context=patch&collapsed=&headers=1&format=raw
# https://llvm.org/viewvc/llvm-project/llvm/trunk/lib/ExecutionEngine/JIT/Intercept.cpp?r1=128086&r2=137567
Patch30:	llvm-glibc.patch
BuildRoot:	%_tmppath/%name-%version-%release-root
Requires:	clamav-lib = %epoch:%version-%release
Requires:	data(clamav)
BuildRequires:	zlib-devel bzip2-devel gmp-devel curl-devel
BuildRequires:	ncurses-devel openssl-devel libxml2-devel
BuildRequires:	%_includedir/tcpd.h
%{?with_bytecode:BuildRequires:	bc tcl groff graphviz}
%if %{have_ocaml}
%{?with_bytecode:BuildRequires:	ocaml}
%endif

%package filesystem
Summary:	Filesystem structure for clamav
Group:		Applications/File
Provides:	user(%username)  = 4
Provides:	group(%username) = 4
# Prevent version mix
Conflicts:	%name < %epoch:%version-%release
Conflicts:	%name > %epoch:%version-%release
Requires(pre):  shadow-utils
%{?noarch}

%package lib
Summary:	Dynamic libraries for the Clam Antivirus scanner
Group:		System Environment/Libraries
Requires:	data(clamav)

%package devel
Summary:	Header files and libraries for the Clam Antivirus scanner
Group:		Development/Libraries
Source100:	clamd-gen
Requires:	clamav-lib        = %epoch:%version-%release
Requires:	clamav-filesystem = %epoch:%version-%release

%package data-empty
Summary:	Empty data package for the Clam Antivirus scanner
Group:		Applications/File
Provides:	data(clamav) = empty
Conflicts:	data(clamav) < empty
Conflicts:	data(clamav) > empty
%{?noarch}

%package update
Summary:	Auto-updater for the Clam Antivirus scanner data-files
Group:		Applications/File
Source201:	freshclam.sysconfig
Source203:	clamav-update.logrotate
Requires:	clamav-filesystem = %epoch:%version-%release
Requires:	crontabs
Requires(pre):		/etc/cron.d
Requires(postun):	/etc/cron.d
Requires(post):		%__chown %__chmod
Requires(post):		group(%username)

%package server
Summary:	Clam Antivirus scanner server
Group:		System Environment/Daemons
Source2:	clamd.sysconfig
Source3:	clamd.logrotate
Source5:	clamd-README
Source8:	clamav-notify-servers
Requires:	data(clamav)
Requires:	clamav-filesystem = %epoch:%version-%release
Requires:	clamav-lib        = %epoch:%version-%release
Requires:	nc coreutils
Source520:      clamd-wrapper
%{?systemd_reqs}

%package milter
Summary:	Milter module for the Clam Antivirus scanner
Group:		System Environment/Daemons
Source300:	README.fedora
BuildRequires:	sendmail-devel
Provides:	user(%milteruser)  = 5
Provides:	group(%milteruser) = 5
Requires(post):	coreutils
Requires(pre):  shadow-utils
Provides:	milter(clamav) = sendmail
Provides:	milter(clamav) = postfix
Provides:	clamav-milter-core = %epoch:%version-%release
Obsoletes:	clamav-milter-core < %epoch:%version-%release
Provides:	clamav-milter-sendmail = %epoch:%version-%release
Obsoletes:	clamav-milter-sendmail < %epoch:%version-%release
Source330:	clamav-milter.systemd
%{?systemd_reqs}

%description
Clam AntiVirus is an anti-virus toolkit for UNIX. The main purpose of this
software is the integration with mail servers (attachment scanning). The
package provides a flexible and scalable multi-threaded daemon, a command
line scanner, and a tool for automatic updating via Internet. The programs
are based on a shared library distributed with the Clam AntiVirus package,
which you can use with your own software. The virus database is based on
the virus database from OpenAntiVirus, but contains additional signatures
(including signatures for popular polymorphic viruses, too) and is KEPT UP
TO DATE.

%description filesystem
This package provides the filesystem structure and contains the
user-creation scripts required by clamav.

%description lib
This package contains dynamic libraries shared between applications
using the Clam Antivirus scanner.

%description devel
This package contains headerfiles and libraries which are needed to
build applications using clamav.

%description data-empty
This is an empty package to fulfill inter-package dependencies of the
clamav suite. This package and the 'clamav-data' package are mutually
exclusive.

Use -data when you want a working (but perhaps outdated) virus scanner
immediately after package installation.

Use -data-empty when you are updating the virus database regulary and
do not want to download a >5MB sized rpm-package with outdated virus
definitions.


%description update
This package contains programs which can be used to update the clamav
anti-virus database automatically. It uses the freshclam(1) utility for
this task. To activate it, uncomment the entry in /etc/cron.d/clamav-update.

%description server
ATTENTION: most users do not need this package; the main package has
everything (or depends on it) which is needed to scan for virii on
workstations.

This package contains files which are needed to execute the clamd-daemon.
This daemon does not provide a system-wide service. Instead of, an instance
of this daemon should be started for each service requiring it.

See the README file how this can be done with a minimum of effort.


%description milter
This package contains files which are needed to run the clamav-milter.

## ------------------------------------------------------------

%prep
%setup -q -n %{name}-%{version}%{?prerelease}

%apply -n0 -p1

%apply -n27 -p1 -b .umask
%apply -n30 -p1
%{?apply_end}

install -p -m0644 %SOURCE300 clamav-milter/

mkdir -p libclamunrar{,_iface}

sed -ri \
    -e 's!^#?(LogFile ).*!#\1/var/log/clamd.<SERVICE>!g' \
    -e 's!^#?(LocalSocket ).*!#\1/var/run/clamd.<SERVICE>/clamd.sock!g' \
    -e 's!^(#?PidFile ).*!\1/var/run/clamd.<SERVICE>/clamd.pid!g' \
    -e 's!^#?(User ).*!\1<USER>!g' \
    -e 's!^#?(AllowSupplementaryGroups|LogSyslog).*!\1 yes!g' \
    -e 's! /usr/local/share/clamav,! %homedir,!g' \
    etc/clamd.conf.sample

sed -ri \
    -e 's!^#?(UpdateLogFile )!#\1!g;' \
    -e 's!^#?(LogSyslog).*!\1 yes!g' \
    -e 's!(DatabaseOwner *)clamav$!\1%username!g' etc/freshclam.conf.sample


## ------------------------------------------------------------

%build
CFLAGS="$RPM_OPT_FLAGS -Wall -W -Wmissing-prototypes -Wmissing-declarations -std=gnu99"
export LDFLAGS='-Wl,--as-needed'
# HACK: remove me...
export FRESHCLAM_LIBS='-lz'
# IPv6 check is buggy and does not work when there are no IPv6 interface on build machine
export have_cv_ipv6=yes
%configure \
	--disable-static \
	--disable-rpath \
	--disable-silent-rules \
	--disable-clamav \
	--with-user=%username \
	--with-group=%username \
	--with-libcurl=%{_prefix} \
	--with-dbdir=/var/lib/clamav \
	--enable-milter \
	--enable-clamdtop \
	%{!?with_bytecode:--disable-llvm} \

# TODO: check periodically that CLAMAVUSER is used for freshclam only


# build with --as-needed and disable rpath
sed -i \
	-e 's! -shared ! -Wl,--as-needed\0!g'					\
	-e '/sys_lib_dlsearch_path_spec=\"\/lib \/usr\/lib /s!\"\/lib \/usr\/lib !/\"/%_lib /usr/%_lib !g'	\
	libtool


make %{?_smp_mflags}


## ------------------------------------------------------------

%install
rm -rf "$RPM_BUILD_ROOT" _doc*
make DESTDIR="$RPM_BUILD_ROOT" install

function smartsubst() {
	local tmp
	local regexp=$1
	shift

	tmp=$(mktemp /tmp/%name-subst.XXXXXX)
	for i; do
		sed -e "$regexp" "$i" >$tmp
		cmp -s $tmp "$i" || cat $tmp >"$i"
		rm -f $tmp
	done
}


install -d -m 0755 \
	$RPM_BUILD_ROOT%_sysconfdir/{mail,clamd.d,logrotate.d,tmpfiles.d} \
	$RPM_BUILD_ROOT%_var/{log,run} \
	$RPM_BUILD_ROOT%milterstatedir \
	$RPM_BUILD_ROOT%pkgdatadir/template \
	$RPM_BUILD_ROOT%_initrddir \
	$RPM_BUILD_ROOT%homedir \

rm -f	$RPM_BUILD_ROOT%_sysconfdir/clamd.conf.sample \
	$RPM_BUILD_ROOT%_libdir/*.la


touch $RPM_BUILD_ROOT%homedir/daily.cld
touch $RPM_BUILD_ROOT%homedir/main.cld

## prepare the server-files
install -D -m 0644 -p %SOURCE2		_doc_server/clamd.sysconfig
install -D -m 0644 -p %SOURCE3		_doc_server/clamd.logrotate
install -D -m 0644 -p %SOURCE5		_doc_server/README
install -D -m 0644 -p etc/clamd.conf.sample	_doc_server/clamd.conf

install -m 0644 -p %SOURCE520		$RPM_BUILD_ROOT%pkgdatadir/
install -m 0755 -p %SOURCE100		$RPM_BUILD_ROOT%pkgdatadir/
cp -pa _doc_server/*			$RPM_BUILD_ROOT%pkgdatadir/template

smartsubst 's!/usr/share/clamav!%pkgdatadir!g' $RPM_BUILD_ROOT%pkgdatadir/clamd-wrapper


## prepare the update-files
install -D -m 0644 -p %SOURCE203	$RPM_BUILD_ROOT%_sysconfdir/logrotate.d/clamav-update
install -D -m 0755 -p %SOURCE8		$RPM_BUILD_ROOT%_sbindir/clamav-notify-servers
touch $RPM_BUILD_ROOT%freshclamlog

install -D -p -m 0644 %SOURCE201	$RPM_BUILD_ROOT%_sysconfdir/sysconfig/freshclam
mv -f $RPM_BUILD_ROOT%_sysconfdir/freshclam.conf{.sample,}


### The milter stuff
sed -r \
    -e 's!^#?(User).*!\1 %milteruser!g' \
    -e 's!^#?(AllowSupplementaryGroups|LogSyslog) .*!\1 yes!g' \
    -e 's! /tmp/clamav-milter.socket! %milterstatedir/clamav-milter.socket!g' \
    -e 's! /var/run/clamav-milter.pid! %milterstatedir/clamav-milter.pid!g' \
    -e 's! /tmp/clamav-milter.log! %milterlog!g' \
    etc/clamav-milter.conf.sample > $RPM_BUILD_ROOT%_sysconfdir/mail/clamav-milter.conf

install -D -p -m 0644 %SOURCE330 $RPM_BUILD_ROOT%_unitdir/clamav-milter.service

cat << EOF > $RPM_BUILD_ROOT%_sysconfdir/tmpfiles.d/clamav-milter.conf
d %milterstatedir 0710 %milteruser %milteruser
EOF

rm -f $RPM_BUILD_ROOT%_sysconfdir/clamav-milter.conf.sample
touch $RPM_BUILD_ROOT{%milterstatedir/clamav-milter.{socket,pid},%milterlog}

rm -rf $RPM_BUILD_ROOT%_sysconfdir/init
rm -f  $RPM_BUILD_ROOT%_initrddir/*
rm -rf $RPM_BUILD_ROOT%_var/run/*/*.pid
%{!?with_tmpfiles: rm -rf $RPM_BUILD_ROOT%_sysconfdir/tmpfiles.d}

# keep clamd-wrapper in every case because it might be needed by other
# packages
ln -s %pkgdatadir/clamd-wrapper		$RPM_BUILD_ROOT%_initrddir/clamd-wrapper

## ------------------------------------------------------------

%check
make check

## ------------------------------------------------------------

%clean
rm -rf "$RPM_BUILD_ROOT"

## ------------------------------------------------------------

%pre filesystem
getent group %{username} >/dev/null || groupadd -r %{username}
getent passwd %{username} >/dev/null || \
    useradd -r -g %{username} -d %{homedir} -s /sbin/nologin \
    -c "Clamav database update user" %{username}
exit 0


%post server
test "$1" != "1" || /bin/systemctl daemon-reload >/dev/null 2>&1 || :

%postun server
/bin/systemctl daemon-reload >/dev/null 2>&1 || :


%post update
test -e %freshclamlog || {
	touch %freshclamlog
	%__chmod 0664 %freshclamlog
	%__chown root:%username %freshclamlog
	! test -x /sbin/restorecon || /sbin/restorecon %freshclamlog
}

%triggerin update -- %name-update < 0.97.3-1704
# remove me after F19
! test -x /sbin/restorecon || /sbin/restorecon %freshclamlog &>/dev/null || :


%pre milter
getent group %{milteruser} >/dev/null || groupadd -r %{milteruser}
getent passwd %{milteruser} >/dev/null || \
    useradd -r -g %{milteruser} -d %{milterstatedir} -s /sbin/nologin \
    -c "Clamav Milter user" %{milteruser}
exit 0


%post milter
test -e %milterlog || {
	touch %milterlog
	chmod 0620             %milterlog
	chown root:%milteruser %milterlog
	! test -x /sbin/restorecon || /sbin/restorecon %milterlog
}
/bin/systemd-tmpfiles --create %_sysconfdir/tmpfiles.d/clamav-milter.conf || :


%triggerin milter -- %name-milter < 0.97.3-1704
# remove me after F19
! test -x /sbin/restorecon || /sbin/restorecon %milterlog &>/dev/null || :


%systemd_install milter-systemd clamav-milter.service


%post   lib -p /sbin/ldconfig
%postun lib -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc AUTHORS BUGS COPYING ChangeLog FAQ NEWS README UPGRADE
%doc docs/*.pdf
%_bindir/*
%_mandir/man[15]/*
%exclude %_bindir/clamav-config
%exclude %_bindir/freshclam
%exclude %_mandir/*/freshclam*

## -----------------------

%files lib
%defattr(-,root,root,-)
%_libdir/*.so.*

## -----------------------

%files devel
%defattr(-,root,root,-)
%_includedir/*
%_libdir/*.so
%pkgdatadir/template
%pkgdatadir/clamd-gen
%_libdir/pkgconfig/*
%_bindir/clamav-config

## -----------------------

%files filesystem
%attr(-,%username,%username) %dir %homedir
%attr(-,root,root)           %dir %pkgdatadir

## -----------------------

%files data-empty
%defattr(-,%username,%username,-)
%ghost %attr(0664,%username,%username) %homedir/main.cvd
%ghost %attr(0664,%username,%username) %homedir/daily.cvd


## -----------------------

%files update
%defattr(-,root,root,-)
%_bindir/freshclam
%_mandir/*/freshclam*
%config(noreplace) %verify(not mtime)    %_sysconfdir/freshclam.conf
%config(noreplace) %verify(not mtime)    %_sysconfdir/logrotate.d/*
%config(noreplace) %_sysconfdir/sysconfig/freshclam
%_unitdir/clamav-freshclam.service

%ghost %attr(0664,root,%username) %verify(not size md5 mtime) %freshclamlog
%ghost %attr(0664,%username,%username) %homedir/*.cld


## -----------------------

%files server
%defattr(-,root,root,-)
%doc _doc_server/*
%_mandir/man[58]/clamd*
%_sbindir/*
%dir %_sysconfdir/clamd.d

%exclude %_sbindir/*milter*
%exclude %_mandir/man8/clamav-milter*

%defattr(-,root,root,-)
%_initrddir/clamd-wrapper
%pkgdatadir/clamd-wrapper
%_unitdir/clamav-daemon.service
%_unitdir/clamav-daemon.socket

## -----------------------

## -----------------------

%files milter
%defattr(-,root,root,-)
%doc clamav-milter/README.fedora
%_sbindir/*milter*
%_mandir/man8/clamav-milter*
%config(noreplace) %_sysconfdir/mail/clamav-milter.conf
%ghost %attr(0620,root,%milteruser) %verify(not size md5 mtime) %milterlog
%ghost %milterstatedir/clamav-milter.socket

%if 0%{?with_tmpfiles:1}
  %_sysconfdir/tmpfiles.d/clamav-milter.conf
  %ghost %dir %attr(0710,%milteruser,%milteruser) %milterstatedir
%else
  %dir %attr(0710,%milteruser,%milteruser) %milterstatedir
%endif

 %defattr(-,root,root,-)
 %_unitdir/clamav-milter.service


%changelog
* Thu Jan 29 2015 Robert Scheck <robert@fedoraproject.org> - 0.98.6-1
- Upgrade to 0.98.6 and updated daily.cvd (#1187050)
