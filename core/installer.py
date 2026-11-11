"""First-run download of yt-dlp / ffmpeg / deno into bin_dir(), plus the yt-dlp updater.
Plain Python (no tkinter). Everything reports through log(msg, tag)."""
import platform
import shutil
import stat
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

from . import binaries, proc
from .paths import IS_WINDOWS, bin_dir

EXE = binaries.EXE
_GH = "https://github.com"
_FF = f"{_GH}/yt-dlp/FFmpeg-Builds/releases/download/latest"
# ── ONE place to change download sources ────────────────────────────────────
if IS_WINDOWS:
    YTDLP_URL = f"{_GH}/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
    FFMPEG_URL = f"{_FF}/ffmpeg-master-latest-win64-gpl.zip"          # ~160 MB
    DENO_URL = f"{_GH}/denoland/deno/releases/latest/download/deno-x86_64-pc-windows-msvc.zip"
else:
    YTDLP_URL = f"{_GH}/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux"
    FFMPEG_URL = f"{_FF}/ffmpeg-master-latest-linux64-gpl.tar.xz"     # ~120 MB
    DENO_URL = f"{_GH}/denoland/deno/releases/latest/download/deno-x86_64-unknown-linux-gnu.zip"
SUPPORTED = platform.machine().lower() in ("x86_64", "amd64")


def _chmod_x(p: Path) -> None:
    if not IS_WINDOWS:
        p.chmod(p.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _download(url: str, dest: Path, log, label: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "music-downloader"})
    log(f"[sys] downloading {label}...\n", "info")
    with urllib.request.urlopen(req, timeout=30) as r, open(part, "wb") as f:
        total = int(r.headers.get("Content-Length") or 0)
        done, mark = 0, 25
        while chunk := r.read(1 << 16):
            f.write(chunk)
            done += len(chunk)
            if total and done * 100 // total >= mark:
                log(f"[sys] {label}: {mark}%\n", "progress")
                mark += 25
    part.replace(dest)
    _chmod_x(dest)


def _unpack(archive: Path, wanted: set[str], out: Path) -> None:
    def save(src, name):
        tmp = out / (name + ".part")
        with open(tmp, "wb") as f:
            shutil.copyfileobj(src, f)
        tmp.replace(out / name)
        _chmod_x(out / name)

    if archive.name.endswith(".zip"):
        with zipfile.ZipFile(archive) as z:
            for m in z.namelist():
                if not m.endswith("/") and Path(m).name in wanted:
                    with z.open(m) as src:
                        save(src, Path(m).name)
    else:
        with tarfile.open(archive) as t:
            for m in t:
                if m.isfile() and Path(m.name).name in wanted:
                    save(t.extractfile(m), Path(m.name).name)


def _fetch_archive(url: str, names: list[str], log, label: str) -> None:
    out = bin_dir()
    arc = out / url.rsplit("/", 1)[1]
    try:
        _download(url, arc, log, label)
        log(f"[sys] unpacking {label}...\n", "info")
        _unpack(arc, {n + EXE for n in names}, out)
    finally:
        arc.unlink(missing_ok=True)
    missing = [n for n in names if not (out / (n + EXE)).is_file()]
    if missing:
        raise RuntimeError(f"{label}: {', '.join(missing)} not found in archive")


def ensure(cfg, log) -> None:
    """Download whatever is missing. Safe to call on every start."""
    if not SUPPORTED:
        if not (binaries.ytdlp_cmd(cfg) and binaries.ffmpeg_path(cfg)):
            log("[sys] auto-download supports x86_64 only — install yt-dlp and ffmpeg "
                "(with MP3 support) from your package manager\n", "warning")
        return
    try:
        if not binaries.ytdlp_cmd(cfg):
            _download(YTDLP_URL, bin_dir() / ("yt-dlp" + EXE), log, "yt-dlp")
        if not binaries.ffmpeg_path(cfg):
            _fetch_archive(FFMPEG_URL, ["ffmpeg", "ffprobe"], log, "ffmpeg")
        if cfg.get("fetch_deno", True) and not binaries.has_js_runtime():
            _fetch_archive(DENO_URL, ["deno"], log, "deno (JS runtime for YouTube)")
    except Exception as e:
        log(f"[sys] setup failed: {e}\n", "error")


def _version(cmd: list[str]) -> str:
    try:
        return proc.run(cmd + ["--version"], timeout=20).stdout.strip()
    except Exception:
        return "?"


def update_ytdlp(cfg, log) -> None:
    cmd = binaries.ytdlp_cmd(cfg)
    if not cmd:
        log("[sys] yt-dlp not found — update skipped\n", "warning")
        return
    _, src = binaries.locate("yt-dlp", cfg)
    if src in ("system", "config"):          # not ours to modify
        log(f"[sys] using {src} yt-dlp {_version(cmd)} — update it with its own package manager\n", "info")
        return
    if src == "managed":
        update_cmd = cmd + ["-U"]            # self-updates in place, in a writable dir
    elif sys.prefix != sys.base_prefix:      # source mode inside a venv
        update_cmd = [sys.executable, "-m", "pip", "install", "-U", "yt-dlp", "-q"]
    else:
        log(f"[sys] yt-dlp {_version(cmd)} (not in a venv — not touching it)\n", "info")
        return
    try:
        r = proc.run(update_cmd, timeout=120)
        out = (r.stdout + r.stderr).strip()
        if "up to date" in out.lower() or (src is None and r.returncode == 0):
            log("[sys] yt-dlp up to date\n", "success")
        elif r.returncode == 0:
            log("[sys] yt-dlp updated successfully\n", "success")
        else:
            log(f"[sys] yt-dlp update: {out[:120]}\n", "warning")
    except Exception as e:
        log(f"[sys] yt-dlp update failed: {e}\n", "warning")
