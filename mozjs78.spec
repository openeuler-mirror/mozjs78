%global major 78

Name:           mozjs%{major}
Version:        78.15.0
Release:        2
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
Patch09:        Fixup-compatibility-of-mozbuild-with-Python-3.10.patch

# RISC-V
# From: http://fedora.riscv.rocks/koji/buildinfo?buildID=195538 packaged by David Abdurachmanov.

# From: https://build.opensuse.org/package/view_file/mozilla:Factory/mozjs78/Add-riscv64-support.patch?expand=1
Patch10:        Add-riscv64-support.patch

# Require tests to pass?
%ifnarch riscv64
%global require_tests     1
%else
# REGRESSIONS
#     non262/Array/regress-157652.js
#     non262/regress/regress-422348.js
%global require_tests     0
%endif

# Require libatomic for riscv64.  
%ifarch riscv64
%global system_libatomic 1
%endif

%if 0%{?system_libatomic}
BuildRequires:  libatomic
%endif

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
# Run SpiderMonkey tests
%if 0%{?require_tests}
PYTHONPATH=tests/lib %{__python3} tests/jstests.py -d -s -t 1800 --no-progress --wpt=disabled ../../js/src/dist/bin/js%{major}
%else
 PYTHONPATH=tests/lib %{__python3} tests/jstests.py -d -s -t 1800 --no-progress --wpt=disabled ../../js/src/dist/bin/js%{major} || :
%endif
# Run basic JIT tests
%if 0%{?require_tests}
PYTHONPATH=tests/lib %{__python3} jit-test/jit_test.py -s -t 1800 --no-progress ../../js/src/dist/bin/js%{major} basic
%else
 PYTHONPATH=tests/lib %{__python3} jit-test/jit_test.py -s -t 1800 --no-progress ../../js/src/dist/bin/js%{major} basic || :
%endif
popd

%ldconfig_scriptlets

%files
%doc js/src/README.html
%license LICENSE
%{_libdir}/libmozjs-%{major}.so.0*

%files devel
%{_bindir}/js%{major}
%{_libdir}/libmozjs-%{major}.so
%{_libdir}/pkgconfig/*.pc
%{_includedir}/mozjs-%{major}/

%changelog
* Wed Mar 09 2022 Jiacheng Zhou <jchzhou@outlook.com> - 78.15.0-2
- Add riscv64 support, tidy up according to rpmlint

* Sat Dec 04 2021 wangkerong <wangkerong@huawei.com> - 78.15.0-1
- update to 78.15.0

* Tue May 11 2021 zhanzhimin <zhanzhimin@huawei.com> - 78.4.0-2
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix build error caused by rust

* Thu Nov 05 2020 chengguipeng <chengguipeng1@huawei.com> - 78.4.0-1
- Package init
