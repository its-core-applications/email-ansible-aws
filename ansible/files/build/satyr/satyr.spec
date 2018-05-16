Name: satyr
Version: 0.26
Release: 1%{?dist}
Summary: Tools to create anonymous, machine-friendly problem reports
License: GPLv2+
URL: https://github.com/abrt/satyr
Source0: https://github.com/abrt/%{name}/archive/%{version}.tar.gz#%{name}-%{version}.tar.gz
BuildRequires: python2-devel
BuildRequires: elfutils-devel
BuildRequires: elfutils-libelf-devel
BuildRequires: binutils-devel
BuildRequires: rpm-devel
BuildRequires: libtool
BuildRequires: pkgconfig
BuildRequires: automake
BuildRequires: gcc-c++

%description
Satyr is a library that can be used to create and process microreports.
Microreports consist of structured data suitable to be analyzed in a fully
automated manner, though they do not necessarily contain sufficient information
to fix the underlying problem. The reports are designed not to contain any
potentially sensitive data to eliminate the need for review before submission.
Included is a tool that can create microreports and perform some basic
operations on them.

%package devel
Summary: Development libraries for %{name}
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
Development libraries and headers for %{name}.

%package python
Summary: Python bindings for %{name}
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description python
Python bindings for %{name}.

%prep
%autosetup

%build
./gen-version
autoreconf -fi

%configure \
        --disable-static \
        --without-python3

make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}

# Remove all libtool archives (*.la) from modules directory.
find %{buildroot} -name "*.la" | xargs rm --

%check
make check || {
    # find and print the logs of failed test
    # do not cat tests/testsuite.log because it contains a lot of bloat
    find tests -name "testsuite.log" -print -exec cat '{}' \;
    exit 1
}


%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%doc README NEWS COPYING
%{_bindir}/satyr
%{_mandir}/man1/%{name}.1*
%{_libdir}/lib*.so.*

%files devel
%{_includedir}/*
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*

%files python
%dir %{python_sitearch}/%{name}
%{python_sitearch}/%{name}/*
%{_mandir}/man3/satyr-python.3*

%changelog
* %(date "+%a %b %d %Y") (Automated RPM build) - %{version}-%{release}
- See git log for actual changes.
