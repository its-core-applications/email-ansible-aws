Name:    hyperscan
Version: 4.7.0
Release: 1%{?dist}
Summary: High-performance regular expression matching library

License: BSD
URL:     https://01.org/hyperscan
Source0: https://github.com/01org/%{name}/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1: http://downloads.sourceforge.net/project/boost/boost/1.61.0/boost_1_61_0.tar.gz

BuildRequires:  cmake
BuildRequires:	pcre-devel
BuildRequires:	python
BuildRequires:  ragel
BuildRequires:	sqlite-devel
BuildRequires:  libpcap-devel

Requires:	pcre
Requires:	sqlite

#package requires SSE support and fails to build on non x86_64 archs
ExclusiveArch: x86_64

%description
Hyperscan is a high-performance multiple regex matching library. It
follows the regular expression syntax of the commonly-used libpcre
library, but is a standalone library with its own C API.

Hyperscan uses hybrid automata techniques to allow simultaneous
matching of large numbers (up to tens of thousands) of regular
expressions and for the matching of regular expressions across streams
of data.

Hyperscan is typically used in a DPI library stack.

%package static
Summary: Static library library files for the hyperscan library
Provides: %{name}%{?_isa}

%description static
Hyperscan is a high-performance multiple regex matching library. It
follows the regular expression syntax of the commonly-used libpcre
library, but is a standalone library with its own C API.

Hyperscan uses hybrid automata techniques to allow simultaneous
matching of large numbers (up to tens of thousands) of regular
expressions and for the matching of regular expressions across streams
of data.

Hyperscan is typically used in a DPI library stack.

This package provides static library files for the hyperscan library.

%package devel
Summary: Libraries and header files for the hyperscan library
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
Hyperscan is a high-performance multiple regex matching library. It
follows the regular expression syntax of the commonly-used libpcre
library, but is a standalone library with its own C API.

Hyperscan uses hybrid automata techniques to allow simultaneous
matching of large numbers (up to tens of thousands) of regular
expressions and for the matching of regular expressions across streams
of data.

Hyperscan is typically used in a DPI library stack.

This package provides the libraries, include files and other resources
needed for developing Hyperscan applications.

%prep
%autosetup
(cd include && tar zxf %{SOURCE1} boost_1_61_0/boost --strip-components=1)


%build
%cmake -DBUILD_SHARED_LIBS:BOOL=OFF -DBUILD_STATIC_AND_SHARED:BOOL=ON \
       -DCMAKE_POSITION_INDEPENDENT_CODE:BOOL=true .

make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}
cp lib/libhs.a %{buildroot}%{_libdir}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%doc %{_defaultdocdir}/%{name}/examples/README.md
%doc %{_defaultdocdir}/%{name}/examples/*.cc
%doc %{_defaultdocdir}/%{name}/examples/*.c
%license COPYING
%license LICENSE
%{_libdir}/*.so.*
%{_libdir}/*.so

%files static
%{_libdir}/*.a

%files devel
%{_libdir}/pkgconfig/libhs.pc
%{_includedir}/hs/

%changelog
* %(date "+%a %b %d %Y") (Automated RPM build) - %{version}-%{release}
- See git log for actual changes.
