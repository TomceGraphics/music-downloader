"""Output folder picker (config key: output_folder). Lives on the settings page."""
import customtkinter as ctk
from tkinter import filedialog

from ui.theme import C_INPUT, C_SECONDARY, R_MD, S2, S3
from ui.widgets import Label, ghost_btn
from .base import Feature


class OutputFolderFeature(Feature):
    id = "output_folder"
    name = "Output folder"
    slot = "settings"

    def build_ui(self, parent, ctx):
        self.ctx = ctx
        row = ctk.CTkFrame(parent, fg_color=C_INPUT, corner_radius=R_MD)
        row.pack(fill="x")
        self.lbl = Label(row, ctx.output_folder, size=12, color=C_SECONDARY, anchor="w")
        self.lbl.pack(side="left", fill="x", expand=True, padx=S3, pady=S2)
        ghost_btn(row, "Browse", self._browse, width=80, height=30, icon="folder").pack(side="right", padx=S2, pady=S2)

    def _browse(self):
        folder = filedialog.askdirectory(initialdir=self.ctx.output_folder)
        if folder:
            self.ctx.output_folder = folder
            self.lbl.configure(text=folder)
