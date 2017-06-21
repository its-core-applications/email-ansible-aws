Name:           dash
Version:        0.5.9.1
Release:        1%{?dist}
Summary:        Small and fast POSIX-compliant shell
Group:          System Environment/Shells
# BSD: DASH in general
# GPLv2+: From src/mksignames.c
# Public Domain: From src/bltin/test.c
# Copyright only: From src/hetio.h
License:        BSD and GPLv2+ and Public Domain and Copyright only
URL:            http://gondor.apana.org.au/~herbert/%{name}/
#Source0:        http://gondor.apana.org.au/~herbert/%{name}/files/%{name}-%{version}.tar.gz
Source0:        https://vereveel.marwnad.com/tmp/%{name}-%{version}.tar.gz
Patch0:         %{name}-0.5.7-format-security.patch

%description
DASH is a POSIX-compliant implementation of /bin/sh that aims to be as small as
possible. It does this without sacrificing speed where possible. In fact, it is
significantly faster than bash (the GNU Bourne-Again SHell) for most tasks.

%prep
%setup -q
%patch0 -p1

%build
%configure --bindir=/bin
make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}

%post
grep -q '^/bin/dash$' %{_sysconfdir}/shells || \
    echo '/bin/dash' >> %{_sysconfdir}/shells

%postun
if [ $1 -eq 0 ]; then
    sed -i '/^\/bin\/dash$/d' %{_sysconfdir}/shells
fi

%files
%doc COPYING ChangeLog
/bin/%{name}
%{_mandir}/man1/%{name}.1*

%changelog
* Mon Sep 29 2014 Petr Šabata <contyk@redhat.com> - 0.5.8-1
- Update to 0.5.8

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.7-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Jun 24 2014 Petr Šabata <contyk@redhat.com> - 0.5.7-10
- Fix FTBFS due to -Werror=format-security (#1037030)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.7-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Aug 01 2013 Petr Šabata <contyk@redhat.com> - 0.5.7-8
- Simplify the installation

* Wed Jul 31 2013 Petr Šabata <contyk@redhat.com> - 0.5.7-7
- Correct the License tag once again
- Utilize the %%{name} and %%{_mandir} macros a bit more
- Don't package the INSTALL file

* Mon Jun 10 2013 Petr Šabata <contyk@redhat.com> - 0.5.7-6
- Use the sysconfdir macro in scriptlets

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.7-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.7-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.7-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Nov 15 2011 Petr Šabata <contyk@redhat.com> - 0.5.7-2
- Don't use --fixed-strings in scriptlets grep match (#753887)

* Wed Aug 17 2011 Petr Sabata <contyk@redhat.com> - 0.5.7-1
- 0.5.7 bump

* Mon May 23 2011 Petr Sabata <psabata@redhat.com> - 0.5.6-5
- Try to add dash to /etc/shells every time, not just on new installs (#706138)
- Also, make the grep regexps a bit more strict, just to be sure

* Thu May 19 2011 Petr Sabata <psabata@redhat.com> - 0.5.6-4
- Install/remove dash from /etc/shells (#706138)
- Buildroot and defattr cleanup
- Add INSTALL, COPYING, ChangeLog to doc

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jun 21 2010 Huzaifa Sidhpurwala <huzaifas@redhat.com> - 0.5.6-2
- New upstream realease
- Version bump

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.5.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sat May 23 2009 Andreas Thienemann <andreas@bawue.net> - 0.5.5.1-2
- Added patch from upstream git to not close stdout on err. This improves
  initramfs use of dash.

* Mon Apr 13 2009 Warren Togami <wtogami@redhat.com> - 0.5.5.1-1
- 0.5.5.1

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Feb 08 2008 Warren Togami <wtogami@redhat.com> 0.5.4-3
- rebuild for gcc-4.3

* Wed Nov 07 2007 Warren Togami <wtogami@redhat.com> 0.5.4-2
- move to /bin/dash
- BSD license tag

* Fri Nov 02 2007 Warren Togami <wtogami@redhat.com> 0.5.4-1
- initial package


