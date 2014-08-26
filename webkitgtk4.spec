## NOTE: Lots of files in various subdirectories have the same name (such as
## "LICENSE") so this short macro allows us to distinguish them by using their
## directory names (from the source tree) as prefixes for the files.
%global add_to_license_files() \
        mkdir -p _license_files ; \
        cp -p %1 _license_files/$(echo '%1' | sed -e 's!/!.!g')

Name:           webkitgtk4
Version:        2.5.3
Release:        6%{?dist}
Summary:        GTK+ Web content engine library

License:        LGPLv2
URL:            http://www.webkitgtk.org/
Source0:        http://webkitgtk.org/releases/webkitgtk-%{version}.tar.xz

Patch0:         webkit-1.1.14-nspluginwrapper.patch
Patch1:         webkitgtk-aarch64.patch
Patch2:         webkitgtk-2.5.2-cloop_fix.patch
Patch3:         webkitgtk-2.5.2-cloop_fix_32.patch
Patch4:         webkitgtk-2.5.2-commit_align.patch
# https://bugs.webkit.org/show_bug.cgi?id=135647
Patch5:         webkitgtk-2.4.2-ppc64le.patch
# https://bugs.webkit.org/show_bug.cgi?id=136130
Patch6:         webkitgtk-2.5.3-toggle-buttons.patch

BuildRequires:  at-spi2-core-devel
BuildRequires:  bison
BuildRequires:  cairo-devel
BuildRequires:  cmake
BuildRequires:  enchant-devel
BuildRequires:  flex
BuildRequires:  fontconfig-devel
BuildRequires:  freetype-devel
BuildRequires:  geoclue2-devel
BuildRequires:  gettext
BuildRequires:  glib2-devel
BuildRequires:  gobject-introspection-devel
BuildRequires:  gperf
BuildRequires:  gstreamer1-devel
BuildRequires:  gstreamer1-plugins-base-devel
BuildRequires:  gtk2-devel
BuildRequires:  gtk3-devel
BuildRequires:  harfbuzz-devel
BuildRequires:  libicu-devel
BuildRequires:  libjpeg-devel
BuildRequires:  libpng-devel
BuildRequires:  libsecret-devel
BuildRequires:  libsoup-devel
BuildRequires:  libwebp-devel
BuildRequires:  libxslt-devel
BuildRequires:  libXt-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  pcre-devel
BuildRequires:  perl-Switch
BuildRequires:  ruby
BuildRequires:  sqlite-devel
%ifarch ppc
BuildRequires:  libatomic
%endif
Requires:       geoclue2

# Filter out provides for private libraries
%global __provides_exclude_from ^%{_libdir}/webkit2gtk-4\\.0/.*\\.so$

%description
WebKitGTK+ is the port of the portable web rendering engine WebKit to the
GTK+ platform.

This package contains WebKitGTK+ for GTK+ 3.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries, build data, and header
files for developing applications that use %{name}.

%prep
%setup -q -n webkitgtk-%{version}
%patch0 -p1 -b .nspluginwrapper
%patch2 -p1 -b .cloop_fix
%ifarch s390 ppc
%patch3 -p1 -b .cloop_fix_32
%endif
%ifarch aarch64
%patch1 -p1 -b .aarch64
%endif
%ifarch %{power64} aarch64 ppc
%patch4 -p1 -b .commit_align
%endif
%ifarch %{power64}
%patch5 -p1 -b .ppc64le
%endif
%patch6 -p1 -b .toggle-buttons

# Remove bundled libraries
rm -rf Source/ThirdParty/leveldb/
rm -rf Source/ThirdParty/gtest/
rm -rf Source/ThirdParty/qunit/

%build
# Use linker flags to reduce memory consumption
%global optflags %{optflags} -Wl,--no-keep-memory -Wl,--reduce-memory-overheads

%ifarch s390 %{arm}
# Decrease debuginfo verbosity to reduce memory consumption even more
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')
%endif

%ifarch ppc
# Use linker flag -relax to get WebKit build under ppc(32) with JIT disabled
%global optflags %{optflags} -Wl,-relax -latomic
%endif

%ifarch s390 s390x ppc %{power64} aarch64
%global optflags %{optflags} -DENABLE_YARR_JIT=0
%endif

mkdir -p %{_target_platform}
pushd %{_target_platform}
%cmake \
  -DPORT=GTK \
  -DCMAKE_BUILD_TYPE=Release \
%ifarch s390 s390x ppc %{power64} aarch64
  -DENABLE_JIT=OFF \
  -DENABLE_LLINT_C_LOOP=ON \
%endif
  ..
popd

make %{?_smp_mflags} -C %{_target_platform}

%install
%make_install -C %{_target_platform}

%find_lang WebKit2GTK-4.0

# Finally, copy over and rename various files for %%license inclusion
%add_to_license_files Source/JavaScriptCore/COPYING.LIB
%add_to_license_files Source/JavaScriptCore/icu/LICENSE
%add_to_license_files Source/ThirdParty/ANGLE/LICENSE
%add_to_license_files Source/ThirdParty/ANGLE/src/third_party/compiler/LICENSE
%add_to_license_files Source/ThirdParty/ANGLE/src/third_party/murmurhash/LICENSE
%add_to_license_files Source/WebCore/icu/LICENSE
%add_to_license_files Source/WebCore/LICENSE-APPLE
%add_to_license_files Source/WebCore/LICENSE-LGPL-2
%add_to_license_files Source/WebCore/LICENSE-LGPL-2.1
%add_to_license_files Source/WebInspectorUI/APPLE_IMAGES_LICENSE.rtf
%add_to_license_files Source/WebInspectorUI/UserInterface/External/CodeMirror/LICENSE
%add_to_license_files Source/WebInspectorUI/UserInterface/External/Esprima/LICENSE
%add_to_license_files Source/WTF/icu/LICENSE
%add_to_license_files Source/WTF/wtf/dtoa/COPYING
%add_to_license_files Source/WTF/wtf/dtoa/LICENSE

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files -f WebKit2GTK-4.0.lang
%license _license_files/*
%{_libdir}/libjavascriptcoregtk-4.0.so.*
%{_libdir}/libwebkit2gtk-4.0.so.*
%{_libdir}/girepository-1.0/JavaScriptCore-4.0.typelib
%{_libdir}/girepository-1.0/WebKit2-4.0.typelib
%{_libdir}/girepository-1.0/WebKit2WebExtension-4.0.typelib
%{_libdir}/webkit2gtk-4.0/
%{_libexecdir}/webkitgtk-4.0/

%files devel
%{_bindir}/jsc
%{_includedir}/webkitgtk-4.0/
%{_libdir}/libjavascriptcoregtk-4.0.so
%{_libdir}/libwebkit2gtk-4.0.so
%{_libdir}/pkgconfig/javascriptcoregtk-4.0.pc
%{_libdir}/pkgconfig/webkit2gtk-4.0.pc
%{_libdir}/pkgconfig/webkit2gtk-web-extension-4.0.pc
%{_datadir}/gir-1.0/JavaScriptCore-4.0.gir
%{_datadir}/gir-1.0/WebKit2-4.0.gir
%{_datadir}/gir-1.0/WebKit2WebExtension-4.0.gir

%changelog
* Tue Aug 26 2014 David Tardon <dtardon@redhat.com> - 2.5.3-6
- rebuild for ICU 53.1

* Mon Aug 25 2014 Tomas Popela <tpopela@redhat.com> - 2.5.3-5
- Add support for secondary arches

* Fri Aug 22 2014 Michael Catanzaro <mcatanzaro@gnome.org> - 2.5.3-4
- Add webkitgtk-2.5.3-toggle-buttons.patch

* Thu Aug 21 2014 Kalev Lember <kalevlember@gmail.com> - 2.5.3-3
- More package review fixes (#1131284)
- Correct the license tag to read LGPLv2
- Filter out provides for private libraries

* Tue Aug 19 2014 Kalev Lember <kalevlember@gmail.com> - 2.5.3-2
- Remove bundled leveldb, gtest, qunit in %%prep (#1131284)

* Fri Aug 15 2014 Kalev Lember <kalevlember@gmail.com> - 2.5.3-1
- Update to 2.5.3

* Fri Aug 01 2014 Kalev Lember <kalevlember@gmail.com> - 2.5.1-1
- Initial Fedora packaging, based on the webkitgtk3 package
