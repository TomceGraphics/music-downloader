"""Browser cookie import selector (config keys: browser, browser_profile).
browser_profile is optional — set it in config.json for Flatpak browsers, e.g.
~/.var/app/org.mozilla.firefox/.mozilla/firefox/<profile>"""
import tkinter as tk

import customtkinter as ctk

from ui.theme import (C_DIM, C_HOVER, C_INPUT, C_SECONDARY, C_SURFACE, C_TEXT, F, R_MD, S1, S2)
from ui.widgets import Label
from .base import Feature

BROWSER_OPTIONS = ["none", "chrome", "edge", "firefox", "brave", "chromium", "opera", "vivaldi"]


class CookiesFeature(Feature):
    id = "cookies"
    name = "Cookie import"
    slot = "settings"
    config_defaults = {"browser": "none", "browser_profile": ""}

    def build_ui(self, parent, ctx):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x")
        Label(row, "Import cookies from your browser to access login-gated content.",
              size=12, color=C_SECONDARY).pack(side="left")
        self.var = tk.StringVar(value=ctx.get("browser", "none"))
        self.menu = ctk.CTkOptionMenu(
            row, values=BROWSER_OPTIONS, variable=self.var, font=F(12), fg_color=C_INPUT,
            button_color=C_INPUT, button_hover_color=C_HOVER, text_color=C_TEXT,
            dropdown_fg_color=C_SURFACE, dropdown_text_color=C_TEXT, dropdown_hover_color=C_HOVER,
            corner_radius=R_MD, width=130, height=32, command=lambda v: ctx.set("browser", v))
        self.menu.pack(side="right")
        Label(parent, "Close the browser before importing — it locks the cookie database while open.",
              size=11, color=C_DIM).pack(anchor="w", pady=(S2, 0))
