"""Settings toggle for the 'download finished' desktop notification (config key: notify_when_done).
The notification itself is sent by ctx.notify(), which only fires while the window is not focused."""
import customtkinter as ctk

from ui.theme import C_BLUE, C_SECONDARY, C_INPUT, F
from .base import Feature


class NotifyFeature(Feature):
    id = "notify"
    name = "Notifications"
    slot = "settings"
    config_defaults = {"notify_when_done": True}

    def build_ui(self, parent, ctx):
        self.sw = ctk.CTkSwitch(
            parent, text="Notify me when a download finishes (only if this window is in the background)",
            font=F(12), text_color=C_SECONDARY, progress_color=C_BLUE, button_color=("#ffffff", "#f2f2f2"),
            fg_color=C_INPUT, command=lambda: ctx.set("notify_when_done", bool(self.sw.get())))
        if ctx.get("notify_when_done", True):
            self.sw.select()
        self.sw.pack(anchor="w")
