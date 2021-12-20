%global commit0 45997ade65d18806f52e3a2f5b8ca2c3e3283554
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:           libucl
Version:        0.8.2
Release:        0.1.20220110.%{shortcommit0}%{?dist}
Summary:        Parser for UCL (universal configuration language)
License:        BSD
URL:            https://github.com/vstakhov/libucl
Source0:        https://github.com/vstakhov/%{name}/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz

%description
Libucl is a parser and C API to parse and generate ucl objects.

%package devel
Summary:        Development files for %{name}
Requires:       %{name} = %{version}-%{release}

%package utils
Summary:        Utilities for %{name}
Requires:       %{name} = %{version}-%{release}

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%description utils
The %{name}-utils package contains command line utilities for %{name}.

%prep
%autosetup -p 1 -n %{name}-%{commit0}

%build
autoreconf -fi
%configure --enable-utils --disable-static

make %{?_smp_mflags}

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} INSTALL_OPTS='' install
rm -f %{buildroot}/%{_libdir}/libucl.la

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{_libdir}/libucl.so.*

%files utils
%defattr(-,root,root,-)
%{_bindir}/ucl_chargen
%{_bindir}/ucl_objdump
%{_bindir}/ucl_tool

%files devel
%defattr(-,root,root,-)
%{_includedir}/ucl.h
%{_includedir}/ucl++.h
%{_libdir}/libucl.so
%{_libdir}/pkgconfig/libucl.pc
%{_mandir}/man3/libucl.3*

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%changelog
* %(date "+%a %b %d %Y") (Automated RPM build) - %{version}-%{release}
- See git log for actual changes.
