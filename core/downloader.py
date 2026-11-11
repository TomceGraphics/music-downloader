"""yt-dlp download worker. Pure Python: no tkinter. All output goes through callbacks."""
import re
from pathlib import Path

from . import proc

_ERROR_RE = re.compile(r"^ERROR:", re.IGNORECASE)
_WARN_RE = re.compile(r"^WARNING:", re.IGNORECASE)
_ITEM_RE = re.compile(r"Downloading item (\d+) of (\d+)")
_PCT_RE = re.compile(r"([\d.]+)%")
_SPEED_ETA_RE = re.compile(r"\bat\s+(.+?)\s+ETA\s+(\S+)")
_DEST_RE = re.compile(r"Destination:\s*(.+?)\s*$")
_QUOTED_RE = re.compile(r'"(.+)"')
_SKIP_RE = re.compile(r"^\[download\]\s+(.*?)\s+has already been recorded")


def archive_path(folder: str) -> str:
    return str(Path(folder) / "archive.txt")


def base_cmd(ytdlp_cmd, js_args, ffmpeg_path: str, folder: str) -> list[str]:
    return list(ytdlp_cmd) + list(js_args) + [
        "--ffmpeg-location", ffmpeg_path,
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "--embed-thumbnail",
        "--embed-metadata",                 # (--add-metadata was an alias; removed)
        "--concurrent-fragments", "4",
        "--download-archive", archive_path(folder),
        "--ignore-errors",
        "--no-warnings",
        "--progress",
        "--newline",
        "-o", str(Path(folder) / "%(artist)s - %(title)s.%(ext)s"),
    ]


class _Tracker:
    """Turns yt-dlp output into track events for the UI:
    start / name / progress / stage / done / skip / fail  (all carry index=...)."""

    def __init__(self, cb):
        self.cb, self.idx, self.state, self.path = cb, 0, "idle", None

    def _emit(self, kind, **d):
        if self.cb:
            self.cb(kind, index=self.idx, **d)

    def begin(self, idx: int, total: int):
        self.finish()
        self.idx, self.state, self.path = idx, "active", None
        self._emit("start", total=total)

    def ensure(self):                      # single videos print no "item N of M" line
        if self.idx == 0:
            self.begin(1, 1)

    def finish(self):
        if self.idx and self.state == "active":
            self._emit("done", path=self.path)
            self.state = "done"

    def name(self, dest: str):
        self.ensure()
        self._emit("name", name=Path(dest).stem)

    def progress(self, pct: float, line: str):
        self.ensure()
        m = _SPEED_ETA_RE.search(line)
        speed, eta = (m.group(1), m.group(2)) if m else ("", "")
        self._emit("progress", pct=pct, speed="" if "Unknown" in speed else speed,
                   eta="" if "Unknown" in eta else eta)

    def stage(self, line: str):
        self.ensure()
        if "[ExtractAudio]" in line:
            m = _DEST_RE.search(line)
            if m:
                self.path = m.group(1)
            self._emit("stage", stage="converting")
        else:
            m = _QUOTED_RE.search(line)
            if m and not self.path:
                self.path = m.group(1)
            self._emit("stage", stage="tagging")

    def skip(self, label: str):
        self.ensure()
        self.state = "skipped"
        self._emit("skip", label=label)

    def fail(self, msg: str):
        self.ensure()
        self.state = "failed"
        self._emit("fail", msg=msg)


def _stream_proc(p, log_cb, progress_cb, counter_cb, track_cb=None) -> dict:
    total = current = failed = skipped = 0
    tracker = _Tracker(track_cb)

    for raw in p.stdout:
        line = raw.rstrip("\n")
        if not line:
            continue

        m = _ITEM_RE.search(line)
        if m:
            current, total = int(m.group(1)), int(m.group(2))
            counter_cb(current, total)
            log_cb(line + "\n", "info")
            tracker.begin(current, total)
            continue

        if "[download]" in line and "%" in line:
            m2 = _PCT_RE.search(line)
            if m2:
                try:
                    progress_cb(float(m2.group(1)))
                    tracker.progress(float(m2.group(1)), line)
                except Exception:
                    pass
            log_cb(line + "\n", "progress")
        elif "[ExtractAudio]" in line or "[EmbedThumbnail]" in line:
            tracker.stage(line)
            log_cb(line + "\n", "meta")
        elif _ERROR_RE.match(line):
            failed += 1
            tracker.fail(line.split("ERROR:", 1)[-1].strip()[:90])
            log_cb(line + "\n", "error")
        elif _WARN_RE.match(line):
            log_cb(line + "\n", "warning")
        elif "has already been recorded" in line:
            skipped += 1
            sm = _SKIP_RE.match(line)
            tracker.skip(sm.group(1) if sm else "")
            log_cb(line + "\n", "skip")
        elif "[download] Destination" in line or "Merging" in line:
            dm = _DEST_RE.search(line)
            if dm and "[download]" in line:
                tracker.name(dm.group(1))
            log_cb(line + "\n", "success")
        else:
            log_cb(line + "\n", "normal")

    p.wait()
    tracker.finish()

    if total == 0:
        total = 1
        current = 1 if p.returncode == 0 else 0

    return {"rc": p.returncode, "total": total, "current": current,
            "failed": failed, "skipped": skipped, "ok": max(0, current - failed)}


def run_download(url: str, folder: str, *, ytdlp_cmd, js_args, ffmpeg_path, cookie_spec,
                 log_cb, progress_cb, counter_cb, done_cb, track_cb=None) -> None:
    """cookie_spec: '' / 'none' for no cookies, else 'browser' or 'browser:/profile/path'."""
    if not ffmpeg_path:
        log_cb("ffmpeg not found — it may still be downloading (see log), or install ffmpeg\n", "error")
        done_cb(None); return
    if not ytdlp_cmd:
        log_cb("ERROR: yt-dlp not found — restart the app to download it, or install yt-dlp\n", "error")
        done_cb(None); return

    log_cb(f"{url}\n\n", "info")
    base = base_cmd(ytdlp_cmd, js_args, ffmpeg_path, folder)

    def _run(cmd) -> dict:
        return _stream_proc(proc.popen(cmd), log_cb, progress_cb, counter_cb, track_cb)

    if cookie_spec and cookie_spec != "none":
        log_cb(f"cookies from {cookie_spec.split(':')[0]}\n", "info")
        try:
            stats = _run(base + ["--cookies-from-browser", cookie_spec, url])
            tracks_downloaded = stats["ok"] + stats["skipped"]
            if stats["rc"] == 0 or tracks_downloaded > 0:
                if stats["rc"] != 0:
                    log_cb(f"\nfinished with some errors (exit {stats['rc']})\n", "warning")
                else:
                    log_cb("\ndownload complete\n", "success")
                done_cb(stats); return
            log_cb("\ncookie extraction failed — retrying without cookies...\n", "warning")
        except Exception as e:
            log_cb(f"error: {e}\n", "error"); done_cb(None); return

    log_cb("downloading without cookies (public content only)\n", "info")
    try:
        stats = _run(base + [url])
        if stats["rc"] == 0:
            log_cb("\ndownload complete\n", "success")
        else:
            log_cb(f"\nyt-dlp exited {stats['rc']}\n", "warning")
        done_cb(stats)
    except FileNotFoundError:
        log_cb("yt-dlp not found — restart the app to re-download it\n", "error"); done_cb(None)
    except Exception as e:
        log_cb(f"error: {e}\n", "error"); done_cb(None)
