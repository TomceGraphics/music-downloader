#!/usr/bin/env bash
# Linux build (Fedora/Ubuntu/...). venv-based, no sudo.
# Output: dist/music-downloader-vX.Y.Z-linux-<arch>.tar.gz (+ .sha256)
set -euo pipefail
cd "$(dirname "$0")"

PY="${PYTHON:-python3}"
"$PY" -c "import tkinter" 2>/dev/null || {
  echo "Tk is missing. Fedora: sudo dnf install python3-tkinter   Debian/Ubuntu: sudo apt install python3-tk"
  exit 1
}
command -v strip >/dev/null || { echo "note: 'strip' not found (sudo dnf install binutils) — skipping symbol stripping"; export PYI_NO_STRIP=1; }

VENV=.venv-build
[ -d "$VENV" ] || "$PY" -m venv "$VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -m pip install -q --upgrade pip
python -m pip install -q -r requirements.txt -r requirements-build.txt

VERSION="$(python packaging/info.py version)"
SLUG="$(python packaging/info.py slug)"
NAME="${SLUG}-v${VERSION}-linux-$(uname -m)"

rm -rf build dist
pyinstaller --noconfirm --clean music-downloader.spec

# package: <NAME>/{app/, install.sh, <slug>.desktop, icon.png}
STAGE="dist/pkg/${NAME}"
mkdir -p "$STAGE"
cp -r "dist/${SLUG}" "$STAGE/app"
cp packaging/install.sh "assets/${SLUG}.desktop" assets/icon.png "$STAGE/"
chmod +x "$STAGE/install.sh"
tar -C dist/pkg -czf "dist/${NAME}.tar.gz" "$NAME"
( cd dist && sha256sum "${NAME}.tar.gz" > "${NAME}.tar.gz.sha256" )

echo
echo "built:    dist/${NAME}.tar.gz"
echo "unpacked: $(du -sh "dist/${SLUG}" | cut -f1)   archive: $(du -h "dist/${NAME}.tar.gz" | cut -f1)"
echo "run now:  dist/${SLUG}/${SLUG}"
