
%{!?pyver: %global pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

Name:           monkeyfarm
Version:        2.0.4
Release:        3.alpha%{?dist}
Summary:        Next Generation Build Environment

Group:          Applications/System        
License:        GPLv2 
URL:            http://buildenv.com
Source0:        http://mf-hub.rpmdev.rackspace.com/downloads/%{name}/%{name}-%{version}.tar.gz 
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

BuildRequires:  python >= 2.6, python-distribute
Requires:       python >= 2.6
Requires:       shadow-utils

%description
Next Generation Build Environment.

%package doc
Summary: Documentation for MonkeyFarm
Group: Documentation
BuildRequires: python-configobj, python-genshi, python-jinja2

%if 0%{?rhel} == 06 
BuildRequires: python-sphinx10
%else
BuildRequires: python-sphinx
%endif

%description doc
This package provides the Sphinx documentation for the MonkeyFarm. 

%package core
Summary:        MonkeyFarm Core CLI Component
Group:          Applications/System
BuildRequires:  python-zope-interface
Requires:       python-%{name}-interface == %{version}
Requires:       python-cement >= 0.8.11
Requires:       python-rosendale-simplecache >= 0.2.4 
Requires:       python-rosendale-clibasic >= 0.2.4 
Requires:       python-genshi
Requires:       python-jsonpickle

%description core
MonkeyFarm Core CLI Component

%package client
Summary:        MonkeyFarm Client Utilities
Group:          Applications/System
Requires:       %{name}-core = %{version}-%{release} 

%description client
MonkeyFarm Client Utilities

%package regulator
Summary:        MonkeyFarm Regulator Daemon Utilites
Group:          Applications/System
Requires:       %{name}-core = %{version}-%{release}

%description regulator
MonkeyFarm Regulator Daemon Utilities

%package worker
Summary:        MonkeyFarm Worker Daemon Utilities
Group:          Applications/System
Requires:       %{name}-core = %{version}-%{release}
Requires:       createrepo

%description worker
MonkeyFarm Worker Daemon Utilities

%package hub
Summary:        MonkeyFarm Web/API Hub Application 
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}
Requires:       %{name}-doc = %{version}-%{release}
Requires:       TurboGears2 >= 2.1, python-tg-devtools
Requires:       python-TurboMail, python-tw-forms, python-toscawidgets
Requires:       python-zope-sqlalchemy, python-repoze-tm2
Requires:       python-repoze-what-quickstart, python-repoze-what-pylons

%description hub 
MonkeyFarm Web/API Hub Application 

%package -n python-%{name}-interface
Summary:        MonkeyFarm API Bindings for Python
Group:          Development/Languages
License:        BSD
# this is a stand-alone client library, and does not (should not) 
# require the base package
Requires:       python, python-zope-interface

%description -n python-%{name}-interface
MonkeyFarm Python Interface Library 

%package plugin-generic-build
Summary:        MonkeyFarm Generic Build Handler Plugin 
Group:          Applications/System
Requires:       %{name}-core = %{version}-%{release}

%description plugin-generic-build
MonkeyFarm Generic Build Handler Plugin

%package plugin-rpm 
Summary:        MonkeyFarm RPM Build Handler Plugin
Group:          Applications/System
Requires:       %{name}-core = %{version}-%{release}
Requires:       rpm, rpmdevtools, createrepo, mock

%description plugin-rpm
MonkeyFarm RPM Build Handler Plugin

%package plugin-git
Summary:        MonkeyFarm Git VCS Handler Plugin
Group:          Applications/System
Requires:       %{name}-core = %{version}-%{release}
Requires:       git

%description plugin-git
MonkeyFarm Git VCS Handler Plugin

%package plugin-bzr
Summary:        MonkeyFarm Bazaar VCS Handler Plugin
Group:          Applications/System
Requires:       %{name}-core = %{version}-%{release}
Requires:       bzr

%description plugin-bzr
MonkeyFarm Bazaar VCS Handler Plugin

%package plugin-launchpad
Summary:        MonkeyFarm LaunchPad Build/VCS Handler Plugin
Group:          Applications/System
Requires:       %{name}-core = %{version}-%{release}
Requires:       bzr

%description plugin-launchpad
MonkeyFarm LaunchPad Build/VCS Handler Plugin


%prep
%setup -q

sed -i 's/tag_build = dev/tag_build = /' src/monkeyfarm.hub/setup.cfg

%build
for i in core client hub regulator worker; do
    pushd src/monkeyfarm.$i
    %{__python} setup.py build
    popd
done

# plugins
for i in generic_build git bzr rpm launchpad; do
    pushd src/plugins/monkeyfarm.$i
    %{__python} setup.py build
    popd
done

# interfaces
for i in python; do 
    pushd src/interfaces/$i/
    %{__python} setup.py build
    popd
done

# build docs
%if 0%{?rhel} == 06
sphinx-1.0-build doc/source doc/build/html
%else
sphinx-build doc/source doc/build/html 
%endif

%install
rm -rf %{buildroot}
%{__mkdir} -p %{buildroot}%{_sysconfdir}/%{name}/plugins.d/ \
              %{buildroot}%{_sysconfdir}/init.d/ \
              %{buildroot}%{_sysconfdir}/logrotate.d/ \
              %{buildroot}%{_sysconfdir}/httpd/conf.d/ \
              %{buildroot}%{_localstatedir}/run/%{name}/ \
              %{buildroot}%{_localstatedir}/cache/%{name}/ \
              %{buildroot}%{_localstatedir}/cache/%{name}/python-egg-cache \
              %{buildroot}%{_localstatedir}/log/%{name}/ \
              %{buildroot}%{_localstatedir}/lib/%{name}/ \
              %{buildroot}%{_localstatedir}/lib/%{name}/data/ \
              %{buildroot}%{_localstatedir}/lib/%{name}/work/ \
              %{buildroot}%{_datadir}/%{name}/hub/ \
              %{buildroot}%{_sbindir}


for i in core client hub regulator worker; do
    pushd src/monkeyfarm.$i
    %{__python} setup.py install --skip-build --root %{buildroot}
    popd
done

# plugins
for i in generic_build git bzr rpm launchpad; do
    pushd src/plugins/monkeyfarm.$i
    %{__python} setup.py install --skip-build --root %{buildroot}
    popd
done

# interfaces
for i in python; do 
    pushd src/interfaces/$i/
    %{__python} setup.py install --skip-build --root %{buildroot}
    popd
done

# quick fix for bins that should be sbins
mv %{buildroot}%{_bindir}/mf-regulatord %{buildroot}%{_sbindir}/mf-regulatord
mv %{buildroot}%{_bindir}/mf-workerd %{buildroot}%{_sbindir}/mf-workerd

# configurations
%{__install} src/monkeyfarm.client/config/mf.conf-minimal \
        %{buildroot}%{_sysconfdir}/%{name}/mf.conf
%{__install} src/monkeyfarm.regulator/config/mf-regulatord.conf \
        %{buildroot}%{_sysconfdir}/%{name}/mf-regulatord.conf
%{__install} src/monkeyfarm.worker/config/mf-workerd.conf \
        %{buildroot}%{_sysconfdir}/%{name}/mf-workerd.conf
%{__install} src/monkeyfarm.hub/mf-hub.conf-production \
        %{buildroot}%{_sysconfdir}/%{name}/mf-hub.conf
%{__install} src/monkeyfarm.hub/TERMS_OF_USE \
        %{buildroot}%{_sysconfdir}/%{name}/TERMS_OF_USE


# hub/apache configs
%{__install} util/monkeyfarm.wsgi \
    %{buildroot}%{_datadir}/%{name}/hub/monkeyfarm.wsgi

# this is served statically by apache
mv %{buildroot}%{python_sitelib}/mf_hub/public %{buildroot}%{_datadir}/%{name}/hub/public

# create a symlink for the doc
ln -sf %{_docdir}/%{name}-doc-%{version}/html %{buildroot}%{_datadir}/%{name}/hub/public/doc

# init scripts
%{__install} util/mf-regulatord.init \
    %{buildroot}%{_sysconfdir}/init.d/mf-regulatord
%{__install} util/mf-workerd.init \
    %{buildroot}%{_sysconfdir}/init.d/mf-workerd

# logrotate scripts
%{__install} -m 0644 util/mf-regulatord.logrotate \
    %{buildroot}%{_sysconfdir}/logrotate.d/mf-regulatord
%{__install} -m 0644 util/mf-workerd.logrotate \
    %{buildroot}%{_sysconfdir}/logrotate.d/mf-workerd

# plugin configs
for i in generic_build git bzr rpm launchpad; do
    %{__install} src/plugins/monkeyfarm.${i}/config/plugins.d/${i}.conf \
        %{buildroot}%{_sysconfdir}/monkeyfarm/plugins.d/${i}.conf
done

# rosendale plugins
%{__install} src/monkeyfarm.core/config/plugins.d/simplecache.conf \
        %{buildroot}%{_sysconfdir}/%{name}/plugins.d/simplecache.conf
%{__install} src/monkeyfarm.core/config/plugins.d/clibasic.conf \
        %{buildroot}%{_sysconfdir}/%{name}/plugins.d/clibasic.conf

# Create %%ghost files
touch %{buildroot}%{_localstatedir}/run/%{name}/mf-regulatord.pid
touch %{buildroot}%{_localstatedir}/run/%{name}/mf-workerd.pid

# cleanup
rm -f %{buildroot}%{python_sitelib}/mf/model/example*
rm -f %{buildroot}%{python_sitelib}/mf/bootstrap/example*
rm -f %{buildroot}%{python_sitelib}/mf/controllers/example*
rm -rf %{buildroot}%{python_sitelib}/mf/templates/example/


%clean
rm -rf %{buildroot}

%pre
getent group monkeyfarm >/dev/null || groupadd -r monkeyfarm
getent passwd monkeyfarm >/dev/null || \
    useradd -r -g monkeyfarm -d /var/lib/monkeyfarm -s /sbin/nologin \
    -c "MonkeyFarm System Account" monkeyfarm
exit 0

%post regulator 
if [ $1 = 1 ]; then
    /sbin/chkconfig --add mf-regulatord
fi
if [ $1 -ge 1 ]; then
    /sbin/service mf-regulatord condrestart || :
fi

%post worker 
if [ $1 = 1 ]; then
    /sbin/chkconfig --add mf-workerd
fi
if [ $1 -ge 1 ]; then
    /sbin/service mf-workerd condrestart || :
fi

%preun regulator
if [ $1 = 0 ]; then
    /sbin/service mf-regulatord stop || :
    /sbin/chkconfig --del mf-regulatord
fi

%preun worker 
if [ $1 = 0 ]; then
    /sbin/service mf-workerd stop || :
    /sbin/chkconfig --del mf-workerd
fi


%post hub
if [ "$1" == "1" ]; then
    secret=$(echo $RANDOM-$RANDOM-$RANDOM-$RANDOM-$RANDOM)
    sed -i "s/CHANGE-ME-MUST-BE-A-UNIQUE-SECRET/$secret/g" %{_sysconfdir}/%{name}/mf-hub.conf
fi

%files
%defattr(-,root,root,-)
%doc LICENSE README
%doc util/upgrade/
%dir %{python_sitelib}/mf
%attr(775,root,root) %dir %{_datadir}/%{name}/
%attr(775,root,monkeyfarm) %dir %{_localstatedir}/lib/%{name}/
%attr(750,monkeyfarm,monkeyfarm) %dir %{_localstatedir}/lib/%{name}/data
%attr(770,root,monkeyfarm) %dir %{_localstatedir}/lib/%{name}/work
%attr(770,root,monkeyfarm) %dir %{_localstatedir}/log/%{name}/
%ghost %attr(775,root,monkeyfarm) %dir %{_localstatedir}/run/%{name}/
%ghost %attr(775,root,monkeyfarm) %dir %{_localstatedir}/cache/%{name}/
%ghost %attr(775,root,monkeyfarm) %dir %{_localstatedir}/cache/%{name}/python-egg-cache/

%files core
%defattr(-,root,root,-)
%doc src/monkeyfarm.core/README
%config(noreplace) %{_sysconfdir}/%{name}/plugins.d/clibasic.conf
%config(noreplace) %{_sysconfdir}/%{name}/plugins.d/simplecache.conf
%{python_sitelib}/mf/core/
%dir %{python_sitelib}/mf/lib/
%dir %{python_sitelib}/mf/controllers/
%dir %{python_sitelib}/mf/helpers/
%dir %{python_sitelib}/mf/bootstrap/
%dir %{python_sitelib}/mf/model/
%dir %{python_sitelib}/mf/templates/
%dir %{python_sitelib}/mf/templates/root/
%dir %{_sysconfdir}/%{name}/
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/mf.conf
%{python_sitelib}/mf/lib/daemonize.py*
%{python_sitelib}/mf/lib/t_helper.py*
%{python_sitelib}/mf/controllers/root.py*
%{python_sitelib}/mf/helpers/misc.py*
%{python_sitelib}/mf/bootstrap/root.py*
%{python_sitelib}/mf/model/root.py*
%{python_sitelib}/mf/templates/root/__init__.py*
%{python_sitelib}/mf/templates/root/api_error.txt
%{python_sitelib}/mf/templates/root/error.txt
%{python_sitelib}/%{name}.core-%{version}-py%{pyver}-nspkg.pth
%{python_sitelib}/%{name}.core-%{version}-py%{pyver}.egg-info/

%files client 
%defattr(-,root,root,-)
%doc src/monkeyfarm.client/README
%{python_sitelib}/mf/lib/client.py*
%{python_sitelib}/mf/bootstrap/arch.py*
%{python_sitelib}/mf/bootstrap/distro.py*
%{python_sitelib}/mf/bootstrap/bug_handler.py*
%{python_sitelib}/mf/bootstrap/build.py*
%{python_sitelib}/mf/bootstrap/build_handler.py*
%{python_sitelib}/mf/bootstrap/client.py*
%{python_sitelib}/mf/bootstrap/group.py*
%{python_sitelib}/mf/bootstrap/package.py*
%{python_sitelib}/mf/bootstrap/package_branch.py*
%{python_sitelib}/mf/bootstrap/project.py*
%{python_sitelib}/mf/bootstrap/release.py*
%{python_sitelib}/mf/bootstrap/system.py*
%{python_sitelib}/mf/bootstrap/tag.py*
%{python_sitelib}/mf/bootstrap/target.py*
%{python_sitelib}/mf/bootstrap/task.py*
%{python_sitelib}/mf/bootstrap/user.py*
%{python_sitelib}/mf/bootstrap/vcs_handler.py*
%{python_sitelib}/mf/controllers/arch.py*
%{python_sitelib}/mf/controllers/distro.py*
%{python_sitelib}/mf/controllers/bug_handler.py*
%{python_sitelib}/mf/controllers/build.py*
%{python_sitelib}/mf/controllers/build_handler.py*
%{python_sitelib}/mf/controllers/client.py*
%{python_sitelib}/mf/controllers/group.py*
%{python_sitelib}/mf/controllers/package.py*
%{python_sitelib}/mf/controllers/package_branch.py*
%{python_sitelib}/mf/controllers/project.py*
%{python_sitelib}/mf/controllers/release.py*
%{python_sitelib}/mf/controllers/system.py*
%{python_sitelib}/mf/controllers/tag.py*
%{python_sitelib}/mf/controllers/target.py*
%{python_sitelib}/mf/controllers/task.py*
%{python_sitelib}/mf/controllers/user.py*
%{python_sitelib}/mf/controllers/vcs_handler.py*
%{python_sitelib}/mf/templates/arch/
%{python_sitelib}/mf/templates/distro/
%{python_sitelib}/mf/templates/bug_handler/
%{python_sitelib}/mf/templates/build/
%{python_sitelib}/mf/templates/build_handler/
%{python_sitelib}/mf/templates/client/
%{python_sitelib}/mf/templates/group/
%{python_sitelib}/mf/templates/package/
%{python_sitelib}/mf/templates/package_branch/
%{python_sitelib}/mf/templates/project/
%{python_sitelib}/mf/templates/release/
%{python_sitelib}/mf/templates/system/
%{python_sitelib}/mf/templates/tag/
%{python_sitelib}/mf/templates/target/
%{python_sitelib}/mf/templates/task/
%{python_sitelib}/mf/templates/user/
%{python_sitelib}/mf/templates/vcs_handler/
%{python_sitelib}/%{name}.client-%{version}-py%{pyver}-nspkg.pth
%{python_sitelib}/%{name}.client-%{version}-py%{pyver}.egg-info/
%{_bindir}/mf

%files hub 
%defattr(-,root,root,-)
%doc util/README.rpm src/monkeyfarm.hub/README util/monkeyfarm.apache 
%attr(0640,root,monkeyfarm) %config(noreplace) %{_sysconfdir}/%{name}/mf-hub.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/TERMS_OF_USE
%{_datadir}/%{name}/hub/
%{python_sitelib}/mf_hub
%{python_sitelib}/%{name}.hub-%{version}-py%{pyver}.egg-info/

%files regulator
%defattr(-,root,root,-)
%doc src/monkeyfarm.regulator/README
%attr(0640,root,monkeyfarm) %config(noreplace) %{_sysconfdir}/%{name}/mf-regulatord.conf
%attr(0755,root,root) %{_sysconfdir}/init.d/mf-regulatord
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/logrotate.d/mf-regulatord
%ghost %attr(644,monkeyfarm,monkeyfarm) %{_localstatedir}/run/%{name}/mf-regulatord.pid
%{python_sitelib}/mf/templates/regulator/
%{python_sitelib}/mf/lib/regulator.py*
%{python_sitelib}/mf/bootstrap/regulator.py*
%{python_sitelib}/mf/controllers/regulator.py*
%{python_sitelib}/%{name}.regulator-%{version}-py%{pyver}-nspkg.pth
%{python_sitelib}/%{name}.regulator-%{version}-py%{pyver}.egg-info/
%{_sbindir}/mf-regulatord

%files worker
%defattr(-,root,root,-)
%doc src/monkeyfarm.worker/README
%attr(0640,root,monkeyfarm) %config(noreplace) %{_sysconfdir}/%{name}/mf-workerd.conf
%attr(0755,root,root) %{_sysconfdir}/init.d/mf-workerd
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/logrotate.d/mf-workerd
%ghost %attr(644,monkeyfarm,monkeyfarm) %{_localstatedir}/run/%{name}/mf-workerd.pid
%{python_sitelib}/mf/templates/worker/
%{python_sitelib}/mf/lib/worker.py*
%{python_sitelib}/mf/bootstrap/worker.py*
%{python_sitelib}/mf/controllers/worker.py*
%{python_sitelib}/%{name}.worker-%{version}-py%{pyver}-nspkg.pth
%{python_sitelib}/%{name}.worker-%{version}-py%{pyver}.egg-info/
%{_sbindir}/mf-workerd

%files doc
%defattr(-,root,root,-)
%doc doc/build/html

%files plugin-generic-build 
%defattr(-,root,root,-)
%doc src/plugins/monkeyfarm.generic_build/README
%attr(0644,-,-) %config(noreplace) %{_sysconfdir}/%{name}/plugins.d/generic_build.conf
%{python_sitelib}/mf/templates/generic_build/
%{python_sitelib}/mf/bootstrap/generic_build.py*
%{python_sitelib}/mf/controllers/generic_build.py*
%{python_sitelib}/mf/lib/generic_build.py*
%{python_sitelib}/%{name}.generic_build-%{version}-py%{pyver}-nspkg.pth
%{python_sitelib}/%{name}.generic_build-%{version}-py%{pyver}.egg-info/

%files plugin-git
%defattr(-,root,root,-)
%doc src/plugins/monkeyfarm.git/README
%attr(0644,-,-) %config(noreplace) %{_sysconfdir}/%{name}/plugins.d/git.conf
%{python_sitelib}/mf/templates/git/
%{python_sitelib}/mf/bootstrap/git.py*
%{python_sitelib}/mf/controllers/git.py*
%{python_sitelib}/mf/lib/git.py*
%{python_sitelib}/%{name}.git-%{version}-py%{pyver}-nspkg.pth
%{python_sitelib}/%{name}.git-%{version}-py%{pyver}.egg-info/

%files plugin-bzr
%defattr(-,root,root,-)
%doc src/plugins/monkeyfarm.bzr/README
%attr(0644,-,-) %config(noreplace) %{_sysconfdir}/%{name}/plugins.d/bzr.conf
%{python_sitelib}/mf/templates/bzr/
%{python_sitelib}/mf/bootstrap/bzr.py*
%{python_sitelib}/mf/controllers/bzr.py*
%{python_sitelib}/mf/lib/bzr.py*
%{python_sitelib}/%{name}.bzr-%{version}-py%{pyver}-nspkg.pth
%{python_sitelib}/%{name}.bzr-%{version}-py%{pyver}.egg-info/

%files plugin-rpm
%defattr(-,root,root,-)
%doc src/plugins/monkeyfarm.rpm/README
%attr(0644,-,-) %config(noreplace) %{_sysconfdir}/%{name}/plugins.d/rpm.conf
%{python_sitelib}/mf/templates/rpm/
%{python_sitelib}/mf/bootstrap/rpm.py*
%{python_sitelib}/mf/controllers/rpm.py*
%{python_sitelib}/mf/lib/rpm.py*
%{python_sitelib}/%{name}.rpm-%{version}-py%{pyver}-nspkg.pth
%{python_sitelib}/%{name}.rpm-%{version}-py%{pyver}.egg-info/

%files plugin-launchpad
%defattr(-,root,root,-)
%doc src/plugins/monkeyfarm.launchpad/README
%attr(0644,-,-) %config(noreplace) %{_sysconfdir}/%{name}/plugins.d/launchpad.conf
%{python_sitelib}/mf/templates/launchpad/
%{python_sitelib}/mf/bootstrap/launchpad.py*
%{python_sitelib}/mf/controllers/launchpad.py*
%{python_sitelib}/mf/lib/launchpad.py*
%{python_sitelib}/%{name}.launchpad-%{version}-py%{pyver}-nspkg.pth
%{python_sitelib}/%{name}.launchpad-%{version}-py%{pyver}.egg-info/


%files -n python-%{name}-interface 
%defattr(-,root,root,-)
%doc src/interfaces/python/README src/interfaces/python/LICENSE
%{python_sitelib}/%{name}/
%{python_sitelib}/%{name}.interface-%{version}-py%{pyver}.egg-info/

%changelog
* Mon Jun 13 2011 BJ Dierkes <wdierkes@rackspace.com> - 2.0.4-3.alpha
- BuildRequires: python-sphinx10 on rhel 6

* Tue Jun 10 2011 BJ Dierkes <wdierkes@rackspace.com> - 2.0.4-1.alpha
- Latest sources
- Added logrotate scripts

* Wed Apr 20 2011 BJ Dierkes <wdierkes@rackspace.com> - 2.0.3.1-1.8.alpha
- Latest sources

* Wed Apr 13 2011 BJ Dierkes <wdierkes@rackspace.com> - 2.0.3-2.alpha
- The python-monkeyfarm-interface Requires: python-zope-interface
- The -plugin-rpm package Requires: rpmdevtools (for spectool)

* Wed Apr 13 2011 BJ Dierkes <wdierkes@rackspace.com> - 2.0.3-1.alpha
- Latest sources.
- Rename mock subpackage to rpm

* Tue Jan 24 2011 BJ Dierkes <wdierkes@rackspace.com> - 2.0.2-1.alpha
- Latest sources.

* Wed Dec 01 2010 BJ Dierkes <wdierkes@rackspace.com> - 2.0.1-2.alpha
- Initial spec build

