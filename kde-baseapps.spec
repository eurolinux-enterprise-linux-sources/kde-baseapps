Name:    kde-baseapps
Summary: KDE Core Applications
Version: 4.10.5
Release: 6%{?dist}

License: GPLv2
URL:     https://projects.kde.org/projects/kde/kde-baseapps
%global revision %(echo %{version} | cut -d. -f3)
%if %{revision} >= 50
%global stable unstable
%else
%global stable stable
%endif
Source0: http://download.kde.org/%{stable}/%{version}/src/kde-baseapps-%{version}.tar.xz

## upstreamable patches
# search path for plugins
Patch0: kdebase-4.1.80-nsplugins-paths.patch

# make menuitem Home visible
Patch2: kdebase-4.2.1-home-icon.patch

# fix disabling automatic spell checking in the Konqueror UI (kde#228593)
Patch3: kdebase-4.4.0-konqueror-kde#228593.patch

# Password & User account becomes non responding
Patch4: kdebase-4.3.4-bz#609039-chfn-parse.patch

# add x-scheme-handler/http for konqueror so it can be set
# as default browser in GNOME
Patch5: kde-baseapps-4.9.2-konqueror-mimetyp.patch

Patch6: kde-baseapps-4.10.5-remove-env-shebang.patch

# Bug 1344052 - Drop functionality doesn't work on .desktop files
Patch7: kde-baseapps-allow-to-drop-files-on-readonly-desktop-files.patch

## upstream patches

%ifnarch s390 s390x
Requires: eject
%endif

Requires: %{name}-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

Obsoletes: kdebase < 6:4.7.97-10
Provides:  kdebase = 6:%{version}-%{release}

Obsoletes: kdebase4 < %{version}-%{release}
Provides:  kdebase4 = %{version}-%{release}

Obsoletes: d3lphin
Obsoletes: dolphin < 1.0.2-1
Provides:  dolphin = %{version}-%{release}

Obsoletes: kde-plasma-folderview < 6:4.3.1-1
Provides:  kde-plasma-folderview = %{?epoch:%{epoch}:}%{version}-%{release}

Obsoletes: konq-plugins < 4.6.80-1
Provides:  konq-plugins = %{version}-%{release}

Provides: konqueror = %{version}-%{release}

BuildRequires: desktop-file-utils
BuildRequires: kactivities-devel >= %{version}
BuildRequires: kdelibs4-devel >= %{version}
BuildRequires: nepomuk-core-devel >= %{version}
BuildRequires: nepomuk-widgets-devel >= %{version}
%if 0%{?fedora}
BuildRequires: libtidy-devel
%endif
BuildRequires: pkgconfig
BuildRequires: pkgconfig(glib-2.0)
BuildRequires: pkgconfig(libstreams)

Requires: kde-runtime >= %{version}
# for upgrade path, when konsole, kwrite were split out since 4.7.90
# remove unconditional or f18+ only? (bug #834137)  -- rex
%if 0%{?fedora} < 17 && 0%{?rhel} < 7
Requires: konsole
Requires: kwrite
%endif

%description
Core applications for KDE 4, including:
dolphin : File manager
kdepasswd : Changes a UNIX password.
kdialog : Nice dialog boxes from shell scripts
keditbookmarks : Bookmark oranizer and editor
kfind : File find utility
kfmclient : Tool for opening URLs from the command line
konqueror : Web browser, file manager and document viewer

%package -n kde-plasma-folderview
Summary: FolderView plasma applet
Requires: %{name}-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
%description -n kde-plasma-folderview
%{summary}.

%package libs
Summary: Runtime libraries for %{name}
Obsoletes: kdebase-libs < 6:4.7.97-10
Provides:  kdebase-libs < 6:%{version}-%{release}
Provides:  kdebase-libs%{?_isa} < 6:%{version}-%{release}
# lib(dolphin|konq) likely require appsdir resources, and other goodies
Requires: %{name} = %{?epoch:%{epoch}:}%{version}-%{release}
%{?_kde4_version:Requires: kdelibs4%{?_isa} >= %{_kde4_version}}
%description libs
%{summary}.

%package devel
Summary:  Development files for %{name}
Obsoletes: kdebase-devel < 6:4.7.97-10
Provides:  kdebase-devel = 6:%{version}-%{release}
Obsoletes: kdebase4-devel < %{version}-%{release}
Provides:  kdebase4-devel = %{version}-%{release}
Requires: %{name}-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires: kdelibs4-devel
%description devel
%{summary}.


%prep
%setup -q -n kde-baseapps-%{version}

%patch0 -p2 -b .nsplugins-paths
%patch2 -p2 -b .home-icon
%patch3 -p2 -b .kde#228593
%patch4 -p2 -b .bz#631481
%patch5 -p1 -b .mimetyp.patch
%patch6 -p1 -b .remove-env-shebang
%patch7 -p1 -b .allow-to-drop-files-on-readonly-desktop-files

%build
mkdir -p %{_target_platform}
pushd %{_target_platform}
%{cmake_kde4} ..
popd

make %{?_smp_mflags} -C %{_target_platform}


%install
rm -rf %{buildroot}
make install/fast DESTDIR=%{buildroot} -C %{_target_platform}

# konquerorsu only show in KDE
echo 'OnlyShowIn=KDE;' >> %{buildroot}%{_kde4_datadir}/applications/kde4/konquerorsu.desktop

# create/own some dirs
mkdir -p %{buildroot}%{_kde4_appsdir}/konqueror/{kpartplugins,icons,opensearch}

## unpackaged files
# libs for which there is no (public) api
rm -f %{buildroot}%{_libdir}/lib{dolphin,kbookmarkmodel_,konqueror}private.so

# move devel symlinks
mkdir -p %{buildroot}%{_kde4_libdir}/kde4/devel
pushd %{buildroot}%{_kde4_libdir}
for i in lib*.so
do
  case "$i" in
    libkonq.so|libkonqsidebarplugin.so)
      linktarget=`readlink "$i"`
      rm -f "$i"
      ln -sf "../../$linktarget" "kde4/devel/$i"
      ;;
    *)
      ;;
  esac
done
popd

# fix documentation multilib conflict in index.cache
for f in konqueror dolphin ; do
   bunzip2 %{buildroot}%{_kde4_docdir}/HTML/en/$f/index.cache.bz2
   sed -i -e 's!name="id[a-z]*[0-9]*"!!g' %{buildroot}%{_kde4_docdir}/HTML/en/$f/index.cache
   sed -i -e 's!#id[a-z]*[0-9]*"!!g' %{buildroot}%{_kde4_docdir}/HTML/en/$f/index.cache
   bzip2 -9 %{buildroot}%{_kde4_docdir}/HTML/en/$f/index.cache
done

%find_lang %{name} --all-name --with-kde --without-mo


%check
for f in %{buildroot}%{_kde4_datadir}/applications/kde4/*.desktop ; do
  desktop-file-validate $f
done


%clean
rm -rf %{buildroot}


%post
touch --no-create %{_kde4_iconsdir}/hicolor &> /dev/null ||:
touch --no-create %{_kde4_iconsdir}/oxygen &> /dev/null ||:

%posttrans
gtk-update-icon-cache %{_kde4_iconsdir}/hicolor &> /dev/null ||:
gtk-update-icon-cache %{_kde4_iconsdir}/oxygen &> /dev/null ||:
update-desktop-database -q &> /dev/null ||:

%postun
if [ $1 -eq 0 ] ; then
  touch --no-create %{_kde4_iconsdir}/hicolor &> /dev/null ||:
  touch --no-create %{_kde4_iconsdir}/oxygen &> /dev/null ||:
  gtk-update-icon-cache %{_kde4_iconsdir}/hicolor &> /dev/null ||:
  gtk-update-icon-cache %{_kde4_iconsdir}/oxygen &> /dev/null ||:
  update-desktop-database -q &> /dev/null ||:
fi

%files -f %{name}.lang
%doc COPYING
%{_kde4_bindir}/dolphin
%{_kde4_bindir}/fsview
%{_kde4_bindir}/kbookmarkmerger
%{_kde4_bindir}/kdepasswd
%{_kde4_bindir}/kdialog
%{_kde4_bindir}/keditbookmarks
%{_kde4_bindir}/kfind
%{_kde4_bindir}/kfmclient
%{_kde4_bindir}/konqueror
%{_kde4_bindir}/nspluginscan
%{_kde4_bindir}/nspluginviewer
%{_kde4_bindir}/servicemenudeinstallation
%{_kde4_bindir}/servicemenuinstallation
%{_kde4_datadir}/applications/kde4/Home.desktop
%{_kde4_datadir}/applications/kde4/dolphin.desktop
%{_kde4_datadir}/applications/kde4/kdepasswd.desktop
%{_kde4_datadir}/applications/kde4/keditbookmarks.desktop
%{_kde4_datadir}/applications/kde4/kfind.desktop
%{_kde4_datadir}/applications/kde4/kfmclient.desktop
%{_kde4_datadir}/applications/kde4/kfmclient_dir.desktop
%{_kde4_datadir}/applications/kde4/kfmclient_html.desktop
%{_kde4_datadir}/applications/kde4/kfmclient_war.desktop
%{_kde4_datadir}/applications/kde4/konqbrowser.desktop
%{_kde4_datadir}/applications/kde4/konquerorsu.desktop
%{_kde4_appsdir}/akregator/
%{_kde4_appsdir}/dolphin/
%{_kde4_appsdir}/dolphinpart/
%{_kde4_appsdir}/domtreeviewer/
%{_kde4_appsdir}/fsview/
%{_kde4_appsdir}/kbookmark/
%{_kde4_appsdir}/kcmcss/
%{_kde4_appsdir}/kcontrol/
%{_kde4_appsdir}/kdm/
%{_kde4_appsdir}/keditbookmarks/
%{_kde4_appsdir}/khtml/
%{_kde4_appsdir}/konqsidebartng/
%{_kde4_appsdir}/konqueror/
%{_kde4_appsdir}/kwebkitpart/
%{_kde4_appsdir}/nsplugin/
%{_kde4_datadir}/config.kcfg/*
%{_datadir}/dbus-1/interfaces/*
%{_kde4_iconsdir}/hicolor/*/*/*
%{_kde4_iconsdir}/oxygen/*/*/*
%{_kde4_datadir}/kde4/services/*.desktop
%{_kde4_datadir}/kde4/services/*.protocol
%{_kde4_datadir}/kde4/services/ServiceMenus/
%{_kde4_datadir}/kde4/services/kded/*.desktop
%{_kde4_datadir}/kde4/services/useragentstrings/
%{_kde4_datadir}/kde4/servicetypes/*.desktop
%{_kde4_libdir}/kde4/*.so
%{_mandir}/man1/kbookmarkmerger.1.gz
%{_mandir}/man1/kfind.1.gz
%{_kde4_datadir}/autostart/konqy_preload.desktop
%{_kde4_configdir}/*
%{_kde4_datadir}/templates/*.desktop
%{_kde4_datadir}/templates/.source/*
%{_kde4_libdir}/libkdeinit4_*.so

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files libs
%{_kde4_libdir}/libkbookmarkmodel_private.so.4*
%{_kde4_libdir}/libdolphinprivate.so.4*
%{_kde4_libdir}/libkonq.so.5*
%{_kde4_libdir}/libkonqsidebarplugin.so.4*
%{_kde4_libdir}/libkonquerorprivate.so.4*

%files devel
%{_kde4_includedir}/*.h
%{_kde4_libdir}/kde4/devel/libkonq.so
%{_kde4_libdir}/kde4/devel/libkonqsidebarplugin.so


%changelog
* Tue Oct 17 2017 Jan Grulich <jgrulich@redhat.com>
- Require same version of kde-runtime as kde-baseapps
  Resolves: bz#1503023

* Mon Oct 16 2017 Jan Grulich <jgrulich@redhat.com>
- Allow to drop files on readonly desktop files
  Resolves: bz#1344052

* Tue Jan 28 2014 Daniel Mach <dmach@redhat.com> - 4.10.5-4
- Mass rebuild 2014-01-24

* Mon Jan 13 2014 Jan Grulich <jgrulich@redhat.com> - 4.10.5-3
- Do not use shebang with env (#987023)

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 4.10.5-2
- Mass rebuild 2013-12-27

* Sun Jun 30 2013 Than Ngo <than@redhat.com> - 4.10.5-1
- 4.10.5

* Sat Jun 01 2013 Rex Dieter <rdieter@fedoraproject.org> - 4.10.4-1
- 4.10.4

* Mon May 06 2013 Than Ngo <than@redhat.com> - 4.10.3-1
- 4.10.3

* Mon Apr 29 2013 Than Ngo <than@redhat.com> - 4.10.2-2
- fix multilib issue

* Sun Mar 31 2013 Rex Dieter <rdieter@fedoraproject.org> - 4.10.2-1
- 4.10.2

* Sat Mar 02 2013 Rex Dieter <rdieter@fedoraproject.org> 4.10.1-1
- 4.10.1

* Thu Jan 31 2013 Rex Dieter <rdieter@fedoraproject.org> - 4.10.0-1
- 4.10.0

* Sun Jan 20 2013 Rex Dieter <rdieter@fedoraproject.org> - 4.9.98-1
- 4.9.98

* Fri Jan 04 2013 Rex Dieter <rdieter@fedoraproject.org> - 4.9.97-1
- 4.9.97

* Thu Dec 20 2012 Rex Dieter <rdieter@fedoraproject.org> - 4.9.95-1
- 4.9.95

* Thu Dec 13 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.90-3
- Dolphin cannot start due to symbol lookup error (#886964)

* Mon Dec 03 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.90-2
- BR: kactivites-devel nepomuk-core-devel

* Mon Dec 03 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.90-1
- 4.9.90 (4.10 beta2)

* Mon Dec 03 2012 Than Ngo <than@redhat.com> - 4.9.4-1
- 4.9.4

* Thu Nov 29 2012 Dan Vrátil <dvratil@redhat.com> - 4.9.3-2
- Dolphin Solid optimizations

* Sat Nov 03 2012 Rex Dieter <rdieter@fedoraproject.org> - 4.9.3-1
- 4.9.3

* Tue Oct 16 2012 Than Ngo <than@redhat.com> - 4.9.2-3
- add x-scheme-handler/http for konqueror so it can be set as default browser in GNOME

* Sat Sep 29 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.2-2
- tarball respin

* Fri Sep 28 2012 Rex Dieter <rdieter@fedoraproject.org> - 4.9.2-1
- 4.9.2

* Tue Sep 11 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.1-2
- Cryptsetup crashes Dolphin on Closing of Loop Devic (#842164,kde#306167)

* Mon Sep 03 2012 Than Ngo <than@redhat.com> - 4.9.1-1
- 4.9.1
- drop references to kdepimlibs

* Thu Jul 26 2012 Lukas Tinkl <ltinkl@redhat.com> - 4.9.0-1
- 4.9.0

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.8.97-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jul 11 2012 Rex Dieter <rdieter@fedoraproject.org> - 4.8.97-1
- 4.8.97

* Wed Jun 27 2012 Jaroslav Reznik <jreznik@redhat.com> - 4.8.95-1
- 4.8.95

* Wed Jun 20 2012 Rex Dieter <rdieter@fedoraproject.org> 4.8.90-2
- Please remove kwrite dependency (#834137)

* Sat Jun 09 2012 Rex Dieter <rdieter@fedoraproject.org> - 4.8.90-1
- 4.8.90

* Fri Jun 01 2012 Jaroslav Reznik <jreznik@redhat.com> 4.8.80-2
- respin

* Mon May 28 2012 Rex Dieter <rdieter@fedoraproject.org> 4.8.80-1
- 4.8.80

* Mon Apr 30 2012 Jaroslav Reznik <jreznik@redhat.com> - 4.8.3-1
- 4.8.3
- removed Dolphin timeout patch

* Mon Apr 16 2012 Rex Dieter <rdieter@fedoraproject.org> 4.8.2-2
- dolphin keyboard search timeout improvement (kde#297458, kde#297488)

* Fri Mar 30 2012 Rex Dieter <rdieter@fedoraproject.org> - 4.8.2-1
- 4.8.2

* Mon Mar 05 2012 Jaroslav Reznik <jreznik@redhat.com> - 4.8.1-1
- 4.8.1

* Tue Feb 28 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.8.0-3
- Rebuilt for c++ ABI breakage

* Wed Jan 25 2012 Than Ngo <than@redhat.com> - 4.8.0-2
- fix kde#292250, make sure that Control+click toggles the selection state

* Fri Jan 20 2012 Jaroslav Reznik <jreznik@redhat.com> - 4.8.0-1
- 4.8.0

* Fri Jan 13 2012 Radek Novacek <rnovacek@redhat.com> 4.7.97-12
- Remove unnecessary BRs

* Fri Jan 13 2012 Rex Dieter <rdieter@fedoraproject.org> 6:4.7.97-11
- %%check: desktop-file-validate
- %%doc COPYING
- fix some errant Provides

* Wed Jan 04 2012 Rex Dieter <rdieter@fedoraproject.org> 6:4.7.97-10
- kdebase => kde-baseapps rename

* Wed Jan 04 2012 Rex Dieter <rdieter@fedoraproject.org> 6:4.7.97-1
- 4.7.97

* Wed Dec 21 2011 Radek Novacek <rnovacek@redhat.com> - 6:4.7.95-1
- 4.7.95

* Sun Dec 04 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7.90-1
- 4.7.90
- Build with glib support (#759882)

* Mon Nov 21 2011 Jaroslav Reznik <jreznik@redhat.com> 4.7.80-1
- 4.7.80 (beta 1)
- fix conditional for kwebkitpart

* Sat Oct 29 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7.3-1
- 4.7.3
- pkgconfig-style deps
- more kde-baseapps Provides

* Wed Oct 26 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6:4.7.2-3
- Rebuilt for glibc bug#747377

* Sat Oct 08 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7.2-2
- rebase folderview/rename patch (kde#270414)

* Tue Oct 04 2011 Rex Dieter <rdieter@fedoraproject.org> 4.7.2-1
- 4.7.2

* Wed Sep 21 2011 Rex Dieter <rdieter@fedoraproject.org> 6:4.7.1-2
- Rename any file using folderview causes an error message (kde#270414)

* Fri Sep 02 2011 Than Ngo <than@redhat.com> - 6:4.7.1-1
- 4.7.1

* Tue Jul 26 2011 Jaroslav Reznik <jreznik@redhat.com> 6:4.7.0-1
- 4.7.0

* Fri Jul 22 2011 Rex Dieter <rdieter@fedoraproject.org> 6:4.6.95-11
- Requires: konsole kwrite, for upgrade path

* Thu Jul 21 2011 Rex Dieter <rdieter@fedoraproject.org> 6:4.6.95-10
- drop kate, konsole, to be packaged separately.
- update summary to mention included apps/utilities
- Provides: kde-baseapps (matching new upstream tarball)

* Mon Jul 18 2011 Rex Dieter <rdieter@fedoraproject.org> 6:4.6.95-2
- Provides: konqueror, konsole

* Fri Jul 08 2011 Jaroslav Reznik <jreznik@redhat.com> - 6:4.6.95-1
- 4.6.95 (rc2)

* Mon Jun 27 2011 Than Ngo <than@redhat.com> - 6:4.6.90-1
- 4.6.90 (rc1)

* Wed Jun 01 2011 Radek Novacek <rnovacek@redhat.com> 6:4.6.80-1
- 4.6.80
- import separately packaged kwrite and konsole
- drop upstreamed patches (nsplugins_sdk_headers and nsplugins_flash)
- add konq-plugins

* Mon May 23 2011 Rex Dieter <rdieter@fedoraproject.org> 6:4.6.3-2
- nspluginviewer crashes with flash-plugin 10.3 (kde#273323)

* Thu Apr 28 2011 Rex Dieter <rdieter@fedoraproject.org> 6:4.6.3-1
- 4.6.3

* Wed Apr 06 2011 Than Ngo <than@redhat.com> - 6:4.6.2-1
- 4.6.2

* Sun Mar 06 2011 Kevin Kofler <Kevin@tigcc.ticalc.org> 6:4.6.1-3
- fix Dolphin regression

* Thu Mar 03 2011 Rex Dieter <rdieter@fedoraproject.org> 6:4.6.1-2
- respin tarball

* Mon Feb 28 2011 Rex Dieter <rdieter@fedoraproject.org> 6:4.6.1-1
- 4.6.1

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6:4.6.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Jan 21 2011 Jaroslav Reznik <jreznik@redhat.com> 6:4.6.0-1
- 4.6.0

* Wed Jan 05 2011 Jaroslav Reznik <jreznik@redhat.com> 6:4.5.95-1
- 4.5.95 (4.6rc2)

* Wed Dec 22 2010 Rex Dieter <rdieter@fedoraproject.org> 6:4.5.90-1
- 4.5.90 (4.6rc1)

* Sat Dec 04 2010 Thomas Janssen <thomasj@fedoraproject.org> 6:4.5.85-1
- 4.5.85 (4.6beta2)

* Mon Nov 22 2010 Rex Dieter <rdieter@fedoraproject.org> - 6:4.5.80-2
- drop extraneous BR's

* Sat Nov 20 2010 Rex Dieter <rdieter@fedoraproject.org> - 6:4.5.80-1
- 4.5.80 (4.6beta1)

* Fri Oct 29 2010 Than Ngo <than@redhat.com> - 6:4.5.3-1
- 4.5.3

* Wed Oct 13 2010 Rex Dieter <rdieter@fedoraproject.org> - 6:4.5.2-2
- FolderView keeps sorting icons (kde#227157)

* Fri Oct 01 2010 Rex Dieter <rdieter@fedoraproject.org> - 6:4.5.2-1
- 4.5.2

* Thu Sep 30 2010 Than Ngo <than@redhat.com> - 6:4.5.1-4
- Password & User account becomes non responding

* Wed Sep 29 2010 jkeating - 6:4.5.1-3
- Rebuilt for gcc bug 634757

* Mon Sep 20 2010 Rex Dieter <rdieter@fedoraproject.org> - 6:4.5.1-2
- konsole minimum tab width is too wide (#632217, kde#166573)

* Fri Aug 27 2010 Jaroslav Reznik <jreznik@redhat.com> - 6:4.5.1-1
- 4.5.1

* Tue Aug 03 2010 Than Ngo <than@redhat.com> - 6:4.5.0-1
- 4.5.0

* Sun Jul 25 2010 Rex Dieter <rdieter@fedoraproject.org> - 6:4.4.95-1
- 4.5 RC3 (4.4.95)

* Wed Jul 07 2010 Rex Dieter <rdieter@fedoraproject.org> - 6:4.4.92-1
- 4.5 RC2 (4.4.92)

* Tue Jul 06 2010 Rex Dieter <rdieter@fedoraproject.org> - 6:4.4.90-2
- update %%summary/%%description
- tighten deps

* Fri Jun 25 2010 Jaroslav Reznik <jreznik@redhat.com> - 6:4.4.90-1
- 4.5 RC1 (4.4.90)

* Mon Jun 07 2010 Jaroslav Reznik <jreznik@redhat.com> - 6:4.4.85-1
- 4.5 Beta 2 (4.4.85)

* Fri May 21 2010 Jaroslav Reznik <jreznik@redhat.com> - 6:4.4.80-1
- 4.5 Beta 1 (4.4.80)

* Sat May 01 2010 Kevin Kofler <Kevin@tigcc.ticalc.org> - 6:4.4.3-2
- completely drop commented out konsole-session patch (fixed upstream)
- add backwards compatibility hack for a config option change by that patch

* Fri Apr 30 2010 Jaroslav Reznik <jreznik@redhat.com> - 6:4.4.3-1
- 4.4.3

* Mon Mar 29 2010 Lukas Tinkl <ltinkl@redhat.com> - 6:4.4.2-1
- 4.4.2

* Mon Mar 15 2010 Rex Dieter <rdieter@fedoraproject.org> - 6:4.4.1-2
- drop kappfinder (keep option for -kappfinder subpkg)
- use whitelist for conflicting libs
- libs: Requires: %%name

* Sat Feb 27 2010 Rex Dieter <rdieter@fedoraproject.org> - 6:4.4.1-1
- 4.4.1

* Fri Feb 26 2010 Kevin Kofler <Kevin@tigcc.ticalc.org> - 6:4.4.0-5
- fix disabling automatic spell checking in the Konqueror UI (kde#228593)

* Thu Feb 25 2010 Kevin Kofler <Kevin@tigcc.ticalc.org> - 6:4.4.0-4
- backport fix for folderview getting resorted on file creation (kde#227157)

* Wed Feb 10 2010 Kevin Kofler <Kevin@tigcc.ticalc.org> - 6:4.4.0-3
- BR webkitpart-devel >= 0.0.5

* Wed Feb 10 2010 Rex Dieter <rdieter@fedoraproject.org> - 6:4.4.0-2
- disable webkitpart support (until upstream naming/api stabilizes)

* Fri Feb 05 2010 Than Ngo <than@redhat.com> - 6:4.4.0-1
- 4.4.0

* Mon Feb 01 2010 Rex Dieter <rdieter@fedoraproject.org> - 4.3.98-2
- remove extra spaces from konsole selections (#560721)

* Sun Jan 31 2010 Rex Dieter <rdieter@fedoraproject.org> - 4.3.98-1
- KDE 4.3.98 (4.4rc3)

* Wed Jan 20 2010 Lukas Tinkl <ltinkl@redhat.com> - 4.3.95-1
- KDE 4.3.95 (4.4rc2)

* Wed Jan 06 2010 Rex Dieter <rdieter@fedoraproject.org> - 4.3.90-1
- kde-4.3.90 (4.4rc1)

* Fri Dec 18 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.85-1
- kde-4.3.85 (4.4beta2)

* Wed Dec 16 2009 Jaroslav Reznik <jreznik@redhat.com> - 4.3.80-4
- Repositioning the KDE Brand (#547361)

* Wed Dec 09 2009 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.3.80-3
- rebuild against Nepomuk-enabled kdelibs

* Wed Dec 09 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.80-2
- BR: shared-desktop-ontologies-devel

* Tue Dec 01 2009 Lukáš Tinkl <ltinkl@redhat.com> - 4.3.80-1
- KDE 4.4 beta1 (4.3.80)

* Tue Nov 24 2009 Ben Boeckel <MathStuf@gmail.com> - 4.3.75-0.2.svn1048496
- Fix webkitkde version requirement

* Sun Nov 22 2009 Ben Boeckel <MathStuf@gmail.com> - 4.3.75-0.1.svn1048496
- Update to 4.3.75 snapshot

* Thu Nov 19 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.3-4
- rebuild (for qt-4.6.0-rc1, f13+)

* Wed Nov 11 2009 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.3.3-3
- allow 'Open Folder in Tabs' in Konsole to support SSH bookmarks (kde#177637)
  (upstream patch backported from 4.4)

* Mon Nov 09 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.3-2
- BR: webkitpart-devel >= 0.0.2

* Sat Oct 31 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.3-1
- 4.3.3

* Fri Oct 09 2009 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.3.2-3
- backport upstream patch for bookmark editor drag&drop crash (kde#160679)

* Wed Oct 07 2009 Than Ngo <than@redhat.com> - 4.3.2-2
- fix Dolphin crash (regression)

* Sun Oct 04 2009 Than Ngo <than@redhat.com> - 4.3.2-1
- 4.3.2

* Sun Sep 27 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.1-4
- BR: webkitpart-devel
- fix Provides: kdebase4%%{?_isa} (not kdelibs)

* Sun Sep 27 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.1-3
- own %%_kde4_appsdir/konqueror/{kpartplugins,icons,opensearch}
- %%lang'ify HTML docs
- Provides: kdelibs4%%{?_isa}

* Wed Sep  2 2009 Lukáš Tinkl <ltinkl@redhat.com> - 4.3.1-2
- fix context menus in Konsole (kdebug:186745)

* Fri Aug 28 2009 Than Ngo <than@redhat.com> - 4.3.1-1
- 4.3.1
- drop/revert kde-plasma-folderview subpkg

* Tue Aug 25 2009 Rex Dieter <rdieter@fedoraproject.org> 4.3.0-2
- kde-plasma-folderview subpkg
- %%?_isa'ify -libs deps

* Thu Jul 30 2009 Than Ngo <than@redhat.com> - 4.3.0-1
- 4.3.0

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6:4.2.98-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul 21 2009 Than Ngo <than@redhat.com> - 4.2.98-1
- 4.3rc3

* Thu Jul 09 2009 Than Ngo <than@redhat.com> - 4.2.96-1
- 4.3rc2

* Thu Jun 25 2009 Than Ngo <than@redhat.com> - 4.2.95-1
- 4.3rc1

* Wed Jun 03 2009 Rex Dieter <rdieter@fedoraproject.org> - 6:4.2.90-1
- KDE-4.3 beta2 (4.2.90)

* Tue Jun 02 2009 Lorenzo Villani <lvillani@binaryhelix.net> - 6:4.2.85-2
- Fedora 8 is EOL'ed, drop conditionals and cleanup the specfile

* Wed May 13 2009 Lukáš Tinkl <ltinkl@redhat.com> - 4.2.85-1
- KDE 4.3 beta 1

* Tue Apr 21 2009 Lukáš Tinkl <ltinkl@redhat.com> - 4.2.2-3
- #496447 -  fix disabling konsole's flow control

* Wed Apr 01 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.2-2
- optimize scriptlets

* Mon Mar 30 2009 Lukáš Tinkl <ltinkl@redhat.com> - 4.2.2-1
- KDE 4.2.2

* Mon Mar 09 2009 Than Ngo <than@redhat.com> - 4.2.1-3
- apply patch to fix regression in konsole, layout regression affecting apps
  using the KPart

* Wed Mar 04 2009 Than Ngo <than@redhat.com> - 4.2.1-2
- apply patch to fix regression in konsole, double-click selection works again

* Fri Feb 27 2009 Than Ngo <than@redhat.com> - 4.2.1-1
- 4.2.1

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6:4.2.0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 16 2009 Lukáš Tinkl <ltinkl@redhat.com> - 4.2.0-6
- unbreak apps like vim or mc under Konsole

* Thu Feb 12 2009 Rex Dieter <rdieter@fedorparoject.org> - 4.2.0-5
- avoid_kde3_services patch
- fix home-icon patch

* Thu Feb 12 2009 Lukáš Tinkl <ltinkl@redhat.com> - 4.2.0-4
- add Home icon to the Applications menu by default (#457756)

* Wed Feb 11 2009 Than Ngo <than@redhat.com> - 4.2.0-3
- apply patch to make dolphin working well with 4.5

* Wed Jan 28 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.0-2
- KDEInit could not launch '/usr/bin/konsole' (kdebug#162729)

* Thu Jan 22 2009 Than Ngo <than@redhat.com> - 4.2.0-1
- 4.2.0

* Wed Jan 07 2009 Than Ngo <than@redhat.com> - 4.1.96-1
- 4.2rc1

* Thu Dec 11 2008 Than Ngo <than@redhat.com> -  4.1.85-1
- 4.2beta2

* Thu Nov 27 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 6:4.1.80-4
- BR plasma-devel instead of kdebase-workspace-devel

* Sun Nov 23 2008 Lorenzo Villani <lvillani@binaryhelix.net> - 6:4.1.80-3
- rebase nsplugins-path patch

* Thu Nov 20 2008 Than Ngo <than@redhat.com>  4.1.80-2
- merged

* Wed Nov 19 2008 Lorenzo Villani <lvillani@binaryhelix.net> - 6:4.1.80-1
- 4.1.80
- patch100 was backported from 4.2 (4.1.6x), removed from patch list
- ported 4.1.2 konsole patches
- drop the second konsole patch (upstreamed)
- using make install/fast
- BR cmake >= 2.6.2

* Wed Nov 12 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.1.3-2
- readd kde#156636 patch (Konsole keyboard actions backport)

* Tue Nov  4 2008 Lukáš Tinkl <ltinkl@redhat.com> 4.1.3-1
- KDE 4.1.3

* Thu Oct 16 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.1.2-5
- backport kbd actions for switching to Nth tab in Konsole from 4.2 (kde#156636)

* Mon Oct 06 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.1.2-4
- updated konsole session management patch from Stefan Becker

* Mon Oct 06 2008 Than Ngo <than@redhat.com> 4.1.2-3
- bz#465451, backport konsole session management, thanks to Stefan Becker

* Mon Sep 29 2008 Rex Dieter <rdieter@fedoraproject.org> 4.1.2-2
- make VERBOSE=1
- respin against new(er) kde-filesystem

* Fri Sep 26 2008 Rex Dieter <rdieter@fedoraproject.org> 4.1.2-1
- 4.1.2

* Thu Sep 18 2008 Than Ngo <than@redhat.com> 4.1.1-2
- make bookmark silent

* Fri Aug 29 2008 Than Ngo <than@redhat.com> 4.1.1-1
- 4.1.1

* Fri Jul 25 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.1.0-1.1
- always check for Plasma actually being present (fixes F8 kdebase4 build)

* Wed Jul 23 2008 Than Ngo <than@redhat.com> 4.1.0-1
- 4.1.0

* Tue Jul 22 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.99-2
 respin (libraw1394)

* Fri Jul 18 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.99-1
- 4.0.99

* Fri Jul 11 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.98-2
- BR: pciutils-devel

* Thu Jul 10 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.98-1
- 4.0.98

* Sun Jul 06 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.85-1
- 4.0.85

* Fri Jun 27 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.84-1
- 4.0.84

* Tue Jun 24 2008 Lukáš Tinkl <ltinkl@redhat.com> - 4.0.83-2
- #426108: Add more directories to konqueror's default
  plugin search path list

* Thu Jun 19 2008 Than Ngo <than@redhat.com> 4.0.83-1
- 4.0.83 (beta2)

* Mon Jun 16 2008 Than Ngo <than@redhat.com> 4.0.82-2
- BR kdebase-workspace-devel (F9+)

* Sun Jun 15 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.82-1
- 4.0.82

* Tue May 27 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.80-3
- respun tarball from upstream

* Tue May 27 2008 Than Ngo <than@redhat.com> 4.0.80-2
- rebuild to fix undefined symbol issue in dolphin

* Mon May 26 2008 Than Ngo <than@redhat.com> 4.0.80-1
- 4.1 beta1

* Sun May 11 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.72-2
- quote semicolon in fix for #442834
- only do the echo when konquerorsu.desktop is actually shipped (#445989)

* Tue May 06 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.72-1
- update to 4.0.72 (4.1 alpha 1)
- drop backported kde#160422 and nspluginviewer patches
- add minimum versions to soprano-devel and strigi-devel BRs

* Fri Apr 18 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.3-9
- kwrite.desktop: Categories += Utility (#438786)

* Thu Apr 17 2008 Than Ngo <than@redhat.com> 4.0.3-8
- konquerorsu only show in KDE, #442834

* Mon Apr 14 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.3-7
- nspluginviewer patch (kde#160413)

* Sun Apr 06 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.3-6
- backport Konsole window size fixes from 4.1 (#439638, kde#160422)

* Thu Apr 03 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.3-5
- rebuild (again) for the fixed %%{_kde4_buildtype}

* Mon Mar 31 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.3-4
- add missing BR libraw1394-devel (thanks to Karsten Hopp)
- don't BR libusb-devel on s390 or s390x

* Mon Mar 31 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.3-3
- rebuild for NDEBUG and _kde4_libexecdir

* Fri Mar 28 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.3-2
- add Requires: kdebase-runtime oxygen-icon-theme (#438632)

* Fri Mar 28 2008 Than Ngo <than@redhat.com> 4.0.3-1
- 4.0.3
- drop fix for favicons infinite loop, it's included in new version
- omit multilib upgrade hacks
- omit extraneous BR's
- (re)include oxgygen/scalable icons

* Fri Feb 29 2008 Lukáš Tinkl <ltinkl@redhat.com> 4.0.2-2
- fix favicons infinite loop

* Thu Feb 28 2008 Than Ngo <than@redhat.com> 4.0.2-1
- 4.0.2

* Mon Feb 18 2008 Than Ngo <than@redhat.com> 4.0.1-4
- fix nsplugins hangs during login

* Mon Feb 04 2008 Than Ngo <than@redhat.com> 4.0.1-3
- respin

* Fri Feb 01 2008 Than Ngo <than@redhat.com> 4.0.1-2
- add flash fix from stable svn branch

* Thu Jan 31 2008 Than Ngo <than@redhat.com> 4.0.1-1
- 4.0.1

* Wed Jan 30 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.0-3
- resurrect -libs (f9+)
- improve %%description

* Sat Jan 19 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.0-2.1
- Obsoletes: dolphin, d3lphin, Provides: dolphin everywhere

* Tue Jan 08 2008 Rex Dieter <rdieter[AT]fedoraproject.org> 4.0.0-2
- respun tarball

* Mon Jan 07 2008 Than Ngo <than@redhat.com> 4.0.0-1
- 4.0.0
