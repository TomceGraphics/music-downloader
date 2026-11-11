"""Appearance: follow the OS light/dark setting, or force one (config key: appearance)."""
import customtkinter as ctk

from ui import theme
from ui.theme import C_BLUE, C_HOVER, C_INPUT, C_SECONDARY, C_TEXT, F, R_MD
from ui.widgets import Label
from .base import Feature

CHOICES = {"System": "system", "Light": "light", "Dark": "dark"}


class AppearanceFeature(Feature):
    id = "appearance"
    name = "Appearance"
    slot = "settings"
    config_defaults = {"appearance": "system"}

    def build_ui(self, parent, ctx):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x")
        Label(row, "Theme", size=12, color=C_SECONDARY).pack(side="left")
        current = next((k for k, v in CHOICES.items() if v == ctx.get("appearance", "system")), "System")

        def change(label):
            ctx.set("appearance", CHOICES[label])
            theme.apply_appearance(CHOICES[label])

        self.seg = ctk.CTkSegmentedButton(
            row, values=list(CHOICES), command=change, font=F(12), height=32, corner_radius=R_MD,
            fg_color=C_INPUT, selected_color=C_BLUE, selected_hover_color=C_BLUE,
            unselected_color=C_INPUT, unselected_hover_color=C_HOVER, text_color=C_TEXT)
        self.seg.set(current)
        self.seg.pack(side="right")
