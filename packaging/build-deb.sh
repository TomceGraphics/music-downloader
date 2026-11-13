#!/usr/bin/env bash
# Build a .deb (Debian, Ubuntu, Mint, ...). Run ./build.sh first. No sudo needed.
# Output: dist/music-downloader_<version>_<arch>.deb
set -euo pipefail
cd "$(dirname "$0")/.."
command -v dpkg-deb >/dev/null || { echo "dpkg-deb not found (this script needs a Debian/Ubuntu host)" >&2; exit 1; }

SLUG="$(python3 packaging/info.py slug)"; VERSION="$(python3 packaging/info.py version)"
REPO="$(python3 packaging/info.py repo)"; ARCH="$(dpkg --print-architecture)"
PKG="dist/pkg-deb/${SLUG}_${VERSION}_${ARCH}"

bash packaging/stage.sh "$PKG"
mkdir -p "$PKG/DEBIAN"
cat > "$PKG/DEBIAN/control" <<CONTROL
Package: ${SLUG}
Version: ${VERSION}
Section: sound
Priority: optional
Architecture: ${ARCH}
Maintainer: ${MAINTAINER:-Music Downloader <noreply@users.noreply.github.com>}
Installed-Size: $(du -sk "$PKG/opt" | cut -f1)
Depends: libc6 (>= 2.35), libx11-6, libfontconfig1
Recommends: ffmpeg
Suggests: nodejs
Homepage: https://github.com/${REPO}
Description: Download music as tagged MP3s using yt-dlp
 A small desktop app: paste a playlist or video link and get MP3 files with
 title, artist and cover art embedded. Shows live per-track progress, skips
 tracks you already have, and finds duplicates.
 .
 yt-dlp, ffmpeg and a JavaScript runtime are fetched on first run if the
 system does not already provide them.
CONTROL

dpkg-deb --root-owner-group --build "$PKG" "dist/${SLUG}_${VERSION}_${ARCH}.deb" >/dev/null
echo "built: dist/${SLUG}_${VERSION}_${ARCH}.deb  ($(du -h "dist/${SLUG}_${VERSION}_${ARCH}.deb" | cut -f1))"
