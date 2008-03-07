#Module-Specific definitions
%define apache_version 2.2.4
%define mod_name mod_auth_pgsql
%define mod_conf 13_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Basic authentication for the apache web server using a PostgreSQL database
Name:		apache-%{mod_name}
Version:	2.0.3
Release:	%mkrel 11
Group:		System/Servers
License:	Apache License
URL:		http://www.giuseppetanzilli.it/mod_auth_pgsql2/
Source0:	http://www.giuseppetanzilli.it/mod_auth_pgsql2/dist/%{mod_name}-%{version}.tar.bz2
Source1:	%{mod_conf}
Patch0:		mod_auth_pgsql-2.0.3-nonpgsql.diff
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):  apache-conf >= %{apache_version}
Requires(pre):  apache >= %{apache_version}
Requires:	apache-conf >= %{apache_version}
Requires:	apache >= %{apache_version}
BuildRequires:  apache-devel >= %{apache_version}
BuildRequires:	postgresql-devel
BuildRequires:	openssl-devel
Epoch:		1
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot

%description
mod_auth_pgsql can be used to limit access to documents served by a web server
by checking fields in a table in a PostgresQL database.

%prep

%setup -q -n %{mod_name}-%{version}
%patch0 -p0 -b .nonpgsql

cp %{SOURCE1} %{mod_conf}

%build

%{_sbindir}/apxs -I%{_includedir}/pgsql -L%{_libdir} \
    "-lpq -lcrypto -lssl" -c mod_auth_pgsql.c -n mod_auth_pgsql.so

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
        %{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc README INSTALL *.html
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
