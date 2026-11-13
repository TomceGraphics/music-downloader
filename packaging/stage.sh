#!/usr/bin/env bash
# Shared by build-deb.sh and build-rpm.sh: lay the PyInstaller output out as an FHS tree.
#   usage: packaging/stage.sh <dest-dir>      (needs dist/<slug>/ from ./build.sh)
set -euo pipefail
cd "$(dirname "$0")/.."
SLUG="$(python3 packaging/info.py slug)"
DEST="$1"
[ -x "dist/$SLUG/$SLUG" ] || { echo "dist/$SLUG/$SLUG not found: run ./build.sh first" >&2; exit 1; }

rm -rf "$DEST"
mkdir -p "$DEST/opt" "$DEST/usr/bin" "$DEST/usr/share/applications" \
         "$DEST/usr/share/icons/hicolor/512x512/apps" "$DEST/usr/share/doc/$SLUG" \
         "$DEST/usr/share/licenses/$SLUG"
cp -r "dist/$SLUG" "$DEST/opt/$SLUG"
ln -s "/opt/$SLUG/$SLUG" "$DEST/usr/bin/$SLUG"
sed 's|"@EXEC@"|'"$SLUG"'|; s|@ICON@|'"$SLUG"'|' "assets/$SLUG.desktop" > "$DEST/usr/share/applications/$SLUG.desktop"
install -m 644 assets/icon.png "$DEST/usr/share/icons/hicolor/512x512/apps/$SLUG.png"
install -m 644 LICENSE "$DEST/usr/share/licenses/$SLUG/LICENSE"
install -m 644 LICENSE "$DEST/usr/share/doc/$SLUG/copyright"
install -m 644 THIRD_PARTY_NOTICES.md "$DEST/usr/share/doc/$SLUG/"
chmod -R u+rwX,go+rX,go-w "$DEST"
