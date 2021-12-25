%global major 78

Name:           mozjs%{major}
Version:        78.15.0
Release:        1
Summary:        SpiderMonkey JavaScript library
License:        MPLv2.0 and MPLv1.1 and BSD and GPLv2+ and GPLv3+ and LGPLv2+ and AFL and ASL 2.0
URL:            https://developer.mozilla.org/en-US/docs/Mozilla/Projects/SpiderMonkey
Source0:        https://ftp.mozilla.org/pub/firefox/releases/%{version}esr/source/firefox-%{version}esr.source.tar.xz

# Patches from mozjs68, rebased for mozjs78:
Patch01:        fix-soname.patch
Patch02:        copy-headers.patch
Patch03:        tests-increase-timeout.patch
Patch04:        icu_sources_data.py-Decouple-from-Mozilla-build-system.patch
Patch05:        icu_sources_data-Write-command-output-to-our-stderr.patch
# Build fixes - https://hg.mozilla.org/mozilla-central/rev/ca36a6c4f8a4a0ddaa033fdbe20836d87bbfb873
Patch06:        emitter.patch
# Build fixes
Patch07:        init_patch.patch
# TODO: Check with mozilla for cause of these fails and re-enable spidermonkey compile time checks if needed
Patch08:        spidermonkey_checks_disable.patch

Patch6000:        backport-fixup-compatibility-of-mozbuild-with-python-3.10.patch

BuildRequires:  autoconf213 cargo clang-devel gcc gcc-c++ perl-devel pkgconfig(libffi) pkgconfig(zlib) 
BuildRequires:  python3-devel python3-six readline-devel zip nasm llvm llvm-devel icu rust

%description
SpiderMonkey is the code-name for Mozilla Firefox's C++ implementation of
JavaScript. It is intended to be embedded in other applications
that provide host environments for JavaScript.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package_help

%prep
%autosetup -p1 -n firefox-%{version}
cp LICENSE js/src/
rm -rf ../../modules/zlib

%build
pushd js/src
export CC=gcc
export CXX=g++
export RUSTFLAGS="-C embed-bitcode"
export CFLAGS="%{optflags}"
export CXXFLAGS="$CFLAGS"
export LINKFLAGS="%{?__global_ldflags}"
export PYTHON="%{__python3}"

autoconf-2.13
%configure \
  --without-system-icu --with-system-zlib --disable-tests --disable-strip --with-intl-api \
  --enable-readline --enable-shared-js --disable-optimize --enable-pie --disable-jemalloc

%make_build
popd

%install
pushd js/src
%make_install
# Fix permissions
chmod -x %{buildroot}%{_libdir}/pkgconfig/*.pc
# Remove unneeded files
rm %{buildroot}%{_bindir}/js%{major}-config
rm %{buildroot}%{_libdir}/libjs_static.ajs
# Rename library and create symlinks, following fix-soname.patch
mv %{buildroot}%{_libdir}/libmozjs-%{major}.so \
   %{buildroot}%{_libdir}/libmozjs-%{major}.so.0.0.0
ln -s libmozjs-%{major}.so.0.0.0 %{buildroot}%{_libdir}/libmozjs-%{major}.so.0
ln -s libmozjs-%{major}.so.0 %{buildroot}%{_libdir}/libmozjs-%{major}.so
popd

%check
pushd js/src
PYTHONPATH=tests/lib %{__python3} tests/jstests.py -d -s -t 1800 --no-progress --wpt=disabled ../../js/src/dist/bin/js%{major}
PYTHONPATH=tests/lib %{__python3} jit-test/jit_test.py -s -t 1800 --no-progress ../../js/src/dist/bin/js%{major} basic
popd

%ldconfig_scriptlets

%files
%license LICENSE
%{_libdir}/libmozjs-%{major}.so.0*

%files devel
%{_bindir}/js%{major}
%{_libdir}/libmozjs-%{major}.so
%{_libdir}/pkgconfig/*.pc
%{_includedir}/mozjs-%{major}/

%files help
%doc js/src/README.html

%changelog
* Sat Dec 04 2021 wangkerong <wangkerong@huawei.com> - 78.15.0-1
- update to 78.15.0

* Tue May 11 2021 zhanzhimin <zhanzhimin@huawei.com> - 78.4.0-2
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix build error caused by rust

* Thu Nov 05 2020 chengguipeng <chengguipeng1@huawei.com> - 78.4.0-1
- Package init
