# RPM spec: repackages the PyInstaller bundle (built by ./build.sh). Used by packaging/build-rpm.sh.
%global debug_package %{nil}
%global __os_install_post %{nil}
%global _build_id_links none
AutoReqProv: no

Name:           music-downloader
Version:        %{app_version}
Release:        1
Summary:        Download music as tagged MP3s using yt-dlp
License:        MIT
URL:            https://github.com/%{app_repo}
Requires:       glibc >= 2.35
Requires:       libX11
Requires:       fontconfig

%description
A small desktop app: paste a playlist or video link and get MP3 files with
title, artist and cover art embedded. Shows live per-track progress, skips
tracks you already have, and finds duplicates.

yt-dlp, ffmpeg and a JavaScript runtime are fetched on first run if the
system does not already provide them.

%prep
%build

%install
mkdir -p %{buildroot}
cp -a %{stage}/. %{buildroot}/

%files
/opt/music-downloader
/usr/bin/music-downloader
/usr/share/applications/music-downloader.desktop
/usr/share/icons/hicolor/512x512/apps/music-downloader.png
/usr/share/licenses/music-downloader/LICENSE
/usr/share/doc/music-downloader
