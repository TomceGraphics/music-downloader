#!/usr/bin/env bash
# Build an .rpm (Fedora, RHEL-likes, openSUSE). Run ./build.sh first. No sudo needed.
# Needs `rpmbuild` (Fedora: sudo dnf install rpm-build   Ubuntu: sudo apt install rpm).
# Output: dist/music-downloader-<version>-1.<arch>.rpm
set -euo pipefail
cd "$(dirname "$0")/.."
command -v rpmbuild >/dev/null || { echo "rpmbuild not found (Fedora: sudo dnf install rpm-build; Ubuntu: sudo apt install rpm)" >&2; exit 1; }

SLUG="$(python3 packaging/info.py slug)"; VERSION="$(python3 packaging/info.py version)"
REPO="$(python3 packaging/info.py repo)"
TOP="$PWD/dist/pkg-rpm"; STAGE="$TOP/stage"

rm -rf "$TOP/RPMS"
bash packaging/stage.sh "$STAGE"
rpmbuild -bb packaging/rpm/music-downloader.spec --target "$(uname -m)" \
  --define "_topdir $TOP" --define "app_version $VERSION" --define "app_repo $REPO" --define "stage $STAGE" \
  >"$TOP/build.log" 2>&1 || { cat "$TOP/build.log" >&2; exit 1; }
cp "$TOP"/RPMS/*/*.rpm dist/
echo "built: $(ls dist/*.rpm | head -1)"
