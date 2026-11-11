"""Collapsible log ("Details"). Hidden by default; the button turns amber when something needs attention."""
import tkinter as tk

import customtkinter as ctk

from . import icons, theme
from .theme import (C_BORDER, C_LOG_BG, C_SECONDARY, C_SELECT, C_WARNING, F, FMONO, LOG_TAGS,
                    R_MD, S2, S3, pick)
from datetime import datetime


class LogPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.open = False
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x")
        self.toggle_btn = ctk.CTkButton(bar, text="Details", font=F(12), width=90, height=28, anchor="w",
                                        fg_color="transparent", hover_color=("#ebebe8", "#2d2d2d"),
                                        text_color=C_SECONDARY, corner_radius=R_MD, compound="right",
                                        image=icons.get("chev-down"), command=self.toggle)
        self.toggle_btn.pack(side="left")
        self.clear_btn = ctk.CTkButton(bar, text="Clear", font=F(11), width=56, height=24, fg_color="transparent",
                                       hover_color=("#ebebe8", "#2d2d2d"), text_color=C_SECONDARY,
                                       corner_radius=R_MD, command=self.clear)

        self.wrap = ctk.CTkFrame(self, fg_color=C_LOG_BG, corner_radius=R_MD, border_color=C_BORDER, border_width=1)
        self.box = tk.Text(self.wrap, font=FMONO(11), relief="flat", borderwidth=0, highlightthickness=0,
                           wrap="word", state="disabled", padx=S3 + 2, pady=S2 + 2, height=8)
        self.box.configure(font=(FMONO(11)[0], -round(14 * theme.SCALE)))
        self.box.pack(fill="both", expand=True, padx=1, pady=1)
        self.apply_theme()

    def apply_theme(self):
        self.box.configure(bg=pick(C_LOG_BG), fg=pick(C_SECONDARY), insertbackground=pick(C_SECONDARY),
                           selectbackground=pick(C_SELECT))
        for tag, col in LOG_TAGS:
            self.box.tag_config(tag, foreground=pick(col))

    def toggle(self):
        self.open = not self.open
        if self.open:
            self.wrap.pack(fill="x", pady=(S2, 0))
            self.clear_btn.pack(side="right")
            self.toggle_btn.configure(image=icons.get("chev-up"), text_color=C_SECONDARY)
        else:
            self.wrap.pack_forget()
            self.clear_btn.pack_forget()
            self.toggle_btn.configure(image=icons.get("chev-down"))

    def log(self, msg: str, tag: str = "normal"):
        self.box.configure(state="normal")
        self.box.insert("end", f"{datetime.now():%H:%M:%S}  ", "ts")
        self.box.insert("end", msg, tag)
        self.box.see("end")
        self.box.configure(state="disabled")
        if tag in ("error", "warning") and not self.open:
            self.toggle_btn.configure(text_color=C_WARNING)

    def clear(self):
        self.box.configure(state="normal")
        self.box.delete("1.0", "end")
        self.box.configure(state="disabled")
