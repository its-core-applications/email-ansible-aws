Name:          nmh
Version:       1.7.1
Release:       1%{?dist}
Summary:       A capable mail handling system with a command line interface
Group:         Applications/Internet
License:       BSD
URL:           http://savannah.nongnu.org/projects/nmh
BuildRequires: flex ncurses-devel
Source0:       http://download.savannah.gnu.org/releases/%{name}/%{name}-%{version}.tar.gz

%description
Nmh is an email system based on the MH email system and is intended to
be a (mostly) compatible drop-in replacement for MH.  Nmh isn't a
single comprehensive program.  Instead, it consists of a number of
fairly simple single-purpose programs for sending, receiving, saving,
retrieving and otherwise manipulating email messages.  You can freely
intersperse nmh commands with other shell commands or write custom
scripts which utilize nmh commands.  nmh only has a command line
interface; if you want a more sophisticated user interface, you'll
want to also install exmh.

%prep
%setup -q

%build
%configure --with-cyrus-sasl
make all dist

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} INSTALL_OPTS='' install

# Eesh, this is ugly
gz_manpages='-e '

if find %{buildroot} -name 'inc.1*' | \
        egrep -q '/usr(/lib|/share)?/man/([^/]+/)?man'; then
    gz_manpages='-e s#\(/man/man./.*\)#\1.gz#'
fi

find %{buildroot} -name etc -prune -o ! -type d -print | \
        sed -e "s#^%{buildroot}##" "$gz_manpages" > nmh_files


%clean
rm -rf %{buildroot}

%files -f nmh_files
%defattr(-,root,root,-)
%config(noreplace) %_sysconfdir/*

