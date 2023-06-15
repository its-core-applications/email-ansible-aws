Summary: A security tool which acts as a wrapper for TCP daemons
Name: tcp_wrappers
Version: 7.6
Release: 201%{?dist}

%global LIB_MAJOR 0
%global LIB_MINOR 7
%global LIB_REL 6

License: BSD
Source: http://ftp.porcupine.org/pub/security/%{name}_%{version}-ipv6.4.tar.gz
URL: http://ftp.porcupine.org/pub/security/index.html
Patch0: tcpw7.2-config.patch
Patch1: tcpw7.2-setenv.patch
Patch2: tcpw7.6-netgroup.patch
Patch3: tcp_wrappers-7.6-bug11881.patch
Patch4: tcp_wrappers-7.6-bug17795.patch
Patch5: tcp_wrappers-7.6-bug17847.patch
Patch6: tcp_wrappers-7.6-fixgethostbyname.patch
Patch7: tcp_wrappers-7.6-docu.patch
Patch8: tcp_wrappers-7.6-man.patch
Patch9: tcp_wrappers.usagi-ipv6.patch
Patch11: tcp_wrappers-7.6-shared.patch
Patch12: tcp_wrappers-7.6-sig.patch
Patch14: tcp_wrappers-7.6-ldflags.patch
Patch15: tcp_wrappers-7.6-fix_sig-bug141110.patch
Patch16: tcp_wrappers-7.6-162412.patch
Patch17: tcp_wrappers-7.6-220015.patch
Patch19: tcp_wrappers-7.6-siglongjmp.patch
Patch20: tcp_wrappers-7.6-sigchld.patch
Patch21: tcp_wrappers-7.6-196326.patch
Patch22: tcp_wrappers_7.6-249430.patch
Patch23: tcp_wrappers-7.6-inetdconf.patch
Patch24: tcp_wrappers-7.6-bug698464.patch
Patch26: tcp_wrappers-7.6-xgets.patch
Patch27: tcp_wrappers-7.6-initgroups.patch
Patch28: tcp_wrappers-7.6-warnings.patch
Patch29: tcp_wrappers-7.6-uchart_fix.patch
Patch30: tcp_wrappers-7.6-altformat.patch
# RFE: rhbz#1181815
Patch31: tcp_wrappers-7.6-aclexec.patch
Patch32: tcp_wrappers-inetcf-c99.patch
# required by sin_scope_id in ipv6 patch
BuildRequires: make
BuildRequires: glibc-devel >= 2.2
BuildRequires: gcc
BuildRequires: libnsl2-devel
Requires: tcp_wrappers-libs%{?_isa} = %{version}-%{release}

%description
The tcp_wrappers package provides small daemon programs which can
monitor and filter incoming requests for systat, finger, FTP, telnet,
rlogin, rsh, exec, tftp, talk and other network services.

Install the tcp_wrappers program if you need a security tool for
filtering incoming network services requests.

This version also supports IPv6.

%package libs
Summary: Libraries for tcp_wrappers

%description libs
tcp_wrappers-libs contains the libraries of the tcp_wrappers package.

%package devel
Summary: Development libraries and headers for tcp_wrappers
Requires: tcp_wrappers-libs%{?_isa} = %{version}-%{release}

%description devel
tcp_wrappers-devel contains the libraries and header files needed to
develop applications with tcp_wrappers support.

%prep
%setup -q -n %{name}_%{version}-ipv6.4
%patch0 -p1 -b .config
%patch1 -p1 -b .setenv
%patch2 -p1 -b .netgroup
%patch3 -p1 -b .bug11881
%patch4 -p1 -b .bug17795
%patch5 -p1 -b .bug17847
%patch6 -p1 -b .fixgethostbyname
%patch7 -p1 -b .docu
%patch8 -p1 -b .man
%patch9 -p1 -b .usagi-ipv6
%patch11 -p1 -b .shared
%patch12 -p1 -b .sig
%patch14 -p1 -b .ldflags
%patch15 -p1 -b .fix_sig
%patch16 -p1 -b .162412
%patch17 -p1 -b .220015
%patch19 -p1 -b .siglongjmp
%patch20 -p1 -b .sigchld
%patch21 -p1 -b .196326
%patch22 -p1 -b .249430
%patch23 -p1 -b .inetdconf
%patch24 -p1 -b .698464
%patch26 -p1 -b .xgets
%patch27 -p1 -b .initgroups
%patch29 -p1 -b .uchart_fix
%patch30 -p1 -b .altformat
%patch28 -p1 -b .warnings
%patch31 -p1 -b .aclexec
%patch32 -p1

%build
make \
RPM_OPT_FLAGS="$RPM_OPT_FLAGS -fPIC -DPIC -D_REENTRANT -DHAVE_STRERROR -DACLEXEC" \
LDFLAGS="$RPM_LD_FLAGS" \
MAJOR=%{LIB_MAJOR} MINOR=%{LIB_MINOR} REL=%{LIB_REL} linux %{?_smp_mflags}


%install
rm -rf ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}%{_includedir}
mkdir -p ${RPM_BUILD_ROOT}/%{_libdir}
mkdir -p ${RPM_BUILD_ROOT}%{_mandir}/man{3,5,8}
mkdir -p ${RPM_BUILD_ROOT}%{_sbindir}

install -p -m644 hosts_access.3 ${RPM_BUILD_ROOT}%{_mandir}/man3
install -p -m644 hosts_access.5 hosts_options.5 ${RPM_BUILD_ROOT}%{_mandir}/man5
install -p -m644 tcpd.8 tcpdchk.8 tcpdmatch.8 safe_finger.8 try-from.8 ${RPM_BUILD_ROOT}%{_mandir}/man8
ln -sf hosts_access.5 ${RPM_BUILD_ROOT}%{_mandir}/man5/hosts.allow.5
ln -sf hosts_access.5 ${RPM_BUILD_ROOT}%{_mandir}/man5/hosts.deny.5
#cp -a libwrap.a ${RPM_BUILD_ROOT}%{_libdirdir}
cp -a libwrap.so* ${RPM_BUILD_ROOT}/%{_libdir}
#install -p -m644 libwrap.so.0.7.6 ${RPM_BUILD_ROOT}/%{_libdir}
install -p -m644 tcpd.h ${RPM_BUILD_ROOT}%{_includedir}
install -m755 safe_finger ${RPM_BUILD_ROOT}%{_sbindir}
install -m755 tcpd ${RPM_BUILD_ROOT}%{_sbindir}
install -m755 try-from ${RPM_BUILD_ROOT}%{_sbindir}
install -m755 tcpdmatch ${RPM_BUILD_ROOT}%{_sbindir}

# XXX remove utilities that expect /etc/inetd.conf (#16059).
#install -m755 tcpdchk ${RPM_BUILD_ROOT}%{_sbindir}
rm -f ${RPM_BUILD_ROOT}%{_mandir}/man8/tcpdchk.*

%files
%{!?_licensedir:%global license %%doc}
%license DISCLAIMER
%doc BLURB CHANGES README* Banners.Makefile
%{_sbindir}/*
%{_mandir}/man8/*

%files libs
%{!?_licensedir:%global license %%doc}
%license DISCLAIMER
%doc BLURB CHANGES README* Banners.Makefile
%{_libdir}/*.so.*
%{_mandir}/man5/*

%files devel
%{_includedir}/*
%{_libdir}/*.so
%{_mandir}/man3/*

%changelog
* %(date "+%a %b %d %Y") (Automated RPM build) - %{version}-%{release}
- See git log for actual changes.
