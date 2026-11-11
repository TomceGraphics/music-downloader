"""Scrollable track list with per-row state. Pure presentation: fed by ctx.track_event(...)."""
import tkinter as tk

import customtkinter as ctk

from . import icons
from .theme import (C_BLUE, C_DIM, C_HOVER, C_INPUT, C_RED, C_SECONDARY, C_SURFACE, C_TEXT,
                    F, R_MD, R_SM, S1, S2, S3, S4, S6)
from .widgets import Label

MAX_ROWS = 150          # older rows are dropped so huge playlists stay snappy
COVER = 40


def split_name(name: str) -> tuple[str, str]:
    """'Artist - Title' -> (title, artist)."""
    if " - " in name:
        artist, title = name.split(" - ", 1)
        return title.strip(), artist.strip()
    return name.strip(), ""


class TrackRow(ctk.CTkFrame):
    def __init__(self, parent, index: int):
        super().__init__(parent, fg_color=C_SURFACE, corner_radius=R_MD)
        self.artist = ""
        self._photo = None
        self.grid_columnconfigure(1, weight=1)

        # fixed square box; the label inside shows the note icon, then the cover bitmap
        self.cover_box = ctk.CTkFrame(self, width=COVER, height=COVER, corner_radius=R_SM, fg_color=C_INPUT)
        self.cover_box.grid(row=0, column=0, rowspan=3, padx=S3, pady=S2)
        self.cover_box.pack_propagate(False)
        self.cover = ctk.CTkLabel(self.cover_box, text="", image=icons.get("note"), corner_radius=0,
                                  fg_color="transparent")
        self.cover.place(relx=0.5, rely=0.5, anchor="center")
        self.title = Label(self, f"Track {index}", size=13, weight="bold", anchor="w")
        self.title.grid(row=0, column=1, sticky="ew", pady=(S2, 0))
        self.sub = Label(self, "starting…", size=11, color=C_SECONDARY, anchor="w")
        self.sub.grid(row=1, column=1, sticky="ew")
        self.bar = ctk.CTkProgressBar(self, height=3, corner_radius=2, fg_color=C_INPUT, progress_color=C_BLUE)
        self.bar.set(0)
        self.bar.grid(row=2, column=1, sticky="ew", padx=(0, S3), pady=(S1, S2))
        # right-hand cell: either a percentage or a state icon (separate labels: CTk cannot clear an image)
        self.pct = Label(self, "", size=12, color=C_SECONDARY, width=40)
        self.icon = ctk.CTkLabel(self, text="", image=None, width=40)
        self.pct.grid(row=0, column=2, rowspan=3, padx=(0, S3))
        self.icon.grid(row=0, column=2, rowspan=3, padx=(0, S3))
        self.pct.grid_remove()
        self.icon.grid_remove()

    def _right(self, pct: str = "", icon: str | None = None):
        """Show a percentage or a state icon in the right-hand cell (or nothing)."""
        self.pct.grid_remove()
        self.icon.grid_remove()
        if icon:
            self.icon.configure(image=icons.get(icon))
            self.icon.grid()
        elif pct:
            self.pct.configure(text=pct)
            self.pct.grid()

    def _sub(self, *parts, color=C_SECONDARY):
        self.sub.configure(text="  ·  ".join(p for p in parts if p), text_color=color)

    def set_name(self, name: str):
        title, self.artist = split_name(name)
        self.title.configure(text=title or name)
        self._sub(self.artist, "downloading")

    def set_progress(self, pct: float, speed: str = "", eta: str = ""):
        self.bar.grid()
        self.bar.set(pct / 100)
        self._right(pct=f"{pct:.0f}%")
        self._sub(self.artist, speed, f"ETA {eta}" if eta else "")

    def set_stage(self, stage: str):
        self.bar.set(1)
        self._sub(self.artist, "Converting to MP3…" if stage == "converting" else "Embedding cover and tags…")

    def set_done(self):
        self.bar.grid_remove()
        self._right(icon="check")
        self._sub(self.artist or "Done")

    def set_skipped(self, label: str = ""):
        self.bar.grid_remove()
        self._right(icon="skip")
        self.title.configure(text_color=C_SECONDARY)
        self._sub("Already in your archive")

    def set_failed(self, msg: str = ""):
        self.bar.grid_remove()
        self._right(icon="cross")
        self._sub(msg or "Failed", color=C_RED)

    def set_cover(self, path: str):
        try:
            self._photo = tk.PhotoImage(file=path)
            self.cover.configure(image=self._photo)
        except Exception:
            pass


class TrackList(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x", pady=(0, S2))
        Label(head, "TRACKS", size=10, weight="bold", color=C_SECONDARY).pack(side="left")
        self.count = Label(head, "", size=11, color=C_SECONDARY)
        self.count.pack(side="right")

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0,
                                             scrollbar_button_color=C_HOVER, scrollbar_button_hover_color=C_DIM)
        self.scroll.pack(fill="both", expand=True)
        self.rows: dict[int, TrackRow] = {}
        self.empty = ctk.CTkFrame(self.scroll, fg_color="transparent")
        ctk.CTkLabel(self.empty, text="", image=icons.get("note")).pack(pady=(S6, S2))
        Label(self.empty, "No tracks yet", size=14, weight="bold").pack()
        Label(self.empty, "Paste a playlist or video link above and press Download.",
              size=12, color=C_SECONDARY).pack(pady=(S1, 0))
        self.empty.pack(fill="x", pady=S6)

    def reset(self):
        for row in self.rows.values():
            row.destroy()
        self.rows.clear()
        self.count.configure(text="")
        self.empty.pack(fill="x", pady=S6)

    def _row(self, index: int) -> TrackRow:
        if index not in self.rows:
            self.empty.pack_forget()
            row = TrackRow(self.scroll, index)
            row.pack(fill="x", pady=(0, S2))
            self.rows[index] = row
            if len(self.rows) > MAX_ROWS:
                self.rows.pop(min(self.rows)).destroy()
            self._schedule_scroll()
        return self.rows[index]

    def _schedule_scroll(self):
        """Keep the newest row in view. Debounced; refreshes the scroll region first so it is never stale."""
        if getattr(self, "_scroll_job", None):
            self.after_cancel(self._scroll_job)
        self._scroll_job = self.after(80, self._scroll_end)

    def _scroll_end(self):
        self._scroll_job = None
        cv = self.scroll._parent_canvas
        cv.update_idletasks()
        cv.configure(scrollregion=cv.bbox("all"))
        cv.yview_moveto(1.0)

    def _at_end(self) -> bool:
        # also 'following' while a scroll is already pending, so late layout changes don't drop us behind
        return getattr(self, "_scroll_job", None) is not None or self.scroll._parent_canvas.yview()[1] >= 0.97

    def handle(self, kind: str, index: int = 1, **d):
        if kind == "reset":
            return self.reset()
        at_end = self._at_end()               # follow the newest row, unless you scrolled up to look
        row = self._row(index)
        if kind == "start":
            self.count.configure(text=f"{index} of {d.get('total', index)}")
        elif kind == "name":
            row.set_name(d["name"])
        elif kind == "progress":
            row.set_progress(d["pct"], d.get("speed", ""), d.get("eta", ""))
        elif kind == "stage":
            row.set_stage(d["stage"])
        elif kind == "done":
            row.set_done()
        elif kind == "skip":
            row.set_skipped(d.get("label", ""))
        elif kind == "fail":
            row.set_failed(d.get("msg", ""))
        elif kind == "cover":
            row.set_cover(d["path"])
        if at_end:
            self._schedule_scroll()
