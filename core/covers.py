"""Pull the embedded cover out of an MP3 as a small square PNG using ffmpeg.
Tk reads PNG natively, so the app needs no Pillow. Plain Python (no tkinter)."""
import atexit
import hashlib
import shutil
import tempfile
from pathlib import Path

from . import proc

_dir: Path | None = None


def _cache_dir() -> Path:
    global _dir
    if _dir is None:
        _dir = Path(tempfile.mkdtemp(prefix="music-downloader-covers-"))
        atexit.register(shutil.rmtree, _dir, True)
    return _dir


def extract_cover(ffmpeg: str, mp3: str, px: int = 40) -> str | None:
    """Return the path of a px x px PNG (centre-cropped), or None if there is no cover."""
    key = hashlib.md5(mp3.encode("utf-8"), usedforsecurity=False).hexdigest()
    out = _cache_dir() / f"{key}_{px}.png"
    cmd = [ffmpeg, "-y", "-v", "error", "-i", mp3, "-an", "-frames:v", "1",
           "-vf", f"scale={px}:{px}:force_original_aspect_ratio=increase,crop={px}:{px}", str(out)]
    try:
        r = proc.run(cmd, timeout=20)
        return str(out) if r.returncode == 0 and out.is_file() else None
    except Exception:
        return None
