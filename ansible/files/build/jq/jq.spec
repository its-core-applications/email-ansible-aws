Name:           jq
Version:        1.7.1
Release:        1%{?dist}
Summary:        Command-line JSON processor

License:        MIT and ASL 2.0 and CC-BY and GPLv3
URL:            https://jqlang.github.io/jq/
Source0:        https://github.com/jqlang/jq/releases/download/%{name}-%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  flex
BuildRequires:  bison
BuildRequires:  chrpath
BuildRequires:  oniguruma-devel
BuildRequires:  make
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool


%description
lightweight and flexible command-line JSON processor

 jq is like sed for JSON data – you can use it to slice
 and filter and map and transform structured data with
 the same ease that sed, awk, grep and friends let you
 play with text.

 It is written in portable C, and it has zero runtime
 dependencies.

 jq can mangle the data format that you have into the
 one that you want with very little effort, and the
 program to do so is often shorter and simpler than
 you'd expect.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Development files for %{name}


%prep
%autosetup -n %{name}-%{version} -p1

%build
autoreconf -if
%configure --disable-static
%make_build

%install
%make_install
find %{buildroot} -name '*.la' -exec rm -f {} ';'

# Delete build-time RPATH
chrpath -d %{buildroot}%{_bindir}/%{name}

%files
%license COPYING
%doc AUTHORS COPYING NEWS.md README.md
%{_bindir}/%{name}
%{_libdir}/libjq.so.*
%{_datadir}/man/man1/jq.1.gz

%files devel
%{_includedir}/jq.h
%{_includedir}/jv.h
%{_libdir}/libjq.so
%{_libdir}/pkgconfig/libjq.pc

%changelog
* %(date "+%a %b %d %Y") (Automated RPM build) - %{version}-%{release}
- See git log for actual changes.
