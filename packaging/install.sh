#!/usr/bin/env bash
# User-local install, no sudo:  ./install.sh   |   ./install.sh --uninstall
# Adds the app to your menu (GNOME/KDE) and a `music-downloader` command in ~/.local/bin.
set -euo pipefail

SLUG=music-downloader
HERE="$(cd "$(dirname "$0")" && pwd)"
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
APP_DIR="$HOME/.local/opt/$SLUG"
BIN="$HOME/.local/bin/$SLUG"
DESKTOP="$DATA/applications/$SLUG.desktop"
ICON="$DATA/icons/hicolor/512x512/apps/$SLUG.png"

refresh() { command -v update-desktop-database >/dev/null && update-desktop-database "$DATA/applications" || true; }

if [ "${1:-}" = "--uninstall" ]; then
  rm -rf "$APP_DIR" "$BIN" "$DESKTOP" "$ICON"
  refresh
  echo "Removed. Your music, config (~/.config/$SLUG) and downloaded tools (~/.local/share/$SLUG) were left alone."
  exit 0
fi

[ -x "$HERE/app/$SLUG" ] || { echo "Run this from the extracted release folder (app/ not found)."; exit 1; }

mkdir -p "$HOME/.local/opt" "$HOME/.local/bin" "$DATA/applications" "$(dirname "$ICON")"
rm -rf "$APP_DIR"
cp -r "$HERE/app" "$APP_DIR"
ln -sf "$APP_DIR/$SLUG" "$BIN"
install -m 644 "$HERE/icon.png" "$ICON"
sed "s|@EXEC@|$APP_DIR/$SLUG|; s|@ICON@|$ICON|" "$HERE/$SLUG.desktop" > "$DESKTOP"
chmod 644 "$DESKTOP"
refresh

echo "Installed. Find 'Music Downloader' in your app menu, or run: $SLUG"
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) echo "Note: add ~/.local/bin to your PATH to use the command." ;; esac
