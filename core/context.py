"""AppContext — the ONLY object features talk to. No tkinter imports.

Every UI-touching method is thread-safe: it queues the update and the window shell
runs it on the Tk main thread (ctx.pump, polled by the shell). Feature authors
never need to think about threading."""
import queue
import threading

from . import binaries
from .config import Config


class AppContext:
    def __init__(self, config: Config):
        self.config = config
        self._q: queue.Queue = queue.Queue()
        self._ui = None
        self.ui_scale = 1.0          # set by the window; features may size bitmaps with it

    # ── wiring (used by ui/main_window.py only) ─────────────────────────
    def bind_ui(self, ui) -> None:
        self._ui = ui

    def pump(self) -> None:
        """Main thread only: run UI updates queued by worker threads."""
        while True:
            try:
                fn = self._q.get_nowait()
            except queue.Empty:
                return
            try:
                fn()
            except Exception:
                pass

    def _ui_call(self, _method: str, *args, **kw) -> None:
        # '_method' is underscored so event data such as name=... can pass through **kw
        self._q.put(lambda: getattr(self._ui, _method)(*args, **kw))

    # ── config (auto-saved) ─────────────────────────────────────────────
    def get(self, key: str, default=None):
        return self.config.get(key, default)

    def set(self, key: str, value) -> None:
        self.config.set(key, value)

    @property
    def output_folder(self) -> str:
        return self.config.get("output_folder")

    @output_folder.setter
    def output_folder(self, folder: str) -> None:
        self.config.set("output_folder", folder)

    # ── tools (resolved on each access, so they work right after first-run download) ──
    @property
    def ffmpeg_path(self) -> str | None:
        return binaries.ffmpeg_path(self.config)

    @property
    def ytdlp_cmd(self) -> list[str]:
        return binaries.ytdlp_cmd(self.config)

    @property
    def js_args(self) -> list[str]:
        return binaries.js_runtime_args(self.config)

    # ── UI feedback (thread-safe) ───────────────────────────────────────
    def log(self, msg: str, tag: str = "normal") -> None:
        """tags: success error warning info progress meta skip normal. Include the trailing \\n."""
        self._ui_call("log", msg, tag)

    def set_status(self, msg: str) -> None:
        self._ui_call("set_status", msg)

    def set_dot(self, color: str) -> None:
        self._ui_call("set_dot", color)

    def set_progress(self, pct: float) -> None:
        """0–100."""
        self._ui_call("set_progress", pct)

    def set_counter(self, cur: int, total: int) -> None:
        self._ui_call("set_counter", cur, total)

    def set_counter_text(self, text: str = "", color: str | None = None) -> None:
        self._ui_call("set_counter_text", text, color)

    def track_event(self, kind: str, **data) -> None:
        """Track list: reset | start | name | progress | stage | done | skip | fail | cover (index=...)."""
        self._ui_call("track_event", kind, **data)

    def set_footer(self, text: str, url: str | None = None) -> None:
        """Footer text at the bottom-left; with a url it becomes a clickable link."""
        self._ui_call("set_footer", text, url)

    def notify(self, title: str, body: str) -> None:
        """Desktop notification, only if enabled in settings and the window is not focused."""
        if self.config.get("notify_when_done", True):
            self._ui_call("notify_if_inactive", title, body)

    def on_main(self, fn, *args) -> None:
        """Run fn(*args) on the Tk main thread (use before touching your own widgets)."""
        self._q.put(lambda: fn(*args))

    def run_in_thread(self, fn, *args) -> threading.Thread:
        t = threading.Thread(target=fn, args=args, daemon=True)
        t.start()
        return t
