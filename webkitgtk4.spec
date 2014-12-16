## NOTE: Lots of files in various subdirectories have the same name (such as
## "LICENSE") so this short macro allows us to distinguish them by using their
## directory names (from the source tree) as prefixes for the files.
%global add_to_license_files() \
        mkdir -p _license_files ; \
        cp -p %1 _license_files/$(echo '%1' | sed -e 's!/!.!g')

%global _hardened_build 1

Name:           webkitgtk4
Version:        2.7.3
Release:        1%{?dist}
Summary:        GTK+ Web content engine library

License:        LGPLv2
URL:            http://www.webkitgtk.org/
Source0:        http://webkitgtk.org/releases/webkitgtk-%{version}.tar.xz

Patch0:         webkit-1.1.14-nspluginwrapper.patch
Patch2:         webkitgtk-2.5.90-cloop_fix.patch
Patch3:         webkitgtk-2.5.2-commit_align.patch
# https://bugzilla.gnome.org/show_bug.cgi?id=726326
# https://bugs.webkit.org/show_bug.cgi?id=135973
Patch4:         webkitgtk-2.7.2-disable-codec-installer.patch

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
BuildRequires:  gtk-doc
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

# Obsolete libwebkit2gtk from the webkitgtk3 package
Obsoletes:      libwebkit2gtk < 2.5.0
Provides:       libwebkit2gtk = %{version}-%{release}

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

%package        doc
Summary:        Documentation files for %{name}
BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}

%description    doc
This package contains developer documentation for %{name}.

%prep
%setup -q -n webkitgtk-%{version}
%patch0 -p1 -b .nspluginwrapper
%patch2 -p1 -b .cloop_fix
%ifarch %{power64} aarch64 ppc
%patch3 -p1 -b .commit_align
%endif
%patch4 -p1 -b .disable_codec_installer

# Remove bundled libraries
rm -rf Source/ThirdParty/leveldb/
rm -rf Source/ThirdParty/gtest/
rm -rf Source/ThirdParty/qunit/

%build
%ifarch s390 aarch64
# Use linker flags to reduce memory consumption - on other arches the ld.gold is
# used and also it doesn't have the --reduce-memory-overheads option
%global optflags %{optflags} -Wl,--no-keep-memory -Wl,--reduce-memory-overheads
%endif

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

# Disable ld.gold on s390 as it does not have it.
# Also for aarch64 as the support is in upstream, but not packaged in Fedora.
mkdir -p %{_target_platform}
pushd %{_target_platform}
%cmake \
  -DPORT=GTK \
  -DCMAKE_BUILD_TYPE=Release \
  -DENABLE_GTKDOC=ON \
%ifarch s390 aarch64
  -DUSE_LD_GOLD=OFF \
%endif
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
%{_libexecdir}/webkit2gtk-4.0/

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

%files doc
%dir %{_datadir}/gtk-doc
%dir %{_datadir}/gtk-doc/html
%{_datadir}/gtk-doc/html/webkit2gtk-4.0/
%{_datadir}/gtk-doc/html/webkitdomgtk-4.0/

%changelog
* Tue Dec 16 2014 Tomas Popela <tpopela@redhat.com> - 2.7.3-1
- Update to 2.7.3

* Tue Dec 09 2014 Michael Catanzaro <mcatanzaro@gnome.org> - 2.7.2-3
- Disable the PackageKit codec installer

* Sun Dec 07 2014 Michael Catanzaro <mcatanzaro@gnome.org> - 2.7.2-2
- Enable hardened build

* Mon Nov 24 2014 Tomas Popela <tpopela@redhat.com> - 2.7.2-1
- Update to 2.7.2
- Don't use ld.gold on s390 and aarch64

* Wed Nov 12 2014 Tomas Popela <tpopela@redhat.com> - 2.7.1-5
- Enable JIT where possible (accidentally turned off when updating to 2.5.90)

* Fri Nov 07 2014 Kalev Lember <kalevlember@gmail.com> - 2.7.1-4
- Build developer documentation

* Fri Oct 31 2014 Michael Catanzaro <mcatanzaro@gnome.org> - 2.7.1-3
- Obsolete libwebkit2gtk < 2.5.0 to be future-proof

* Fri Oct 31 2014 Kalev Lember <kalevlember@gmail.com> - 2.7.1-2
- Bump libwebkit2gtk obsoletes version

* Wed Oct 29 2014 Tomas Popela <tpopela@redhat.com> - 2.7.1-1
- Update to 2.7.1

* Wed Oct 22 2014 Tomas Popela <tpopela@redhat.com> - 2.6.2-1
- Update to 2.6.2

* Tue Oct 21 2014 Tomas Popela <tpopela@redhat.com> - 2.6.1-2
- Disable the SSLv3 to address the POODLE vulnerability

* Tue Oct 14 2014 Tomas Popela <tpopela@redhat.com> - 2.6.1-1
- Update to 2.6.1

* Thu Sep 25 2014 Tomas Popela <tpopela@redhat.com> - 2.6.0-1
- Add the wrongly removed CLoop patch and remove the one that was upstreamed

* Wed Sep 24 2014 Kalev Lember <kalevlember@gmail.com> - 2.6.0-1
- Update to 2.6.0

* Mon Sep 22 2014 Tomas Popela <tpopela@redhat.com> - 2.5.90-1
- Update to 2.5.90

* Tue Aug 26 2014 Kalev Lember <kalevlember@gmail.com> - 2.5.3-7
- Obsolete libwebkit2gtk from the webkitgtk3 package

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
