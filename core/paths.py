"""Where things live: frozen/source detection and per-user directories."""
import os
import sys
from pathlib import Path

from .version import APP_NAME, APP_SLUG

FROZEN = getattr(sys, "frozen", False)
IS_WINDOWS = sys.platform.startswith("win")
_WIN_NAME = APP_NAME.replace(" ", "")


def resource_dir() -> Path:
    """Read-only bundled assets (assets/icon.png ...)."""
    if FROZEN:
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parent.parent


def _xdg(var: str, fallback: str) -> Path:
    return Path(os.environ.get(var) or Path.home() / fallback)


def config_dir() -> Path:
    """~/.config/music-downloader  |  %APPDATA%\\MusicDownloader"""
    if IS_WINDOWS:
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
        return base / _WIN_NAME
    return _xdg("XDG_CONFIG_HOME", ".config") / APP_SLUG


def data_dir() -> Path:
    """~/.local/share/music-downloader  |  %LOCALAPPDATA%\\MusicDownloader"""
    if IS_WINDOWS:
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
        return base / _WIN_NAME
    return _xdg("XDG_DATA_HOME", ".local/share") / APP_SLUG


def bin_dir() -> Path:
    """Downloaded yt-dlp / ffmpeg / deno live here (writable, survives updates)."""
    return data_dir() / "bin"


def default_music_dir() -> Path:
    return Path.home() / "Music"


def legacy_config_file() -> Path:
    """Old location (next to the exe / script) — read once for migration."""
    base = Path(sys.executable).parent if FROZEN else resource_dir()
    return base / "config.json"
