"""Locate yt-dlp, ffmpeg and a JavaScript runtime. No downloading here (see installer.py).

Lookup order per tool: config override -> system PATH -> managed copy in bin_dir()
(order flips if config 'prefer_system_binaries' is false)."""
import importlib.util
import shutil
import sys
from functools import lru_cache
from pathlib import Path

from . import proc
from .paths import FROZEN, IS_WINDOWS, bin_dir

EXE = ".exe" if IS_WINDOWS else ""


def managed(name: str) -> str | None:
    p = bin_dir() / (name + EXE)
    return str(p) if p.is_file() else None


def locate(name: str, cfg) -> tuple[str | None, str | None]:
    """Return (path, source) where source is 'config' | 'system' | 'managed' | None."""
    key = "ytdlp_path" if name == "yt-dlp" else f"{name}_path"
    override = cfg.get(key, "")
    if override and Path(override).is_file():
        return override, "config"
    pairs = [(shutil.which(name), "system"), (managed(name), "managed")]
    if not cfg.get("prefer_system_binaries", True):
        pairs.reverse()
    for path, src in pairs:
        if path:
            return path, src
    return None, None


def ytdlp_cmd(cfg) -> list[str]:
    """Command prefix for yt-dlp, or [] if none is available yet."""
    path, _ = locate("yt-dlp", cfg)
    if path:
        return [path]
    if not FROZEN and importlib.util.find_spec("yt_dlp"):   # dev fallback: pip-installed package
        return [sys.executable, "-m", "yt_dlp"]
    return []


@lru_cache(maxsize=8)
def has_mp3_encoder(ffmpeg: str) -> bool:
    """Some distro builds (e.g. Fedora's ffmpeg-free) cannot encode MP3."""
    try:
        return "libmp3lame" in proc.run([ffmpeg, "-hide_banner", "-encoders"], timeout=20).stdout
    except Exception:
        return False


def ffmpeg_path(cfg) -> str | None:
    """A usable ffmpeg (with ffprobe next to it, and MP3 support) or None."""
    path, src = locate("ffmpeg", cfg)
    if path and src == "system":
        has_probe = Path(path).with_name("ffprobe" + EXE).is_file()
        if not (has_probe and has_mp3_encoder(path)):
            return managed("ffmpeg")
    return path


def js_runtime_args(cfg) -> list[str]:
    """yt-dlp enables only Deno by default; point it at whatever we have.
    Verify syntax with: yt-dlp --help | grep -A3 js-runtimes"""
    if shutil.which("deno"):
        return []
    if managed("deno"):
        return ["--js-runtimes", f"deno:{managed('deno')}"]
    for rt in ("node", "bun"):
        if shutil.which(rt):
            return ["--js-runtimes", rt]
    return []


def has_js_runtime() -> bool:
    return bool(shutil.which("deno") or managed("deno") or shutil.which("node") or shutil.which("bun"))
