%define real_name Mail-SpamAssassin
%{!?perl_vendorlib: %define perl_vendorlib %(eval "`%{__perl} -V:installvendorlib`"; echo $installvendorlib)}

%global saversion 3.004001

Summary: Spam filter for email which can be invoked from mail delivery agents
Name: spamassassin
Version: 3.4.1
Epoch: 17
Release: 2%{?dist}
License: ASL 2.0
Group: Applications/Internet
URL: http://spamassassin.apache.org/
Source0: http://www.apache.org/dist/%{name}/source/%{real_name}-%{version}.tar.bz2
Source1: http://www.apache.org/dist/%{name}/source/%{real_name}-rules-%{version}.r1675274.tgz
Source5: spamassassin.sysconfig
Source6: sa-update.logrotate
Source7: sa-update.crontab
Source8: sa-update.cronscript
Source9: sa-update.force-sysconfig
Source10: spamassassin-helper.sh
Source11: spamassassin-official.conf
Source14: spamassassin.service

Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires: /sbin/chkconfig /sbin/service
Requires(post): diffutils

BuildRequires: perl >= 2:5.8.0
BuildRequires: perl(Net::DNS)
BuildRequires: perl(Time::HiRes)
BuildRequires: perl(HTML::Parser)
BuildRequires: perl(NetAddr::IP)
BuildRequires: openssl-devel
BuildRequires: systemd-units

Requires: perl(HTTP::Date)
Requires: perl(LWP::UserAgent)
Requires: perl(Net::DNS)
Requires: perl(Time::HiRes)
Requires: perl(DB_File)
Requires: perl(Mail::SPF)
Requires: perl(Encode::Detect)
Requires: procmail
Requires: gnupg

# We use portreserve to prevent our TCP port being stolen.
# Require the package here so that we know /etc/portreserve/ exists.
Requires: portreserve

# Hard requirements
BuildRequires: perl-devel
BuildRequires: perl-HTML-Parser >= 3.43
Requires: perl-HTML-Parser >= 3.43
BuildRequires: perl(Archive::Tar)
Requires: perl(Archive::Tar)

# Needed for spamc/spamd SSL
Requires: perl(IO::Socket::SSL)
# Needed for IPv6
Requires: perl(IO::Socket::INET6)
# Needed for DKIM
Requires: perl(Mail::DKIM)

Requires(post): systemd-units
Requires(post): systemd-sysv
Requires(preun): systemd-units
Requires(postun): systemd-units

Obsoletes: perl-Mail-SpamAssassin

%description
SpamAssassin provides you with a way to reduce if not completely eliminate
Unsolicited Commercial Email (SPAM) from your incoming email.  It can
be invoked by a MDA such as sendmail or postfix, or can be called from
a procmail script, .forward file, etc.  It uses a genetic-algorithm
evolved scoring system to identify messages which look spammy, then
adds headers to the message so they can be filtered by the user's mail
reading software.  This distribution includes the spamd/spamc components
which create a server that considerably speeds processing of mail.

%prep
%setup -q -n %{real_name}-%{version}

%build
export CFLAGS="$RPM_OPT_FLAGS"
%{__perl} Makefile.PL DESTDIR=$RPM_BUILD_ROOT/ SYSCONFDIR=%{_sysconfdir} INSTALLDIRS=vendor ENABLE_SSL=yes < /dev/null
%{__make} OPTIMIZE="$RPM_OPT_FLAGS" %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall PREFIX=%buildroot/%{prefix} \
        INSTALLMAN1DIR=%buildroot/%{_mandir}/man1 \
        INSTALLMAN3DIR=%buildroot/%{_mandir}/man3 \
        LOCAL_RULES_DIR=%{buildroot}/etc/mail/spamassassin
chmod 755 %buildroot/%{_bindir}/* # allow stripping

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/mail/spamassassin
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/cron.d
install -m644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/spamassassin

# installed mode 755 as it's executed by users. 
install -m 0755 %{SOURCE10} %buildroot/etc/mail/spamassassin
install -m 0644 %{SOURCE6} %buildroot/etc/logrotate.d/sa-update
install -m 0644 %{SOURCE7} %buildroot/etc/cron.d/sa-update
install -m 0644 %{SOURCE9} %buildroot%{_sysconfdir}/sysconfig/sa-update
# installed mode 744 as non root users can't run it, but can read it.
install -m 0744 %{SOURCE8} %buildroot%{_datadir}/spamassassin/sa-update.cron
mkdir -p %buildroot%{_unitdir}
install -m 0644 %{SOURCE14} %buildroot%{_unitdir}/spamassassin.service

[ -x /usr/lib/rpm/brp-compress ] && /usr/lib/rpm/brp-compress

find $RPM_BUILD_ROOT \( -name perllocal.pod -o -name .packlist \) -exec rm -v {} \;
find $RPM_BUILD_ROOT -type d -depth -exec rmdir {} 2>/dev/null ';'

# Default rules from separate tarball
cd $RPM_BUILD_ROOT%{_datadir}/spamassassin/
tar xfvz %{SOURCE1}
sed -i -e 's|\@\@VERSION\@\@|%{saversion}|' *.cf
cd -

find $RPM_BUILD_ROOT/usr -type f -print |
        sed "s@^$RPM_BUILD_ROOT@@g" |
        grep -v perllocal.pod |
        grep -v "\.packlist" > %{name}-%{version}-filelist
if [ "$(cat %{name}-%{version}-filelist)X" = "X" ] ; then
    echo "ERROR: EMPTY FILE LIST"
    exit -1
fi
find $RPM_BUILD_ROOT%{perl_vendorlib}/* -type d -print |
        sed "s@^$RPM_BUILD_ROOT@%dir @g" >> %{name}-%{version}-filelist

mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/run/spamassassin
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/spamassassin

# sa-update channels and keyring directory
mkdir   -m 0700             $RPM_BUILD_ROOT%{_sysconfdir}/mail/spamassassin/sa-update-keys/
mkdir   -m 0755             $RPM_BUILD_ROOT%{_sysconfdir}/mail/spamassassin/channel.d/
install -m 0644 %{SOURCE11} $RPM_BUILD_ROOT%{_sysconfdir}/mail/spamassassin/channel.d/

# Tell portreserve which port we want it to protect.
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/portreserve
echo 783 > $RPM_BUILD_ROOT%{_sysconfdir}/portreserve/spamd

%files -f %{name}-%{version}-filelist
%defattr(-,root,root)
%doc LICENSE NOTICE CREDITS Changes README TRADEMARK UPGRADE
%doc USAGE sample-nonspam.txt sample-spam.txt 
%dir %{_sysconfdir}/mail
%config(noreplace) %{_sysconfdir}/mail/spamassassin
%config(noreplace) %{_sysconfdir}/sysconfig/spamassassin
%config(noreplace) %{_sysconfdir}/sysconfig/sa-update
%{_sysconfdir}/cron.d/sa-update
%dir %{_datadir}/spamassassin
%dir %{_localstatedir}/run/spamassassin
%dir %{_localstatedir}/lib/spamassassin
%config(noreplace) %{_sysconfdir}/logrotate.d/sa-update
%config(noreplace) %{_sysconfdir}/portreserve/spamd
%{_unitdir}/spamassassin.service

%clean
rm -rf $RPM_BUILD_ROOT

%post
%systemd_post spamassassin.service

%postun
%systemd_postun spamassassin.service

%preun
%systemd_preun spamassassin.service

%triggerun -- spamassassin < 3.3.2-2
%{_bindir}/systemd-sysv-convert --save spamassassin >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del spamassassin >/dev/null 2>&1 || :
/bin/systemctl try-restart spamassassin.service >/dev/null 2>&1 || :

%changelog
* %(date "+%a %b %d %Y") (Automated RPM build) - %{version}-%{release}
- See git log for actual changes.
