%define username	saslauth
%define hint		Saslauthd user
%define homedir		/run/saslauthd

%define _plugindir2 %{_libdir}/sasl2
%define bootstrap_cyrus_sasl 0

%global _performance_build 1

Summary: The Cyrus SASL library
Name: cyrus-sasl
Version: 2.1.26
Release: 52%{?dist}
License: BSD with advertising
Group: System Environment/Libraries
URL: https://www.cyrusimap.org/sasl/
Source0: ftp://ftp.cyrusimap.org/%{name}/%{name}-%{version}.tar.gz
Source5: saslauthd.service
Source9: saslauthd.sysconfig
Requires: %{name}-lib%{?_isa} = %{version}-%{release}
Patch1:  cyrus-sasl-2.1.26-servername.patch
Patch11: cyrus-sasl-2.1.25-no_rpath.patch
Patch15: cyrus-sasl-2.1.20-saslauthd.conf-path.patch
Patch23: cyrus-sasl-2.1.23-man.patch
Patch24: cyrus-sasl-2.1.21-sizes.patch
Patch31: cyrus-sasl-2.1.22-kerberos4.patch
Patch32: cyrus-sasl-2.1.26-warnings.patch
Patch42: cyrus-sasl-2.1.26-relro.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=816250
Patch43: cyrus-sasl-2.1.26-null-crypt.patch
Patch44: cyrus-sasl-2.1.26-release-server_creds.patch
# AM_CONFIG_HEADER is obsolete, use AC_CONFIG_HEADERS instead
Patch45: cyrus-sasl-2.1.26-obsolete-macro.patch
# missing size_t declaration in sasl.h
Patch46: cyrus-sasl-2.1.26-size_t.patch
# disable incorrect check for MkLinux
Patch47: cyrus-sasl-2.1.26-ppc.patch
# detect gsskrb5_register_acceptor_identity macro (#976538)
Patch48: cyrus-sasl-2.1.26-keytab.patch
Patch49: cyrus-sasl-2.1.26-md5global.patch
# improve sql libraries detection (#1029918)
Patch50: cyrus-sasl-2.1.26-sql.patch
# Treat SCRAM-SHA-1/DIGEST-MD5 as more secure than PLAIN (#970718)
Patch51: cyrus-sasl-2.1.26-prefer-SCRAM-SHA-1-over-PLAIN.patch
# Revert updated GSSAPI flags as in RFC 4752 to restore backward compatibility (#1154566)
Patch52: cyrus-sasl-2.1.26-revert-gssapi-flags.patch
# Support non-confidentiality/non-integrity requests from AIX SASL GSSAPI implementation (#1174322)
Patch54: cyrus-sasl-2.1.26-gssapi-non-encrypt.patch
# Update client library to be thread safe (#1147659)
Patch55: cyrus-sasl-2.1.26-make-client-thread-sage.patch
# Parsing short prefix matches the whole mechanism name (#1089267)
Patch56: cyrus-sasl-2.1.26-handle-single-character-mechanisms.patch
# Fix confusing message when config file has typo (#1022479)
Patch57: cyrus-sasl-2.1.26-error-message-when-config-has-typo.patch
# GSSAPI: Use per-connection mutex where possible (#1263017)
Patch58: cyrus-sasl-2.1.26-gssapi-use-per-connection-mutex.patch
# Too much loogging in GSSAPI resolved (#1187097)
Patch60: cyrus-sasl-2.1.26-user-specified-logging.patch

Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: autoconf, automake, libtool, gdbm-devel, groff
BuildRequires: krb5-devel >= 1.2.2, openssl-devel, pam-devel, pkgconfig
BuildRequires: zlib-devel
Requires(post): chkconfig, /sbin/service systemd-units
Requires(pre): /usr/sbin/useradd /usr/sbin/groupadd systemd-units
Requires(postun): /usr/sbin/userdel /usr/sbin/groupdel systemd-units
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
%setup -q
chmod -x doc/*.html
chmod -x include/*.h
%patch1  -p1 -b .servername
%patch11 -p1 -b .no-rpath
%patch15 -p1 -b .path
%patch23 -p1 -b .man
%patch24 -p1 -b .sizes
%patch31 -p1 -b .krb4
%patch32 -p1 -b .warnings
%patch42 -p1 -b .relro
%patch43 -p1 -b .null-crypt
%patch44 -p1 -b .release-server_creds
%patch45 -p1 -b .obsolete-macro
%patch46 -p1 -b .size_t
%patch47 -p1 -b .ppc
%patch48 -p1 -b .keytab
%patch49 -p1 -b .md5global.h
%patch50 -p1 -b .sql
%patch51 -p1 -b .sha1vsplain
%patch52 -p1 -b .revert
%patch54 -p1 -b .gssapi-non-encrypt
%patch55 -p1 -b .threads
%patch56 -p1 -b .prefix
%patch57 -p1 -b .typo
%patch58 -p1 -b .mutex
%patch60 -p1 -b .too-much-logging

%build
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
make -C saslauthd testsaslauthd
make -C sample


%install
test "$RPM_BUILD_ROOT" != "/" && rm -rf $RPM_BUILD_ROOT

make install DESTDIR=$RPM_BUILD_ROOT sasldir=%{_plugindir2}
make install DESTDIR=$RPM_BUILD_ROOT sasldir=%{_plugindir2} -C plugins

install -m755 -d $RPM_BUILD_ROOT%{_bindir}
./libtool --mode=install \
install -m755 sample/client $RPM_BUILD_ROOT%{_bindir}/sasl2-sample-client
./libtool --mode=install \
install -m755 sample/server $RPM_BUILD_ROOT%{_bindir}/sasl2-sample-server
./libtool --mode=install \
install -m755 saslauthd/testsaslauthd $RPM_BUILD_ROOT%{_sbindir}/testsaslauthd

# Install the saslauthd mdoc page in the expected location.  Sure, it's not
# really a man page, but groff seems to be able to cope with it.
install -m755 -d $RPM_BUILD_ROOT%{_mandir}/man8/
install -m644 -p saslauthd/saslauthd.mdoc $RPM_BUILD_ROOT%{_mandir}/man8/saslauthd.8
install -m644 -p saslauthd/testsaslauthd.8 $RPM_BUILD_ROOT%{_mandir}/man8/testsaslauthd.8

# Install the init script for saslauthd and the init script's config file.
install -m755 -d $RPM_BUILD_ROOT/etc/rc.d/init.d $RPM_BUILD_ROOT/etc/sysconfig
install -d -m755 $RPM_BUILD_ROOT/%{_unitdir}
install -m644 -p %{SOURCE5} $RPM_BUILD_ROOT/%{_unitdir}/saslauthd.service
install -m644 -p %{SOURCE9} $RPM_BUILD_ROOT/etc/sysconfig/saslauthd

# Install the config dirs if they're not already there.
install -m755 -d $RPM_BUILD_ROOT/%{_sysconfdir}/sasl2
install -m755 -d $RPM_BUILD_ROOT/%{_plugindir2}

# Remove unpackaged files from the buildroot.
rm -f $RPM_BUILD_ROOT%{_libdir}/sasl2/libotp.*
rm -f $RPM_BUILD_ROOT%{_libdir}/sasl2/*.a
rm -f $RPM_BUILD_ROOT%{_libdir}/sasl2/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
rm -f $RPM_BUILD_ROOT%{_mandir}/cat8/saslauthd.8


%clean
test "$RPM_BUILD_ROOT" != "/" && rm -rf $RPM_BUILD_ROOT

%pre
getent group %{username} >/dev/null || groupadd -g 76 -r %{username}
getent passwd %{username} >/dev/null || useradd -r -g %{username} -d %{homedir} -s /sbin/nologin -c "%{hint}" %{username}

%post
%systemd_post saslauthd.service

%preun
%systemd_preun saslauthd.service

%postun
%systemd_postun_with_restart saslauthd.service

%triggerun -n cyrus-sasl -- cyrus-sasl < 2.1.23-32
/usr/bin/systemd-sysv-convert --save saslauthd >/dev/null 2>&1 || :
/sbin/chkconfig --del saslauthd >/dev/null 2>&1 || :
/bin/systemctl try-restart saslauthd.service >/dev/null 2>&1 || :

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
%doc AUTHORS COPYING NEWS README doc/*.html
%{_libdir}/libsasl*.so.*
%dir %{_sysconfdir}/sasl2
%dir %{_plugindir2}/
%{_plugindir2}/*.so*

%files devel
%defattr(-,root,root)
%doc doc/*.txt
%{_bindir}/sasl2-sample-client
%{_bindir}/sasl2-sample-server
%{_includedir}/*
%{_libdir}/libsasl*.*so
%{_libdir}/pkgconfig/*.pc
%{_mandir}/man3/*

%changelog
* %(date "+%a %b %d %Y") (Automated RPM build) - %{version}-%{release}
- See git log for actual changes.
