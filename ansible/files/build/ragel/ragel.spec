Name:           ragel
Version:        6.10
Release:        1%{?dist}
Summary:        Finite state machine compiler
License:        GPL-2.0+
URL:            http://complang.org/ragel/
Source0:         http://www.colm.net/files/%{name}/%{name}-%version.tar.gz
Source1:        http://www.colm.net/files/%{name}/%{name}-%version.tar.gz.asc
BuildRequires:  gcc-c++

%description
Ragel compiles finite state machines from regular languages into
executable C, C++, Objective-C, or D code. Ragel state machines can
not only recognize byte sequences as regular expression machines do,
but can also execute code at arbitrary points in the recognition of a
regular language. Code embedding is done using inline operators that
do not disrupt the regular language syntax.

%prep
%setup -q
#%setup -qn ragel-%version

%build
%configure --docdir="%_docdir/%name"
make %{?_smp_mflags}

%check
make check

%install
make install DESTDIR=%{buildroot}

%files
%defattr(-,root,root)
%_bindir/ragel
%_mandir/man1/ragel.1*
%_defaultdocdir/%name/

%changelog
* %(date "+%a %b %d %Y") (Automated RPM build) - %{version}-%{release}
- See git log for actual changes.
