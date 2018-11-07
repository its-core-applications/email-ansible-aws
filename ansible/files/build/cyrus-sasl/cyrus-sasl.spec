%define username        saslauth
%define hint            Saslauthd user
%define homedir         /run/saslauthd

%define _plugindir2 %{_libdir}/sasl2
%define bootstrap_cyrus_sasl 0

%global _performance_build 1

Summary: The Cyrus SASL library
Name: cyrus-sasl
Version: 2.1.27
Release: 1%{?dist}
License: BSD with advertising
Group: System Environment/Libraries
URL: https://www.cyrusimap.org/sasl/
Source0: https://github.com/cyrusimap/%{name}/archive/%{name}-%{version}.tar.gz
Source5: saslauthd.service
Source9: saslauthd.sysconfig
Requires: %{name}-lib%{?_isa} = %{version}-%{release}
# https://github.com/cyrusimap/cyrus-sasl/pull/472
Patch0:  cyrus-sasl-2.1.27-saslauthd-krb5.patch

BuildRequires: autoconf, automake, libtool, gdbm-devel, groff
BuildRequires: krb5-devel >= 1.2.2, openssl-devel, pam-devel, pkgconfig
BuildRequires: zlib-devel
BuildRequires: systemd
%{?systemd_requires}
Requires(post): chkconfig, /sbin/service
Requires(pre): /usr/sbin/useradd /usr/sbin/groupadd
Requires(postun): /usr/sbin/userdel /usr/sbin/groupdel
Requires: /sbin/nologin
Requires: systemd >= 219
Provides: user(%username)
Provides: group(%username)


%description
The %{name} package contains the Cyrus implementation of SASL.
SASL is the Simple Authentication and Security Layer, a method for
adding authentication support to connection-based protocols.

%package lib
Group: System Environment/Libraries
Summary: Shared libraries needed by applications which use Cyrus SASL

%description lib
The %{name}-lib package contains shared libraries which are needed by
applications which use the Cyrus SASL library.

%package devel
Requires: %{name}-lib%{?_isa} = %{version}-%{release}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: pkgconfig
Group: Development/Libraries
Summary: Files needed for developing applications with Cyrus SASL

%description devel
The %{name}-devel package contains files needed for developing and
compiling applications which use the Cyrus SASL library.


%prep
%autosetup -p 1 -n %{name}-%{name}-%{version}
chmod -x include/*.h

%build
autoreconf -fi
# Find Kerberos.
krb5_prefix=`krb5-config --prefix`
if test x$krb5_prefix = x%{_prefix} ; then
        krb5_prefix=
else
        CPPFLAGS="-I${krb5_prefix}/include $CPPFLAGS"; export CPPFLAGS
        LDFLAGS="-L${krb5_prefix}/%{_lib} $LDFLAGS"; export LDFLAGS
fi

# Find OpenSSL.
LIBS="-lcrypt"; export LIBS
if pkg-config openssl ; then
        CPPFLAGS="`pkg-config --cflags-only-I openssl` $CPPFLAGS"; export CPPFLAGS
        LDFLAGS="`pkg-config --libs-only-L openssl` $LDFLAGS"; export LDFLAGS
fi

CFLAGS="$RPM_OPT_FLAGS $CFLAGS $CPPFLAGS -fPIE"; export CFLAGS
LDFLAGS="$LDFLAGS -pie -Wl,-z,now"; export LDFLAGS

echo "$CFLAGS"
echo "$CPPFLAGS"
echo "$LDFLAGS"

%configure \
        --enable-shared --disable-static \
        --disable-java \
        --with-plugindir=%{_plugindir2} \
        --with-configdir=%{_plugindir2}:%{_sysconfdir}/sasl2 \
        --disable-krb4 \
        --enable-gssapi${krb5_prefix:+=${krb5_prefix}} \
        --with-gss_impl=mit \
        --with-rc4 \
        --with-dblib=none \
        --with-saslauthd=/run/saslauthd --without-pwcheck \
        --without-ldap \
        --with-devrandom=/dev/urandom \
        --disable-anon \
        --disable-cram \
        --disable-digest \
        --disable-ntlm \
        --enable-plain \
        --enable-login \
        --enable-alwaystrue \
        --disable-httpform \
        --disable-otp \
        --disable-ldapdb \
        --disable-sql \
        "$@"
        # --enable-auth-sasldb -- EXPERIMENTAL
make sasldir=%{_plugindir2}


%install
make install DESTDIR=%{buildroot} sasldir=%{_plugindir2}

# Install the saslauthd mdoc page in the expected location.  Sure, it's not
# really a man page, but groff seems to be able to cope with it.
install -m755 -d %{buildroot}%{_mandir}/man8/
install -m644 -p saslauthd/saslauthd.mdoc %{buildroot}%{_mandir}/man8/saslauthd.8
install -m644 -p saslauthd/testsaslauthd.8 %{buildroot}%{_mandir}/man8/testsaslauthd.8

# Install the init script for saslauthd and the init script's config file.
install -m755 -d %{buildroot}/etc/sysconfig
install -m755 -d %{buildroot}/%{_unitdir}
install -m644 -p %{SOURCE5} %{buildroot}/%{_unitdir}/saslauthd.service
install -m644 -p %{SOURCE9} %{buildroot}/etc/sysconfig/saslauthd

# Install the config dirs if they're not already there.
install -m755 -d %{buildroot}/%{_sysconfdir}/sasl2
install -m755 -d %{buildroot}/%{_plugindir2}

# Remove unpackaged files from the buildroot.
rm -f %{buildroot}%{_plugindir2}/libotp.*
rm -f %{buildroot}%{_plugindir2}/*.a
rm -f %{buildroot}%{_plugindir2}/*.la
rm -f %{buildroot}%{_libdir}/*.la
rm -f %{buildroot}%{_mandir}/cat8/saslauthd.8


%pre
getent group %{username} >/dev/null || groupadd -g 76 -r %{username}
getent passwd %{username} >/dev/null || useradd -r -g %{username} -d %{homedir} -s /sbin/nologin -c "%{hint}" %{username}

%post
%systemd_post saslauthd.service

%preun
%systemd_preun saslauthd.service

%postun
%systemd_postun_with_restart saslauthd.service

%post lib -p /sbin/ldconfig
%postun lib -p /sbin/ldconfig

%files
%defattr(-,root,root)
%doc saslauthd/LDAP_SASLAUTHD
%{_mandir}/man8/*
%{_sbindir}/pluginviewer
%{_sbindir}/saslauthd
%{_sbindir}/testsaslauthd
%config(noreplace) /etc/sysconfig/saslauthd
%{_unitdir}/saslauthd.service
%ghost /run/saslauthd

%files lib
%defattr(-,root,root)
%doc AUTHORS COPYING README
%{_libdir}/libsasl*.so.*
%dir %{_sysconfdir}/sasl2
%dir %{_plugindir2}/
%{_plugindir2}/*.so*

%files devel
%defattr(-,root,root)
%{_includedir}/*
%{_libdir}/libsasl*.*so
%{_libdir}/pkgconfig/*.pc
%{_mandir}/man3/*

%changelog
* %(date "+%a %b %d %Y") (Automated RPM build) - %{version}-%{release}
- See git log for actual changes.
