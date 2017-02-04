Name:           jemalloc
Version:        4.4.0

Release:        1%{?dist}
Summary:        General-purpose scalable concurrent malloc implementation

Group:          System Environment/Libraries
License:        BSD
URL:            http://www.canonware.com/jemalloc/
Source0:        http://www.canonware.com/download/jemalloc/%{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  /usr/bin/xsltproc

%description
General-purpose scalable concurrent malloc(3) implementation.
This distribution is the stand-alone "portable" implementation of %{name}.

%package devel
Summary:        Development files for %{name}
Requires:       %{name} = %{version}-%{release}
Group:          Development/Libraries

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%prep
%setup -q

%build
%configure --enable-xmalloc
make %{?_smp_mflags}

%check
make check

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
# Install this with doc macro instead
rm %{buildroot}%{_datadir}/doc/%{name}/jemalloc.html

# None of these in fedora
find %{buildroot}%{_libdir}/ -name '*.a' -exec rm -vf {} ';'

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{_libdir}/libjemalloc.so.*
%{_bindir}/jemalloc.sh
%{_bindir}/jeprof
%doc COPYING README VERSION
%doc doc/jemalloc.html

%files devel
%defattr(-,root,root,-)
%{_includedir}/jemalloc
%{_libdir}/libjemalloc.so
%{_libdir}/pkgconfig/jemalloc.pc
%{_bindir}/jemalloc-config
%{_mandir}/man3/jemalloc.3*

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%changelog
* %(date "+%a %b %d %Y") (Automated RPM build) - %{version}-%{release}
- See git log for actual changes.
