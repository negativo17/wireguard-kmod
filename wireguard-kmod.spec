%global kmod_name wireguard

%global debug_package %{nil}

# Generate kernel symbols requirements:
%global _use_internal_dependency_generator 0

%define __spec_install_post \
  %{__arch_install_post}\
  %{__os_install_post}\
  %{__mod_compress_install_post}

%define __mod_compress_install_post \
  if [ $kernel_version ]; then \
    find %{buildroot} -type f -name '*.ko' | xargs %{__strip} --strip-debug; \
    find %{buildroot} -type f -name '*.ko' | xargs xz; \
  fi

%{!?kversion: %global kversion %(uname -r)}

Name:           %{kmod_name}-kmod
Version:        1.0.20220627
Release:        5%{?dist}
Summary:        Kernel module for wireguard
License:        GPLv2
URL:            https://www.wireguard.com/

Source0:        https://git.zx2c4.com/wireguard-linux-compat/snapshot/wireguard-linux-compat-%{version}.tar.xz

BuildRequires:  elfutils-libelf-devel
BuildRequires:  gcc
BuildRequires:  kernel-devel
BuildRequires:  kmod
BuildRequires:  redhat-rpm-config

%if 0%{?rhel} == 7
BuildRequires:  kernel-abi-whitelists
%else
BuildRequires:  kernel-abi-stablelists
BuildRequires:  kernel-rpm-macros
%endif

%description
This package provides the wireguard kenel driver module.
It is built to depend upon the specific ABI provided by a range of releases of
the same variant of the Linux kernel and not on any one specific build.

%package -n kmod-%{kmod_name}
Summary:    %{kmod_name} kernel module(s)

Provides:   kabi-modules = %{kversion}
Provides:   %{kmod_name}-kmod = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:   module-init-tools

%description -n kmod-%{kmod_name}
This package provides the %{kmod_name} kernel module(s) built for the Linux kernel
using the family of processors.

%post -n kmod-%{kmod_name}
if [ -e "/boot/System.map-%{kversion}" ]; then
    /usr/sbin/depmod -aeF "/boot/System.map-%{kversion}" "%{kversion}" > /dev/null || :
fi
modules=( $(find /lib/modules/%{kversion}/extra/%{kmod_name} | grep '\.ko$') )
if [ -x "/usr/sbin/weak-modules" ]; then
    printf '%s\n' "${modules[@]}" | /usr/sbin/weak-modules --add-modules
fi

%preun -n kmod-%{kmod_name}
rpm -ql kmod-%{kmod_name}-%{version}-%{release} | grep '\.ko$' > /var/run/rpm-kmod-%{kmod_name}-modules

%postun -n kmod-%{kmod_name}
if [ -e "/boot/System.map-%{kversion}" ]; then
    /usr/sbin/depmod -aeF "/boot/System.map-%{kversion}" "%{kversion}" > /dev/null || :
fi
modules=( $(cat /var/run/rpm-kmod-%{kmod_name}-modules) )
rm /var/run/rpm-kmod-%{kmod_name}-modules
if [ -x "/usr/sbin/weak-modules" ]; then
    printf '%s\n' "${modules[@]}" | /usr/sbin/weak-modules --remove-modules
fi

%prep
%autosetup -p1 -n wireguard-linux-compat-%{version}

echo "override %{kmod_name} * weak-updates/%{kmod_name}" > kmod-%{kmod_name}.conf

%build
make -C %{_usrsrc}/kernels/%{kversion} M=$PWD/src modules

%install
export INSTALL_MOD_PATH=%{buildroot}
export INSTALL_MOD_DIR=extra/%{kmod_name}
make -C %{_usrsrc}/kernels/%{kversion} M=$PWD/src modules_install

install -d %{buildroot}%{_sysconfdir}/depmod.d/
install kmod-%{kmod_name}.conf %{buildroot}%{_sysconfdir}/depmod.d/

# Remove the unrequired files.
rm -f %{buildroot}/lib/modules/%{kversion}/modules.*

%files -n kmod-%{kmod_name}
%license COPYING
/lib/modules/%{kversion}/extra/*
%config /etc/depmod.d/kmod-%{kmod_name}.conf

%changelog
* Wed Jun 05 2024 Simone Caronni <negativo17@gmail.com> - 1.0.20220627-5
- Rebuild for latest kernel.

* Wed Apr 03 2024 Simone Caronni <negativo17@gmail.com> - 1.0.20220627-4
- Sync uname -r with kversion passed from scripts.

* Wed Apr 03 2024 Simone Caronni <negativo17@gmail.com> - 1.0.20220627-3
- Rebuild.

* Sun Mar 26 2023 Simone Caronni <negativo17@gmail.com> - 1.0.20220627-2
- Rebuild.

* Tue Aug 09 2022 Simone Caronni <negativo17@gmail.com> - 1.0.20220627-1
- Update to 1.0.20220627.

* Tue Aug 17 2021 Simone Caronni <negativo17@gmail.com> - 1.0.20210606-1
- First build.
