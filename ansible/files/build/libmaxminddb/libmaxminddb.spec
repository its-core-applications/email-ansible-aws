Summary:        C library for reading MaxMind DB files
Name:           libmaxminddb
Version:        1.7.1
Release:        1%{?dist}
# BSD-3-Clause (src/maxminddb-compat-util.h) and Apache-2.0 (the rest)
License:        Apache-2.0 AND BSD-3-Clause
URL:            https://maxmind.github.io/libmaxminddb/
Source0:        https://github.com/maxmind/libmaxminddb/releases/download/%{version}/%{name}-%{version}.tar.gz
Source1:        maxminddb_config.h
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  gcc
BuildRequires:  make
# Testsuite in %%check
BuildRequires:  gcc-c++
BuildRequires:  perl-interpreter
BuildRequires:  perl(File::Temp)
BuildRequires:  perl(FindBin)
BuildRequires:  perl(IPC::Run3)
BuildRequires:  perl(Test::More) >= 0.88
BuildRequires:  perl(Test::Output)

%description
The libmaxminddb library provides a C library for reading MaxMind DB
files, including the GeoIP2 databases from MaxMind. This is a custom
binary format designed to facilitate fast lookups of IP addresses
while allowing for great flexibility in the type of data associated
with an address.

The MaxMind DB format is an open file format. The specification is
available at https://maxmind.github.io/MaxMind-DB/ and licensed under
the Creative Commons Attribution-ShareAlike 3.0 Unported License.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%prep
%setup -q
autoreconf --force --install

%build
%configure --disable-static
%make_build

%install
%make_install

# Don't install any libtool .la files
rm -f $RPM_BUILD_ROOT%{_libdir}/%{name}.la

# Avoid file conflicts in multilib installations of -devel subpackage
mv -f $RPM_BUILD_ROOT%{_includedir}/maxminddb_config{,-%{__isa_bits}}.h
install -p -m 0644 %{SOURCE1} $RPM_BUILD_ROOT%{_includedir}/maxminddb_config.h

%check
# Tests are linked dynamically, preload the library as RPATH is removed
LD_PRELOAD=$RPM_BUILD_ROOT%{_libdir}/%{name}.so make check

%files
%license LICENSE
%doc Changes.md README.md
%{_bindir}/mmdblookup
%{_libdir}/%{name}.so.0*
%{_mandir}/man1/mmdblookup.1*

%files devel
%{_libdir}/%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
%{_includedir}/maxminddb.h
%{_includedir}/maxminddb_config.h
%{_includedir}/maxminddb_config-%{__isa_bits}.h
%{_mandir}/man3/%{name}.3*
%{_mandir}/man3/MMDB_*.3*

%changelog
* %(date "+%a %b %d %Y") (Automated RPM build) - %{version}-%{release}
- See git log for actual changes.
