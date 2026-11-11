"""URL entry, Paste and Download. The worker is core.downloader.run_download; the track list
is fed from its structured events."""
import re
from pathlib import Path

from core.covers import extract_cover
from core.downloader import run_download
from ui.theme import C_GREEN, C_RED, C_WARNING, S2
from ui.widgets import ghost_btn, primary_btn, text_input
from .base import Feature

_YT_URL = re.compile(r"^https?://(www\.|m\.|music\.)?(youtube\.com|youtu\.be)/\S+$", re.IGNORECASE)


class DownloadFeature(Feature):
    id = "download"
    name = "Source URL"
    slot = "source"

    def build_ui(self, parent, ctx):
        self.ctx = ctx
        self.busy = False
        self.total = 1
        self._last_clip = ""
        parent.grid_columnconfigure(0, weight=1)
        self.entry = text_input(parent, placeholder="Paste a YouTube or YouTube Music link", height=46)
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.bind("<Return>", lambda _e: self.start())
        ghost_btn(parent, "Paste", self.paste, width=88, height=46, icon="paste").grid(row=0, column=1, padx=(S2, 0))
        self.btn = primary_btn(parent, "Download", self.start, width=140, height=46, icon="download")
        self.btn.grid(row=0, column=2, padx=(S2, 0))
        self.top = parent.winfo_toplevel()
        self.top.bind("<FocusIn>", self._on_focus, add="+")

    # ── clipboard ────────────────────────────────────────────────────────
    def _clip(self) -> str:
        try:
            return self.top.clipboard_get().strip()
        except Exception:
            return ""

    def paste(self):
        text = self._clip()
        if text:
            self.entry.delete(0, "end")
            self.entry.insert(0, text)

    def _on_focus(self, event):
        """Window regained focus: if you copied a YouTube link, drop it in (only when the field is empty)."""
        if event.widget is not self.top or self.busy or self.entry.get().strip():
            return
        clip = self._clip()
        if clip and clip != self._last_clip and _YT_URL.match(clip):
            self._last_clip = clip
            self.entry.insert(0, clip)

    # ── download ─────────────────────────────────────────────────────────
    def start(self):                                  # main thread
        ctx = self.ctx
        if self.busy:
            return
        url = self.entry.get().strip()
        if not url:
            ctx.log("[err] enter a URL first\n", "error"); return

        folder = ctx.output_folder
        Path(folder).mkdir(parents=True, exist_ok=True)
        browser = ctx.get("browser", "none")
        profile = (ctx.get("browser_profile", "") or "").strip()
        cookie = browser if browser == "none" or not profile else f"{browser}:{profile}"

        self.busy = True
        self.total = 1
        self.btn.configure(state="disabled", text="Downloading…")
        ctx.track_event("reset")
        ctx.set_progress(0)
        ctx.set_counter_text("")
        ctx.set_status("downloading")
        ctx.set_dot(C_WARNING)
        ctx.run_in_thread(self._work, url, folder, cookie)

    def _work(self, url, folder, cookie):             # worker thread
        ctx = self.ctx
        run_download(url, folder, ytdlp_cmd=ctx.ytdlp_cmd, js_args=ctx.js_args,
                     ffmpeg_path=ctx.ffmpeg_path, cookie_spec=cookie, log_cb=ctx.log,
                     progress_cb=lambda _p: None, counter_cb=lambda *_a: None,
                     done_cb=self._done, track_cb=self._on_track)

    def _on_track(self, kind, index=1, **d):          # worker thread
        ctx = self.ctx
        if kind == "start":
            self.total = max(1, d.get("total", 1))
            ctx.set_progress((index - 1) / self.total * 100)
        elif kind == "progress":
            ctx.set_progress(((index - 1) + d["pct"] / 100) / self.total * 100)
            parts = [f"{index} / {self.total}", d.get("speed", ""), f"ETA {d['eta']}" if d.get("eta") else ""]
            ctx.set_counter_text("  ·  ".join(p for p in parts if p))
        elif kind == "done" and d.get("path"):
            ctx.run_in_thread(self._cover, index, d["path"])
        ctx.track_event(kind, index=index, **d)

    def _cover(self, index, path):                    # worker thread: ffmpeg -> small PNG
        ffmpeg = self.ctx.ffmpeg_path
        png = extract_cover(ffmpeg, path, round(40 * self.ctx.ui_scale)) if ffmpeg else None
        if png:
            self.ctx.track_event("cover", index=index, path=png)

    def _done(self, stats):                           # worker thread
        ctx = self.ctx
        ctx.on_main(self._reset_button)
        if stats is None:
            ctx.set_progress(0); ctx.set_status("failed"); ctx.set_dot(C_RED); return

        total, failed, skipped = stats["total"], stats["failed"], stats["skipped"]
        downloaded = max(0, stats["ok"] - skipped)
        clean = failed == 0
        ctx.set_progress(100 if stats["ok"] > 0 else 0)
        ctx.set_dot(C_GREEN if clean else C_WARNING)
        if total > 1:
            parts = [f"{downloaded} downloaded"] + ([f"{skipped} skipped"] if skipped else []) \
                    + ([f"{failed} failed"] if failed else [])
            summary = "  ·  ".join(parts)
            ctx.set_counter_text(summary, C_GREEN if clean else C_WARNING)
            ctx.set_status(summary)
            ctx.notify("Download finished", summary)
        else:
            ctx.set_counter_text("")
            ctx.set_status("done" if clean else "finished with errors")
            ctx.notify("Download finished" if clean else "Download finished with errors", "1 track")

    def _reset_button(self):                          # main thread
        self.busy = False
        self.btn.configure(state="normal", text="Download")
