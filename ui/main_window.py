"""The window shell: nav, main page (URL, progress, tracks, details), settings page, footer.
Hosts features in slots ('source', 'settings', 'footer'); contains no feature logic."""
import tkinter as tk
import webbrowser

import customtkinter as ctk

from core import notify
from core.paths import IS_WINDOWS, resource_dir
from core.version import APP_NAME, VERSION, WM_CLASS
from . import icons, theme
from .log_panel import LogPanel
from .theme import (C_BG, C_BLUE, C_DIM, C_HOVER, C_INPUT, C_SECONDARY, C_SURFACE, C_TEXT,
                    R_MD, S1, S2, S3, S4, S5, S6, init_fonts)
from .track_list import TrackList
from .widgets import Card, Label, StatusPill, ghost_btn


class App(ctk.CTk):
    def __init__(self, ctx, features):
        super().__init__(className=WM_CLASS)       # WM_CLASS lets GNOME match the .desktop file
        init_fonts(self)
        try:
            scale = float(ctk.ScalingTracker.get_window_scaling(self))
        except Exception:
            scale = 1.0
        theme.set_scale(scale)
        ctx.ui_scale = scale
        self.title(f"{APP_NAME}  v{VERSION}")
        self.geometry("860x720")
        self.minsize(720, 600)
        self.configure(fg_color=C_BG)
        self._set_icon()

        self.ctx = ctx
        self._mode = theme.mode_index()
        self._page = "main"
        self._target = self._shown = 0.0
        self._animating = False
        ctx.bind_ui(self)
        self._build(features)
        self.bind("<Escape>", lambda _e: self.show_page("main"))
        self.bind("<Control-comma>", lambda _e: self.toggle_settings())
        self.after(40, self._pump)
        for feat in features:
            ctx.run_in_thread(self._startup, feat)

    # ── plumbing ──────────────────────────────────────────────────────────
    def _pump(self):
        self.ctx.pump()
        if theme.mode_index() != self._mode:                 # OS / user switched light <-> dark
            self._mode = theme.mode_index()
            self.logp.apply_theme()
        self.after(40, self._pump)

    def _startup(self, feat):
        try:
            feat.on_startup(self.ctx)
        except Exception as e:
            self.ctx.log(f"[sys] {feat.id} startup failed: {e}\n", "error")

    def _set_icon(self):
        png = resource_dir() / "assets" / "icon.png"
        ico = resource_dir() / "assets" / "icon.ico"
        try:
            if IS_WINDOWS and ico.exists():
                self.after(250, lambda: self.iconbitmap(str(ico)))   # CTk resets the icon at ~200 ms
            elif png.exists():
                self._icon = tk.PhotoImage(file=str(png))
                self.iconphoto(True, self._icon)
        except Exception:
            pass

    # ── layout ────────────────────────────────────────────────────────────
    def _build(self, features):
        slot = lambda name: [f for f in features if f.slot == name]

        nav = ctk.CTkFrame(self, fg_color=C_SURFACE, corner_radius=0, height=56)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)
        Label(nav, APP_NAME, size=14, weight="bold").pack(side="left", padx=S5)
        self.gear = ctk.CTkButton(nav, text="", image=icons.get("gear"), width=36, height=36, fg_color="transparent",
                                  hover_color=C_HOVER, corner_radius=R_MD, command=self.toggle_settings)
        self.gear.pack(side="right", padx=(S1, S4))
        self.pill = StatusPill(nav)
        self.pill.pack(side="right")

        # footer is packed BEFORE the pages so their requested height can never squeeze it out
        footer = ctk.CTkFrame(self, fg_color=C_SURFACE, corner_radius=0, height=52)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        self.footer_lbl = Label(footer, f"v{VERSION}", size=11, color=C_DIM)
        self.footer_lbl.pack(side="left", padx=S5)
        for f in slot("footer"):
            f.build_ui(footer, self.ctx)

        stage = ctk.CTkFrame(self, fg_color="transparent")
        stage.pack(fill="both", expand=True)

        # main page
        self.main = ctk.CTkFrame(stage, fg_color="transparent")
        src = ctk.CTkFrame(self.main, fg_color="transparent")
        src.pack(fill="x")
        for f in slot("source"):
            f.build_ui(src, self.ctx)
        prog = ctk.CTkFrame(self.main, fg_color="transparent")
        prog.pack(fill="x", pady=(S4, 0))
        self.progress = ctk.CTkProgressBar(prog, fg_color=C_INPUT, progress_color=C_BLUE, height=6, corner_radius=3)
        self.progress.pack(side="left", fill="x", expand=True)
        self.progress.set(0)
        self.info = Label(prog, "", size=11, color=C_SECONDARY)
        self.info.pack(side="right", padx=(S3, 0))
        self.tracks = TrackList(self.main)
        self.tracks.pack(fill="both", expand=True, pady=(S4, 0))
        self.logp = LogPanel(self.main)
        self.logp.pack(fill="x", pady=(S2, 0))

        # settings page: every 'settings' feature gets its own card
        self.settings = ctk.CTkFrame(stage, fg_color="transparent")
        head = ctk.CTkFrame(self.settings, fg_color="transparent")
        head.pack(fill="x", pady=(0, S4))
        ghost_btn(head, "Back", lambda: self.show_page("main"), width=84, icon="back").pack(side="left")
        Label(head, "Settings", size=16, weight="bold").pack(side="left", padx=S4)
        for f in slot("settings"):
            card = Card(self.settings, f.name)
            card.pack(fill="x", pady=(0, S3))
            f.build_ui(card.body, self.ctx)

        self.show_page("main")

    def show_page(self, page: str):
        self._page = page
        for name, frame in (("main", self.main), ("settings", self.settings)):
            frame.pack_forget()
        target = self.main if page == "main" else self.settings
        target.pack(fill="both", expand=True, padx=S6, pady=(S5, S4))

    def toggle_settings(self):
        self.show_page("main" if self._page == "settings" else "settings")

    # ── UI hooks, called on the main thread through AppContext ────────────
    def log(self, msg: str, tag: str = "normal"):
        self.logp.log(msg, tag)

    def clear_log(self):
        self.logp.clear()

    def set_status(self, msg: str):
        self.pill.set_text(msg)

    def set_dot(self, color):
        self.pill.set_dot(color)

    def set_progress(self, pct: float):
        """Eased: the bar glides to the target instead of jumping."""
        self._target = min(1.0, max(0.0, pct / 100))
        if not self._animating:
            self._animating = True
            self._tick()

    def _tick(self):
        diff = self._target - self._shown
        if abs(diff) < 0.002:
            self._shown = self._target
            self.progress.set(self._shown)
            self._animating = False
            return
        self._shown += diff * 0.22
        self.progress.set(self._shown)
        self.after(16, self._tick)

    def set_counter(self, cur: int, total: int):
        self.info.configure(text=f"{cur} / {total}", text_color=C_SECONDARY)

    def set_counter_text(self, text: str = "", color=None):
        self.info.configure(text=text, text_color=color or C_SECONDARY)

    def track_event(self, kind: str, **data):
        self.tracks.handle(kind, **data)

    def set_footer(self, text: str, url: str | None = None):
        self.footer_lbl.configure(text=text, text_color=C_BLUE if url else C_DIM, cursor="hand2" if url else "")
        self.footer_lbl.unbind("<Button-1>")
        if url:
            self.footer_lbl.bind("<Button-1>", lambda _e: webbrowser.open(url))

    def notify_if_inactive(self, title: str, body: str):
        if self.focus_displayof() is None:                    # only when you are looking elsewhere
            self.ctx.run_in_thread(notify.send, title, body)
